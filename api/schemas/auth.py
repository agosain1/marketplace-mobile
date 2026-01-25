from pydantic import BaseModel
import uuid
from typing import Optional

class UserLogin(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
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


class User(BaseModel):
    id: uuid.UUID
    fname: str
    lname: str
    email: str
    pfp_url: Optional[list[str]] = None