import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from app.database import get_db
from app.routers.auth import require_role, log_audit, hash_password
from app.models.models import Lawyer, User, Role, LawyerVerification, LawyerIDCard
from app.schemas.schemas import LawyerCreate, LawyerResponse, LawyerVerificationCreate, LawyerIDCardResponse

router = APIRouter(prefix="/api/lawyers", tags=["Lawyers & Verification"])

def generate_lawyer_id_code(db: Session) -> str:
    # Generates code sequentially: LAW-2026-000001, LAW-2026-000002, etc.
    year = datetime.utcnow().year
    prefix = f"LAW-{year}-"
    # Find last sequential matching
    last = db.query(Lawyer).filter(Lawyer.lawyer_id_code.like(f"{prefix}%")).order_index_by_id_desc = db.query(Lawyer).order_by(Lawyer.created_at.desc()).first()
    
    if last and last.lawyer_id_code.startswith(prefix):
        try:
            num = int(last.lawyer_id_code.split("-")[-1])
            new_num = num + 1
        except ValueError:
            new_num = 1
    else:
        new_num = 1
        
    return f"{prefix}{new_num:06d}"

@router.post("/register", response_model=LawyerResponse)
def register_lawyer(data: LawyerCreate, db: Session = Depends(get_db)):
    # 1. Check if email exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    # 2. Get lawyer role
    lawyer_role = db.query(Role).filter(Role.name == "LAWYER").first()
    if not lawyer_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lawyer role not found in system databases. Run seeds."
        )
        
    # 3. Create User account
    user = User(
        email=data.email,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
        role_id=lawyer_role.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 4. Create Lawyer Profile
    lawyer_id_code = generate_lawyer_id_code(db)
    lawyer = Lawyer(
        user_id=user.id,
        lawyer_id_code=lawyer_id_code,
        enrollment_number=data.enrollment_number,
        bar_council=data.bar_council,
        practice_areas=data.practice_areas,
        platform_verification_status="PENDING",
        official_enrollment_verification_status="UNVERIFIED"
    )
    db.add(lawyer)
    db.commit()
    db.refresh(lawyer)
    
    # 5. Generate initial Lawyer ID card info
    qr_hash = str(uuid.uuid4())
    card = LawyerIDCard(
        lawyer_id=lawyer.id,
        card_status="ACTIVE",
        qr_verify_hash=qr_hash,
        expiry_date=datetime.utcnow() + timedelta(days=365)
    )
    db.add(card)
    db.commit()
    
    log_audit(db, user.id, user.email, "LAWYER_REGISTER", "SUCCESS", lawyer.id)
    
    return lawyer

@router.get("", response_model=List[LawyerResponse])
def get_all_lawyers(
    db: Session = Depends(get_db), 
    admin: User = Depends(require_role(["ADMIN", "SUPER ADMIN", "VERIFICATION OFFICER"]))
):
    # Returns all lawyers list
    return db.query(Lawyer).order_by(Lawyer.created_at.desc()).all()

@router.get("/profile/{id}", response_model=LawyerResponse)
def get_lawyer_profile(id: str, db: Session = Depends(get_db)):
    lawyer = db.query(Lawyer).filter(Lawyer.id == id).first()
    if not lawyer:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer profile not found"
        )
    return lawyer

@router.post("/verify/{id}", response_model=LawyerResponse)
def verify_lawyer_status(
    id: str, 
    verification: LawyerVerificationCreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(["ADMIN", "SUPER ADMIN", "VERIFICATION OFFICER"]))
):
    lawyer = db.query(Lawyer).filter(Lawyer.id == id).first()
    if not lawyer:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer profile not found"
        )
         
    old_status = lawyer.platform_verification_status
    new_status = verification.new_status.upper()
    
    # Validation of verification state flow
    allowed_statuses = {
        "PENDING", "DOCUMENTS_SUBMITTED", "DOCUMENT_REVIEW", 
        "IDENTITY_REVIEW", "ENROLLMENT_REVIEW", "BACKGROUND_REVIEW", 
        "ADMIN_APPROVAL", "VERIFIED", "REJECTED", "SUSPENDED", "REVOKED"
    }
    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status state. Allowed: {', '.join(allowed_statuses)}"
        )
        
    lawyer.platform_verification_status = new_status
    
    # Check if they are officially verified now
    if new_status == "VERIFIED":
        lawyer.official_enrollment_verification_status = "BAR_COUNCIL_VERIFIED"
    elif new_status in ["REJECTED", "SUSPENDED", "REVOKED"]:
        lawyer.official_enrollment_verification_status = "UNVERIFIED"
        
    # Log state transition to verifications table
    trans = LawyerVerification(
        lawyer_id=lawyer.id,
        previous_status=old_status,
        new_status=new_status,
        changed_by=admin.id,
        reason=verification.reason
    )
    db.add(trans)
    
    # ID card lifecycle adjustment
    if lawyer.id_card:
        if new_status == "VERIFIED":
            lawyer.id_card.card_status = "ACTIVE"
        elif new_status in ["SUSPENDED", "REVOKED"]:
            lawyer.id_card.card_status = "REVIEW_REQUIRED"
            
    db.commit()
    db.refresh(lawyer)
    
    log_audit(db, admin.id, admin.email, "LAWYER_VERIFICATION", f"SUCCESS - {new_status}", lawyer.id)
    return lawyer

