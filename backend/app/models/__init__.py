import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, JSON
from app.database import Base

class LegalProvision(Base):
    __tablename__ = "legal_provisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    act = Column(String(255), nullable=False, index=True)
    section_number = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    official_text = Column(Text, nullable=False)
    plain_explanation = Column(Text, nullable=False)
    conditions_exceptions = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True) # Threat, Assault, Theft, Fraud, Cybercrime, Rights_Procedure, Evidence
    source_url = Column(String(500), nullable=False)
    last_verified = Column(String(50), default="2026-08-01")

class IncidentSession(Base):
    __tablename__ = "incident_sessions"

    session_id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    language = Column(String(10), default="en") # en, te
    incident_category = Column(String(100), nullable=True)
    conversation_history = Column(JSON, default=list)
    extracted_facts = Column(JSON, default=dict)
    safety_alert_issued = Column(Boolean, default=False)
    emotion_detected = Column(String(50), default="calm") # fear, anxiety, distress, anger, urgency, calm
    is_clarified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), nullable=False, index=True)
    statement_text = Column(Text, nullable=False)
    user_edited_statement = Column(Text, nullable=True)
    rights_summary = Column(JSON, default=list)
    evidence_checklist = Column(JSON, default=list)
    recommended_questions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
