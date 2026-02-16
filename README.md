# MindGlow AI — Self-Reflection Chatbot System

Two completely separate AI chatbots for self-reflection. No advice. No judgments. Just space to think.

## The Two Chatbots

### 🌟 Reflect — Your Inner Voice
**Purpose:** Non-directive emotional exploration  
**Method:** Open-ended questions only, warm presence, never gives advice  
**Use for:** Processing feelings, self-reflection, emotional clarity

### 🧠 Inner Learning — Socratic Discovery Guide  
**Purpose:** Knowledge discovery through questioning  
**Method:** Pure Socratic method, guides you to form your own understanding  
**Use for:** Learning concepts, exploring ideas, developing insights

---

## Quick Start

### 1. Set up virtual environment (recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your OpenAI API key
```bash
# Copy the example config
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_key_here
```

### 4. Test the chatbots
```bash
# Interactive terminal interface
python test_bots.py
```

Or run the automated demo:
```bash
python demo.py
```

---

## Using the Chatbots

### Interactive Terminal Interface

Run `python test_bots.py` and choose from the menu:
- **1** — Test Reflect bot (emotional exploration)
- **2** — Test Inner Learning bot (knowledge discovery)
- **3** — Run automated quick tests
- **4** — Exit

**Commands during chat:**
- Type your message normally to chat
- Type `reset` to clear conversation history
- Type `quit` to return to main menu

### Using in Your Code

```python
from chatbot_reflect import ReflectBot
from chatbot_learning import InnerLearningBot

# Create instances
reflect = ReflectBot()
learning = InnerLearningBot()

# Chat with Reflect
response = reflect.chat("I feel overwhelmed today")
print(response['reply'])          # The bot's response
print(response['language'])       # Detected language (en, ar, etc.)
print(response['crisis_detected']) # True if crisis indicators found

# Chat with Inner Learning  
response = learning.chat("How does machine learning work?")
print(response['reply'])          # Socratic question to guide discovery
print(response['was_filtered'])   # True if teaching phrases were caught

# Reset conversation history
reflect.reset()
learning.reset()
```

### Response Format

Both chatbots return a dictionary:
```python
{
    "reply": "The chatbot's response...",
    "language": "en",               # ISO 639-1 language code
    "was_filtered": False,          # True if directive phrases detected
    "filter_reason": None,          # Details if filtered
    "crisis_detected": False,       # True if crisis detected (Reflect only)
    "crisis_resources": None,       # Crisis helpline info (if detected)
    "crisis_indicators": []         # Matched crisis phrases (if any)
}
```

---

## Core Features

✅ **Two Separate Chatbots** — Completely distinct implementations with different personalities  
✅ **Response Filtering** — Auto-detects directive phrases and regenerates responses  
✅ **Crisis Detection** — Identifies self-harm indicators and provides resources (Reflect bot)  
✅ **Multi-Language Support** — Auto-detects user language and responds accordingly  
✅ **Conversation Memory** — Each bot maintains context across exchanges  
✅ **Pure Non-Directive** — Both bots use only questions, never give advice or answers

### Response Filtering

Both chatbots actively filter their responses to ensure they maintain their non-directive approach:

**Reflect bot blocks:**
- "you should", "try doing", "I recommend"
- "you need to", "have you considered"
- "it might help to", "why don't you"
- Any directive or advisory language

**Inner Learning bot blocks:**
- All directive phrases above, plus:
- "the answer is", "let me explain"
- "here's how it works", "actually"
- Any teaching or instructional language

If blocked phrases are detected, the bot automatically regenerates its response (up to 2 retries).

### Crisis Detection (Reflect Bot)

The Reflect bot monitors for self-harm indicators:
- "want to die", "end my life", "kill myself"
- "suicidal", "no reason to live"
- "self-harm", "better off dead"

When detected:
1. Returns compassionate, non-directive response
2. Provides crisis helpline resources in user's language
3. Logs event details (crisis_detected=True in response)

---

## Project Structure

```
chatbot_reflect.py     — Reflect chatbot (emotional exploration)
chatbot_learning.py    — Inner Learning chatbot (Socratic method)
config.py              — System prompts, settings, crisis resources
filters.py             — Response filtering & crisis detection
memory.py              — Embedding utilities (for future features)
test_bots.py           — Interactive terminal testing interface
demo.py                — Automated demo of both chatbots
```

---

## Examples

### Reflect Bot Example
```
💬 You: I've been feeling really overwhelmed lately

💭 Reflect: I hear that feeling of being overwhelmed is present for you 
            right now. What does that overwhelm feel like in your body?

💬 You: It feels heavy in my chest

💭 Reflect: There's a heaviness you're noticing in your chest. What's that 
            heaviness trying to tell you, if it could speak?
```

### Inner Learning Bot Example
```
💬 You: How does photosynthesis work?

🧠 Inner Learning: That's a fascinating process to explore! When you think 
                   about plants and sunlight, what do you already know or 
                   sense is happening?

💬 You: Plants use sunlight to make food somehow?

🧠 Inner Learning: You're already touching on something key there — plants 
                   and sunlight and making food. What do you think the 
                   sunlight is actually doing in that process?
```

---

## Philosophy

**MindGlow** is built on one core principle:

> **No advice. No solutions. No judgments. Just space to think.**

Both chatbots help you discover your own insights by:
- Asking open-ended questions
- Reflecting back what you share
- Holding space without rushing
- Never telling you what to do or think
- Letting silence and pauses be okay

The **Reflect** bot explores emotions. The **Inner Learning** bot explores ideas. Both guide you to your own understanding.

---

## Requirements

- Python 3.9+
- OpenAI API key
- Dependencies: `openai`, `python-dotenv`, `numpy`, `langdetect`

---

## License

This project is for educational and personal use. Use responsibly and ethically.
