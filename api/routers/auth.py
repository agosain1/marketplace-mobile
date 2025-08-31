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
from google.auth.transport import requests
from google.oauth2 import id_token


load_dotenv()

from api.database import get_db_cursor
from api.services.email_service import get_email_service


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


class ResendCode(BaseModel):
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
    return ''.join(random.choices(string.digits, k = 6))


def send_verification_email(email: str, code: str, fname: str):
    """Send verification code via MailerSend API"""
    email_service = get_email_service()
    email_service.send_verification_email(email, code, fname)

def store_verification_code(user_id, code: str):
    """Store verification code in database"""
    with get_db_cursor() as cur:
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes = 10)
        cur.execute("""
                    INSERT INTO verification_codes (user_id, code, expires_at)
                    VALUES (%s, %s, %s) ON CONFLICT (user_id)
            DO
                    UPDATE SET
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
        cur.execute(
            "SELECT id, email, password, email_verified, google_id FROM users WHERE email = %s",
            (login.email,))
        user = cur.fetchone()

        if not user:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid email or password"
            )

        # Check if this is a Google user trying to login with password
        if user['google_id'] and not user['password']:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "This account was created with Google. Please use 'Continue with Google' to sign in."
            )

        # Check if user has a password (regular user)
        if not user['password']:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid email or password"
            )

        # Verify password for regular users
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
            expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                minutes = 10)
            cur.execute("""
                        INSERT INTO verification_codes (user_id, code, expires_at)
                        VALUES (%s, %s, %s) ON CONFLICT (user_id)
                DO
                        UPDATE SET
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
                    "id": str(user['id']),
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
                detail = "User with this email already exists. Try using 'login' instead."
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
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes = 10)
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
                    DELETE
                    FROM verification_codes
                    WHERE user_id = %s
                      AND code = %s
                      AND expires_at > NOW() RETURNING user_id
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
                "id": str(user['id']),
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

    # Import S3 service here to avoid circular imports
    try:
        from api.services.s3_service import get_s3_service
        s3_available = True
    except ImportError:
        s3_available = False
        print("S3 service not available, skipping image cleanup")

    with get_db_cursor() as cur:
        # First, get all listing images to delete from S3
        all_image_urls = []
        if s3_available:
            cur.execute("SELECT images FROM listings WHERE seller_id = %s", (user_id,))
            listings_with_images = cur.fetchall()

            for listing in listings_with_images:
                if listing['images'] and isinstance(listing['images'], list):
                    # Filter out placeholder images, only delete S3 images
                    s3_images = [url for url in listing['images'] if
                                 not url.startswith('https://placebear.com')]
                    all_image_urls.extend(s3_images)

        # Delete all user's listings from database
        cur.execute("DELETE FROM listings WHERE seller_id = %s", (user_id,))

        # Delete the user account
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))

        if cur.rowcount == 0:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )

    # Delete images from S3 after database transaction is complete
    if s3_available and all_image_urls:
        try:
            get_s3_service().delete_listing_images(all_image_urls)
            print(f"Deleted {len(all_image_urls)} images from S3 for deleted account")
        except Exception as e:
            print(f"Warning: Failed to delete some S3 images for deleted account: {str(e)}")

    return {"message": "Account successfully deleted"}


@router.post('/google')
def google_signin(google_auth: GoogleAuth):
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
            email_verified = idinfo.get('email_verified', False)

            # Try to get name from token, fall back to profile data
            first_name = idinfo.get('given_name') or google_auth.profile.get('given_name', '')
            last_name = idinfo.get('family_name') or google_auth.profile.get('family_name', '')

        except ValueError as e:
            # Invalid token
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = f"Invalid Google token: {str(e)}"
            )

        with get_db_cursor() as cur:
            # Check if user already exists by email
            cur.execute("SELECT id, email, google_id, email_verified FROM users WHERE email = %s",
                        (google_email,))
            existing_user = cur.fetchone()

            if existing_user:
                # Update existing user with Google ID if not set
                if not existing_user['google_id']:
                    cur.execute(
                        "UPDATE users SET google_id = %s, email_verified = %s WHERE id = %s",
                        (google_sub, True, existing_user['id']))

                # Create JWT token for existing user
                token = create_jwt_token(existing_user['id'], existing_user['email'])
                return {
                    "token": token,
                    "user": {
                        "id": str(existing_user['id']),
                        "email": existing_user['email']
                    }
                }
            else:
                # Create new user account (let database auto-generate id)
                cur.execute("""
                            INSERT INTO users (fname, lname, email, google_id, email_verified,
                                               created_at)
                            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, email
                            """, (
                                first_name or 'Google',
                                last_name or 'User',
                                google_email,
                                google_sub,
                                True,  # Google accounts are pre-verified
                                datetime.datetime.now(datetime.timezone.utc)
                            ))

                new_user = cur.fetchone()

                # Create JWT token for new user
                token = create_jwt_token(new_user['id'], new_user['email'])
                return {
                    "token": token,
                    "user": {
                        "id": str(new_user['id']),
                        "email": new_user['email']
                    }
                }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other errors
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Google authentication failed: {str(e)}"
        )
