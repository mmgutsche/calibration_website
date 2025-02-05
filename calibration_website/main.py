from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from calibration_website.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
)
from calibration_website.database import get_session
from calibration_website.models import User, Score
from calibration_website.schemas import UserCreate, UserOut, ScoreOut
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import os
import json
import random
import logging
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import datetime

load_dotenv()


DEBUG = os.getenv("DEBUG", "False").lower() in [
    "true",
    "1",
]  # This converts the DEBUG environment variable to a boolean

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.warning("Running in DEBUG mode")

app = FastAPI()


# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


# Configure rate limiter

# Load questions from a JSON file
with open("questions.json", "r") as f:
    questions = json.load(f)
# Add SessionMiddleware


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://calibration.marcelgutsche.de"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],  # You can specify allowed methods here
    allow_headers=["*"],  # You can specify allowed headers here
)


app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "your_secret_key"),
    max_age=86400,  # Session will expire after 1 hour
)


@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login-page.html", {"request": request})


@app.get("/register")
async def register_page(request: Request):
    response = templates.TemplateResponse("register-page.html", {"request": request})
    return response


async def check_user_exists(db: AsyncSession, username: str) -> bool:
    """Check if a user with the given username already exists."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first() is not None


async def create_user_in_db(db: AsyncSession, user_create: UserCreate) -> User:
    """Create a new user in the database."""
    hashed_password = get_password_hash(user_create.password)
    assert user_create.date_of_birth is None or isinstance(
        user_create.date_of_birth, datetime.date
    )
    new_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        date_of_birth=user_create.date_of_birth,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@app.post("/register", response_model=UserOut)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_session),
):
    logging.debug(f"Creating user: {user}")

    try:
        # Check if username already exists
        logging.debug(f"Check DB for existing user: {user.username}")
        if await check_user_exists(db, user.username):
            logging.warning(f"Username already registered: {user.username}")
            raise HTTPException(status_code=409, detail="Username already registered")

        # Create new user
        new_user = await create_user_in_db(db, user)
        logging.info(f"User created successfully: {user.username}")
        return new_user

    except HTTPException as e:
        raise e

    except Exception as e:
        logging.error(f"Error creating user: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error creating user")


@app.post("/token")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    redirect_url: str = Form("/"),
    db: AsyncSession = Depends(get_session),
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    request.session["is_authenticated"] = True
    request.session["username"] = user.username
    # this line is maybe not necessary
    request.session["access_token"] = access_token  # Store the token in the session
    # Perform the redirection after setting the session
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")


@app.get("/profile")
async def profile(request: Request, db: AsyncSession = Depends(get_session)):
    if not request.session.get("is_authenticated"):
        return RedirectResponse(url="/")

    username = request.session.get("username")
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if not user:
        return RedirectResponse(url="/")

    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user},
    )


@app.delete("/profile")
async def delete_profile(
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    if not request.session.get("is_authenticated"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    username = request.session.get("username")

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await db.execute(delete(User).where(User.id == user.id))
    await db.commit()

    request.session.clear()

    return JSONResponse(content={"detail": "User profile deleted successfully"})


@app.get("/api/score-history", response_model=list[ScoreOut])
async def get_score_history(request: Request, db: AsyncSession = Depends(get_session)):
    if not request.session.get("is_authenticated"):
        raise HTTPException(status_code=403, detail="Not authenticated")

    username = request.session.get("username")
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    scores_result = await db.execute(
        select(Score).where(Score.user_id == user.id).order_by(Score.date.desc())
    )
    scores = scores_result.scalars().all()

    return scores


@app.get("/check-auth")
async def check_auth(request: Request):
    is_authenticated = request.session.get("is_authenticated", False)
    username = request.session.get("username", "") if is_authenticated else ""
    return {"is_authenticated": is_authenticated, "username": username}


async def get_user(request: Request, redirect: bool = True) -> dict:
    is_authenticated = request.session.get("is_authenticated", False)
    if not is_authenticated:
        if redirect:
            raise HTTPException(
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                headers={"Location": "/login"},  # Redirect to login page
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )
    username = request.session.get("username")
    return {"username": username, "user_is_authenticated": is_authenticated}


@app.get("/")
async def main_get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.head("/")
async def main_head(request: Request):
    # Return an empty response for HEAD requests
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(
        path="static/favicon.ico", media_type="image/vnd.microsoft.icon"
    )


@app.get("/imprint")
async def imprint(request: Request):
    return templates.TemplateResponse("imprint.html", {"request": request})


@app.get("/questions")
def get_questions():
    random_questions = random.sample(questions, 10)
    return JSONResponse(content=random_questions)


@app.get("/questionnaire")
async def questionnaire(request: Request):
    is_authenticated = request.session.get("is_authenticated", False)
    return templates.TemplateResponse(
        "questionnaire.html",
        {"request": request, "is_authenticated": is_authenticated},
    )


@app.get("/how-to-improve")
async def how_to_improve(request: Request, user=Depends(get_user)):
    return templates.TemplateResponse(
        "how-to-improve.html",
        {"request": request, "user_is_authenticated": user["user_is_authenticated"]},
    )


@app.post("/submit")
async def submit(request: Request, db: AsyncSession = Depends(get_session)):
    data = await request.json()

    error_response = validate_input_data(data)
    if error_response:
        return error_response

    selected_questions = data.get("questions")
    answers = data.get("answers")

    score, detailed_results = calculate_score(selected_questions, answers)

    # Save results to database if user is authenticated
    username = request.session.get("username")
    if username:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        db_score = Score(score=score, details=detailed_results, user_id=user.id)
        db.add(db_score)
        await db.commit()
        await db.refresh(db_score)

    response_data = {
        "score": float(score),
        "detailed_results": detailed_results,
    }
    print(response_data)
    return JSONResponse(content=response_data)


def validate_input_data(data):
    if not data:
        return JSONResponse(content={"error": "No data provided"}, status_code=400)
    if "questions" not in data or "answers" not in data:
        return JSONResponse(
            content={"error": "Questions or answers missing"}, status_code=400
        )
    if not isinstance(data["questions"], list) or not isinstance(data["answers"], dict):
        return JSONResponse(
            content={"error": "Incorrect data types for questions or answers"},
            status_code=400,
        )

    for i, question in enumerate(data["questions"]):
        if f"lower_{i}" not in data["answers"] or f"upper_{i}" not in data["answers"]:
            return JSONResponse(
                content={"error": f"Bounds for question {i} not provided"},
                status_code=400,
            )
        try:
            float(data["answers"][f"lower_{i}"])
            float(data["answers"][f"upper_{i}"])
        except ValueError:
            return JSONResponse(
                content={"error": f"Non-numeric bounds provided for question {i}"},
                status_code=400,
            )

    return None


def calculate_score(selected_questions, answers):
    correct_count = 0
    detailed_results = []
    for i, question_answer_d in enumerate(selected_questions):
        lower = float(answers.get(f"lower_{i}"))
        upper = float(answers.get(f"upper_{i}"))
        correct = lower <= question_answer_d["answer"] <= upper
        detailed_results.append(
            {
                "question": question_answer_d["question"],
                "correct": correct,
                "correct_answer": question_answer_d["answer"],
                "lower_bound": lower,
                "upper_bound": upper,
            }
        )
        if correct:
            correct_count += 1
    score = round((correct_count / len(selected_questions)) * 100)
    return score, detailed_results


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
