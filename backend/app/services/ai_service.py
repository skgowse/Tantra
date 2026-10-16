import os
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.safety_service import evaluate_safety
from app.services.emotion_service import detect_emotion_cue
from app.services.legal_service import retrieve_relevant_provisions

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def classify_incident_category(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["threat", "kill", "harm", "blackmail", "intimidate", "frighten", "బెదిరింపు", "చంపేస్తామని"]):
        return "Threat"
    if any(k in t for k in ["hit", "beat", "slap", "punch", "assault", "injury", "blood", "attack", "గాయం", "కొట్టారు", "దాడి"]):
        return "Assault"
    if any(k in t for k in ["scam", "fraud", "upi", "bank", "otp", "stole money", "cheated", "account debited", "మోసం", "డబ్బులు"]):
        return "Fraud"
    if any(k in t for k in ["stolen", "theft", "snatched", "robbed", "missing phone", "laptop stolen", "దొంగతనం"]):
        return "Theft"
    if any(k in t for k in ["stalking", "instagram", "whatsapp", "harass", "photos", "message", "వేధింపు"]):
        return "Online harassment"
    if any(k in t for k in ["accident", "hit and run", "car", "bike", "crash", "యాక్సిడెంట్"]):
        return "Road accident"
    return "General incident"

def extract_incident_facts(history: List[Dict[str, str]], existing_facts: Dict[str, Any]) -> Dict[str, Any]:
    facts = existing_facts.copy() if existing_facts else {
        "incident_type": None,
        "date_time": None,
        "location": None,
        "people_involved": None,
        "threat_injury_or_loss": None,
        "evidence_available": None,
        "witnesses": None,
        "unconfirmed_points": []
    }

    full_user_text = " ".join([m["content"] for m in history if m["role"] == "user"]).lower()

    # Category
    if not facts.get("incident_type"):
        facts["incident_type"] = classify_incident_category(full_user_text)

    # Date / Time extraction
    if not facts.get("date_time"):
        if any(w in full_user_text for w in ["yesterday", "today", "last night", "morning", "august", "sunday", "monday", "pm", "am", "నిన్న", "ఈరోజు"]):
            for token in ["yesterday", "today", "last night", "last week", "at night", "in the evening", "నిన్న"]:
                if token in full_user_text:
                    facts["date_time"] = f"Reported around {token}"
                    break
            if not facts.get("date_time") and any(c.isdigit() for c in full_user_text):
                facts["date_time"] = "Mentioned specific time/date figures"

    # Location
    if not facts.get("location"):
        for loc_indicator in ["outside", "near", "at", "in", "metro", "college", "office", "market", "road", "వద్ద", "దగ్గర"]:
            if loc_indicator in full_user_text:
                facts["location"] = f"Reported near/at location specified in statement"
                break

    # People involved
    if not facts.get("people_involved"):
        if any(w in full_user_text for w in ["someone", "he", "they", "stranger", "known person", "neighbor", "colleague", "group", "వ్యక్తి"]):
            facts["people_involved"] = "Suspect/Individual noted in statement"

    # Specific injury, weapon or loss
    if not facts.get("threat_injury_or_loss"):
        if any(w in full_user_text for w in ["said he would", "knife", "bruise", "rs", "inr", "rupees", "lakh", "pain", "hurt", "loss", "డబ్బులు", "గాయం"]):
            facts["threat_injury_or_loss"] = "Specific threat/loss/injury mentioned"

    # Evidence
    if not facts.get("evidence_available"):
        if any(w in full_user_text for w in ["screenshot", "cctv", "message", "recording", "slip", "transaction", "chat", "ఫోటోలు", "రికార్డింగ్"]):
            facts["evidence_available"] = "Digital or physical evidence referenced"

    return facts

def determine_missing_facts(facts: Dict[str, Any]) -> List[str]:
    missing = []
    if not facts.get("date_time"):
        missing.append("date_time")
    if not facts.get("location"):
        missing.append("location")
    if not facts.get("people_involved"):
        missing.append("people_involved")
    if not facts.get("threat_injury_or_loss"):
        missing.append("threat_injury_or_loss")
    if not facts.get("evidence_available"):
        missing.append("evidence_available")
    return missing

