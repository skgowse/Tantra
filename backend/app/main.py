import uuid
import logging
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import (
    RATE_LIMIT_ENABLED,
    RATE_LIMIT_DEFAULT_LIMIT,
    RATE_LIMIT_DEFAULT_WINDOW,
    RATE_LIMIT_AI_LIMIT,
    RATE_LIMIT_AI_WINDOW,
    MAX_JSON_BODY_SIZE,
    MAX_UPLOAD_SIZE,
    ENVIRONMENT
)
from app.database import engine, Base, get_db
from app.models import LegalProvision, IncidentSession, IncidentReport
from app.schemas import (
    ChatMessageRequest,
    ChatResponse,
    ResetChatRequest,
    AnalyzeRequest,
    AnalyzeResponse,
    StatementEditRequest,
    IncidentStatementResponse,
    DocumentAnalysisResponse
)
from app.security import (
    SecurityHeadersMiddleware,
    RequestSizeLimitMiddleware,
    InMemoryRateLimiter,
    RateLimitMiddleware,
    mask_pii,
    sanitize_input_text,
    neutralize_prompt_injection
)
from app.services.safety_service import EMERGENCY_CONTACTS
from app.services.legal_service import seed_legal_provisions_if_empty
from app.services.ai_service import generate_assistant_turn, generate_comprehensive_analysis
from app.services.summary_service import generate_factual_incident_summary
from app.services.doc_service import analyze_document_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("legal_tantra.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables and seed verified provisions
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        seed_legal_provisions_if_empty(db)
        logger.info("Database initialized and verified statutes seeded successfully.")
    finally:
        db.close()
    yield

app = FastAPI(
    title="Legal Tantra API",
    description="AI-Assisted Legal Awareness and Incident Preparation Platform for India",
    version="2.1.0",
    lifespan=lifespan
)

# Initialize rate limiter
rate_limiter = InMemoryRateLimiter(
    default_limit=RATE_LIMIT_DEFAULT_LIMIT,
    default_window=RATE_LIMIT_DEFAULT_WINDOW,
    ai_limit=RATE_LIMIT_AI_LIMIT,
    ai_window=RATE_LIMIT_AI_WINDOW,
    enabled=RATE_LIMIT_ENABLED
)
app.state.rate_limiter = rate_limiter

# Middlewares are added so that outer layers execute first on incoming requests:
# Incoming: CORS -> SecurityHeaders -> RequestSizeLimit -> RateLimit -> Route handler
# Outgoing: Route handler -> RateLimit -> RequestSizeLimit -> SecurityHeaders -> CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware, max_json_size=MAX_JSON_BODY_SIZE, max_upload_size=MAX_UPLOAD_SIZE)
app.add_middleware(RateLimitMiddleware, limiter=rate_limiter)

# =====================================================================
# SYSTEM & HEALTH ENDPOINTS
# =====================================================================
@app.get("/api/health")
def health_check():
    return {
        "status": "Operational",
        "service": "Legal Tantra API",
        "version": "2.1.0",
        "database": "SQLite (Zero-Dependency Local)",
        "security": {
            "rate_limiting": "Active (Sliding-Window)",
            "headers": "OWASP Compliant (CSP, X-Frame-Options, Nosniff)",
            "request_size_limits": f"JSON: {MAX_JSON_BODY_SIZE // 1024}KB, Upload: {MAX_UPLOAD_SIZE // (1024*1024)}MB",
            "pii_logging": "Masked",
            "prompt_injection_defense": "Active"
        },
        "language_support": ["en", "te"],
        "legal_sources": ["BNS 2023", "BNSS 2023", "BSA 2023", "IT Act 2000", "Consumer Protection Act 2019", "PWDVA 2005", "Specific Relief Act 1963"],
        "compliance": "Pre-authority Citizen Factual Aid; Does not substitute licensed legal counsel"
    }

@app.get("/api/emergency/contacts")
def get_emergency_contacts():
    return {"emergency_contacts": EMERGENCY_CONTACTS}

# =====================================================================
# CHAT INTAKE & CONVERSATION
# =====================================================================
@app.post("/api/chat/message")
def chat_message(req: ChatMessageRequest, db: Session = Depends(get_db)):
    raw_message = req.message.strip()
    if not raw_message:
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")

    # Sanitize input and neutralize prompt injection attempts
    sanitized = sanitize_input_text(raw_message)
    secure_message = neutralize_prompt_injection(sanitized)

    # Privacy-conscious logging (no raw PII logged)
    logger.info(f"Citizen chat message received (Session: {req.session_id or 'new'}): {mask_pii(secure_message[:80])}...")

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
    history.append({"role": "user", "content": secure_message})

    # AI Turn (with hybrid deterministic fallback)
    ai_response = generate_assistant_turn(
        messages=history,
        language=req.language,
        db=db,
        existing_facts=session_record.extracted_facts or {}
    )

    # Append assistant turn
    history.append({"role": "assistant", "content": ai_response["reply"]})

    # Update session without logging PII
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
        "safety_details": ai_response.get("safety_details"),
        "emotion_cue": ai_response["emotion_cue"],
        "extracted_facts": ai_response["extracted_facts"],
        "missing_facts": ai_response["missing_facts"],
        "suggested_next_step": ai_response.get("suggested_next_step"),
        "jurisdiction_hint": ai_response.get("jurisdiction_hint", "uncertain")
    }

