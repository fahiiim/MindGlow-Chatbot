"""
Inner Learning Chatbot — Socratic discovery guide.
Pure questioning method. No teaching. No answers. Ever.
"""

from openai import OpenAI
from config import get_settings, INNER_LEARNING_SYSTEM_PROMPT
from filters import detect_language, check_for_directives


class InnerLearningBot:
    """The Inner Learning chatbot - Socratic discovery companion."""
    
    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.conversation_history = []
        self.name = "Inner Learning"
        
    def chat(self, user_message: str) -> dict:
        """
        Process a user message and return a Socratic response.
        Returns dict with: reply, language, was_filtered, etc.
        """
        # Detect language
        language = detect_language(user_message)
        
        # Build conversation context
        messages = [{"role": "system", "content": INNER_LEARNING_SYSTEM_PROMPT}]
        
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
            "was_filtered": was_filtered,
            "filter_reason": filter_reason,
        }
    
    def _generate_with_filter(self, messages, max_retries=2):
        """Generate response and check for instructional/directive language."""
        was_filtered = False
        filter_reason = None
        
        # Additional patterns specific to teaching/instructing
        teaching_violations = [
            "the answer is", "actually,", "let me explain",
            "here's how it works", "it works like this",
            "the definition", "basically,", "in other words"
        ]
        
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
            
            # Check for teaching violations
            teaching_found = [v for v in teaching_violations if v.lower() in reply.lower()]
            
            violations = directives + teaching_found
            
            if not violations:
                return reply, was_filtered, filter_reason
            
            # Violation found - retry
            if attempt < max_retries:
                messages.append({"role": "assistant", "content": reply})
                messages.append({
                    "role": "system",
                    "content": f"⚠️ VIOLATION: You're teaching/instructing. Detected: {', '.join(violations)}. "
                            "Use ONLY questions. Guide discovery, don't give answers."
                })
                was_filtered = True
                filter_reason = f"Filtered teaching patterns: {', '.join(violations)}"
            else:
                # Final attempt still has violations
                was_filtered = True
                filter_reason = f"Still teaching after {max_retries} retries: {', '.join(violations)}"
        
        return reply, was_filtered, filter_reason
    
    def reset(self):
        """Clear conversation history."""
        self.conversation_history = []
        print(f"✨ {self.name} conversation reset.\n")
