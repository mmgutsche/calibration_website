import pytest
from sqlalchemy.future import select
from calibration_website.models import User  # Import your User model
from sqlalchemy import text


@pytest.mark.asyncio
async def test_schema_creation(db_session):
    # Execute a simple query to check if the 'users' table exists
    async with db_session as session:
        query = "SELECT * FROM sqlite_master WHERE type='table' AND name='users';"
        result = await session.execute(text(query))
        table_info = result.fetchone()
        assert table_info is not None, "The 'users' table should exist in the database."


@pytest.mark.asyncio
async def test_database_starts_empty(db_session):
    # Use async for to retrieve the session from the async generator
    async with db_session as session:
        # Now use the session to execute your query
        result = await session.execute(select(User))
        users = result.scalars().all()
        assert len(users) == 0, "Database should start empty for this test to be valid"