@app.post("/api/chat/reset")
def reset_chat_session(req: ResetChatRequest, db: Session = Depends(get_db)):
    session_id = req.session_id
    if session_id:
        db.query(IncidentSession).filter(IncidentSession.session_id == session_id).delete()
        db.commit()
    return {"message": "Session reset successfully", "new_session_id": str(uuid.uuid4())}

# =====================================================================
# LEGAL ANALYSIS
# =====================================================================
@app.post("/api/incident/analyze")
def analyze_incident(req: AnalyzeRequest, db: Session = Depends(get_db)):
    facts = req.facts
    if not facts and req.session_id:
        session_record = db.query(IncidentSession).filter(IncidentSession.session_id == req.session_id).first()
        if session_record:
            facts = session_record.extracted_facts

    if not facts:
        facts = {"incident_type": "Unspecified Incident", "details": "No facts recorded"}

    analysis = generate_comprehensive_analysis(facts, req.language, db)
    return analysis

# =====================================================================
# FACTUAL INCIDENT SUMMARY GENERATION (STRICTLY NON-FABRICATED)
# =====================================================================
@app.post("/api/incident/summary")
def generate_incident_summary(req: AnalyzeRequest, db: Session = Depends(get_db)):
    session_id = req.session_id or str(uuid.uuid4())
    facts = req.facts

    if not facts and req.session_id:
        session_record = db.query(IncidentSession).filter(IncidentSession.session_id == req.session_id).first()
        if session_record:
            facts = session_record.extracted_facts

    if not facts:
        facts = {"incident_type": "Reported incident", "date_time": "Not provided", "location": "Not provided"}

    summary_data = generate_factual_incident_summary(facts, req.language)

    report_record = IncidentReport(
        session_id=session_id,
        statement_text=summary_data["statement_text"],
        user_edited_statement=summary_data["statement_text"],
        evidence_checklist=summary_data["evidence_checklist"],
        recommended_questions=summary_data["recommended_questions"]
    )
    db.add(report_record)
    db.commit()
    db.refresh(report_record)

    return {
        "report_id": report_record.id,
        "session_id": session_id,
        "target_authority": summary_data["target_authority"],
        "statement_text": report_record.statement_text,
        "evidence_checklist": report_record.evidence_checklist,
        "recommended_questions": report_record.recommended_questions,
        "verification_checklist": summary_data["verification_checklist"]
    }

@app.put("/api/incident/summary/{report_id}")
def update_incident_summary(report_id: str, req: StatementEditRequest, db: Session = Depends(get_db)):
    report_record = db.query(IncidentReport).filter(IncidentReport.id == report_id).first()
    if not report_record:
        raise HTTPException(status_code=404, detail="Incident report not found")
    sanitized_text = sanitize_input_text(req.user_edited_statement)
    report_record.user_edited_statement = sanitized_text
    db.commit()
    return {"message": "Statement updated successfully", "statement_text": report_record.user_edited_statement}

# =====================================================================
# LEGAL KNOWLEDGE LIBRARY
# =====================================================================
@app.get("/api/legal/library")
def get_legal_library(category: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(LegalProvision)
    if category and category != "All":
        safe_cat = sanitize_input_text(category)
        q = q.filter(LegalProvision.category.ilike(f"%{safe_cat}%"))
    provisions = q.all()
    return {"provisions": provisions}

@app.get("/api/legal/search")
def search_legal_library(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    clean_q = sanitize_input_text(q).strip()
    if not clean_q:
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")
    search_term = f"%{clean_q}%"
    provisions = db.query(LegalProvision).filter(
        (LegalProvision.title.ilike(search_term)) |
        (LegalProvision.act.ilike(search_term)) |
        (LegalProvision.section_number.ilike(search_term)) |
        (LegalProvision.plain_explanation.ilike(search_term))
    ).all()
    return {"query": clean_q, "results": provisions}

# =====================================================================
# DOCUMENT ANALYZER
# =====================================================================
@app.post("/api/document/analyze")
async def analyze_document(
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None)
):
    content = ""
    filename = "Pasted text"
    if file:
        filename = sanitize_input_text(file.filename or "Uploaded document")
        bytes_data = await file.read()
        if len(bytes_data) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Uploaded file exceeds maximum limit of {MAX_UPLOAD_SIZE // (1024*1024)} MB."
            )
        content = bytes_data.decode("utf-8", errors="ignore")
    elif text_content:
        content = text_content

    if not content.strip():
        raise HTTPException(status_code=400, detail="No document file or text content provided for analysis.")

    sanitized_content = sanitize_input_text(content)
    analysis = analyze_document_text(sanitized_content, filename)
    return analysis
