import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./production.db")

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

Base = declarative_base()


async def get_session():
    async with SessionLocal() as session:
        yield session
