from typing import Dict, Any, List
import re

LEGAL_TERM_GLOSSARY = {
    "cognizable": "A serious crime where a police officer has the authority to make an arrest without a warrant and start an investigation immediately.",
    "non-cognizable": "A category of less serious offences where police cannot arrest without a court warrant or investigate without a Magistrate's order.",
    "fir": "First Information Report—the official written document prepared by police when they receive information about the commission of a cognizable offence.",
    "zero fir": "An FIR registered at any police station regardless of geographical jurisdiction, which is subsequently transferred to the competent police station.",
    "bail": "Temporary release of an accused person awaiting trial, usually upon security deposit or personal bond guaranteeing appearance in court.",
    "anticipatory bail": "A court order granting bail in advance to a person apprehending arrest in a non-bailable offence.",
    "charge sheet": "The final report prepared by investigating police officers after concluding an investigation, outlining charges against the accused.",
    "summons": "An official court order directing an individual to appear before a judge or produce specific documents.",
    "sub judice": "A matter currently under active judicial consideration and awaiting court verdict.",
    "prima facie": "Based on the first impression; accepted as correct until proven otherwise by evidence."
}

def analyze_document_text(content: str, filename: str) -> Dict[str, Any]:
    text_lower = content.lower()
    
    # Extract dates
    dates_found = re.findall(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b', content, re.IGNORECASE)
    
    # Extract case or FIR references
    case_numbers = re.findall(r'\b(?:FIR\s+No\.?|Case\s+No\.?|Cr\.?\s+No\.?|Notice\s+No\.?)\s*[:#-]?\s*[\w\d/-]+', content, re.IGNORECASE)
    
    # Find matched legal terms
    matched_terms = []
    for term, definition in LEGAL_TERM_GLOSSARY.items():
        if term in text_lower:
            matched_terms.append({
                "term": term.upper(),
                "plain_meaning": definition
            })

    # Summary generator
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    first_few_lines = " ".join(lines[:3]) if lines else "Document content uploaded."
    
    summary = (
        f"This document appears to relate to '{filename}'. "
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
        "dates_found": list(set(dates_found)),
        "case_references": list(set(case_numbers)),
        "explained_terms": matched_terms,
        "recommended_questions": recommended_questions
    }
