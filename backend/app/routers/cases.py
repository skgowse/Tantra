from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.database import get_db
from app.routers.auth import get_current_user, log_audit, require_role
from app.models.models import Case, CaseFacts, User, Lawyer, LegalSection
from app.schemas.schemas import (
    CaseCreate, CaseResponse, CaseFactsUpdate, CaseFactsResponse,
    AIInterviewRequest, AIInterviewResponse, AILegalAnalysisResponse
)
from app.services.ai_service import get_ai_provider

router = APIRouter(prefix="/api/cases", tags=["Cases & Analysis"])

def generate_case_number(db: Session) -> str:
    year = datetime.utcnow().year
    prefix = f"CASE-{year}-"
    # Find last case
    last = db.query(Case).filter(Case.case_number.like(f"{prefix}%")).order_by(Case.created_at.desc()).first()
    
    if last and last.case_number.startswith(prefix):
        try:
            num = int(last.case_number.split("-")[-1])
            new_num = num + 1
        except ValueError:
            new_num = 1
    else:
        new_num = 1
        
    return f"{prefix}{new_num:06d}"

def verify_case_access(case_id: str, current_user: User, db: Session) -> Case:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
        
    # Check Case-Level Authorization
    if current_user.role.name in ["ADMIN", "SUPER ADMIN"]:
        # Log administrative view override
        log_audit(db, current_user.id, current_user.email, "ADMIN_CASE_ACCESS", "SUCCESS", case.id)
        return case
        
    if current_user.role.name == "LAWYER":
        lawyer = db.query(Lawyer).filter(Lawyer.user_id == current_user.id).first()
        if not lawyer or case.assigned_lawyer_id != lawyer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You are not the assigned lawyer for this case."
            )
        return case
        
    # Citizen checks
    if case.citizen_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You do not own this case."
        )
        
    return case

