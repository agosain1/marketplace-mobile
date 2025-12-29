from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
import bcrypt
from jose import jwt
import datetime
from dotenv import load_dotenv
import os
import random
import string
from google.auth.transport import requests
from google.oauth2 import id_token


load_dotenv()

from db.database import get_db
from models import Users, VerificationCodes
from services.email_service import get_email_service
from sqlalchemy.orm import Session

router = APIRouter(
    prefix = "/auth",
    tags = ["auth"]
)

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


class Login(BaseModel):
    email: str
    password: str


class Register(BaseModel):
    fname: str
    lname: str
    email: str
    password: str


class VerifyEmail(BaseModel):
    email: str
    code: str


class Email(BaseModel):
    email: str


class GoogleAuth(BaseModel):
    idToken: str
    profile: dict

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_jwt_token(user_id, email: str) -> str:
    """Create JWT token for user"""
    payload = {
        'uuid': str(user_id),
        'email': email,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days = 7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm = JWT_ALGORITHM)


def verify_jwt_token(request: Request):
    """Verify JWT token from HTTP-only cookie"""
    token = request.cookies.get("auth_token")
    
    if not token:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "No authentication token found"
        )

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms = [JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid token"
        )


def generate_verification_code() -> str:
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k = 6))


def send_verification_email(email: str, code: str, fname: str):
    """Send verification code via MailerSend API"""
    email_service = get_email_service()
    email_service.send_verification_email(email, code, fname)

def send_password_reset_email(email: str):
    """Send verification code via MailerSend API"""
    email_service = get_email_service()
    email_service.send_password_reset_email(email)

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


@router.post('/login')
def login(login: Login, response: Response, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(Users).filter(Users.email == login.email).first()
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password"
        )

    # Check if this is a Google user trying to login with password
    if user.google_id and not user.password:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "This account was created with Google. Please use 'Continue with Google' to sign in."
        )

    # Check if user has a password (regular user)
    if not user.password:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password"
        )

    # Verify password for regular users
    if not verify_password(login.password, user.password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password"
        )

    # Check if email is verified
    if not user.email_verified:
        # Generate and store new verification code
        verification_code = generate_verification_code()
        store_verification_code(user.id, verification_code, db)
        
        # Send verification email
        send_verification_email(user.email, verification_code, user.fname)
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Email not verified. We've sent you a new verification code.",
            headers = {"X-Verification-Email": user.email}
        )

    return _create_and_set_cookie(response, user)

@router.post('/forgot-password')
def forgot_password(email: Email, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.email == email.email).first()
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Could not find a user with that email."
        )

    send_password_reset_email(email.email)

    return {
        "message": "We sent you a link in your email to reset your password."
    }

@router.post('/register')
def register(register: Register, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(Users).filter(Users.email == register.email).first()
    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "User with this email already exists. Try using 'login' instead."
        )

    # Hash password
    hashed_password = hash_password(register.password)

    try:
        # Create new user
        new_user = Users(
            fname=register.fname,
            lname=register.lname,
            email=register.email,
            password=hashed_password
        )
        
        db.add(new_user)
        db.flush()  # Flush to get the ID without committing

        # Generate and store verification code (don't commit yet)
        verification_code = generate_verification_code()
        store_verification_code(new_user.id, verification_code, db)

        # Send verification email - if this fails, transaction will be rolled back
        send_verification_email(new_user.email, verification_code, register.fname)

        # Only commit if email was sent successfully
        db.commit()

        return {
            "message": "Registration successful. Please check your email for verification code.",
            "email": new_user.email
        }
        
    except Exception as e:
        # Roll back the transaction if anything fails
        db.rollback()
        print(e)

        # Check if it's an email service error
        if "email" in str(e).lower() or "mail" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed: Unable to send verification email. Please try again later."
            )
        else:
            # Re-raise other exceptions as HTTP errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )


