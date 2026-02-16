"""
Reflect Chatbot — Inner Voice for emotional exploration.
Pure non-directive questioning. No advice. Ever.
"""

from openai import OpenAI
from config import get_settings, REFLECT_SYSTEM_PROMPT, CRISIS_RESOURCES
from filters import detect_language, check_for_directives, detect_crisis


class ReflectBot:
    """The Reflect chatbot - your inner voice companion."""
    
    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.conversation_history = []
        self.name = "Reflect"
        
    def chat(self, user_message: str) -> dict:
        """
        Process a user message and return a response.
        Returns dict with: reply, language, crisis_detected, was_filtered, etc.
        """
        # Detect language
        language = detect_language(user_message)
        
        # Check for crisis
        crisis_indicators = detect_crisis(user_message)
        if crisis_indicators:
            return self._handle_crisis(user_message, language, crisis_indicators)
        
        # Build conversation context
        messages = [{"role": "system", "content": REFLECT_SYSTEM_PROMPT}]
        
        if language and language != "en":
            messages.append({
                "role": "system",
                "content": f"The user is writing in '{language}'. Respond in the same language."
            })
        
        # Add conversation history
        for msg in self.conversation_history[-10:]:  # Keep last 10 exchanges
            messages.append(msg)
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        # Generate response with filtering
        reply, was_filtered, filter_reason = self._generate_with_filter(messages)
        
        # Store in history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": reply})
        
        return {
            "reply": reply,
            "language": language,
            "crisis_detected": False,
            "was_filtered": was_filtered,
            "filter_reason": filter_reason,
        }
    
    def _generate_with_filter(self, messages, max_retries=2):
        """Generate response and check for directive language."""
        was_filtered = False
        filter_reason = None
        
        for attempt in range(max_retries + 1):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )
            reply = response.choices[0].message.content.strip()
            
            # Check for directives
            directives = check_for_directives(reply)
            if not directives:
                return reply, was_filtered, filter_reason
            
            # Directive found - retry
            if attempt < max_retries:
                messages.append({"role": "assistant", "content": reply})
                messages.append({
                    "role": "system",
                    "content": f"⚠️ VIOLATION: Your response contained directive phrases: {', '.join(directives)}. "
                            "Regenerate with ONLY open-ended questions. No advice."
                })
                was_filtered = True
                filter_reason = f"Filtered directives: {', '.join(directives)}"
            else:
                # Final attempt still has directives
                was_filtered = True
                filter_reason = f"Still contains directives after {max_retries} retries: {', '.join(directives)}"
        
        return reply, was_filtered, filter_reason
    
    def _handle_crisis(self, user_message, language, indicators):
        """Handle crisis detection with compassionate response."""
        crisis_resources = CRISIS_RESOURCES.get(language, CRISIS_RESOURCES["default"])
        
        messages = [
            {"role": "system", "content": REFLECT_SYSTEM_PROMPT},
            {
                "role": "system",
                "content": "⚠️ CRISIS: Respond with deep compassion. Acknowledge their pain. NO advice. Just presence."
            },
            {"role": "user", "content": user_message}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=400,
        )
        
        compassionate_reply = response.choices[0].message.content.strip()
        
        return {
            "reply": compassionate_reply,
            "language": language,
            "crisis_detected": True,
            "crisis_resources": crisis_resources,
            "crisis_indicators": indicators,
            "was_filtered": False,
        }
    
    def reset(self):
        """Clear conversation history."""
        self.conversation_history = []
        print(f"✨ {self.name} conversation reset.\n")
