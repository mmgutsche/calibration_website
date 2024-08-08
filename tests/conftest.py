import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from calibration_website.database import Base


@pytest.fixture(scope="function")
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        # Correct query to check existence of the 'users' table
        result = await conn.execute(
            text("SELECT * FROM sqlite_master WHERE type='table' AND name='users';")
        )
        table_exists = result.fetchone()
        assert table_exists is not None, "Tables were not created correctly."

    session = async_session()
    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()
