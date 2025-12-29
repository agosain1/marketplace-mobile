from pydantic import BaseModel

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