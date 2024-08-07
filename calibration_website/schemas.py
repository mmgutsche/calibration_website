from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    profile_picture: Optional[str] = None
    preferences: Optional[dict] = None


class Score(BaseModel):
    id: int
    score: float
    date: datetime
    details: dict  # Assuming details are stored as JSON, map them to a Python dict

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    registration_date: datetime
    date_of_birth: Optional[date] = None
    profile_picture: Optional[str] = None
    preferences: Optional[dict] = None  # Assuming JSON maps to a Python dict
    scores: list[Score] = []  # Include this to show user results

    class Config:
        orm_mode = True