@router.post("", response_model=CaseResponse)
def create_case(data: CaseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    case_no = generate_case_number(db)
    
    new_case = Case(
        case_number=case_no,
        citizen_id=user.id,
        status="AI Interview",
        language=data.language
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    
    # Initialize blank case facts
    facts = CaseFacts(case_id=new_case.id)
    db.add(facts)
    db.commit()
    
    log_audit(db, user.id, user.email, "CASE_CREATE", "SUCCESS", new_case.id)
    return new_case

@router.get("", response_model=List[CaseResponse])
def get_user_cases(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Check permissions/role
    if user.role.name in ["ADMIN", "SUPER ADMIN"]:
        return db.query(Case).order_by(Case.created_at.desc()).all()
    elif user.role.name == "LAWYER":
        lawyer = db.query(Lawyer).filter(Lawyer.user_id == user.id).first()
        if not lawyer:
            return []
        return db.query(Case).filter(Case.assigned_lawyer_id == lawyer.id).order_by(Case.created_at.desc()).all()
    else:
        # Citizen
        return db.query(Case).filter(Case.citizen_id == user.id).order_by(Case.created_at.desc()).all()

@router.get("/{id}", response_model=CaseResponse)
def get_case_by_id(id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    case = verify_case_access(id, user, db)
    return case

@router.put("/{id}/facts", response_model=CaseFactsResponse)
def update_case_facts(
    id: str, 
    data: CaseFactsUpdate, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    case = verify_case_access(id, user, db)
    facts = case.facts
    if not facts:
        facts = CaseFacts(case_id=case.id)
        db.add(facts)
        db.commit()
        db.refresh(facts)
        
    # Update fields
    for field, val in data.dict(exclude_unset=True).items():
        setattr(facts, field, val)
        
    # Trigger case status progression
    if data.confirmed_by_user:
        case.status = "AI Analysis"
        
    db.commit()
    db.refresh(facts)
    
    log_audit(db, user.id, user.email, "CASE_FACTS_UPDATE", "SUCCESS", case.id)
    return facts

@router.post("/{id}/chat", response_model=AIInterviewResponse)
def run_ai_interview_message(
    id: str, 
    data: AIInterviewRequest, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    case = verify_case_access(id, user, db)
    ai = get_ai_provider()
    
    response = ai.generate_interview_response(data.messages, data.language, db)
    
    # If the conversation has successfully gathered all clarifying facts, update case_facts automatically
    if response.is_clarified and response.extracted_facts:
        facts = case.facts
        for field, val in response.extracted_facts.items():
            setattr(facts, field, val)
        case.status = "Fact Confirmation"
        db.commit()
        
    return response

@router.get("/{id}/ai-analysis", response_model=AILegalAnalysisResponse)
def run_preliminary_legal_assessment(
    id: str, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    case = verify_case_access(id, user, db)
    facts = case.facts
    
    if not facts or not facts.confirmed_by_user:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot run analysis before facts are confirmed by the user."
        )
         
    ai = get_ai_provider()
    # Build dictionary from model facts
    facts_dict = {
        "incident_type": facts.incident_type,
        "incident_date": str(facts.incident_date) if facts.incident_date else "",
        "incident_time": str(facts.incident_time) if facts.incident_time else "",
        "location": facts.location,
        "injuries": facts.injuries,
        "property_loss": facts.property_loss,
        "people_involved": facts.people_involved,
        "witnesses": facts.witnesses
    }
    
    analysis = ai.generate_legal_analysis(facts_dict, case.language, db)
    return analysis

@router.post("/{id}/request-lawyer")
def request_lawyer_review(
    id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    case = verify_case_access(id, user, db)
    if case.status != "AI Analysis":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lawyer review can only be requested after running the AI legal analysis."
        )
        
    # Auto-assign first available lawyer in database for MVP simulation
    lawyer = db.query(Lawyer).filter(Lawyer.platform_verification_status == "VERIFIED").first()
    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verified lawyers are currently available on the platform. Please try again later."
        )
        
    case.assigned_lawyer_id = lawyer.id
    case.status = "Lawyer Requested"
    db.commit()
    
    log_audit(db, user.id, user.email, "LAWYER_REVIEW_REQUESTED", "SUCCESS", case.id)
    return {"message": "Lawyer review requested. Case assigned.", "assigned_lawyer": lawyer.user.full_name}

@router.get("/{id}/complaint")
def generate_police_complaint_draft(
    id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    case = verify_case_access(id, user, db)
    facts = case.facts
    
    if not facts or not facts.confirmed_by_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complaint draft cannot be generated before facts are confirmed."
        )
        
    # Construct beautiful formal complaint draft
    date_str = facts.incident_date.strftime("%d %B %Y") if facts.incident_date else "Pending"
    time_str = facts.incident_time.strftime("%I:%M %p") if facts.incident_time else "Pending"
    
    accused_list = []
    for idx, p in enumerate(facts.people_involved or []):
        name = p.get("name", "Unknown")
        role = p.get("role", "Accused")
        accused_list.append(f"{idx+1}. {name} (Role: {role})")
    accused_str = "\n".join(accused_list) if accused_list else "Unknown accused person(s)"
    
    witness_list = []
    for idx, w in enumerate(facts.witnesses or []):
        name = w.get("name", "Unknown")
        witness_list.append(f"{idx+1}. {name}")
    witness_str = "\n".join(witness_list) if witness_list else "None declared"
    
    draft = f"""
================================================================================
                        POLICE COMPLAINT DRAFT (PRELIMINARY)
================================================================================

Date: {datetime.utcnow().strftime("%d-%m-%Y")}

To,
The Officer-in-Charge,
Police Station: {facts.location or "[Nearest Police Station]"},
City/District: India.

Subject: Complaint regarding incident of {facts.incident_type or "Offense"} on {date_str}.

Respected Sir/Madam,

I, {case.citizen.full_name}, residing at [Citizen Address Registered], hereby submit this complaint regarding an incident that occurred on {date_str} at approximately {time_str} at the location: {facts.location or "Pending"}.

1. DESCRIPTION OF INCIDENT:
{facts.incident_type or "General Criminal Offence"} took place. 
Detailed details:
- Injuries sustained: {facts.injuries or "None reported."}
- Property / Financial Loss: {facts.property_loss or "None reported."}

2. DETAILS OF ACCUSED PERSON(S):
{accused_str}

3. WITNESSES:
{witness_str}

4. EVIDENCE ENCLOSED:
Please refer to the digital evidence storage index references for files uploaded securely under Case File Reference ID: {case.case_number}.

5. REQUESTED LEGAL PROVISIONS FOR INVESTIGATION (AI PRELIMINARY REVIEW):
Based on the AI-powered preliminary retrieval, this complaint references:
- Bharatiya Nyaya Sanhita, 2023 (Acts)
- Sections matched during fact review.

REQUEST FOR ACTION:
Therefore, it is requested that a First Information Report (FIR) be registered under the relevant sections of the Bharatiya Nyaya Sanhita (BNS), 2023, and appropriate investigation be initiated immediately.

Yours faithfully,


({case.citizen.full_name})
Complainant Signature
    """
    
    # Progess status
    if case.status in ["AI Analysis", "Lawyer Requested"]:
        case.status = "Complaint Draft"
        db.commit()
        
    return {"complaint_text": draft.strip(), "case_number": case.case_number}
