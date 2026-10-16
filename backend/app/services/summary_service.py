from typing import Dict, Any, List

def generate_factual_incident_summary(facts: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
    """
    Generates a neutral, strictly factual incident summary.
    Applies strict anti-fabrication rules:
    - Never assumes 'no provocation'
    - Never assumes guilt or motive
    - Marks missing information as 'Not provided'
    - Customizes target authority by jurisdiction (Police, Consumer Commission, Civil Court, etc.)
    """
    inc_type = facts.get("incident_type") or "Reported incident (Classification preliminary)"
    jurisdiction = facts.get("jurisdiction_type", "uncertain")
    dt = facts.get("date_time") or "Not provided"
    loc = facts.get("location") or "Not provided"
    people = facts.get("people_involved") or "Not specified by user"
    actions = facts.get("alleged_actions") or "Details as reported by the user"
    impact = facts.get("injuries_or_loss") or "None reported or not provided"
    evidence = facts.get("evidence_mentioned") or "None specified at this time"
    uncertainties = facts.get("uncertainties_or_contradictions", [])

    # Tailor the target authority and suggested venue based on jurisdiction
    if jurisdiction == "consumer":
        target_authority = "District Consumer Disputes Redressal Commission (DCDRC) / National Consumer Helpline"
        purpose_text = "To place on record a grievance regarding consumer deficiency / unfair trade practice and explore formal redressal."
        suggested_questions = [
            "What is the statutory limitation period (usually 2 years) to file a consumer complaint?",
            "Can I file this complaint online through the e-Daakhil portal (edaakhil.nic.in)?",
            "What documentary proof of invoice and payment confirmation is required?"
        ]
        checklist = [
            {"item": "Original tax invoice / cash memo / order confirmation", "checked": True},
            {"item": "Proof of payment (Bank statement, UPI transaction ID)", "checked": True},
            {"item": "Copies of written correspondence / emails sent to seller seeking redressal", "checked": True},
            {"item": "Photographs of defective product or delivery condition", "checked": False}
        ]
    elif jurisdiction == "civil":
        target_authority = "Civil Court / Sub-Divisional Magistrate (SDM) / Legal Services Authority (DLSA)"
        purpose_text = "To record facts concerning a civil or property dispute for legal consultation, mediation, or civil court proceedings."
        suggested_questions = [
            "Is there a registered title deed, lease agreement, or patta document supporting this claim?",
            "Can this matter be resolved through pre-litigation mediation at the District Legal Services Authority (DLSA)?",
            "What temporary injunctive relief (stay order) may be available under Order 39 of the Code of Civil Procedure?"
        ]
        checklist = [
            {"item": "Government identity proof", "checked": True},
            {"item": "Title deeds, lease agreement, or boundary survey records", "checked": True},
            {"item": "Photographs of property / disputed boundary", "checked": False},
            {"item": "Previous tax receipts, municipal utility bills, or mutation records", "checked": False}
        ]
    elif jurisdiction == "employment":
        target_authority = "Office of the Labour Commissioner / Conciliation Officer / Labour Court"
        purpose_text = "To record employment-related grievances (such as unpaid wages, severance, or unlawful termination) for statutory conciliation."
        suggested_questions = [
            "What is the statutory timeline under the Payment of Wages Act or Industrial Disputes Act to seek conciliation?",
            "Has a formal demand notice been served on the employer?",
            "What records of attendance, appointment letter, and salary slips are available?"
        ]
        checklist = [
            {"item": "Offer letter or employment agreement", "checked": True},
            {"item": "Salary slips or bank statement showing salary credits", "checked": True},
            {"item": "Termination letter or email communications with HR/Management", "checked": True},
            {"item": "PF / ESIC contribution statements (if applicable)", "checked": False}
        ]
    elif jurisdiction == "family_dv":
        target_authority = "Protection Officer (PWDVA 2005) / Judicial Magistrate / Women Helpline (1091/181)"
        purpose_text = "To document domestic distress or violence for seeking protection orders, residence orders, or counseling under the Protection of Women from Domestic Violence Act, 2005."
        suggested_questions = [
            "Can a Protection Officer assist in preparing a Domestic Incident Report (DIR) free of cost?",
            "What interim relief (protection from eviction, monetary support) can be granted by the Magistrate?",
            "Is free legal representation available through the District Legal Services Authority (DLSA)?"
        ]
        checklist = [
            {"item": "Identity proof and residential details", "checked": True},
            {"item": "Medical prescription or injury documentation (if any physical harm occurred)", "checked": False},
            {"item": "Saved phone messages, call logs, or audio recordings (if any)", "checked": False},
            {"item": "Marriage certificate or proof of shared domestic relationship", "checked": False}
        ]
    elif jurisdiction == "financial_cyber":
        target_authority = "National Cyber Crime Reporting Portal (1930 / cybercrime.gov.in) & Cyber Police Station"
        purpose_text = "To report suspected cyber / online financial fraud for immediate bank account freezing (Golden Hour) and statutory investigation."
        suggested_questions = [
            "Has the financial fraud acknowledgment reference number from 1930 been recorded?",
            "Has a formal written dispute and chargeback request been submitted to the complainant's home bank?",
            "Which investigating officer or cyber nodal cell is handling the account lien?"
        ]
        checklist = [
            {"item": "Bank account statement with highlighted disputed transactions", "checked": True},
            {"item": "Transaction Reference / UTR numbers and recipient account details", "checked": True},
            {"item": "Screenshots of fake SMS, phishing URL, or WhatsApp chat", "checked": True},
            {"item": "Cyber crime portal acknowledgment slip (if 1930 already dialed)", "checked": False}
        ]
    else:
        # Criminal / General Police Station
        target_authority = "Station House Officer (SHO), Local Police Station"
        purpose_text = "To bring reported cognizable/non-cognizable events to the notice of the police authorities for factual inquiry and necessary lawful action under the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023."
        suggested_questions = [
            "May I please receive an official stamped acknowledgment on a duplicate copy of this statement?",
            "If this discloses a cognizable offence, can I receive a signed copy of the FIR free of cost as mandated under Section 173 of the BNSS, 2023?",
            "Who is the designated Investigating Officer assigned to this inquiry?"
        ]
        checklist = [
            {"item": "Printed copy of this statement for police acknowledgment", "checked": True},
            {"item": "Government identity proof (Aadhaar, Voter ID, or Driving License)", "checked": True},
            {"item": "Electronic device with original messages/recordings preserved (intact metadata)", "checked": False},
            {"item": "Medical prescription or injury examination slip (if physical harm occurred)", "checked": False}
        ]

    uncertainty_block = ""
    if uncertainties:
        uncertainty_block = "\n7. UNRESOLVED OR CLARIFICATION POINTS:\n" + "\n".join([f"- {u}" for u in uncertainties])

    statement_body = f"""================================================================================
                    FACTUAL INCIDENT SUMMARY
================================================================================
(Preliminary Citizen Factual Aid - Prepared with Legal Tantra)
Important: This document is drafted solely from statements provided by the citizen.
It does not constitute an official police document, a legal pleading, or certified legal counsel.

TARGET AUTHORITY / VENUE:
{target_authority}

1. PURPOSE OF APPROACHING THE AUTHORITY:
{purpose_text}

2. INCIDENT CLASSIFICATION (PRELIMINARY):
Reported as: {inc_type}

3. DATE, APPROXIMATE TIME AND LOCATION:
- Date / Time: {dt}
- Location: {loc}

4. PERSONS OR ROLES INVOLVED (AS REPORTED):
{people}

5. FACTUAL ACCOUNT OF EVENTS (AS REPORTED BY CITIZEN):
On the date and location referenced above, the complainant reports the following events:
- Reported narrative: {actions}

6. REPORTED INJURIES, HARM OR FINANCIAL LOSS:
{impact}

7. EVIDENCE AND SUPPORTING RECORDS CITED:
{evidence}
{uncertainty_block}

8. ASSISTANCE SOUGHT:
The complainant respectfully requests the competent authority to:
(a) Receive and formally acknowledge receipt of this factual summary.
(b) Conduct an inquiry in accordance with the applicable law.
(c) Issue an official acknowledgment or reference code for tracking.

--------------------------------------------------------------------------------
Signature of Citizen / Complainant: ____________________
Full Name: ____________________
Date: ____________________
Contact Details: ____________________
================================================================================
Notice: Please verify all statements above before submitting to any authority.
"""

    verification_checklist = [
        "I have reviewed all dates and times to ensure they match what actually happened.",
        "I confirm that all persons, amounts, and statements included are strictly based on my personal knowledge.",
        "I understand that this summary is a factual preparation aid and not an official government document."
    ]

    return {
        "target_authority": target_authority,
        "statement_text": statement_body.strip(),
        "evidence_checklist": checklist,
        "recommended_questions": suggested_questions,
        "verification_checklist": verification_checklist
    }
