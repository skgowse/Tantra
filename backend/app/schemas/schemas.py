from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# =====================================================================
# STRUCTURED FACT EXTRACTION SCHEMA
# =====================================================================
class ExtractedFacts(BaseModel):
    incident_type: Optional[str] = Field(None, description="Reported type of incident (e.g. Physical assault, Property dispute)")
    incident_category: Optional[str] = Field(None, description="Broad category: Criminal, Civil, Consumer, Family, Employment, Uncertain")
    jurisdiction_type: str = Field("uncertain", description="criminal, civil, consumer, family_dv, employment, or uncertain")
    date_time: Optional[str] = Field(None, description="Approximate or specific date and time reported")
    location: Optional[str] = Field(None, description="General or specific location reported")
    people_involved: Optional[str] = Field(None, description="Roles or individuals mentioned by complainant")
    sequence_of_events: Optional[str] = Field(None, description="Chronological account as stated by the user")
    alleged_actions: Optional[str] = Field(None, description="Specific actions reported (e.g. threatened with words, pushed)")
    injuries_or_harm: Optional[str] = Field(None, description="Physical injury, illness, or threat sustained")
    financial_or_property_loss: Optional[str] = Field(None, description="Amount of money, asset, or property involved")
    witnesses: Optional[str] = Field(None, description="Any eyewitnesses mentioned")
    evidence_mentioned: Optional[str] = Field(None, description="Screenshots, transaction slips, call logs, CCTV, etc.")
    previous_reports: Optional[str] = Field(None, description="Whether an authority/police/bank was already contacted")
    user_confirmed_facts: List[str] = Field(default_factory=list, description="Facts explicitly confirmed by the user")
    unanswered_questions: List[str] = Field(default_factory=list, description="Questions asked that were not answered or skipped")
    uncertainties_or_contradictions: List[str] = Field(default_factory=list, description="Points where details were uncertain or changed")

# =====================================================================
# CHAT INTAKE SCHEMAS
# =====================================================================
class ChatMessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    language: str = "en"

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    is_clarified: bool
    safety_alert: bool
    safety_details: Optional[Dict[str, Any]] = None
    emotion_cue: str
    extracted_facts: Dict[str, Any]
    missing_facts: List[str]
    suggested_next_step: Optional[str] = None
    jurisdiction_hint: str = "uncertain"

class ResetChatRequest(BaseModel):
    session_id: Optional[str] = None

# =====================================================================
# LEGAL PROVISION & ANALYSIS SCHEMAS
# =====================================================================
class LegalProvisionItem(BaseModel):
    act: str
    section_number: str
    title: str
    official_text: str
    plain_explanation: str
    conditions_exceptions: Optional[str] = None
    category: str
    forum: Optional[str] = "Police Station / Magistrate"
    source_url: str
    last_verified: str = "2026-08-01"
    verification_status: str = "VERIFIED"

class AnalyzeRequest(BaseModel):
    session_id: Optional[str] = None
    facts: Optional[Dict[str, Any]] = None
    language: str = "en"

class AnalyzeResponse(BaseModel):
    incident_category: str
    jurisdiction_type: str
    recommended_forum: str
    facts_summary: Dict[str, Any]
    provisions: List[Dict[str, Any]]
    rights_guide: List[Dict[str, Any]]
    evidence_checklist: List[Dict[str, Any]]
    next_steps: List[Dict[str, Any]]
    is_simulated_ai: bool
    ai_engine_note: str

# =====================================================================
# INCIDENT SUMMARY & STATEMENT SCHEMAS
# =====================================================================
class StatementEditRequest(BaseModel):
    user_edited_statement: str

class IncidentStatementResponse(BaseModel):
    report_id: str
    session_id: str
    target_authority: str
    statement_text: str
    evidence_checklist: List[Dict[str, Any]]
    recommended_questions: List[str]
    verification_checklist: List[str]

# =====================================================================
# DOCUMENT ANALYZER SCHEMAS
# =====================================================================
class DocumentAnalysisResponse(BaseModel):
    filename: str
    summary: str
    dates_found: List[str]
    case_references: List[str]
    explained_terms: List[Dict[str, str]]
    recommended_questions: List[str]
    identified_forum: Optional[str] = None
