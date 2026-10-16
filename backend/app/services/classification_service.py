import re
from typing import Dict, Any, List, Tuple

CATEGORY_RULES = [
    {
        "category": "Physical Assault or Threats",
        "jurisdiction": "criminal",
        "keywords_en": ["hit", "beat", "slap", "punch", "assault", "injur", "blood", "attack", "threat", "kill", "harm", "blackmail", "intimidat", "frighten", "weapon", "knife", "gun"],
        "keywords_te": ["కొట్టారు", "కొట్ట", "దాడి", "గాయం", "రక్తం", "చంపేస్తామని", "చంపేస్తానని", "చంపే", "బెదిరింపు", "బెదిరించా", "బెదిరిం", "కత్తి", "తుపాకీ"],
        "forum": "Police Station (BNS 2023) / Criminal Magistrate"
    },
    {
        "category": "Harassment or Stalking",
        "jurisdiction": "criminal",
        "keywords_en": ["stalk", "follow", "harass", "instagram", "whatsapp", "unwanted call", "photo leak", "obscene", "creepy message"],
        "keywords_te": ["వేధింపు", "వెంటపడుతున్నారు", "అసభ్య", "ఫొటోలు"],
        "forum": "Police Station (BNS Sec 78) / Women Helpline / Cyber Cell"
    },
    {
        "category": "Theft or Robbery",
        "jurisdiction": "criminal",
        "keywords_en": ["stole", "theft", "snatch", "rob", "burglar", "missing phone", "laptop stolen", "pickpocket", "wallet taken"],
        "keywords_te": ["దొంగతనం", "ఎత్తుకెళ్లారు", "లాక్కున్నారు"],
        "forum": "Police Station (BNS Sec 303 - FIR)"
    },
    {
        "category": "Fraud and Financial Scams",
        "jurisdiction": "financial_cyber",
        "keywords_en": ["scam", "fraud", "upi", "bank", "otp", "stole money", "cheated", "account debit", "phishing", "crypto scam", "fake lottery", "loan app"],
        "keywords_te": ["మోసం", "డబ్బులు", "ఖాతా", "బ్యాంక్"],
        "forum": "National Cyber Crime Helpline (1930) / Cyber Crime Portal / Police"
    },
    {
        "category": "Domestic Violence",
        "jurisdiction": "family_dv",
        "keywords_en": ["husband", "in-laws", "domestic violence", "dowry", "wife beater", "kicked out of house", "marital abuse"],
        "keywords_te": ["గృహ హింస", "భర్త", "అత్తమామలు", "వరకట్నం"],
        "forum": "Protection Officer (PWDVA 2005) / Women Helpline (1091/181) / Magistrate"
    },
    {
        "category": "Missing Persons",
        "jurisdiction": "missing_person",
        "keywords_en": ["missing", "disappeared", "not returned home", "cannot find", "kidnap", "lost child"],
        "keywords_te": ["కనిపించడం లేదు", "జాడ లేదు", "కిడ్నాప్"],
        "forum": "Local Police Station (Mandatory Missing Person Registration)"
    },
    {
        "category": "Property Disputes",
        "jurisdiction": "civil",
        "keywords_en": ["land dispute", "property border", "boundary", "tenant", "landlord", "eviction", "rent dispute", "trespass without force", "title deed", "possession of land"],
        "keywords_te": ["భూమి వివాదం", "ఆస్తి తగాదా", "అద్దె", "ఇంటి యజమాని", "సరిహద్దు"],
        "forum": "Civil Court / Tehsildar / Sub-Divisional Magistrate (SDM)"
    },
    {
        "category": "Consumer Complaints",
        "jurisdiction": "consumer",
        "keywords_en": ["defective product", "warranty refused", "service deficiency", "fake product delivered", "e-commerce refund", "flipkart", "amazon", "flight refund", "hospital overcharge"],
        "keywords_te": ["వస్తువు లోపం", "రీఫండ్", "వినియోగదారుల"],
        "forum": "National Consumer Helpline / District Consumer Commission (DCDRC)"
    },
    {
        "category": "Employment Disputes",
        "jurisdiction": "employment",
        "keywords_en": ["salary not paid", "unpaid wages", "wrongful termination", "fired without notice", "pf not deposited", "employer harassment", "working hours"],
        "keywords_te": ["జీతం ఇవ్వలేదు", "ఉద్యోగం నుండి తీసేశారు", "యాజమాన్యం"],
        "forum": "Labour Commissioner / Conciliation Officer / Labour Court"
    },
    {
        "category": "Family Disputes",
        "jurisdiction": "family",
        "keywords_en": ["divorce", "child custody", "maintenance", "alimony", "family property partition", "inheritance", "will dispute"],
        "keywords_te": ["విడాకులు", "పిల్లల సంరక్షణ", "భరణం", "ఆస్తి పంపకాలు"],
        "forum": "Family Court / District Legal Services Authority (DLSA Mediation)"
    }
]

