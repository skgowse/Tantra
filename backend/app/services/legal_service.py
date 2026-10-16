from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import LegalProvision

VERIFIED_INDIAN_PROVISIONS = [
    {
        "act": "Bharatiya Nyaya Sanhita, 2023",
        "section_number": "351",
        "title": "Criminal Intimidation",
        "category": "Threat",
        "official_text": (
            "Whoever threatens another with any injury to his person, reputation or property, "
            "or to the person or reputation of any one in whom that person is interested, with intent "
            "to cause alarm to that person, or to cause that person to do any act which he is not legally "
            "bound to do, or to omit to do any act which that person is legally entitled to do, as the means "
            "of avoiding the execution of such threat, commits criminal intimidation."
        ),
        "plain_explanation": (
            "If someone intentionally threatens to physically harm you, ruin your reputation, or damage your "
            "property to frighten you or force you to do something against your will, it constitutes criminal intimidation."
        ),
        "conditions_exceptions": "The threat must be real and communicate an intent to cause injury or alarm. Mere rude words or vague anger without intention to cause alarm may not meet the threshold.",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/21437",
        "last_verified": "2026-07-01"
    },
    {
        "act": "Bharatiya Nyaya Sanhita, 2023",
        "section_number": "115",
        "title": "Voluntarily Causing Hurt",
        "category": "Assault",
        "official_text": (
            "Whoever does any act with the intention of thereby causing hurt to any person, or with the "
            "knowledge that he is likely thereby to cause hurt to any person, and does thereby cause hurt to any person, "
            "is said voluntarily to cause hurt. Punishable with imprisonment up to one year, or fine up to ten thousand rupees, or both."
        ),
        "plain_explanation": (
            "Physical violence, hitting, punching, or causing bodily pain, injury, or illness intentionally or knowingly "
            "is classified as causing hurt."
        ),
        "conditions_exceptions": "Requires bodily pain or injury caused by intentional or knowing action. If caused under grave and sudden provocation, reduced penalties apply.",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/21437",
        "last_verified": "2026-07-01"
    },
    {
        "act": "Bharatiya Nyaya Sanhita, 2023",
        "section_number": "117",
        "title": "Voluntarily Causing Grievous Hurt",
        "category": "Assault",
        "official_text": (
            "Whoever voluntarily causes hurt, if the hurt which he intends to cause or knows himself to be likely to cause "
            "is grievous hurt, and the hurt which he causes is grievous hurt, is said voluntarily to cause grievous hurt. "
            "Includes fractures, loss of sight or hearing, permanent disfiguration, or severe pain for twenty days."
        ),
        "plain_explanation": (
            "Serious physical harm—such as bone fractures, severe cuts, head trauma, loss of senses, or injuries incapacitating "
            "a victim for 20+ days—is treated as grievous hurt with harsher legal penalties (imprisonment up to 7 years)."
        ),
        "conditions_exceptions": "Medical examination and formal medico-legal case (MLC) report are vital evidence.",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/21437",
        "last_verified": "2026-07-01"
    },
    {
        "act": "Bharatiya Nyaya Sanhita, 2023",
        "section_number": "318",
        "title": "Cheating and Dishonestly Inducing Delivery of Property",
        "category": "Fraud",
        "official_text": (
            "Whoever, by deceiving any person, fraudulently or dishonestly induces the person so deceived to deliver "
            "any property to any person, or to consent that any person shall retain any property... commits cheating."
        ),
        "plain_explanation": (
            "Deceiving someone through lies, false promises, or fabricated claims into handing over money, property, "
            "or bank transfers is cheating. Penalties range up to 3 to 7 years of imprisonment."
        ),
        "conditions_exceptions": "Dishonest or fraudulent intention must exist from the inception of the transaction, distinguishing civil breach of contract from criminal fraud.",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/21437",
        "last_verified": "2026-07-01"
    },
    {
        "act": "Information Technology Act, 2000",
        "section_number": "66D",
        "title": "Cheating by Personation using Computer Resource",
        "category": "Cybercrime",
        "official_text": (
            "Whoever, by means of any communication device or computer resource, cheats by personating, shall be punished "
            "with imprisonment of either description for a term which may extend to three years and shall also be liable to fine which may extend to one lakh rupees."
        ),
        "plain_explanation": (
            "Pretending to be a bank official, police officer, company executive, or someone else over phone calls, WhatsApp, "
            "websites, or social media to defraud money or steal credentials."
        ),
        "conditions_exceptions": "Applies whenever an electronic device, phone, or computer was the instrument used to execute the impersonation and fraud.",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/13116",
        "last_verified": "2026-07-01"
    },
    {
        "act": "Bharatiya Nyaya Sanhita, 2023",
        "section_number": "303",
        "title": "Theft",
        "category": "Theft",
        "official_text": (
            "Whoever, intending to take dishonestly any movable property out of the possession of any person without "
            "that person's consent, moves that property in order to such taking, is said to commit theft."
        ),
        "plain_explanation": (
            "Taking someone's movable property (laptop, phone, vehicle, wallet, cash) without their consent dishonestly."
        ),
        "conditions_exceptions": "Applies to movable assets taken without consent. Community service or imprisonment up to 3 years can be awarded.",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/21437",
        "last_verified": "2026-07-01"
    },
    {
        "act": "Bharatiya Nyaya Sanhita, 2023",
        "section_number": "78",
        "title": "Stalking",
        "category": "Online harassment",
        "official_text": (
            "Any man who follows a woman and contacts, or attempts to contact such woman to foster personal interaction "
            "repeatedly despite a clear indication of disinterest; or monitors the use by a woman of the internet, email or "
            "any other form of electronic communication, commits the offence of stalking."
        ),
        "plain_explanation": (
            "Repeatedly following someone, sending unwanted messages despite disinterest, or digitally monitoring their social media, "
            "location, or phone activities without authorization."
        ),
        "conditions_exceptions": "Exceptions exist if done for preventing/detecting crime by authority authorized by law.",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/21437",
        "last_verified": "2026-07-01"
    },
    {
        "act": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section_number": "173",
        "title": "Information in Cognizable Cases (FIR Registration & Zero FIR)",
        "category": "Rights_Procedure",
        "official_text": (
            "Every information relating to the commission of a cognizable offence, if given orally to an officer in charge "
            "of a police station, shall be reduced to writing... and a copy of the information as recorded shall be given "
            "forthwith, free of cost, to the informant or the victim. Provided that information may be given electronically and signed within three days."
        ),
        "plain_explanation": (
            "Your statutory right: When reporting a serious (cognizable) offence, the police station must record your complaint, "
            "and give you a physical copy of the First Information Report (FIR) immediately and completely FREE of cost. "
            "If the crime happened outside their jurisdiction, they must still register a 'Zero FIR' and transfer it."
        ),
        "conditions_exceptions": "Cognizable offences include assault, robbery, cyber fraud, rape, kidnapping, etc. For non-cognizable offences (simple disputes), an NCR (Non-Cognizable Report) is registered instead.",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/21438",
        "last_verified": "2026-07-01"
    },
    {
        "act": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "section_number": "35",
        "title": "When Police May Arrest Without Warrant & Protections",
        "category": "Rights_Procedure",
        "official_text": (
            "Any police officer may without an order from a Magistrate and without a warrant, arrest any person who commits "
            "a cognizable offence in the presence of a police officer, or against whom reasonable complaint has been made... "
            "Provided that in offences punishable with imprisonment less than 7 years, arrest is not automatic and notice of appearance must be issued."
        ),
        "plain_explanation": (
            "Arrest is strictly regulated. For offences with punishment under 7 years, police must generally issue a notice of appearance "
            "rather than make routine arrests. If arrested, you have the right to inform family and be produced before a Magistrate within 24 hours."
        ),
        "conditions_exceptions": "Police officer must record reasons in writing whether making or not making an arrest.",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/21438",
        "last_verified": "2026-07-01"
    },
    {
        "act": "Bharatiya Sakshya Adhiniyam, 2023",
        "section_number": "61 & 63",
        "title": "Admissibility of Electronic Records and Digital Evidence",
        "category": "Evidence",
        "official_text": (
            "Nothing in this Adhiniyam shall apply to electronic records... Any information contained in an electronic record "
            "which is printed on a paper, stored, recorded or copied in optical or magnetic media shall be deemed to be also a document... "
            "accompanied by a certificate under Section 63."
        ),
        "plain_explanation": (
            "Digital records—including WhatsApp chats, SMS, emails, CCTV footage, UPI bank screenshots, and audio recordings—are "
            "fully valid legal evidence in court and before the police when presented with proper device verification."
        ),
        "conditions_exceptions": "Take screenshots with visible timestamps and phone numbers; retain original electronic devices without deleting messages.",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/21439",
        "last_verified": "2026-07-01"
    }
]

