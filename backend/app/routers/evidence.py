from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Header, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from typing import List
from app.database import get_db
from app.routers.auth import get_current_user, require_role, log_audit
from app.routers.cases import verify_case_access
from app.models.models import Evidence, DocumentAccessLog, User
from app.schemas.schemas import EvidenceResponse
from app.services.storage_service import StorageProvider

router = APIRouter(prefix="/api/evidence", tags=["Evidence Vault"])
storage = StorageProvider()

@router.post("/upload", response_model=EvidenceResponse)
def upload_evidence(
    case_id: str = Form(...),
    file: UploadFile = File(...),
    content_length: int = Header(None), # Validate headers
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Verify they can write to this case
    verify_case_access(case_id, user, db)
    
    # Set fallback if Header is missing
    size = content_length or (10 * 1024 * 1024)
    
    evidence = storage.upload_and_encrypt(
        file=file,
        case_id=case_id,
        uploaded_by=user.id,
        content_len=size,
        db=db
    )
    return evidence

@router.get("/case/{case_id}", response_model=List[EvidenceResponse])
def get_case_evidence(
    case_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    verify_case_access(case_id, user, db)
    return db.query(Evidence).filter(
        Evidence.case_id == case_id,
        Evidence.deleted_at.is_(None)
    ).all()

@router.get("/download/{id}")
def download_evidence(
    id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    evidence = db.query(Evidence).filter(Evidence.id == id).first()
    if not evidence:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence file record not found"
        )
         
    # Check case level access
    verify_case_access(evidence.case_id, user, db)
    
    decrypted_bytes = storage.decrypt_and_retrieve(evidence, user.id, db)
    
    # Return as stream
    return StreamingResponse(
        BytesIO(decrypted_bytes),
        media_type=evidence.mime_type,
        headers={"Content-Disposition": f"attachment; filename={evidence.filename}"}
    )

@router.delete("/{id}")
def delete_evidence(
    id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    evidence = db.query(Evidence).filter(Evidence.id == id).first()
    if not evidence:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence file record not found"
        )
         
    verify_case_access(evidence.case_id, user, db)
    
    storage.soft_delete(evidence, user.id, db)
    return {"message": f"Successfully deleted {evidence.filename}"}

@router.get("/logs", response_model=List[dict])
def get_document_access_logs(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN", "SUPER ADMIN"]))
):
    logs = db.query(DocumentAccessLog).order_by(DocumentAccessLog.created_at.desc()).all()
    # Map raw logs to dictionary outputs
    res = []
    for l in logs:
        user = db.query(User).filter(User.id == l.user_id).first()
        file = db.query(Evidence).filter(Evidence.id == l.evidence_id).first()
        res.append({
            "id": l.id,
            "user_name": user.full_name if user else "System",
            "file_name": file.filename if file else "Deleted file",
            "case_id": l.case_id,
            "action": l.action,
            "reason": l.reason,
            "created_at": l.created_at
        })
    return res