# Dynamic QR code verification page check
@router.get("/verify-qr/{qr_hash}", response_model=LawyerIDCardResponse)
def verify_lawyer_by_qr(qr_hash: str, db: Session = Depends(get_db)):
    card = db.query(LawyerIDCard).filter(LawyerIDCard.qr_verify_hash == qr_hash).first()
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid QR Code verification ID. Lawyer not found in registry."
        )
        
    lawyer = card.lawyer
    # Dynamic check current status
    status_label = card.card_status
    if lawyer.platform_verification_status in ["SUSPENDED", "REVOKED", "REJECTED"]:
        status_label = "SUSPENDED" if lawyer.platform_verification_status == "SUSPENDED" else "REVOKED"
        
    return LawyerIDCardResponse(
        id=card.id,
        lawyer_id_code=lawyer.lawyer_id_code,
        lawyer_name=lawyer.user.full_name,
        enrollment_number=lawyer.enrollment_number,
        bar_council=lawyer.bar_council,
        practice_areas=lawyer.practice_areas,
        card_status=status_label,
        qr_verify_hash=card.qr_verify_hash,
        issued_date=card.issued_date,
        expiry_date=card.expiry_date
    )

@router.get("/id-card/{lawyer_id}/render")
def render_lawyer_id_card_svg(lawyer_id: str, db: Session = Depends(get_db)):
    lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
    if not lawyer or not lawyer.id_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer ID Card records not found"
        )
        
    # Render SVG dynamically
    color_palette = {
        "VERIFIED": "#10B981", # Green
        "PENDING": "#F59E0B", # Amber
        "SUSPENDED": "#EF4444", # Red
        "REVOKED": "#EF4444"
    }
    status_color = color_palette.get(lawyer.platform_verification_status, "#64748B")
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 240" width="400" height="240">
        <rect width="400" height="240" rx="12" fill="#0B1220" stroke="#2563EB" stroke-width="2"/>
        <circle cx="50" cy="50" r="30" fill="#2563EB"/>
        <text x="95" y="45" font-family="'Inter', sans-serif" font-size="16" font-weight="bold" fill="#FFFFFF">LEGAL AI PLATFORM</text>
        <text x="95" y="62" font-family="'Inter', sans-serif" font-size="10" fill="#64748B">VERIFIED LEGAL PROFESSIONAL</text>
        
        <rect x="20" y="90" width="90" height="110" rx="6" fill="#111827" stroke="#2563EB" stroke-width="1"/>
        <circle cx="65" cy="135" r="20" fill="#64748B"/>
        <path d="M45 180 C 45 160, 85 160, 85 180 Z" fill="#64748B"/>
        
        <text x="125" y="110" font-family="'Inter', sans-serif" font-size="14" font-weight="bold" fill="#FFFFFF">{lawyer.user.full_name}</text>
        <text x="125" y="128" font-family="'Inter', sans-serif" font-size="11" fill="#64748B">ID: {lawyer.lawyer_id_code}</text>
        <text x="125" y="145" font-family="'Inter', sans-serif" font-size="10" fill="#64748B">Enroll: {lawyer.enrollment_number}</text>
        <text x="125" y="162" font-family="'Inter', sans-serif" font-size="10" fill="#64748B">Bar: {lawyer.bar_council}</text>
        
        <rect x="125" y="180" width="120" height="20" rx="4" fill="{status_color}" opacity="0.15"/>
        <text x="135" y="194" font-family="'Inter', sans-serif" font-size="10" font-weight="bold" fill="{status_color}">{lawyer.platform_verification_status}</text>
        
        <g transform="translate(300, 100)">
            <rect width="70" height="70" fill="#FFFFFF" stroke="#000000" stroke-width="2"/>
            <rect x="5" y="5" width="20" height="20" fill="#000000"/>
            <rect x="45" y="5" width="20" height="20" fill="#000000"/>
            <rect x="5" y="45" width="20" height="20" fill="#000000"/>
            <rect x="30" y="30" width="10" height="10" fill="#000000"/>
            <rect x="45" y="45" width="10" height="15" fill="#000000"/>
        </g>
        <text x="300" y="185" font-family="'Inter', sans-serif" font-size="8" fill="#64748B">Scan to Verify</text>
    </svg>"""
    
    from fastapi.responses import Response
    return Response(content=svg, media_type="image/svg+xml")
