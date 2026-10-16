from typing import Dict, Any

EMOTION_PATTERNS = {
    "fear": [
        "scared", "afraid", "terrified", "threatened", "horror", "frightened", "panic",
        "భయంగా ఉంది", "భయపడుతున్నాను", "చంపేస్తామని బెదిరించారు"
    ],
    "anxiety": [
        "worried", "nervous", "anxious", "restless", "stressed", "tense", "sleepless",
        "ఆందోళన", "కంగారుగా ఉంది", "ఏం చేయాలో అర్థం కావడం లేదు"
    ],
    "distress": [
        "crying", "broken", "helpless", "devastated", "suffering", "nightmare", "trauma",
        "ఏడుపు వస్తుంది", "దిక్కుతోచడం లేదు", "బాధగా ఉంది"
    ],
    "anger": [
        "furious", "angry", "rage", "cheated", "betrayed", "robbed", "outraged",
        "కోపంగా ఉంది", "మోసం చేశారు", "అన్యాయం"
    ],
    "confusion": [
        "confused", "don't understand", "no idea", "what to do", "lost", "is this crime",
        "అర్థం కావట్లేదు", "ఇది నేరమా", "ఏం చేయాలో తెలియదు"
    ],
    "urgency": [
        "quick", "fast", "urgent", "emergency", "immediately", "right now", "hurry",
        "త్వరగా", "వెంటనే", "అర్జెంట్"
    ]
}

def detect_emotion_cue(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    scores = {}

    for emotion, cues in EMOTION_PATTERNS.items():
        count = sum(1 for cue in cues if cue in text_lower)
        if count > 0:
            scores[emotion] = count

    if not scores:
        return {
            "primary_cue": "neutral",
            "support_prefix_en": "I understand. Let's look at this step-by-step.",
            "support_prefix_te": "నేను అర్థం చేసుకున్నాను. దీనిని ఒక్కొక్క దశగా పరిశీలిద్దాం.",
            "should_keep_short": False
        }

    # Pick top cue
    primary = max(scores, key=scores.get)

    prefixes = {
        "fear": {
            "en": "I hear you, and it is completely understandable to feel shaken. You are not alone, and we will take this one calm step at a time.",
            "te": "మీరు భయపడుతున్నారని నేను అర్థం చేసుకోగలను. మీరు ఒంటరిగా లేరు, మనం ప్రశాంతంగా దీనిపై స్పష్టత తెచ్చుకుందాం."
        },
        "anxiety": {
            "en": "Please take a deep breath. Understanding the legal options clearly often helps reduce anxiety. Let's break this down together.",
            "te": "దయచేసి కంగారు పడవద్దు. చట్టపరమైన అవకాశాలను అర్థం చేసుకోవడం ద్వారా ఆందోళన తగ్గుతుంది."
        },
        "distress": {
            "en": "I am truly sorry you are going through this painful experience. We will handle this gently and prioritize clarity for you.",
            "te": "మీరు ఈ కష్టమైన పరిస్థితిని ఎదుర్కొంటున్నందుకు బాధగా ఉంది. మీకు సహాయం చేయడానికి మేము సిద్ధంగా ఉన్నాము."
        },
        "anger": {
            "en": "It is completely valid to feel angry when an injustice occurs. Channeling that into documented facts is the strongest way to prepare.",
            "te": "అన్యాయం జరిగినప్పుడు కోపం రావడం సహజం. నిజాలను క్రమపద్ధతిలో నమోదు చేయడం ద్వారా న్యాయం పొందవచ్చు."
        },
        "confusion": {
            "en": "Do not worry about legal terminology. You do not need to know law sections—just describe events in everyday words.",
            "te": "చట్టపరమైన పదాల గురించి ఆందోళన చెందవద్దు. సాధారణ మాటల్లో ఏమి జరిగిందో చెప్పండి."
        },
        "urgency": {
            "en": "I hear the urgency. Let's capture the key essentials quickly.",
            "te": "విషయం అత్యవసరమని అర్థమైంది. ముఖ్యమైన వివరాలను త్వరగా తెలుసుకుందాం."
        }
    }

    selected = prefixes.get(primary, {
        "en": "I understand. Let's walk through the details together.",
        "te": "సరే, వివరాలను వివరంగా పరిశీలిద్దాం."
    })

    return {
        "primary_cue": primary,
        "support_prefix_en": selected["en"],
        "support_prefix_te": selected["te"],
        "should_keep_short": primary in ["fear", "distress", "urgency"]
    }
