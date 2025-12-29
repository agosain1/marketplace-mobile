from fastapi import Request, Response, HTTPException, status, Depends
from sqlalchemy.orm import Session
from models import Users, VerificationCodes, RefreshTokens
from schemas.auth import UserCreate, UserLogin, VerifyEmail, Email
from utils.password import verify_password, hash_password
from utils.verify_account import generate_verification_code, store_verification_code, send_verification_email, send_password_reset_email
from utils.jwt import create_access_token, get_current_user_id, issue_new_access_token, validate_refresh_token
import datetime
import os

ACCESS_TOKEN_MINS = float(os.getenv("ACCESS_TOKEN_MINS"))
REFRESH_TOKEN_DAYS = float(os.getenv("REFRESH_TOKEN_DAYS"))

def register_user(db: Session, user_data: UserCreate):
    existing_user = db.query(Users).filter((Users.email == user_data.email)).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_pwd = hash_password(user_data.password)

    try:
        new_user = Users(
            email=user_data.email,
            fname=user_data.fname,
            lname=user_data.lname,
            password=hashed_pwd,
        )

        db.add(new_user)
        db.flush()

        # Generate and store verification code (don't commit yet)
        verification_code = generate_verification_code()
        store_verification_code(new_user.id, verification_code, db)

        # Send verification email - if this fails, transaction will be rolled back
        # send_verification_email(new_user.email, verification_code, user_data.fname)

        # Only commit if email was sent successfully
        db.commit()
        db.refresh(new_user)

        return new_user

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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )

def authenticate_user(db: Session, user_data: UserLogin):
    user = db.query(Users).filter(Users.email == user_data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect"
        )

    # Check if user has a password (regular user)
    if not user.password:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Email or password is incorrect"
        )

    # Check password (regular user)
    if not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect"
        )

    # Check if email is verified
    if not user.email_verified:
        # Generate and store new verification code
        verification_code = generate_verification_code()
        store_verification_code(user.id, verification_code, db)

        # Send verification email
        # send_verification_email(user.email, verification_code, user.fname)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. We've sent you a new verification code.",
            headers={"X-Verification-Email": user.email}
        )

    return user

def logout_user(request: Request, response: Response, db: Session):
    access_token_id = request.cookies.get("access_token")
    refresh_token_id = request.cookies.get("refresh_token")
    delete_auth_cookies(response)

    # potentially add logout of all devices button
    # revoke all access tokens by user id

    if not access_token_id or not refresh_token_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active session found"
        )

    refresh_token = db.query(RefreshTokens).filter(RefreshTokens.id == refresh_token_id).first()
    # could an error happen here if no refresh_token in db?
    if refresh_token:
        refresh_token.revoked = True
        db.commit()

def reset_password(email: str, db: Session):
    user = db.query(Users).filter(Users.email == email).first()
    if user:
        send_password_reset_email(email)
        # change later
        new_password = 'Abcdef123'
        hashed_pwd = hash_password(new_password)
        user.password = hashed_pwd
        db.commit()

def verify_email_with_code(verify_data: VerifyEmail, db: Session):
    user = db.query(Users).filter(Users.email == verify_data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )

    # Find and verify the code
    verification_code = db.query(VerificationCodes).filter(
        VerificationCodes.user_id == user.id,
        VerificationCodes.code == verify_data.code,
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

    return user

def resend_verification_email(email: Email, db: Session):
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


def create_and_set_cookie(response: Response, user: Users, db: Session):
    access_token_id = create_access_token(str(user.id))
    refresh_token = RefreshTokens(user_id=user.id)
    db.add(refresh_token)
    db.commit()

    response.set_cookie(
        key="access_token",
        value=access_token_id,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * ACCESS_TOKEN_MINS  # variable mins in seconds (default 15)
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token.id,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=24 * 60 * 60 * REFRESH_TOKEN_DAYS  # variable days in seconds (default 7)
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

def delete_auth_cookies(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        domain=None,
        secure=True,
        httponly=True,
        samesite="lax"
    )

    response.delete_cookie(
        key="refresh_token",
        path="/",
        domain=None,
        secure=True,
        httponly=True,
        samesite="lax"
    )