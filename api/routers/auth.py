from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from jose import jwt
from dotenv import load_dotenv
import os
from google.auth.transport import requests
from google.oauth2 import id_token

load_dotenv()

from database import get_db
from models import Users, RefreshTokens
from services.email_service import get_email_service
from services.auth_service import (register_user,
                                   authenticate_user,
                                   delete_auth_cookies,
                                   reset_password,
                                   verify_email_with_code,
                                   resend_verification_email,
                                   create_and_set_cookie,
                                   delete_auth_cookies,
                                   logout_user)
from sqlalchemy.orm import Session
from schemas.auth import UserCreate, UserLogin, Email, VerifyEmail, GoogleAuth
from utils.jwt import validate_refresh_token, get_current_user_id, issue_new_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post('/login')
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data)

    # Check if this is a Google user trying to login with password
    if user.google_id and not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account was created with Google. Please use 'Continue with Google' to sign in."
        )

    return create_and_set_cookie(response, user, db)


@router.post('/forgot-password')
def forgot_password(email: Email, db: Session = Depends(get_db)):
    reset_password(email.email, db)

    return {
        "message": "If there is a user associated with that email, "
                   "we have sent a link to reset your password."
    }


@router.post('/register')
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user = register_user(db, user_data)
    print(user)

    return {
        "message": "Registration successful. Please check your email for verification code.",
        "email": user.email
    }


@router.post('/verify-email')
def verify_email(verify_data: VerifyEmail, response: Response, db: Session = Depends(get_db)):
    user = verify_email_with_code(verify_data, db)

    return create_and_set_cookie(response, user, db)


@router.post('/resend-verification')
def resend_verification(email: Email, db: Session = Depends(get_db)):
    resend_verification_email(email, db)

    return {
        "message": "Verification code sent successfully"
    }


@router.get('/me')
def get_current_user(request: Request, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Validate current authentication token"""
    refresh_token = validate_refresh_token(db, request)
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user = db.query(Users).filter(Users.id == user_id).first()

    user_info = {
        "id": user.id,
        "email": user.email,
        "fname": user.fname,
        "lname": user.lname,
        "pfp_url": user.pfp_url,
    }

    return user_info


@router.post("/refresh")
def refresh_access_token(request: Request, response: Response, db: Session = Depends(get_db)):
    user_id = issue_new_access_token(db, request, response)  # checks refresh inside function

    return {"message": "Access token refreshed successfully", "user_id": user_id}


@router.get("/clear-session")
def clear_session(response: Response):
    delete_auth_cookies(response)
    return {"message": "Session cleared"}


@router.post('/logout')
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    """Logout user by clearing HTTP-only cookie"""
    logout_user(request, response, db)

    return {"message": "Logged out successfully"}


@router.post('/google')
def google_signin(google_auth: GoogleAuth, response: Response, db: Session = Depends(get_db)):
    """Authenticate user with Google ID token"""
    try:
        # Verify the Google ID token
        GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        if not GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google authentication not configured"
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
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )

        # Check if user already exists by email
        existing_user = db.query(Users).filter(Users.email == google_email).first()

        if existing_user:
            # Update existing user with Google ID if not set
            if not existing_user.google_id:
                existing_user.google_id = google_sub
                existing_user.email_verified = True
                db.commit()

            return create_and_set_cookie(response, existing_user, db)

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

            return create_and_set_cookie(response, new_user, db)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )
