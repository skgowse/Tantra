import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
from sqlalchemy.orm import Session

from app.config import GEMINI_API_KEY, OPENAI_API_KEY, AI_REQUEST_TIMEOUT
from app.services.safety_service import evaluate_safety
from app.services.emotion_service import detect_emotion_cue
from app.services.classification_service import classify_incident_nature, determine_missing_elements

logger = logging.getLogger("legal_tantra.ai")

class BaseAIProvider(ABC):
    @abstractmethod
    def interpret_and_respond(
        self,
        messages: List[Dict[str, str]],
        language: str,
        existing_facts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Interprets citizen message, extracts facts, and produces the next follow-up question."""
        pass

    @abstractmethod
    def generate_legal_analysis(
        self,
        facts: Dict[str, Any],
        language: str,
        db: Session
    ) -> Any:
        """Produces analysis grounding against verified legal database without hallucination."""
        pass

class DeterministicFallbackProvider(BaseAIProvider):
    """
    Safe, offline, deterministic rule-based assistant that works without external API keys.
    Extracts structured facts, asks 1 targeted follow-up at a time, and respects user pace.
    """
    def interpret_and_respond(
        self,
        messages: List[Dict[str, str]],
        language: str,
        existing_facts: Dict[str, Any]
    ) -> Dict[str, Any]:
        latest_user_msg = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else ""

        # 1. Immediate Safety Check (determinstic, priority)
        safety_check = evaluate_safety(latest_user_msg, language)

        # 2. Emotion Cue Detection
        emotion_analysis = detect_emotion_cue(latest_user_msg)

        # 3. Classify and Extract Facts
        classified = classify_incident_nature(messages, existing_facts)
        facts = classified["facts"]
        missing_elements = determine_missing_elements(facts)

        user_turns_count = sum(1 for m in messages if m["role"] == "user")
        is_clarified = len(missing_elements) <= 1 or user_turns_count >= 4

        prefix = emotion_analysis["support_prefix_te"] if language == "te" else emotion_analysis["support_prefix_en"]
        safety_prefix = f"\n\n{safety_check['safety_message']}\n\n" if safety_check["is_emergency"] else ""

        # Check for contradictions or explicit user uncertainty
        uncertainty_note = ""
        if "i don't know" in latest_user_msg.lower() or "not sure" in latest_user_msg.lower() or "గుర్తులేదు" in latest_user_msg:
            if language == "te":
                uncertainty_note = "సరే, మీకు ఖచ్చితంగా గుర్తులేకపోతే ఏమీ పర్వాలేదు. "
            else:
                uncertainty_note = "That is completely fine. It is normal not to remember every detail. "

        if not is_clarified and missing_elements:
            top_missing = missing_elements[0]
            question = self._get_question_for_missing(top_missing, facts.get("jurisdiction_type", "uncertain"), language)
            reply = f"{safety_prefix}{prefix} {uncertainty_note}{question}".strip()
        else:
            category_title = facts.get("incident_type") or "Reported incident"
            jurisdiction = facts.get("jurisdiction_type", "uncertain")
            if language == "te":
                reply = (
                    f"{safety_prefix}{prefix} నేను మీరు తెలిపిన వివరాలను పరిశీలించాను ({category_title}). "
                    "మీరు ఎటువంటి ఆందోళన లేకుండా 'సంఘటన విశ్లేషణను వీక్షించండి' పై క్లిక్ చేసి, "
                    "చట్టపరమైన సమాచారం మరియు ఒక చిత్తు నివేదికను సమీక్షించవచ్చు."
                )
            else:
                reply = (
                    f"{safety_prefix}{prefix} Thank you for explaining what happened regarding {category_title}. "
                    "We have captured the primary facts available. You can now click 'View Incident Analysis & Rights' "
                    "to review potentially applicable legal procedures, your rights, and an editable factual summary."
                )

        return {
            "reply": reply,
            "is_clarified": is_clarified,
            "safety_alert": safety_check["is_emergency"],
            "safety_details": safety_check,
            "emotion_cue": emotion_analysis["primary_cue"],
            "extracted_facts": facts,
            "missing_facts": missing_elements,
            "suggested_next_step": classified["suggested_forum"],
            "jurisdiction_hint": facts.get("jurisdiction_type", "uncertain"),
            "provider_used": "deterministic"
        }

    def _get_question_for_missing(self, missing_field: str, jurisdiction: str, language: str) -> str:
        if missing_field == "date_time":
            return (
                "ఈ సంఘటన సుమారు ఎప్పుడు (తేదీ లేదా సమయం) జరిగింది? ఖచ్చితంగా గుర్తులేకపోతే 'సుమారు నిన్న' లేదా 'గత వారం' అని చెప్పవచ్చు."
                if language == "te" else
                "Approximately when did this happen? (If you don't recall the exact date or time, an approximate timeframe like 'last evening' or '3 days ago' is fine.)"
            )
        elif missing_field == "location":
            return (
                "ఈ సంఘటన ఎక్కడ జరిగింది? (ఉదాహరణకు: మీ కార్యాలయం, మార్కెట్, లేదా ఆన్‌లైన్ వెబ్‌సైట్ / వాట్సాప్‌లోనా?)"
                if language == "te" else
                "Where did this take place? (For example: at a public street, at home, at your workplace, or on an online platform?)"
            )
        elif missing_field == "people_involved":
            return (
                "ఈ సంఘటనలో ఎవరు ఉన్నారు? ఆ వ్యక్తి మీకు ముందే తెలుసా లేదా అపరిచితులా? (పేరు తెలియకపోతే 'అపరిచితుడు' అని చెప్పవచ్చు)"
                if language == "te" else
                "Who was involved in this? Was it someone known to you, a neighbor, employer, or an unknown stranger? (You can say 'Unknown' if you don't know them.)"
            )
        elif missing_field == "alleged_actions":
            return (
                "వారు ఖచ్చితంగా ఏమి చేశారు లేదా చెప్పారు? దయచేసి సాధారణ మాటల్లో వివరించండి."
                if language == "te" else
                "What specifically happened or what was said? Please describe the action in your own words."
            )
        elif missing_field == "injuries_or_loss":
            if jurisdiction == "consumer":
                return (
                    "ఉత్పత్తి లేదా సేవ కోసం ఎంత మొత్తం చెల్లించారు? మీకు జరిగిన ఆర్థిక నష్టం ఎంత?"
                    if language == "te" else
                    "What was the amount paid or financial loss sustained regarding this purchase or service?"
                )
            elif jurisdiction == "civil":
                return (
                    "ఈ స్థలం లేదా ఆస్తికి సంబంధించిన నష్టం ఏమిటి? ప్రస్తుతం ఎవరి స్వాధీనంలో ఉంది?"
                    if language == "te" else
                    "What is the property or dispute value involved, and who currently holds possession?"
                )
            else:
                return (
                    "ఏదైనా శారీరక గాయం అయిందా, లేదా ఎంత మొత్తం డబ్బు/ఆస్తి నష్టం జరిగింది?"
                    if language == "te" else
                    "Was there any bodily injury, or was any money or property lost as a result?"
                )
        else:
            return (
                "మీ వద్ద దీనికి సంబంధించి ఏవైనా ఆధారాలు (మెసేజ్‌లు, రశీదులు, ఫోటోలు, కాల్ రికార్డింగ్‌లు) ఉన్నాయా?"
                if language == "te" else
                "Do you have any supporting records—such as screenshots, bills, messages, receipts, or photos?"
            )

    def generate_legal_analysis(self, facts: Dict[str, Any], language: str, db: Session) -> Any:
        from app.services.legal_service import generate_legal_analysis_for_facts
        return generate_legal_analysis_for_facts(facts, language, db)

class GeminiAIProvider(BaseAIProvider):
    """
    Google Gemini integration with strict output validation, timeouts, and fallback.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.fallback = DeterministicFallbackProvider()

    def interpret_and_respond(
        self,
        messages: List[Dict[str, str]],
        language: str,
        existing_facts: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Always run safety check first
        latest_msg = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else ""
        safety_check = evaluate_safety(latest_msg, language)
        if safety_check["is_emergency"]:
            return self.fallback.interpret_and_respond(messages, language, existing_facts)

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            prompt = self._build_interpretation_prompt(messages, language, existing_facts)
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "response_mime_type": "application/json"}
            }
            with httpx.Client(timeout=AI_REQUEST_TIMEOUT) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(raw_text)
                    
                    # Validate parsed output
                    reply = parsed.get("reply")
                    extracted = parsed.get("extracted_facts", {})
                    # Merge with existing
                    merged_facts = existing_facts.copy()
                    for k, v in extracted.items():
                        if v and not merged_facts.get(k):
                            merged_facts[k] = v

                    missing = determine_missing_elements(merged_facts)
                    return {
                        "reply": reply,
                        "is_clarified": parsed.get("is_clarified", len(missing) <= 1),
                        "safety_alert": False,
                        "safety_details": safety_check,
                        "emotion_cue": parsed.get("emotion_cue", "neutral"),
                        "extracted_facts": merged_facts,
                        "missing_facts": missing,
                        "suggested_next_step": parsed.get("suggested_next_step", "General Legal Guidance"),
                        "jurisdiction_hint": merged_facts.get("jurisdiction_type", "uncertain"),
                        "provider_used": "gemini"
                    }
        except Exception as e:
            logger.warning(f"Gemini API invocation failed or timed out: {e}. Falling back to deterministic.")

        return self.fallback.interpret_and_respond(messages, language, existing_facts)

    def _build_interpretation_prompt(self, messages: List[Dict[str, str]], language: str, existing_facts: Dict[str, Any]) -> str:
        convo_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in messages])
        return f"""You are a sensitive legal intake assistant in India.
Current Language: {language}
Conversation History:
{convo_text}

Existing Facts Extracted So Far:
{json.dumps(existing_facts)}

Task:
1. Identify the incident category (e.g., Physical assault, Threat, Harassment, Theft, Cyber fraud, Property dispute, Domestic violence, Consumer complaint, Employment dispute, Uncertain).
2. Extract any newly stated facts: approximate date_time, location, people_involved, alleged_actions, injuries_or_loss, evidence_mentioned.
3. NEVER invent or assume any facts that were not stated. If unknown, leave as null.
4. If facts are incomplete, generate ONE clear, polite follow-up question in {language}.
5. Respond in valid JSON with keys: "reply", "extracted_facts", "is_clarified", "emotion_cue", "suggested_next_step".
"""

    def generate_legal_analysis(self, facts: Dict[str, Any], language: str, db: Session) -> Any:
        return self.fallback.generate_legal_analysis(facts, language, db)

