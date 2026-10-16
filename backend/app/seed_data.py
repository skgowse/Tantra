from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.models import (
    Role, Permission, User, Lawyer, LawyerIDCard, 
    Case, CaseFacts, LegalSource, LegalSection, SystemSetting, AuditLog
)
from app.routers.auth import hash_password

def seed_database(db: Session):
    # Check if seed has already run
    if db.query(Role).first():
        print("Database already seeded. Skipping...")
        return

    print("Running database seed script...")

    # 1. Create Roles
    roles = {
        "SUPER ADMIN": Role(name="SUPER ADMIN"),
        "ADMIN": Role(name="ADMIN"),
        "LEGAL ADMIN": Role(name="LEGAL ADMIN"),
        "VERIFICATION OFFICER": Role(name="VERIFICATION OFFICER"),
        "LAWYER": Role(name="LAWYER"),
        "USER": Role(name="USER") # Citizen
    }
    for r in roles.values():
        db.add(r)
    db.commit()

    # 2. Create System Settings
    settings = [
        SystemSetting(key="ai_enabled", value="true"),
        SystemSetting(key="confidence_threshold", value="0.75"),
        SystemSetting(key="retention_policy_years", value="5"),
        SystemSetting(key="citation_required", value="true")
    ]
    for s in settings:
        db.add(s)
    db.commit()

    # 3. Create Users & Profiles
    admin_user = User(
        email="admin@demo.legal.in",
        full_name="System Super Admin",
        role_id=roles["SUPER ADMIN"].id,
        password_hash=hash_password("adminpassword123")
    )
    officer_user = User(
        email="officer@demo.legal.in",
        full_name="Verification Officer Anjali",
        role_id=roles["VERIFICATION OFFICER"].id,
        password_hash=hash_password("officerpassword123")
    )
    legal_admin = User(
        email="legaladmin@demo.legal.in",
        full_name="Legal Cataloger Dev",
        role_id=roles["LEGAL ADMIN"].id,
        password_hash=hash_password("legalpassword123")
    )
    db.add(admin_user)
    db.add(officer_user)
    db.add(legal_admin)
    db.commit()

    # 4. Create Legal Sources
    source_bns = LegalSource(
        authority="Ministry of Law and Justice, Government of India",
        source_url="https://indiacode.nic.in",
        document_name="Bharatiya Nyaya Sanhita (BNS) Official Gazette",
        publication_date=datetime(2023, 12, 25).date(),
        effective_date=datetime(2024, 7, 1).date(),
        verification_status="ACTIVE"
    )
    db.add(source_bns)
    db.commit()

    # 5. Create Sections
    sec_115 = LegalSection(
        source_id=source_bns.id,
        act="Bharatiya Nyaya Sanhita, 2023",
        section_number="115",
        title="Voluntarily Causing Hurt",
        full_text="Whoever does any act with the intention of thereby causing hurt to any person, or with the knowledge that he is likely thereby to cause hurt to any person, and does thereby cause hurt to any person, is said voluntarily to cause hurt.",
        summary="Punishes voluntarily causing body pain, disease or infirmity to any person with imprisonment up to 1 year or fine.",
        version="2023",
        status="ACTIVE"
    )
    
    sec_351 = LegalSection(
        source_id=source_bns.id,
        act="Bharatiya Nyaya Sanhita, 2023",
        section_number="351",
        title="Assault",
        full_text="Whoever makes any gesture, or any preparation intending or knowing it to be likely that such gesture or preparation will cause any person present to apprehend that he who makes that gesture or preparation is about to use criminal force to that person, is said to commit an assault.",
        summary="Penalizes gestures or preparations that cause apprehension of criminal force.",
        version="2023",
        status="ACTIVE"
    )
    
    sec_318 = LegalSection(
        source_id=source_bns.id,
        act="Bharatiya Nyaya Sanhita, 2023",
        section_number="318",
        title="Cheating",
        full_text="Whoever, by deceiving any person, fraudulently or dishonestly induces the person so deceived to deliver any property to any person, or to consent that any person shall retain any property, is said to cheat.",
        summary="Criminalizes dishonestly inducing delivery of property or cheating through identity manipulation.",
        version="2023",
        status="ACTIVE"
    )
    db.add(sec_115)
    db.add(sec_351)
    db.add(sec_318)
    db.commit()

    # 6. Create Demo Citizens/Users (10 users)
    citizens = []
    for i in range(1, 11):
        cit = User(
            email=f"citizen{i}@demo.legal.in",
            full_name=f"Citizen User {i}",
            role_id=roles["USER"].id,
            password_hash=hash_password(f"citizenpassword{i}")
        )
        db.add(cit)
        citizens.append(cit)
    db.commit()

    # 7. Create Demo Lawyers (5 lawyers)
    lawyer_practice_areas = [
        ["Criminal Law", "Assault Defense"],
        ["Cyber Crime", "Financial Fraud"],
        ["Civil Disputes", "Property Rights"],
        ["Human Rights", "Public Grievances"],
        ["Corporate Disputes", "Consumer Fraud"]
    ]
    lawyers_list = []
    for i in range(1, 6):
        l_user = User(
            email=f"lawyer{i}@demo.legal.in",
            full_name=f"Adv. Rajesh Kumar {i}",
            role_id=roles["LAWYER"].id,
            password_hash=hash_password(f"lawyerpassword{i}")
        )
        db.add(l_user)
        db.commit()

        # Platform status
        p_status = "VERIFIED" if i <= 2 else ("PENDING" if i == 3 else "SUSPENDED")
        o_status = "BAR_COUNCIL_VERIFIED" if p_status == "VERIFIED" else "UNVERIFIED"

        lawyer = Lawyer(
            user_id=l_user.id,
            lawyer_id_code=f"LAW-2026-00000{i}",
            enrollment_number=f"BC/IND/2026/000{i}",
            bar_council="Delhi Bar Council",
            practice_areas=lawyer_practice_areas[i-1],
            platform_verification_status=p_status,
            official_enrollment_verification_status=o_status
        )
        db.add(lawyer)
        db.commit()
        lawyers_list.append(lawyer)

        # ID Card details
        card = LawyerIDCard(
            lawyer_id=lawyer.id,
            card_status="ACTIVE" if p_status == "VERIFIED" else "REVIEW_REQUIRED",
            qr_verify_hash=f"qr-hash-verification-id-00{i}",
            expiry_date=datetime.utcnow() + timedelta(days=365)
        )
        db.add(card)
        db.commit()

    # 8. Create Demo Cases (10 cases)
    case_types = ["Physical Assault", "Online Banking Fraud", "Verbal Threats", "Property Trespass"]
    for i in range(1, 11):
        cit_owner = citizens[i % len(citizens)]
        assigned_lawyer = lawyers_list[i % 2] if i <= 5 else None # Assign verified lawyers to first 5 cases
        status_val = "Completed" if i == 1 else ("Lawyer Review" if i <= 4 else "AI Interview")

        case = Case(
            case_number=f"CASE-2026-00000{i}",
            citizen_id=cit_owner.id,
            assigned_lawyer_id=assigned_lawyer.id if assigned_lawyer else None,
            status=status_val,
            language="en"
        )
        db.add(case)
        db.commit()

        # Add facts details
        facts = CaseFacts(
            case_id=case.id,
            incident_type=case_types[i % len(case_types)],
            incident_date=(datetime.utcnow() - timedelta(days=i)).date(),
            incident_time=datetime.utcnow().time(),
            location=f"Sector {i} Market, New Delhi",
            people_involved=[{"name": f"Accused Entity {i}", "role": "Suspect"}],
            injuries="None declared" if i % 2 == 0 else "Minor bruise details",
            property_loss="INR 5,000" if i % 3 == 0 else "None",
            confirmed_by_user=True if i <= 6 else False
        )
        db.add(facts)
        db.commit()

    # 9. Initial Audit Logs
    db.add(AuditLog(action="SEED_DATABASE", status="SUCCESS", email="admin@demo.legal.in"))
    db.commit()

    print("Database seeding completed successfully.")
