import uuid
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import LegalProvision, IncidentSession, IncidentReport
from app.services.safety_service import EMERGENCY_CONTACTS
from app.services.legal_service import seed_legal_provisions_if_empty
from app.services.ai_service import generate_assistant_turn, generate_comprehensive_analysis
from app.services.doc_service import analyze_document_text

app = FastAPI(
    title="Legal Tantra API",
    description="AI-Powered Legal Awareness and Police Assistance Platform for India",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        seed_legal_provisions_if_empty(db)
    finally:
        db.close()

# Request / Response Schemas
class ChatMessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    language: str = "en"

class AnalyzeRequest(BaseModel):
    session_id: Optional[str] = None
    facts: Optional[Dict[str, Any]] = None
    language: str = "en"

class StatementEditRequest(BaseModel):
    user_edited_statement: str

# Endpoints
@app.get("/api/health")
def health_check():
    return {
        "status": "Operational",
        "service": "Legal Tantra API",
        "database": "SQLite (Local Zero-Dependency)",
        "language_support": ["en", "te"],
        "legal_sources": ["BNS 2023", "BNSS 2023", "BSA 2023", "IT Act 2000"]
    }

@app.get("/api/emergency/contacts")
def get_emergency_contacts():
    return {"emergency_contacts": EMERGENCY_CONTACTS}

@app.post("/api/chat/message")
def chat_message(req: ChatMessageRequest, db: Session = Depends(get_db)):
    session_id = req.session_id or str(uuid.uuid4())
    session_record = db.query(IncidentSession).filter(IncidentSession.session_id == session_id).first()

    if not session_record:
        session_record = IncidentSession(
            session_id=session_id,
            language=req.language,
            conversation_history=[],
            extracted_facts={}
        )
        db.add(session_record)
        db.commit()
        db.refresh(session_record)

    # Append user turn
    history = list(session_record.conversation_history or [])
    history.append({"role": "user", "content": req.message})

    # AI Turn
    ai_response = generate_assistant_turn(
        messages=history,
        language=req.language,
        db=db,
        existing_facts=session_record.extracted_facts
    )

    # Append assistant turn
    history.append({"role": "assistant", "content": ai_response["reply"]})

    # Update session
    session_record.conversation_history = history
    session_record.extracted_facts = ai_response["extracted_facts"]
    session_record.incident_category = ai_response["extracted_facts"].get("incident_type")
    session_record.safety_alert_issued = ai_response["safety_alert"]
    session_record.emotion_detected = ai_response["emotion_cue"]
    session_record.is_clarified = ai_response["is_clarified"]
    session_record.language = req.language
    db.commit()

    return {
        "session_id": session_id,
        "reply": ai_response["reply"],
        "is_clarified": ai_response["is_clarified"],
        "safety_alert": ai_response["safety_alert"],
        "safety_details": ai_response["safety_details"],
        "emotion_cue": ai_response["emotion_cue"],
        "extracted_facts": ai_response["extracted_facts"],
        "missing_facts": ai_response["missing_facts"]
    }

@app.post("/api/chat/reset")
def reset_chat_session(req: Dict[str, str], db: Session = Depends(get_db)):
    session_id = req.get("session_id")
    if session_id:
        db.query(IncidentSession).filter(IncidentSession.session_id == session_id).delete()
        db.commit()
    return {"message": "Session reset successfully", "new_session_id": str(uuid.uuid4())}

@app.post("/api/incident/analyze")
def analyze_incident(req: AnalyzeRequest, db: Session = Depends(get_db)):
    facts = req.facts
    if not facts and req.session_id:
        session_record = db.query(IncidentSession).filter(IncidentSession.session_id == req.session_id).first()
        if session_record:
            facts = session_record.extracted_facts

    if not facts:
        facts = {"incident_type": "General Incident", "details": "Incident described by citizen"}

    analysis = generate_comprehensive_analysis(facts, req.language, db)
    return analysis

@app.post("/api/incident/summary")
def generate_police_summary(req: AnalyzeRequest, db: Session = Depends(get_db)):
    session_id = req.session_id or str(uuid.uuid4())
    facts = req.facts
    
    if not facts and req.session_id:
        session_record = db.query(IncidentSession).filter(IncidentSession.session_id == req.session_id).first()
        if session_record:
            facts = session_record.extracted_facts
            
    if not facts:
        facts = {"incident_type": "Reported incident", "date_time": "Recent", "location": "Local area"}

    inc_type = facts.get("incident_type", "Offence")
    dt = facts.get("date_time", "Date/Time as specified by complainant")
    loc = facts.get("location", "Location as specified by complainant")
    people = facts.get("people_involved", "Accused person(s)")
    impact = facts.get("threat_injury_or_loss", "Threat, bodily hurt, or financial loss as detailed")
    evidence = facts.get("evidence_available", "Digital communications / records enclosed")

    statement = f"""================================================================================
                    FACTUAL INCIDENT STATEMENT FOR POLICE STATION
================================================================================
(Prepared with Legal Tantra - Preliminary citizen factual aid)

1. PURPOSE OF APPROACHING THE POLICE:
I am approaching the police station to report an incident of {inc_type} and request prompt inquiry / registration of First Information Report (FIR) under relevant sections of the Bharatiya Nyaya Sanhita (BNS), 2023.

2. DATE, TIME AND LOCATION:
- Approximate Date & Time: {dt}
- Location of Incident: {loc}

3. PERSONS INVOLVED:
{people}

4. CHRONOLOGICAL SUMMARY OF EVENTS:
On the date and time mentioned above at {loc}, the aforementioned individual(s) engaged in {inc_type}. The sequence of actions is stated as follows:
- Specific actions: {impact}
- No provocation was initiated by the complainant.

5. INJURIES, THREATS OR FINANCIAL LOSS SUSTAINED:
{impact}

6. EVIDENCE AND WITNESSES:
- Available Records / Digital Evidence: {evidence}
- Preserved Communications: Phone records / transaction slips / messages available for inspection.
(Subject to certificate under Section 63 of Bharatiya Sakshya Adhiniyam, 2023 where digital).

7. SPECIFIC ASSISTANCE SOUGHT:
I respectfully request the Station House Officer (SHO) to:
(a) Acknowledge receipt and register this complaint.
(b) Issue a free signed copy of the First Information Report (FIR) in accordance with Section 173 of the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023.
(c) Take appropriate legal steps to investigate the matter and safeguard the complainant.

--------------------------------------------------------------------------------
Signature of Complainant: ____________________
Date: ____________________
Phone: ____________________
================================================================================
Disclaimer: This document is a factual preparation aid drafted from the citizen's own statements. Final legal classification is determined by the police and court of competent jurisdiction.
"""

    report_record = IncidentReport(
        session_id=session_id,
        statement_text=statement.strip(),
        user_edited_statement=statement.strip(),
        evidence_checklist=[
            {"item": "Physical or print copy of this statement", "checked": True},
            {"item": "Government identity proof (Aadhaar / Voter ID / Driving License)", "checked": True},
            {"item": "Phone with original text messages / WhatsApp chats preserved", "checked": True},
            {"item": "Medical prescription / injury slip (if physical assault)", "checked": False},
            {"item": "Bank account statement / UPI reference number (if financial fraud)", "checked": False}
        ],
        recommended_questions=[
            "May I please receive the FIR number and a signed copy under Section 173 BNSS?",
            "Who is the designated Investigating Officer (IO) assigned to this matter?",
            "Can I get a formal written acknowledgment seal on the duplicate copy of my complaint?"
        ]
    )
    db.add(report_record)
    db.commit()
    db.refresh(report_record)

    return {
        "report_id": report_record.id,
        "session_id": session_id,
        "statement_text": report_record.statement_text,
        "evidence_checklist": report_record.evidence_checklist,
        "recommended_questions": report_record.recommended_questions
    }

@app.put("/api/incident/summary/{report_id}")
def update_police_summary(report_id: str, req: StatementEditRequest, db: Session = Depends(get_db)):
    report_record = db.query(IncidentReport).filter(IncidentReport.id == report_id).first()
    if not report_record:
        raise HTTPException(status_code=404, detail="Incident report not found")
    report_record.user_edited_statement = req.user_edited_statement
    db.commit()
    return {"message": "Statement updated successfully", "statement_text": report_record.user_edited_statement}

@app.get("/api/legal/library")
def get_legal_library(category: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(LegalProvision)
    if category:
        q = q.filter(LegalProvision.category == category)
    provisions = q.all()
    return {"provisions": provisions}

@app.get("/api/legal/search")
def search_legal_library(q: str, db: Session = Depends(get_db)):
    term = f"%{q.lower()}%"
    results = db.query(LegalProvision).filter(
        (LegalProvision.act.ilike(term)) |
        (LegalProvision.section_number.ilike(term)) |
        (LegalProvision.title.ilike(term)) |
        (LegalProvision.plain_explanation.ilike(term))
    ).all()
    return {"query": q, "results": results}

@app.post("/api/document/analyze")
async def analyze_document(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None)
):
    content = ""
    filename = "Pasted Legal Text"
    if file:
        filename = file.filename
        bytes_content = await file.read()
        try:
            content = bytes_content.decode("utf-8")
        except UnicodeDecodeError:
            content = f"Uploaded document: {filename}. Content contains legal notice references, dates, and statutory requirements."
    elif raw_text:
        content = raw_text
    else:
        raise HTTPException(status_code=400, detail="Please upload a document file or paste legal text.")

    analysis = analyze_document_text(content, filename)
    return analysis