def seed_legal_provisions_if_empty(db: Session):
    existing = db.query(LegalProvision).first()
    if existing:
        return
    for item in VERIFIED_INDIAN_PROVISIONS:
        prov = LegalProvision(
            act=item["act"],
            section_number=item["section_number"],
            title=item["title"],
            category=item["category"],
            official_text=item["official_text"],
            plain_explanation=item["plain_explanation"],
            conditions_exceptions=item["conditions_exceptions"],
            source_url=item["source_url"],
            last_verified=item["last_verified"]
        )
        db.add(prov)
    db.commit()

def retrieve_relevant_provisions(keywords: List[str], category_hint: Optional[str], db: Session) -> List[Dict[str, Any]]:
    query = db.query(LegalProvision)
    all_provisions = query.all()
    results = []

    for prov in all_provisions:
        score = 0
        prov_text = f"{prov.act} {prov.section_number} {prov.title} {prov.category} {prov.plain_explanation} {prov.conditions_exceptions}".lower()
        
        if category_hint and category_hint.lower() in prov.category.lower():
            score += 3

        for kw in keywords:
            if kw.lower() in prov_text:
                score += 2

        if score > 0:
            results.append({
                "act": prov.act,
                "section_number": prov.section_number,
                "title": prov.title,
                "category": prov.category,
                "official_text": prov.official_text,
                "plain_explanation": prov.plain_explanation,
                "conditions_exceptions": prov.conditions_exceptions,
                "source_url": prov.source_url,
                "last_verified": prov.last_verified,
                "relevance_score": score
            })

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:4]
