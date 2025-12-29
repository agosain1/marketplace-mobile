import random
import string
from services.email_service import get_email_service
from sqlalchemy.orm import Session
import datetime
from models import VerificationCodes

def generate_verification_code() -> str:
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(email: str, code: str, fname: str):
    """Send verification code via MailerSend API"""
    email_service = get_email_service()
    email_service.send_verification_email(email, code, fname)


def send_password_reset_email(email: str):
    """Send verification code via MailerSend API"""
    email_service = get_email_service()
    # email_service.send_password_reset_email(email)


def store_verification_code(user_id, code: str, db: Session):
    """Store verification code in database"""
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)

    # Check if verification code already exists
    existing_code = db.query(VerificationCodes).filter(VerificationCodes.user_id == user_id).first()

    if existing_code:
        # Update existing code
        existing_code.code = code
        existing_code.expires_at = expires_at
        existing_code.created_at = datetime.datetime.now(datetime.timezone.utc)
    else:
        # Create new verification code
        verification_code = VerificationCodes(
            user_id=user_id,
            code=code,
            expires_at=expires_at
        )
        db.add(verification_code)