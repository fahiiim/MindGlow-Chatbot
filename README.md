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

## Quick Start

### 1. Set up virtual environment (recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure environment
```bash
# Copy example config and add your OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Test the chatbots
```bash
# Interactive terminal interface
python test_bots.py
```

Choose from the menu:
- Test **Reflect** bot interactively
- Test **Inner Learning** bot interactively  
- Run automated quick tests
- Type `reset` to clear conversation history
- Type `quit` to return to menu

## API Endpoints

### `POST /chat` — Main Chat
Send a message to either chatbot. Backend provides user info and history from DB.

```json
{
  "chatbot": "reflect",
  "user_info": { "user_id": "user_123", "display_name": "Sarah" },
  "message": "I've been feeling overwhelmed lately",
  "conversation_history": {
    "messages": [
      { "role": "user", "content": "Hi", "timestamp": "2026-02-17T10:00:00Z" },
      { "role": "assistant", "content": "Hello, I'm here with you." }
    ]
  },
  "past_summaries": ["User explored feelings of uncertainty about career changes."]
}
```

**Response includes:**
- `reply` — Bot response
- `detected_language` — Language code (en, ar, etc.)
- `crisis_detected` / `crisis_resources` — If self-harm indicators found
- `response_was_filtered` / `filter_log` — If directive phrases caught
- `embedding` / `reply_embedding` — Vectors for semantic search (store in DB)
- `summary` — Neutral exchange summary (store in DB)

### `POST /chat-with-memory` — Chat + Auto Memory Retrieval
Same as `/chat` but also accepts stored messages with embeddings. Automatically finds relevant past context.

### `POST /semantic-search` — Find Relevant Past Messages
```json
{
  "query": "feeling overwhelmed at work",
  "stored_messages": [
    { "role": "user", "content": "work has been stressful", "embedding": [...], "timestamp": "2026-02-10T10:00:00Z" }
  ],
  "top_k": 5,
  "threshold": 0.75
}
```

### `POST /summary` — Session Summary
```json
{
  "chatbot": "reflect",
  "messages": [
    { "role": "user", "content": "I feel lost" },
    { "role": "assistant", "content": "What does that feeling of being lost look like for you?" }
  ]
}
```

### `POST /embed` — Generate Embedding
```json
{ "text": "I feel peaceful today" }
```

### `GET /health` — Health Check

## Backend Integration Guide

This system is **stateless** — it does NOT store data. Your backend handles all persistence:

### What to store per message:
```
- user_id, chatbot_type, role, content, timestamp
- embedding (from response.embedding / response.reply_embedding)
- detected_language
```

### What to store per session:
```
- session_id, user_id, chatbot_type
- summary (from /summary endpoint or response.summary)
```

### What to store for safety:
```
- crisis events (when response.crisis_detected == true)
- filter logs (when response.response_was_filtered == true)
```

### Recommended flow:
1. User sends message → backend calls `POST /chat`
2. Store user message + embedding, store bot reply + reply_embedding
3. On session end → call `POST /summary`, store it
4. Next session → include stored summaries in `past_summaries`
5. Optionally call `/semantic-search` first to find relevant past context

## Features
- **Response Filter** — Auto-detects directive phrases ("you should", "try doing", etc.) and regenerates
- **Crisis Detection** — Detects self-harm indicators, returns crisis resources, logs for safety review
- **Multi-Language** — Detects language (English, Arabic, etc.), responds in same language
- **Semantic Memory** — Embedding-based retrieval of relevant past conversations
- **Neutral Summaries** — No progress tracking, just themes explored

## Project Structure
```
config.py              — Settings, system prompts, crisis resources
chatbot_reflect.py     — Reflect chatbot class (emotional exploration)
chatbot_learning.py    — Inner Learning chatbot class (Socratic method)
filters.py             — Response filter & crisis detection
memory.py              — Embeddings & semantic search (for future use)
models.py              — Pydantic models (for API integration later)
test_bots.py           — Terminal interface for testing both bots
main.py                — FastAPI application (coming soon)
```

## Next Steps

- [x] Two separate chatbot implementations
- [x] Terminal testing interface
- [x] Response filtering and crisis detection
- [ ] FastAPI integration (for production use)
- [ ] Semantic memory with embeddings
- [ ] Session summaries and continuity
- [ ] Database integration guide