def classify_incident_nature(history: List[Dict[str, str]], existing_facts: Dict[str, Any]) -> Dict[str, Any]:
    full_text = " ".join([m["content"] for m in history if m["role"] == "user"]).lower()
    facts = existing_facts.copy() if existing_facts else {}

    matched_rule = None
    max_matches = 0

    for rule in CATEGORY_RULES:
        matches = sum(1 for kw in rule["keywords_en"] if re.search(r'\b' + re.escape(kw), full_text))
        matches += sum(2 for kw in rule["keywords_te"] if kw in full_text)
        if matches > max_matches:
            max_matches = matches
            matched_rule = rule

    if matched_rule and max_matches >= 1:
        if not facts.get("incident_type"):
            facts["incident_type"] = matched_rule["category"]
        facts["jurisdiction_type"] = matched_rule["jurisdiction"]
        suggested_forum = matched_rule["forum"]
    else:
        if not facts.get("incident_type"):
            facts["incident_type"] = "Uncertain / Mixed Matter"
        facts["jurisdiction_type"] = "uncertain"
        suggested_forum = "Preliminary Review / Clarification Needed"

    # Extract date/time
    if not facts.get("date_time"):
        date_matches = re.findall(r'\b(?:yesterday|today|last night|last week|morning|evening|\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', full_text, re.IGNORECASE)
        if date_matches:
            facts["date_time"] = date_matches[0]
        elif any(w in full_text for w in ["నిన్న", "ఈరోజు", "మొన్న", "రాత్రి", "ఉదయం"]):
            for token in ["నిన్న", "ఈరోజు", "మొన్న", "రాత్రి"]:
                if token in full_text:
                    facts["date_time"] = token
                    break

    # Extract location
    if not facts.get("location"):
        loc_match = re.search(r'\b(?:at|near|outside|in|inside|around)\s+([a-zA-Z0-9\s,]{3,30})', full_text, re.IGNORECASE)
        if loc_match:
            facts["location"] = loc_match.group(0).strip()
        elif any(w in full_text for w in ["కాలేజ్", "కాలేజీ", "రోడ్డు", "బస్టాండ్", "ఇంటి వద్ద", "మార్కెట్"]):
            facts["location"] = "Specified local address in Telangana/Andhra"

    # People involved
    if not facts.get("people_involved"):
        people = []
        for kw in ["stranger", "unknown person", "neighbor", "colleague", "employer", "shopkeeper", "police", "husband", "landlord", "tenant"]:
            if kw in full_text:
                people.append(kw.capitalize())
        for kw in ["అపరిచితుడు", "పక్కింటి వ్యక్తి", "యజమాని", "భర్త"]:
            if kw in full_text:
                people.append(kw)
        if people:
            facts["people_involved"] = ", ".join(people)

    # Alleged actions
    if not facts.get("alleged_actions"):
        for action_word in ["demanded", "threatened", "hit", "stole", "cheated", "refused", "locked", "abused", "కొట్టారు", "బెదిరించారు", "తీసుకున్నారు"]:
            if action_word in full_text:
                facts["alleged_actions"] = f"Reported actions involving '{action_word}'"
                break

    # Injuries or loss
    if not facts.get("injuries_or_loss"):
        loss_match = re.search(r'\b(?:rs\.?|inr|rupees|lakh|crore)\s*[\d,]+', full_text, re.IGNORECASE)
        if loss_match:
            facts["injuries_or_loss"] = f"Financial loss reported: {loss_match.group(0)}"
        elif any(w in full_text for w in ["fracture", "cut", "bruise", "bleeding", "wound", "hospital", "గాయం", "రక్తం"]):
            facts["injuries_or_loss"] = "Physical bodily injury sustained"

    # Evidence
    if not facts.get("evidence_mentioned"):
        evidence_items = []
        for ev in ["screenshot", "cctv", "recording", "call log", "whatsapp", "bill", "invoice", "receipt", "agreement", "ఫోటోలు", "రశీదు", "ఆధారాలు"]:
            if ev in full_text:
                evidence_items.append(ev)
        if evidence_items:
            facts["evidence_mentioned"] = ", ".join(evidence_items)

    return {
        "facts": facts,
        "suggested_forum": suggested_forum
    }

def determine_missing_elements(facts: Dict[str, Any]) -> List[str]:
    """Identifies remaining priority missing factual elements."""
    missing = []
    if not facts.get("date_time"):
        missing.append("date_time")
    if not facts.get("location"):
        missing.append("location")
    if not facts.get("people_involved"):
        missing.append("people_involved")
    if not facts.get("alleged_actions"):
        missing.append("alleged_actions")
    if not facts.get("injuries_or_loss"):
        missing.append("injuries_or_loss")
    if not facts.get("evidence_mentioned"):
        missing.append("evidence_mentioned")
    return missing
