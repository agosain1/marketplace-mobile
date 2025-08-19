from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, Depends, Header
import bcrypt
import jwt
import datetime
from typing import Optional
from dotenv import load_dotenv
import os
import random
import string
import emails


load_dotenv()

from api.database import get_db_cursor


router = APIRouter(
    prefix = "/auth",
    tags = ["auth"]
)

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

# Email configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)


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


class ResendCode(BaseModel):
    email: str


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_jwt_token(user_id: int, email: str) -> str:
    """Create JWT token for user"""
    payload = {
        'uuid': user_id,
        'email': email,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm = JWT_ALGORITHM)


def verify_jwt_token(authorization: Optional[str] = Header(None)):
    """Verify JWT token from Authorization header"""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Missing or invalid authorization header"
        )

    token = authorization.split(' ')[1]
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


def verify_jwt_token_and_email(authorization: Optional[str] = Header(None)):
    """Verify JWT token and check if email is verified"""
    token_data = verify_jwt_token(authorization)
    
    with get_db_cursor() as cur:
        cur.execute("SELECT email_verified FROM users WHERE id = %s", (token_data['uuid'],))
        user = cur.fetchone()
        
        if not user or not user['email_verified']:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Email verification required"
            )
    
    return token_data


def generate_verification_code() -> str:
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(email: str, code: str, fname: str):
    """Send verification code via email"""
    if not SMTP_USER or not SMTP_PASSWORD:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Email service not configured"
        )
    
    subject = "Verify Your Account"
    html_body = f"""
    <html>
        <body>
            <h2>Welcome to Unimarket, {fname}!</h2>
            <p>Your verification code is:</p>
            <h1 style="color: #4CAF50; font-size: 36px; letter-spacing: 4px;">{code}</h1>
            <p>This code will expire in 10 minutes.</p>
            <p>If you didn't create an account, please ignore this email.</p>
        </body>
    </html>
    """
    
    try:
        message = emails.html(
            html=html_body,
            subject=subject,
            mail_from=(FROM_EMAIL, "Marketplace"),
            mail_to=email
        )
        
        response = message.send(
            smtp={
                "host": SMTP_HOST,
                "port": SMTP_PORT,
                "user": SMTP_USER,
                "password": SMTP_PASSWORD,
                "tls": True
            }
        )
        
        if not response.status_code == 250:
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = "Failed to send verification email"
            )
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Email sending failed: {str(e)}"
        )


def store_verification_code(user_id, code: str):
    """Store verification code in database"""
    with get_db_cursor() as cur:
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)
        cur.execute("""
            INSERT INTO verification_codes (user_id, code, expires_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id)
            DO UPDATE SET
                code = EXCLUDED.code,
                created_at = NOW(),
                expires_at = EXCLUDED.expires_at
        """, (user_id, code, expires_at))


@router.post('/login')
def login(login: Login):
    user = None
    user_info = None
    verification_code = None
    
    with get_db_cursor() as cur:
        # Check if user exists
        cur.execute("SELECT id, email, password, email_verified FROM users WHERE email = %s", (login.email,))
        user = cur.fetchone()

        if not user:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid email or password"
            )

        # Verify password
        if not verify_password(login.password, user['password']):
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid email or password"
            )

        # Check if email is verified
        if not user['email_verified']:
            # Get user's first name for email
            cur.execute("SELECT fname FROM users WHERE id = %s", (user['id'],))
            user_info = cur.fetchone()
            
            # Generate and store new verification code
            verification_code = generate_verification_code()
            expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)
            cur.execute("""
                INSERT INTO verification_codes (user_id, code, expires_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id)
                DO UPDATE SET
                    code = EXCLUDED.code,
                    created_at = NOW(),
                    expires_at = EXCLUDED.expires_at
            """, (user['id'], verification_code, expires_at))

        # If user is verified, create JWT token
        if user['email_verified']:
            token = create_jwt_token(user['id'], user['email'])
            return {
                "token": token,
                "user": {
                    "id": user['id'],
                    "email": user['email']
                }
            }
    
    # Handle unverified user outside transaction
    if not user['email_verified']:
        # Send verification email after transaction is committed
        send_verification_email(user['email'], verification_code, user_info['fname'])
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Email not verified. We've sent you a new verification code.",
            headers = {"X-Verification-Email": user['email']}
        )
    return {"message": "An error occurred."}


@router.post('/register')
def register(register: Register):
    with get_db_cursor() as cur:
        # Check if user already exists
        cur.execute("SELECT id FROM users WHERE email = %s", (register.email,))
        existing_user = cur.fetchone()

        if existing_user:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "User with this email already exists"
            )

        # Hash password
        hashed_password = hash_password(register.password)

        # Insert new user (email_verified defaults to FALSE)
        cur.execute("""
                    INSERT INTO users (fname, lname, email, password, created_at)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id, email
                    """, (register.fname, register.lname, register.email, hashed_password,
                          datetime.datetime.now(datetime.timezone.utc)))

        new_user = cur.fetchone()

        # Generate and store verification code in the same transaction
        verification_code = generate_verification_code()
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)
        cur.execute("""
            INSERT INTO verification_codes (user_id, code, expires_at)
            VALUES (%s, %s, %s)
        """, (new_user['id'], verification_code, expires_at))

    # Send verification email after transaction is committed
    send_verification_email(new_user['email'], verification_code, register.fname)

    return {
        "message": "Registration successful. Please check your email for verification code.",
        "email": new_user['email']
    }


@router.post('/verify-email')
def verify_email(verify: VerifyEmail):
    with get_db_cursor() as cur:
        # Find user by email
        cur.execute("SELECT id, email_verified FROM users WHERE email = %s", (verify.email,))
        user = cur.fetchone()

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )

        if user['email_verified']:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Email already verified"
            )

        # Verify code and delete if valid
        cur.execute("""
            DELETE FROM verification_codes 
            WHERE user_id = %s AND code = %s AND expires_at > NOW() 
            RETURNING user_id
        """, (user['id'], verify.code))

        if not cur.fetchone():
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Invalid or expired verification code"
            )

        # Mark email as verified
        cur.execute("UPDATE users SET email_verified = TRUE WHERE id = %s", (user['id'],))

        # Create JWT token
        token = create_jwt_token(user['id'], verify.email)

        return {
            "message": "Email verified successfully",
            "token": token,
            "user": {
                "id": user['id'],
                "email": verify.email
            }
        }


@router.post('/resend-verification')
def resend_verification(resend: ResendCode):
    with get_db_cursor() as cur:
        # Find user by email
        cur.execute("SELECT id, fname, email_verified FROM users WHERE email = %s", (resend.email,))
        user = cur.fetchone()

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )

        if user['email_verified']:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Email already verified"
            )

        # Generate and store new verification code
        verification_code = generate_verification_code()
        store_verification_code(user['id'], verification_code)

        # Send verification email
        send_verification_email(resend.email, verification_code, user['fname'])

        return {
            "message": "Verification code sent successfully"
        }


@router.delete('/delete-account')
def delete_account(token_data: dict = Depends(verify_jwt_token)):
    """Delete user account and all associated data"""
    user_id = token_data['uuid']

    with get_db_cursor() as cur:
        # First, delete all user's listings
        cur.execute("DELETE FROM listings WHERE seller_id = %s", (user_id,))

        # Then delete the user account
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))

        if cur.rowcount == 0:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )

    return {"message": "Account successfully deleted"}
