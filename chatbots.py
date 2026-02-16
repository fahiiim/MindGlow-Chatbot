"""
MindGlow Chatbot Engines — Core logic for Reflect and Inner Learning.
Handles prompt assembly, OpenAI calls, filtering, crisis check, and memory context.
"""

from openai import AsyncOpenAI
from config import (
    get_settings,
    REFLECT_SYSTEM_PROMPT,
    INNER_LEARNING_SYSTEM_PROMPT,
    CRISIS_RESOURCES,
)
from models import (
    ChatRequest,
    ChatResponse,
    ChatbotType,
    Message,
    SummaryRequest,
    SummaryResponse,
    FilterLogEntry,
    CrisisLogEntry,
)
from memory import get_embedding, get_embeddings_batch, build_memory_context, semantic_search
from filters import detect_language, check_for_directives, detect_crisis, create_filter_log, create_crisis_log

MAX_FILTER_RETRIES = 2


def _get_system_prompt(chatbot: ChatbotType) -> str:
    if chatbot == ChatbotType.REFLECT:
        return REFLECT_SYSTEM_PROMPT
    return INNER_LEARNING_SYSTEM_PROMPT


def _build_openai_messages(
    system_prompt: str,
    memory_context: str,
    past_summaries: list[str],
    conversation_history: list[Message],
    current_message: str,
    language: str,
    max_history: int | None = None,
) -> list[dict]:
    """Assemble the full message list for OpenAI API call."""
    settings = get_settings()
    max_hist = max_history or settings.MAX_CONTEXT_MESSAGES

    messages = [{"role": "system", "content": system_prompt}]

    # Inject past session summaries as system context
    if past_summaries:
        summaries_text = "\n\n".join(
            f"[Past session reflection {i+1}]: {s}" for i, s in enumerate(past_summaries[-3:])
        )
        messages.append({
            "role": "system",
            "content": f"[Past session summaries — weave gently, never list them]\n{summaries_text}",
        })

    # Inject semantically relevant memory
    if memory_context:
        messages.append({"role": "system", "content": memory_context})

    # Language instruction
    if language and language != "en":
        messages.append({
            "role": "system",
            "content": f"The user is writing in '{language}'. Respond in the same language.",
        })

    # Conversation history (trimmed)
    history = conversation_history[-max_hist:]
    for msg in history:
        messages.append({"role": msg.role.value, "content": msg.content})

    # Current user message
    messages.append({"role": "user", "content": current_message})
    return messages