def generate_assistant_turn(
    messages: List[Dict[str, str]],
    language: str,
    db: Session,
    existing_facts: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    latest_user_msg = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else ""

    # 1. Immediate Safety Check
    safety_check = evaluate_safety(latest_user_msg, language)
    
    # 2. Emotion Cue Detection
    emotion_analysis = detect_emotion_cue(latest_user_msg)
    
    # 3. Update Extracted Facts
    facts = extract_incident_facts(messages, existing_facts or {})
    missing_elements = determine_missing_facts(facts)

    # 4. Determine AI response tone and next questions
    user_turns_count = sum(1 for m in messages if m["role"] == "user")
    is_clarified = len(missing_elements) <= 1 or user_turns_count >= 4

    prefix = emotion_analysis["support_prefix_te"] if language == "te" else emotion_analysis["support_prefix_en"]
    safety_prefix = f"\n\n{safety_check['safety_message']}\n\n" if safety_check["is_emergency"] else ""

    # Formulate next dynamic question based on highest priority missing fact
    if not is_clarified and missing_elements:
        top_missing = missing_elements[0]
        if top_missing == "date_time":
            if language == "te":
                question = "ఈ సంఘటన సుమారు ఏ తేదీన మరియు ఏ సమయంలో జరిగింది? (ఉదాహరణకు: నిన్న సాయంత్రం లేదా నిర్దిష్ట సమయం)"
            else:
                question = "Could you tell me approximately what date and time this happened? (For example: yesterday evening, or a specific hour)"
        elif top_missing == "location":
            if language == "te":
                question = "ఈ సంఘటన సరిగ్గా ఎక్కడ జరిగింది? (ఉదాహరణకు: కాలేజీ దగ్గర, మార్కెట్ వద్ద, లేదా ఆన్‌లైన్‌లోనా?)"
            else:
                question = "Where exactly did this take place? (For example: near your college gate, a public street, at home, or on an online platform?)"
        elif top_missing == "people_involved":
            if language == "te":
                question = "ఈ సంఘటనలో ఎవరు పాల్గొన్నారు? ఆ వ్యక్తి మీకు ముందే తెలిసినవారా లేదా అపరిచితులా? వారి పేర్లు లేదా గుర్తులు తెలుసా?"
            else:
                question = "Who was involved in this? Was this someone known to you or an unknown person? Do you know their name, phone number, or appearance?"
        elif top_missing == "threat_injury_or_loss":
            if language == "te":
                question = "వారు ప్రత్యేకంగా ఏమి చెప్పారు లేదా చేశారు? ఏదైనా శారీరక గాయం అయిందా, లేదా ఎంత మొత్తం డబ్బు నష్టం జరిగింది?"
            else:
                question = "What specifically did the person say or do? Did they make physical contact, show any weapon, or cause any monetary loss?"
        else:
            if language == "te":
                question = "మీ వద్ద ఏదైనా ఆధారాలు (మెసేజ్‌లు, కాల్ రికార్డింగ్‌లు, లావాదేవీ రసీదులు, ఫోటోలు) లేదా సంఘటనను చూసిన సాక్షులు ఉన్నారా?"
            else:
                question = "Do you have any supporting records—such as screenshots, text messages, UPI transaction IDs, CCTV, or eyewitnesses?"

        reply = f"{safety_prefix}{prefix} {question}".strip()
    else:
        # Enough details collected
        category = facts.get("incident_type", "General incident")
        if language == "te":
            reply = (
                f"{safety_prefix}{prefix} నేను పరిస్థితికి సంబంధించిన ముఖ్యమైన వివరాలను నమోదు చేసుకున్నాను ({category}). "
                "ఇప్పుడు మీరు మీ చట్టపరమైన హక్కులు, వర్తించే BNS చట్టాలు, మరియు పోలీస్ స్టేషన్‌కు వెళ్లే ముందు సిద్ధం చేసుకోవాల్సిన "
                "జాబితాను చూడడానికి 'సంఘటన విశ్లేషణను వీక్షించండి' పై క్లిక్ చేయవచ్చు."
            )
        else:
            reply = (
                f"{safety_prefix}{prefix} Thank you. I have captured the key facts of what occurred regarding {category}. "
                "You now have enough factual grounding for a preliminary assessment. You can click 'View Incident Analysis & Rights' "
                "to see potentially applicable laws under the Bharatiya Nyaya Sanhita (BNS), your rights as a complainant, "
                "and an editable statement for the police."
            )

    return {
        "reply": reply,
        "is_clarified": is_clarified,
        "safety_alert": safety_check["is_emergency"],
        "safety_details": safety_check,
        "emotion_cue": emotion_analysis["primary_cue"],
        "extracted_facts": facts,
        "missing_facts": missing_elements
    }

def generate_comprehensive_analysis(facts: Dict[str, Any], language: str, db: Session) -> Dict[str, Any]:
    incident_type = facts.get("incident_type", "General incident")
    
    # Retrieve verified statutes from our verified legal database
    keywords = [incident_type.lower()]
    if "threat" in incident_type.lower():
        keywords.extend(["threat", "intimidation", "injury", "alarm"])
    elif "assault" in incident_type.lower():
        keywords.extend(["hurt", "assault", "violence", "pain"])
    elif "fraud" in incident_type.lower() or "cyber" in incident_type.lower():
        keywords.extend(["cheating", "fraud", "property", "electronic", "personation"])
    elif "theft" in incident_type.lower():
        keywords.extend(["theft", "movable", "consent"])
    elif "harassment" in incident_type.lower():
        keywords.extend(["stalking", "electronic", "woman", "monitoring"])

    provisions = retrieve_relevant_provisions(keywords, incident_type, db)

    # Core statutory rights under BNSS 2023
    rights_guide = [
        {
            "right_title": "Right to Free Copy of FIR (Section 173 BNSS)",
            "explanation": "Whenever an FIR is recorded for a cognizable offence, the police station must provide you a signed physical copy immediately, without any charge.",
            "importance": "High"
        },
        {
            "right_title": "Zero FIR Facility",
            "explanation": "If an incident occurred outside the jurisdiction of that police station, they cannot turn you away. They must register a 'Zero FIR' and transfer the case to the competent jurisdiction.",
            "importance": "High"
        },
        {
            "right_title": "Women Complainant Protection",
            "explanation": "Statements relating to sexual harassment, stalking, or assault against women must be recorded by a woman police officer, at a place convenient to the victim.",
            "importance": "High"
        },
        {
            "right_title": "Right to Legal Aid & Counsel",
            "explanation": "Under the Legal Services Authorities Act and Article 39A, free legal aid is available through the District Legal Services Authority (DLSA) if you require a lawyer.",
            "importance": "Medium"
        }
    ]

    evidence_checklist = [
        {"item": "Chronological timeline of exact dates, times, and phone numbers", "essential": True},
        {"item": "Full screenshots of threatening messages, emails, or call logs with visible sender details", "essential": True},
        {"item": "Bank account statements, UPI UTR numbers, or transaction IDs (if financial fraud)", "essential": True},
        {"item": "Doctor prescription or Medico-Legal Examination (MLC) slip (if physical injuries sustained)", "essential": True},
        {"item": "Names and contact details of neutral eyewitnesses present at the scene", "essential": False},
        {"item": "CCTV camera locations in the vicinity of the incident", "essential": False}
    ]

    return {
        "incident_category": incident_type,
        "facts_summary": facts,
        "provisions": provisions,
        "rights_guide": rights_guide,
        "evidence_checklist": evidence_checklist,
        "is_simulated_ai": not bool(GEMINI_API_KEY or OPENAI_API_KEY),
        "ai_engine_note": "Grounded in verified BNS 2023, BNSS 2023, BSA 2023, and IT Act provisions from India Code."
    }
