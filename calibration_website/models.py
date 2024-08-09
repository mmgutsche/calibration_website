from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, String, JSON
from sqlalchemy.orm import relationship
import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String, nullable=True)  # Full name
    last_name = Column(String, nullable=True)  # Full name
    registration_date = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    date_of_birth = Column(DateTime, nullable=True)  # Date of birth
    profile_picture = Column(String, nullable=True)  # URL to profile picture
    preferences = Column(JSON, nullable=True)  # JSON field for user preferences

    scores = relationship(
        "Score",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",  # Use selectinload to pre-load related data
    )


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    details = Column(JSON, nullable=False)  # Store detailed results as JSON

    user = relationship("User", back_populates="scores")
