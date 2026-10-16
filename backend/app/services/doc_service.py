from typing import Dict, Any, List
import re

LEGAL_TERM_GLOSSARY = {
    "cognizable": "A serious crime where a police officer has the statutory authority to make an arrest without a warrant and initiate an investigation immediately.",
    "non-cognizable": "A category of less serious offences or civil-nature grievances where police cannot arrest without a court warrant or investigate without a Magistrate's order.",
    "fir": "First Information Report—the official written document recorded by police upon receiving information relating to the commission of a cognizable offence.",
    "zero fir": "An FIR registered at any police station irrespective of jurisdictional boundaries, which is subsequently transmitted to the competent police station.",
    "bail": "Conditional release of a person awaiting trial, usually secured by personal bond or surety guaranteeing future court appearance.",
    "anticipatory bail": "A judicial direction granting pre-arrest bail to an individual who reasonably apprehends arrest in a non-bailable accusation.",
    "charge sheet": "The final investigation report submitted by police to the Magistrate under Section 193 of the BNSS, 2023, outlining findings and formal charges.",
    "summons": "An authoritative judicial or legal process directing an individual to appear before an authority or produce designated documents.",
    "sub judice": "A matter currently under active judicial consideration by a court, precluding public adjudication.",
    "prima facie": "Based on first impression; accepted as correct until disproven by rebutting evidence.",
    "caveat": "A formal notice submitted to a court requesting that no order be passed against the applicant without prior hearing.",
    "injunction": "A judicial order restraining a party from doing an act or compelling them to restore an earlier status quo."
}

def analyze_document_text(content: str, filename: str) -> Dict[str, Any]:
    text_lower = content.lower()

    # Extract dates
    dates_found = re.findall(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b', content, re.IGNORECASE)

    # Extract case or FIR references
    case_numbers = re.findall(r'\b(?:FIR\s+No\.?|Case\s+No\.?|Cr\.?\s+No\.?|Notice\s+No\.?|CC\s+No\.?|OS\s+No\.?)\s*[:#-]?\s*[\w\d/-]+', content, re.IGNORECASE)

    # Identify issuing forum/authority
    identified_forum = "Unspecified Authority"
    if "police station" in text_lower or "station house officer" in text_lower or "sho" in text_lower:
        identified_forum = "Police Department (Local Police Station)"
    elif "consumer disputes" in text_lower or "consumer forum" in text_lower or "dcdrc" in text_lower:
        identified_forum = "Consumer Disputes Redressal Commission"
    elif "magistrate" in text_lower or "court of" in text_lower or "civil judge" in text_lower:
        identified_forum = "Judicial Court / Magistrate"
    elif "labour commissioner" in text_lower or "conciliation officer" in text_lower:
        identified_forum = "Labour Department / Authority"
    elif "cyber crime" in text_lower or "1930" in text_lower:
        identified_forum = "Cyber Crime Reporting Unit"

    # Find matched legal terms
    matched_terms = []
    for term, definition in LEGAL_TERM_GLOSSARY.items():
        if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
            matched_terms.append({
                "term": term.upper(),
                "plain_meaning": definition
            })

    # Summary generator
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    first_few_lines = " ".join(lines[:3]) if lines else "Document content uploaded."

    summary = (
        f"This document appears to relate to '{filename}' issued by or addressed to '{identified_forum}'. "
        f"Key excerpt: \"{first_few_lines[:250]}...\". "
        f"It contains {len(dates_found)} identifiable date reference(s) and {len(case_numbers)} reference code(s)."
    )

    recommended_questions = [
        "What is the statutory deadline or response period mentioned in this document?",
        "Is this an official court summons, a police notice under BNSS Section 35(3), or private legal correspondence?",
        "Should I appear in person or reply in writing through an advocate?"
    ]

    return {
        "filename": filename,
        "summary": summary,
        "identified_forum": identified_forum,
        "dates_found": list(set(dates_found)),
        "case_references": list(set(case_numbers)),
        "explained_terms": matched_terms,
        "recommended_questions": recommended_questions
    }
