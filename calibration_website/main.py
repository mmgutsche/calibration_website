from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware.sessions import SessionMiddleware
from calibration_website.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
)
from calibration_website.database import get_session, init_db
from calibration_website.models import User
from calibration_website.schemas import UserCreate, UserOut
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
import os
import json
import random
import logging
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

load_dotenv()

DEBUG = os.getenv("DEBUG", "False").lower() in [
    "true",
    "1",
]  # This converts the DEBUG environment variable to a boolean

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./production.db")
    # Check if the database file exists, if not, create it
    if database_url.startswith("sqlite+aiosqlite:///"):
        db_path = database_url.replace("sqlite+aiosqlite:///", "")
        if not os.path.exists(db_path):
            await init_db()
    yield


app = FastAPI(lifespan=lifespan)


# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


# Configure rate limiter

# Load questions from a JSON file
with open("questions.json", "r") as f:
    questions = json.load(f)
# Add SessionMiddleware


app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "your_secret_key"),
    max_age=3600,  # Session will expire after 1 hour
)


@app.post("/register", response_model=UserOut)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_session)):
    db_user = await db.execute(select(User).where(User.username == user.username))
    if db_user.scalars().first() is not None:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@app.post("/token")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
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
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")


@app.get("/profile")
async def profile(request: Request):
    if not request.session.get("is_authenticated"):
        return RedirectResponse(url="/")
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "username": request.session.get("username")},
    )


@app.get("/check-auth")
async def check_auth(request: Request):
    is_authenticated = request.session.get("is_authenticated", False)
    username = request.session.get("username", "") if is_authenticated else ""
    return {"is_authenticated": is_authenticated, "username": username}


def get_user(request: Request):
    # This function should check user's login status
    # For example, it might check a cookie, token, or session
    return {"user_is_authenticated": request.session.get("is_authenticated", False)}


@app.get("/")
async def main(request: Request, user=Depends(get_user)):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user_is_authenticated": user["user_is_authenticated"]},
    )


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
async def questionnaire(request: Request, user=Depends(get_user)):
    return templates.TemplateResponse(
        "questionnaire.html",
        {"request": request, "user_is_authenticated": user["user_is_authenticated"]},
    )


@app.get("/how-to-improve")
async def how_to_improve(request: Request, user=Depends(get_user)):
    return templates.TemplateResponse(
        "how-to-improve.html",
        {"request": request, "user_is_authenticated": user["user_is_authenticated"]},
    )


@app.post("/submit")
async def submit(request: Request):
    data = await request.json()

    error_response = validate_input_data(data)
    if error_response:
        return error_response

    selected_questions = data.get("questions")
    answers = data.get("answers")

    score, detailed_results = calculate_score(selected_questions, answers)
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
