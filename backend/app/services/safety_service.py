from typing import Dict, Any, List

EMERGENCY_CONTACTS = [
    {"name": "National Emergency Helpline", "number": "112", "description": "Police, Fire, Ambulance all-in-one emergency helpline across India"},
    {"name": "Women Helpline", "number": "1091", "description": "Immediate 24x7 support for women facing violence or harassment"},
    {"name": "National Cyber Crime Helpline", "number": "1930", "description": "Immediate reporting for financial fraud & cyber extortion (within golden hours)"},
    {"name": "Medical Emergency / Ambulance", "number": "108", "description": "Urgent medical assistance & emergency medical transit"},
    {"name": "Child Helpline", "number": "1098", "description": "Emergency protection and assistance for minors"}
]

# Danger cues in English and Telugu
DANGER_KEYWORDS_EN = [
    "attacking me now", "killing me", "weapon", "knife", "gun", "bleeding heavily",
    "unconscious", "hostage", "inside my house right now", "following me right now",
    "immediate danger", "hurt me right now", "about to hit", "cannot breathe",
    "suicide", "dying"
]

DANGER_KEYWORDS_TE = [
    "ఇప్పుడే దాడి చేస్తున్నారు", "చంపేస్తామని", "కత్తి", "తుపాకీ", "రక్తం కారుతోంది",
    "నా వెనుక పడుతున్నారు", "ఇంటి లోపల ఉన్నారు", "ప్రమాదంలో ఉన్నాను"
]

def evaluate_safety(text: str, language: str = "en") -> Dict[str, Any]:
    text_lower = text.lower()
    is_urgent = False
    triggered_cues: List[str] = []

    for cue in DANGER_KEYWORDS_EN:
        if cue in text_lower:
            is_urgent = True
            triggered_cues.append(cue)

    for cue in DANGER_KEYWORDS_TE:
        if cue in text_lower:
            is_urgent = True
            triggered_cues.append(cue)

    if is_urgent:
        if language == "te":
            safety_message = (
                "⚠️ తక్షణ భద్రత హెచ్చరిక: మీరు లేదా మీ కుటుంబం ప్రస్తుతం తక్షణ ప్రమాదంలో ఉన్నట్లయితే, "
                "వెంటనే సురక్షితమైన ప్రదేశానికి వెళ్లి జాతీయ అత్యవసర నంబర్ 112 కు కాల్ చేయండి. "
                "వైద్య సహాయం అవసరమైతే 108 కు కాల్ చేయండి. మీ భద్రత అన్నింటికన్నా ముఖ్యం."
            )
        else:
            safety_message = (
                "⚠️ IMMEDIATE SAFETY ADVISORY: If you or anyone with you is in immediate physical danger, "
                "please prioritize your safety first. Move to a well-lit, populated, or secure location and "
                "call the National Emergency Number 112 immediately. If someone is severely injured, call 108. "
                "We can proceed with legal preparation once you are safe."
            )
        return {
            "is_emergency": True,
            "safety_message": safety_message,
            "emergency_numbers": EMERGENCY_CONTACTS,
            "triggered_cues": triggered_cues
        }

    return {
        "is_emergency": False,
        "safety_message": None,
        "emergency_numbers": EMERGENCY_CONTACTS,
        "triggered_cues": []
    }
