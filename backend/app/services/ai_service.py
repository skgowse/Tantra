from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.ai_provider import get_ai_provider, BaseAIProvider

def generate_assistant_turn(
    messages: List[Dict[str, str]],
    language: str,
    db: Session,
    existing_facts: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generates next conversational turn using the configured AI provider with fallback."""
    provider: BaseAIProvider = get_ai_provider()
    return provider.interpret_and_respond(
        messages=messages,
        language=language,
        existing_facts=existing_facts or {}
    )

def generate_comprehensive_analysis(
    facts: Dict[str, Any],
    language: str,
    db: Session
) -> Dict[str, Any]:
    """Retrieves grounded legal information without hallucination using verified knowledge base."""
    provider: BaseAIProvider = get_ai_provider()
    result = provider.generate_legal_analysis(facts, language, db)
    if isinstance(result, dict):
        return result
    return {
        "incident_category": facts.get("incident_type", "General incident"),
        "provisions": [],
        "citations": getattr(result, "citations", [])
    }
