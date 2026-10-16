from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any
from datetime import date, time, datetime

# --- AUTH & USER SCHEMAS ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    role_name: str = "USER" # Default to ordinary citizen/user

class UserResponse(UserBase):
    id: str
    role_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str
    id: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    id: Optional[str] = None


# --- LAWYER SCHEMAS ---
class LawyerCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    enrollment_number: str
    bar_council: str
    practice_areas: List[str]

class LawyerResponse(BaseModel):
    id: str
    lawyer_id_code: str
    enrollment_number: str
    bar_council: str
    practice_areas: List[str]
    platform_verification_status: str
    official_enrollment_verification_status: str
    created_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True

class LawyerVerificationCreate(BaseModel):
    new_status: str
    reason: str


# --- LAWYER ID CARD SCHEMAS ---
class LawyerIDCardResponse(BaseModel):
    id: str
    lawyer_id_code: str
    lawyer_name: str
    enrollment_number: str
    bar_council: str
    practice_areas: List[str]
    card_status: str
    qr_verify_hash: str
    issued_date: datetime
    expiry_date: Optional[datetime] = None


# --- CASE & FACTS SCHEMAS ---
class CaseCreate(BaseModel):
    language: str = "en"

class CaseFactsUpdate(BaseModel):
    incident_type: Optional[str] = None
    incident_date: Optional[date] = None
    incident_time: Optional[time] = None
    location: Optional[str] = None
    people_involved: Optional[List[Any]] = None
    injuries: Optional[str] = None
    property_loss: Optional[str] = None
    witnesses: Optional[List[Any]] = None
    confirmed_by_user: Optional[bool] = None

class CaseFactsResponse(BaseModel):
    incident_type: Optional[str] = None
    incident_date: Optional[date] = None
    incident_time: Optional[time] = None
    location: Optional[str] = None
    people_involved: List[Any] = []
    injuries: Optional[str] = None
    property_loss: Optional[str] = None
    witnesses: List[Any] = []
    confirmed_by_user: bool = False
    updated_at: datetime

    class Config:
        from_attributes = True

class CaseResponse(BaseModel):
    id: str
    case_number: str
    citizen_id: str
    assigned_lawyer_id: Optional[str] = None
    status: str
    language: str
    created_at: datetime
    facts: Optional[CaseFactsResponse] = None

    class Config:
        from_attributes = True


# --- LEGAL DATABASE SCHEMAS ---
class LegalSourceCreate(BaseModel):
    authority: str
    source_url: Optional[str] = None
    document_name: str
    publication_date: Optional[date] = None
    effective_date: Optional[date] = None

class LegalSourceResponse(BaseModel):
    id: str
    authority: str
    source_url: Optional[str] = None
    document_name: str
    publication_date: Optional[date] = None
    effective_date: Optional[date] = None
    verification_status: str
    last_verified: datetime

    class Config:
        from_attributes = True

class LegalSectionCreate(BaseModel):
    act: str
    section_number: str
    title: str
    full_text: str
    summary: Optional[str] = None
    version: str = "2023"

class LegalSectionResponse(BaseModel):
    id: str
    act: str
    section_number: str
    title: str
    full_text: str
    summary: Optional[str] = None
    version: str
    status: str

    class Config:
        from_attributes = True


# --- EVIDENCE SCHEMAS ---
class EvidenceResponse(BaseModel):
    id: str
    case_id: str
    uploaded_by: str
    uploaded_at: datetime
    filename: str
    mime_type: str
    file_size: int
    sha256_hash: str
    access_level: str

    class Config:
        from_attributes = True


# --- AUDIT LOGS SCHEMAS ---
class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    email: Optional[str] = None
    action: str
    target_id: Optional[str] = None
    status: str
    client_ip: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- SYSTEM SETTINGS SCHEMAS ---
class SystemSettingResponse(BaseModel):
    key: str
    value: str
    updated_at: datetime

    class Config:
        from_attributes = True

class SystemSettingUpdate(BaseModel):
    value: str


# --- AI / RAG INTERVIEW SCHEMAS ---
class AIInterviewMessage(BaseModel):
    role: str # user or assistant
    content: str

class AIInterviewRequest(BaseModel):
    messages: List[AIInterviewMessage]
    language: str = "en"

class AIInterviewResponse(BaseModel):
    reply: str
    is_clarified: bool = False
    missing_fields: List[str] = []
    extracted_facts: Optional[dict] = None

class AICitation(BaseModel):
    act: str
    section_number: str
    title: str
    summary: str
    why_relevant: str
    confidence: str # High, Possible, Low
    source_authority: str
    last_verified: datetime

class AILegalAnalysisResponse(BaseModel):
    status: str # VERIFIED, HIGH_CONFIDENCE, etc.
    analysis_text: str
    citations: List[AICitation]
    requires_lawyer_review: bool
