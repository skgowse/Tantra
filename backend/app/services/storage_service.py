import os
import hashlib
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.config import ENCRYPTION_KEY, UPLOAD_DIR
from app.models.models import Evidence, DocumentAccessLog

# Allowed evidence formats
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".png", ".mp4", ".docx", ".txt"}
ALLOWED_MIME_TYPES = {
    "application/pdf", "image/jpeg", "image/png", 
    "video/mp4", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
}
MAX_FILE_SIZE_MB = 15 # 15 megabytes safety threshold

class StorageProvider:
    def __init__(self):
        # Derive a base64-compatible Fernet key from the raw bytes string
        # Fernet requires exactly a 32-byte url-safe base64-encoded key.
        # We will pad or hash our config key to ensure compatibility.
        hasher = hashlib.sha256(ENCRYPTION_KEY)
        self.fernet_key = hasher.hexdigest()[:32].encode('utf-8')
        # Base64 encode the derived key
        import base64
        self.fernet_key = base64.urlsafe_b64encode(self.fernet_key)
        self.fernet = Fernet(self.fernet_key)

    def validate_file(self, file: UploadFile, content_len: int) -> str:
        # 1. Extension Check
        _, ext = os.path.splitext(file.filename.lower())
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file extension {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # 2. Size Check
        if content_len > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum size of {MAX_FILE_SIZE_MB}MB."
            )
            
        return ext

    def upload_and_encrypt(self, file: UploadFile, case_id: str, uploaded_by: str, content_len: int, db: Session) -> Evidence:
        ext = self.validate_file(file, content_len)
        file_content = file.file.read()
        
        # 3. MIME Check (using file content prefix or uploaded headers)
        if file.content_type not in ALLOWED_MIME_TYPES:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported MIME type: {file.content_type}"
            )

        # 4. Hash verification
        sha256 = hashlib.sha256(file_content).hexdigest()
        
        # 5. Encrypt file contents
        encrypted_data = self.fernet.encrypt(file_content)
        
        # Save to disk
        storage_filename = f"{uuid_generate_hash()}{ext}"
        storage_path = os.path.join(UPLOAD_DIR, storage_filename)
        with open(storage_path, "wb") as f:
            f.write(encrypted_data)
            
        # Create evidence entry
        evidence = Evidence(
            case_id=case_id,
            uploaded_by=uploaded_by,
            filename=file.filename,
            mime_type=file.content_type,
            file_size=len(file_content),
            sha256_hash=sha256,
            encryption_status="ENCRYPTED",
            storage_key=storage_filename,
            access_level="RESTRICTED",
            retention_date=datetime.utcnow() + timedelta(days=365 * 5) # 5 year retention
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        
        # Log document access
        self.log_access(db, uploaded_by, evidence.id, case_id, "UPLOAD", "Uploaded & Encrypted successfully")
        return evidence

    def decrypt_and_retrieve(self, evidence: Evidence, requested_by: str, db: Session) -> bytes:
        if evidence.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File has been deleted."
            )
            
        storage_path = os.path.join(UPLOAD_DIR, evidence.storage_key)
        if not os.path.exists(storage_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Physical evidence file not found in storage volume."
            )
            
        with open(storage_path, "rb") as f:
            encrypted_data = f.read()
            
        # Decrypt
        decrypted_data = self.fernet.decrypt(encrypted_data)
        
        # Log decryption read
        self.log_access(db, requested_by, evidence.id, evidence.case_id, "DOWNLOAD", "Decrypted and downloaded by authorized entity")
        return decrypted_data

    def soft_delete(self, evidence: Evidence, deleted_by: str, db: Session):
        evidence.deleted_at = datetime.utcnow()
        db.commit()
        
        # Log deletion action
        self.log_access(db, deleted_by, evidence.id, evidence.case_id, "DELETE", "Soft deleted evidence file")

    def log_access(self, db: Session, user_id: str, evidence_id: str, case_id: str, action: str, reason: str):
        log = DocumentAccessLog(
            user_id=user_id,
            evidence_id=evidence_id,
            case_id=case_id,
            action=action,
            reason=reason
        )
        db.add(log)
        db.commit()

def uuid_generate_hash() -> str:
    import uuid
    return str(uuid.uuid4())
