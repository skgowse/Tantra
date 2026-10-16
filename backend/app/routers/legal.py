from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.routers.auth import require_role, log_audit, get_current_user
from app.models.models import LegalSource, LegalSection, User
from app.schemas.schemas import (
    LegalSourceCreate, LegalSourceResponse, 
    LegalSectionCreate, LegalSectionResponse
)

router = APIRouter(prefix="/api/legal", tags=["Legal Knowledge Base"])

@router.get("/sources", response_model=List[LegalSourceResponse])
def get_sources(db: Session = Depends(get_db)):
    return db.query(LegalSource).order_by(LegalSource.document_name.asc()).all()

@router.post("/sources", response_model=LegalSourceResponse)
def create_source(
    data: LegalSourceCreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN", "SUPER ADMIN", "LEGAL ADMIN"]))
):
    source = LegalSource(
        authority=data.authority,
        source_url=data.source_url,
        document_name=data.document_name,
        publication_date=data.publication_date,
        effective_date=data.effective_date,
        verification_status="UPLOADED",
        last_verified=datetime.utcnow()
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    
    log_audit(db, admin.id, admin.email, "LEGAL_SOURCE_UPLOADED", "SUCCESS", source.id)
    return source

@router.put("/sources/{id}/status", response_model=LegalSourceResponse)
def update_source_status(
    id: str, 
    new_status: str, 
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN", "SUPER ADMIN", "LEGAL ADMIN"]))
):
    source = db.query(LegalSource).filter(LegalSource.id == id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Legal source not found"
        )
        
    allowed_statuses = {"UPLOADED", "PROCESSING", "EXTRACTED", "ADMIN_REVIEW", "APPROVED", "INDEXED", "ACTIVE", "RETIRED"}
    new_status = new_status.upper()
    if new_status not in allowed_statuses:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Allowed: {', '.join(allowed_statuses)}"
        )
         
    source.verification_status = new_status
    source.last_verified = datetime.utcnow()
    db.commit()
    db.refresh(source)
    
    log_audit(db, admin.id, admin.email, f"LEGAL_SOURCE_STATUS_{new_status}", "SUCCESS", source.id)
    return source

@router.get("/sections", response_model=List[LegalSectionResponse])
def get_sections(db: Session = Depends(get_db)):
    return db.query(LegalSection).filter(LegalSection.status == "ACTIVE").all()

@router.post("/sources/{source_id}/sections", response_model=LegalSectionResponse)
def create_section(
    source_id: str,
    data: LegalSectionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN", "SUPER ADMIN", "LEGAL ADMIN"]))
):
    source = db.query(LegalSource).filter(LegalSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated Legal Source not found"
        )
        
    section = LegalSection(
        source_id=source.id,
        act=data.act,
        section_number=data.section_number,
        title=data.title,
        full_text=data.full_text,
        summary=data.summary,
        version=data.version,
        status="ACTIVE"
    )
    db.add(section)
    db.commit()
    db.refresh(section)
    
    log_audit(db, admin.id, admin.email, "LEGAL_SECTION_CREATED", "SUCCESS", section.id)
    return section
