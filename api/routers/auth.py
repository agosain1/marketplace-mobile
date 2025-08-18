from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, Depends, Header
import bcrypt
import jwt
import datetime
from typing import Optional
from dotenv import load_dotenv
import os


load_dotenv()

from api.database import get_db_cursor


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
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days = 7)
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


@router.post('/login')
def login(login: Login):
    with get_db_cursor() as cur:
        # Check if user exists
        cur.execute("SELECT id, email, password FROM users WHERE email = %s", (login.email,))
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

        # Create JWT token
        token = create_jwt_token(user['id'], user['email'])

        return {
            "token": token,
            "user": {
                "id": user['id'],
                "email": user['email']
            }
        }


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

        # Insert new user
        cur.execute("""
                    INSERT INTO users (fname, lname, email, password, created_at)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id, email
                    """, (register.fname, register.lname, register.email, hashed_password,
                          datetime.datetime.utcnow()))

        new_user = cur.fetchone()

        # Create JWT token
        token = create_jwt_token(new_user['id'], new_user['email'])

        return {
            "token": token,
            "user": {
                "id": new_user['id'],
                "email": new_user['email']
            }
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
