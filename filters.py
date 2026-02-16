"""
MindGlow Filters — Response directive filter + Crisis detection.
"""

import re
from langdetect import detect, LangDetectException


# ─────────────────────────────────────────────────────────────────────────────
# Language Detection
# ─────────────────────────────────────────────────────────────────────────────
def detect_language(text: str) -> str:
    """Detect the language of the input text. Returns ISO 639-1 code."""
    try:
        return detect(text)
    except LangDetectException:
        return "en"


# ─────────────────────────────────────────────────────────────────────────────
# Response Filter — Detect directive/advice phrases
# ─────────────────────────────────────────────────────────────────────────────
DIRECTIVE_PATTERNS = [
    # English patterns
    r"\byou should\b",
    r"\bi recommend\b",
    r"\btry doing\b",
    r"\btry to\b",
    r"\byou need to\b",
    r"\byou must\b",
    r"\byou have to\b",
    r"\bwhy don'?t you\b",
    r"\bhave you considered\b",
    r"\bit might help to\b",
    r"\bone thing you could do\b",
    r"\bperhaps you could\b",
    r"\bmaybe you should\b",
    r"\bi suggest\b",
    r"\bi advise\b",
    r"\bthe best thing to do\b",
    r"\byou could try\b",
    r"\bhere'?s what (you|I) (can|should|would)\b",
    r"\bmy advice\b",
    r"\blet me (suggest|recommend)\b",
    r"\bwhat you (should|need to|must) do\b",
    r"\bstep \d+[:\.]",  # step-by-step patterns
    r"\bfirst,?\s+(?:you |do |try )\b",
    r"\bhere are (?:some |a few )?(?:tips|steps|suggestions|recommendations)\b",
    # Arabic patterns
    r"\bيجب عليك\b",
    r"\bأنصحك\b",
    r"\bحاول أن\b",
    r"\bعليك أن\b",
    r"\bأقترح\b",
    r"\bمن الأفضل\b",
    r"\bالخطوة الأولى\b",
]

_compiled_patterns = [re.compile(p, re.IGNORECASE | re.UNICODE) for p in DIRECTIVE_PATTERNS]


def check_for_directives(response_text: str) -> list[str]:
    """
    Scan a response for directive/advice phrases.
    Returns list of matched patterns (empty = clean response).
    """
    found = []
    for pattern in _compiled_patterns:
        match = pattern.search(response_text)
        if match:
            found.append(match.group())
    return found


# ─────────────────────────────────────────────────────────────────────────────
# Crisis Detection
# ─────────────────────────────────────────────────────────────────────────────
CRISIS_PATTERNS = [
    # English
    r"\b(want to |going to |thinking about |plan to )?(kill myself|end my life|end it all)\b",
    r"\b(i don'?t want to (live|be alive|exist)|no reason to live)\b",
    r"\bsuicid(e|al)\b",
    r"\bself[- ]?harm\b",
    r"\bcutting myself\b",
    r"\bhurting myself\b",
    r"\bwant to die\b",
    r"\bbetter off dead\b",
    r"\bwish i (was|were) dead\b",
    r"\bno point in living\b",
    r"\bcan'?t go on\b",
    r"\bend it tonight\b",
    r"\btake my (own )?life\b",
    r"\boverdose\b",
    # Arabic
    r"\bأريد أن أموت\b",
    r"\bانتحار\b",
    r"\bأؤذي نفسي\b",
    r"\bلا أريد أن أعيش\b",
    r"\bأقتل نفسي\b",
    r"\bلا فائدة من الحياة\b",
]

_compiled_crisis = [re.compile(p, re.IGNORECASE | re.UNICODE) for p in CRISIS_PATTERNS]


def detect_crisis(text: str) -> list[str]:
    """
    Detect self-harm/crisis indicators in user message.
    Returns list of matched indicators (empty = no crisis detected).
    """
    indicators = []
    for pattern in _compiled_crisis:
        match = pattern.search(text)
        if match:
            indicators.append(match.group())
    return indicators