@router.post('/verify-email')
def verify_email(verify: VerifyEmail, response: Response, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(Users).filter(Users.email == verify.email).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )

    if user.email_verified:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Email already verified"
        )

    # Find and verify the code
    verification_code = db.query(VerificationCodes).filter(
        VerificationCodes.user_id == user.id,
        VerificationCodes.code == verify.code,
        VerificationCodes.expires_at > datetime.datetime.now(datetime.timezone.utc)
    ).first()

    if not verification_code:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Invalid or expired verification code"
        )

    # Delete the verification code and mark email as verified
    db.delete(verification_code)
    user.email_verified = True
    db.commit()

    # Create JWT token and set HTTP-only cookie
    return _create_and_set_cookie(response, user)


@router.post('/resend-verification')
def resend_verification(email: Email, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(Users).filter(Users.email == email.email).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )

    if user.email_verified:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Email already verified"
        )

    # Generate and store new verification code
    verification_code = generate_verification_code()
    store_verification_code(user.id, verification_code, db)

    # Send verification email
    send_verification_email(email.email, verification_code, user.fname)

    return {
        "message": "Verification code sent successfully"
    }


@router.get('/validate-token')
def validate_token(token_data: dict = Depends(verify_jwt_token), db: Session = Depends(get_db)):
    """Validate current authentication token"""
    user_id = token_data['uuid']
    
    user = db.query(Users).filter(Users.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user_info = {
        "id": user.id,
        "email": user.email,
        "fname": user.fname,
        "lname": user.lname,
        "pfp_url": user.pfp_url,
    }

    return {
        "success": True,
        "user": user_info
    }


@router.post('/logout')
def logout(response: Response):
    """Logout user by clearing HTTP-only cookie"""
    is_production = os.getenv("NODE_ENV") == "production"
    response.delete_cookie(
        key="auth_token",
        httponly=True,
        secure=is_production,
        samesite="lax"
    )
    
    return {"success": True, "message": "Logged out successfully"}


@router.post('/google')
def google_signin(google_auth: GoogleAuth, response: Response, db: Session = Depends(get_db)):
    """Authenticate user with Google ID token"""
    try:
        # Verify the Google ID token
        GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        if not GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = "Google authentication not configured"
            )

        # Verify the ID token with Google
        try:
            # Verify token with Google's servers
            idinfo = id_token.verify_oauth2_token(
                google_auth.idToken,
                requests.Request(),
                GOOGLE_CLIENT_ID
            )

            # Extract user information from verified token
            google_email = idinfo['email']
            google_sub = idinfo['sub']  # Google's unique user ID

            # Try to get name from token, fall back to profile data
            first_name = idinfo.get('given_name') or google_auth.profile.get('given_name', '')
            last_name = idinfo.get('family_name') or google_auth.profile.get('family_name', '')
            picture = idinfo.get('picture') or google_auth.profile.get('picture')

        except ValueError as e:
            # Invalid token
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = f"Invalid Google token: {str(e)}"
            )

        # Check if user already exists by email
        existing_user = db.query(Users).filter(Users.email == google_email).first()

        if existing_user:
            # Update existing user with Google ID if not set
            if not existing_user.google_id:
                existing_user.google_id = google_sub
                existing_user.email_verified = True
                db.commit()

            return _create_and_set_cookie(response, existing_user)

        else:
            # Create new user account
            new_user = Users(
                fname=first_name or 'Google',
                lname=last_name or 'User',
                email=google_email,
                google_id=google_sub,
                email_verified=True,  # Google accounts are pre-verified
                pfp_url=[picture]
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            return _create_and_set_cookie(response, new_user)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other errors
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Google authentication failed: {str(e)}"
        )

def _create_and_set_cookie(response: Response, user: Users):
    # If user is verified, create JWT token and set HTTP-only cookie
    token = create_jwt_token(user.id, user.email)

    response.set_cookie(
        key = "auth_token",
        value = token,
        max_age = 7 * 24 * 60 * 60,  # 7 days in seconds
        httponly = True,
        secure = True,  # Only secure in production (HTTPS)
        samesite = "lax"
    )

    user_info = {
        "id": user.id,
        "email": user.email,
        "fname": user.fname,
        "lname": user.lname,
        "pfp_url": user.pfp_url,
    }

    return {
        "success": True,
        "user": user_info
    }
