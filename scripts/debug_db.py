# scripts/debug_db.py

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from calibration_website.models import User  # Ensure correct import of your models
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./production.db")


async def debug_db():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with AsyncSession(engine) as session:
        async with session.begin():
            result = await session.execute(select(User))
            users = result.scalars().all()
            print("Users:")
            for user in users:
                print(user.username)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(debug_db())
