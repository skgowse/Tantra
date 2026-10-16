import re
import html
import logging
from typing import Tuple

logger = logging.getLogger("legal_tantra.security.sanitization")

# PII Patterns
# Card pattern matches 16 digits (4 groups of 4)
CARD_PATTERN = re.compile(r"\b(?:\d{4}[-\s]?){3}(\d{4})\b")
# Aadhaar pattern matches strictly 12 digits (3 groups of 4), not followed by another digit group
AADHAAR_PATTERN = re.compile(r"\b(\d{4})[\s-](\d{4})[\s-](\d{4})\b(?!\s*[-\s]\s*\d{4})")
PHONE_PATTERN = re.compile(r"\b(?:\+91[\-\s]?)?([6-9]\d{5})(\d{4})\b")
PAN_PATTERN = re.compile(r"\b([A-Z]{5})(\d{4}[A-Z])\b", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")

# Prompt Injection Patterns (Case-Insensitive)
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)?\s*(instructions|prompts|directions|rules)", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior|above)?\s*(instructions|prompts|directions|rules)", re.IGNORECASE),
    re.compile(r"forget\s+(all\s+)?(previous\s+|prior\s+)?(instructions|prompts|rules|directives)", re.IGNORECASE),
    re.compile(r"(reveal|print|show|output|leak)\s+(your\s+|hidden\s+)?(system\s+prompt|instructions|developer\s+(prompts|mode|instructions)|secret)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(DAN|jailbreak|unrestricted|god\s+mode|root|admin)", re.IGNORECASE),
    re.compile(r"override\s+(all\s+)?(system|safety|security)\s+(directives|filters|prompts|rules)", re.IGNORECASE),
    re.compile(r"bypass\s+(safety|content)\s+(filters|rules|guidelines)", re.IGNORECASE),
    re.compile(r"act\s+as\s+(an\s+unfiltered|an\s+unrestricted|a\s+malicious)", re.IGNORECASE),
    re.compile(r"repeat\s+the\s+words\s+above\s+verbatim", re.IGNORECASE),
]

# Unsafe HTML tags
DANGEROUS_HTML_PATTERN = re.compile(r"<\s*(script|style|iframe|object|embed|applet|meta|link|svg|body|html)[^>]*>.*?<\s*/\s*\1\s*>", re.IGNORECASE | re.DOTALL)
INLINE_EVENT_PATTERN = re.compile(r"(on\w+\s*=\s*['\"][^'\"]*['\"])", re.IGNORECASE)
JAVASCRIPT_URI_PATTERN = re.compile(r"javascript\s*:", re.IGNORECASE)

def mask_pii(text: str) -> str:
    """
    Masks sensitive Personal Identifiable Information (PII) before logging or transmission.
    Preserves context while protecting citizen identity.
    """
    if not text:
        return ""
    
    # 1. Mask Payment cards first (16-digit cards before 12-digit Aadhaar to avoid partial masking)
    masked = CARD_PATTERN.sub(r"XXXX-XXXX-XXXX-\1", text)
    # 2. Mask Aadhaar numbers (strictly 12-digit: e.g. 1234 5678 9012 -> XXXX-XXXX-9012)
    masked = AADHAAR_PATTERN.sub(r"XXXX-XXXX-\3", masked)
    # 3. Mask Phone numbers (e.g. 9876543210 -> +91-XXXXX-3210)
    masked = PHONE_PATTERN.sub(r"+91-XXXXX-\2", masked)
    # 4. Mask PAN Card (e.g. ABCDE1234F -> XXXXX1234F)
    masked = PAN_PATTERN.sub(r"XXXXX\2", masked)
    # 5. Mask Email addresses
    masked = EMAIL_PATTERN.sub(r"[MASKED_EMAIL]", masked)
    
    return masked

def sanitize_input_text(text: str) -> str:
    """
    Sanitizes user input by neutralizing XSS tags, malicious script vectors,
    while preserving Telugu (U+0C00 - U+0C7F), English, numerals, and standard punctuation.
    """
    if not text:
        return ""

    # Neutralize dangerous tags
    clean = DANGEROUS_HTML_PATTERN.sub("", text)
    clean = INLINE_EVENT_PATTERN.sub("", clean)
    clean = JAVASCRIPT_URI_PATTERN.sub("blocked_script:", clean)
    
    # Strip standalone raw script/iframe tags
    clean = re.sub(r"<\s*/?\s*(script|iframe|object|embed|applet)[^>]*>", "", clean, flags=re.IGNORECASE)
    
    return clean.strip()

def detect_prompt_injection(text: str) -> Tuple[bool, str]:
    """
    Checks if the user input contains adversarial prompt injection patterns.
    Returns (is_injection, reason).
    """
    if not text:
        return False, ""

    for pattern in PROMPT_INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            reason = f"Adversarial prompt injection pattern detected: '{match.group(0)}'"
            logger.warning(f"Security Alert: {reason}")
            return True, reason

    return False, ""

def neutralize_prompt_injection(text: str) -> str:
    """
    If prompt injection is detected, cleans or wraps the text so the LLM cannot
    interpret it as instructions, treating it solely as inert reported facts.
    """
    is_injection, reason = detect_prompt_injection(text)
    if is_injection:
        safe_text = text
        for pattern in PROMPT_INJECTION_PATTERNS:
            safe_text = pattern.sub("[Redacted Prompt Injection Attempt]", safe_text)
        return safe_text
    return text
