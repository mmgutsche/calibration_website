# tests/test_user_registration.py
import pytest
import datetime
from httpx import AsyncClient
from sqlalchemy import text
from calibration_website.main import app  # Import the FastAPI application
from calibration_website.database import get_session


from calibration_website.models import User
from calibration_website.main import app, check_user_exists


@pytest.mark.asyncio
async def test_check_user_exists(db_session):
    app.dependency_overrides[get_session] = lambda: db_session

    # Create a test user
    test_user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password="password123",
        first_name="Test",
        last_name="User",
        date_of_birth=datetime.datetime(2000, 1, 1),
    )
    db_session.add(test_user)
    await db_session.commit()

    # Check if the test user exists
    exists = await check_user_exists(db_session, "testuser")
    assert exists

    # Check if a non-existing user exists
    exists = await check_user_exists(db_session, "nonexistinguser")
    assert not exists


@pytest.mark.asyncio
async def test_user_registration(db_session):
    app.dependency_overrides[get_session] = lambda: db_session

    # Log the initial state of the database
    result = await db_session.execute(text("SELECT * FROM users;"))
    users_before = result.fetchall()
    print("Users before test:", users_before)
    assert len(users_before) == 0, "Database is not empty before the test"

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/register",
            json={
                "username": "testuser",
                "password": "password123",
                "email": "testuser@example.com",
                "first_name": "Test",
                "last_name": "User",
                "date_of_birth": "2000-01-01",
            },
        )
        assert response.status_code == 200, response.text
        # Additional validation checks can be added here
        # Log the initial state of the database
        result = await db_session.execute(text("SELECT * FROM users;"))
        users_after = result.fetchall()
        print("Users after test:", users_after)
        assert len(users_after) == 1, "User was not added to the database"
        assert (
            users_after[0].username == "testuser"
        ), "The added user has incorrect data"