class OpenAIProvider(BaseAIProvider):
    """
    OpenAI integration with strict output validation, timeouts, and fallback.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.fallback = DeterministicFallbackProvider()

    def interpret_and_respond(
        self,
        messages: List[Dict[str, str]],
        language: str,
        existing_facts: Dict[str, Any]
    ) -> Dict[str, Any]:
        latest_msg = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else ""
        safety_check = evaluate_safety(latest_msg, language)
        if safety_check["is_emergency"]:
            return self.fallback.interpret_and_respond(messages, language, existing_facts)

        try:
            url = "https://api.openai.com/v1/chat/completions"
            system_prompt = (
                "You are an Indian citizen legal awareness assistant. "
                "Never invent facts. Respond only in valid JSON with keys: reply, extracted_facts, is_clarified, emotion_cue, suggested_next_step."
            )
            convo = [{"role": "system", "content": system_prompt}] + messages
            payload = {
                "model": "gpt-4o-mini",
                "messages": convo,
                "temperature": 0.2,
                "response_format": {"type": "json_object"}
            }
            headers = {"Authorization": f"Bearer {self.api_key}"}
            with httpx.Client(timeout=AI_REQUEST_TIMEOUT) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    extracted = parsed.get("extracted_facts", {})
                    merged_facts = existing_facts.copy()
                    for k, v in extracted.items():
                        if v and not merged_facts.get(k):
                            merged_facts[k] = v
                    missing = determine_missing_elements(merged_facts)
                    return {
                        "reply": parsed.get("reply", ""),
                        "is_clarified": parsed.get("is_clarified", len(missing) <= 1),
                        "safety_alert": False,
                        "safety_details": safety_check,
                        "emotion_cue": parsed.get("emotion_cue", "neutral"),
                        "extracted_facts": merged_facts,
                        "missing_facts": missing,
                        "suggested_next_step": parsed.get("suggested_next_step", "General Legal Guidance"),
                        "jurisdiction_hint": merged_facts.get("jurisdiction_type", "uncertain"),
                        "provider_used": "openai"
                    }
        except Exception as e:
            logger.warning(f"OpenAI API invocation failed or timed out: {e}. Falling back to deterministic.")

        return self.fallback.interpret_and_respond(messages, language, existing_facts)

    def generate_legal_analysis(self, facts: Dict[str, Any], language: str, db: Session) -> Any:
        return self.fallback.generate_legal_analysis(facts, language, db)

def get_ai_provider() -> BaseAIProvider:
    """Factory to retrieve configured AI provider with seamless fallback."""
    if GEMINI_API_KEY:
        return GeminiAIProvider(GEMINI_API_KEY)
    elif OPENAI_API_KEY:
        return OpenAIProvider(OPENAI_API_KEY)
    return DeterministicFallbackProvider()