async def generate_response(
    client: AsyncOpenAI,
    request: ChatRequest,
    memory_context: str = "",
) -> tuple[ChatResponse, FilterLogEntry | None, CrisisLogEntry | None]:
    """
    Full pipeline: detect language → crisis check → generate → filter → embed → summarize.
    Returns (ChatResponse, optional FilterLogEntry, optional CrisisLogEntry).
    """
    settings = get_settings()
    filter_log: FilterLogEntry | None = None
    crisis_log: CrisisLogEntry | None = None

    # 1. Detect language
    language = detect_language(request.message)

    # 2. Crisis detection
    crisis_indicators = detect_crisis(request.message)
    if crisis_indicators:
        crisis_resources = CRISIS_RESOURCES.get(language, CRISIS_RESOURCES["default"])
        crisis_log = create_crisis_log(
            user_id=request.user_info.user_id,
            user_message=request.message,
            indicators=crisis_indicators,
            language=language,
        )

        # Still generate a compassionate response, but prepend crisis resources
        # The bot should acknowledge the person, not ignore them
        system_prompt = _get_system_prompt(request.chatbot)
        crisis_system_addition = (
            "\n\n⚠️ CRISIS DETECTED: The user may be in distress. "
            "Respond with deep compassion and warmth. Acknowledge their pain. "
            "Do NOT give advice. Simply hold space and let them know they matter. "
            "Crisis resources will be attached separately."
        )
        messages = _build_openai_messages(
            system_prompt=system_prompt + crisis_system_addition,
            memory_context=memory_context,
            past_summaries=request.past_summaries,
            conversation_history=request.conversation_history.messages,
            current_message=request.message,
            language=language,
        )

        completion = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )
        reply = completion.choices[0].message.content.strip()

        # Generate embeddings for storage
        embeddings = await get_embeddings_batch(client, [request.message, reply])

        return (
            ChatResponse(
                reply=reply,
                detected_language=language,
                crisis_detected=True,
                crisis_resources=crisis_resources,
                response_was_filtered=False,
                embedding=embeddings[0],
                reply_embedding=embeddings[1],
            ),
            None,
            crisis_log,
        )

    # 3. Build messages and generate
    system_prompt = _get_system_prompt(request.chatbot)
    messages = _build_openai_messages(
        system_prompt=system_prompt,
        memory_context=memory_context,
        past_summaries=request.past_summaries,
        conversation_history=request.conversation_history.messages,
        current_message=request.message,
        language=language,
    )

    reply = ""
    was_filtered = False
    filter_reason = None

    for attempt in range(MAX_FILTER_RETRIES + 1):
        completion = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )
        reply = completion.choices[0].message.content.strip()

        # 4. Filter check
        directives_found = check_for_directives(reply)
        if not directives_found:
            break

        # Directive detected — log and retry
        if attempt == 0:
            original_response = reply  # save first attempt for logging

        if attempt < MAX_FILTER_RETRIES:
            # Add a stronger reminder and retry
            messages.append({"role": "assistant", "content": reply})
            messages.append({
                "role": "system",
                "content": (
                    "⚠️ Your response contained directive language: "
                    f"{', '.join(directives_found)}. "
                    "This violates your core rules. Regenerate without ANY advice, "
                    "suggestions, or directive phrases. Ask an open-ended question instead."
                ),
            })
        else:
            # Final attempt still has directives — use it but log
            was_filtered = True
            filter_reason = f"Directives after {MAX_FILTER_RETRIES + 1} attempts: {', '.join(directives_found)}"
            filter_log = create_filter_log(
                chatbot=request.chatbot,
                user_id=request.user_info.user_id,
                original_response=original_response,
                reasons=directives_found,
                regenerated_response=reply,
            )

    # 5. Generate embeddings for user message + reply
    embeddings = await get_embeddings_batch(client, [request.message, reply])

    # 6. Generate a micro-summary for this exchange
    summary = await _generate_exchange_summary(client, request.chatbot, request.message, reply, language)

    return (
        ChatResponse(
            reply=reply,
            detected_language=language,
            crisis_detected=False,
            response_was_filtered=was_filtered,
            filter_log=filter_reason,
            embedding=embeddings[0],
            reply_embedding=embeddings[1],
            summary=summary,
        ),
        filter_log,
        crisis_log,
    )


async def _generate_exchange_summary(
    client: AsyncOpenAI,
    chatbot: ChatbotType,
    user_message: str,
    reply: str,
    language: str,
) -> str:
    """Generate a short, neutral summary of this exchange for session continuity."""
    settings = get_settings()
    bot_label = "Reflect" if chatbot == ChatbotType.REFLECT else "Inner Learning"

    completion = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a neutral summarizer for the {bot_label} chatbot in MindGlow. "
                    "Create a 1-2 sentence neutral summary of this exchange. "
                    "Do NOT track progress, evaluate emotions, or judge. "
                    "Simply note the theme explored. Write in the same language as the user. "
                    f"User language: {language}"
                ),
            },
            {"role": "user", "content": f"User: {user_message}\nAssistant: {reply}"},
        ],
        temperature=0.3,
        max_tokens=100,
    )
    return completion.choices[0].message.content.strip()


async def generate_session_summary(
    client: AsyncOpenAI,
    request: SummaryRequest,
) -> SummaryResponse:
    """Generate a neutral summary of an entire conversation session."""
    settings = get_settings()
    language = detect_language(request.messages[0].content) if request.messages else "en"
    bot_label = "Reflect" if request.chatbot == ChatbotType.REFLECT else "Inner Learning"

    conversation_text = "\n".join(
        f"{msg.role.value}: {msg.content}" for msg in request.messages
    )

    completion = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a neutral summarizer for the {bot_label} chatbot in MindGlow. "
                    "Create a 2-3 sentence neutral summary of this session. "
                    "Do NOT track progress, score, or evaluate. Do NOT judge emotions. "
                    "Simply describe the themes and areas that were explored. "
                    f"Write in the same language as the conversation. Language: {language}"
                ),
            },
            {"role": "user", "content": conversation_text},
        ],
        temperature=0.3,
        max_tokens=200,
    )

    return SummaryResponse(
        summary=completion.choices[0].message.content.strip(),
        detected_language=language,
    )
