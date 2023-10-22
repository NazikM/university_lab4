from fastapi import Form
from sqlalchemy import Column, String, Integer
from pydantic import BaseModel, EmailStr

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    otp_secret = Column(String)


class UserCreateSchema(BaseModel):
    email: EmailStr = Form(...)
    password: str = Form(...)
    otp_secret: str | None = Form(None)
    otp_verif_code: str = Form(...)

    @classmethod
    def as_form(
            cls,
            email: str = Form(...),
            password: str = Form(...),
            otp_secret: str | None = Form(None),
            otp_verif_code: str = Form(...)
    ):
        return cls(email=email, password=password, otp_secret=otp_secret, otp_verif_code=otp_verif_code)
