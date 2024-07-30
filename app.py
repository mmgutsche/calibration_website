from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import random
from datetime import datetime
import os

import logging

from dotenv import load_dotenv

app = FastAPI()

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


load_dotenv()

DEBUG = os.getenv("DEBUG", "False").lower() in [
    "true",
    "1",
]  # This converts the DEBUG environment variable to a boolean

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)


# Configure rate limiter

# Load questions from a JSON file
with open("questions.json", "r") as f:
    questions = json.load(f)


@app.get("/")
async def index(request: Request):
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


@app.post("/submit")
async def submit(request: Request):
    data = await request.json()

    error_response = validate_input_data(data)
    if error_response:
        return error_response

    selected_questions = data.get("questions")
    answers = data.get("answers")

    score, detailed_results = calculate_score(selected_questions, answers)

    return JSONResponse(content={"score": score, "detailed_results": detailed_results})


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
    # showing different logging levels
    app.run(debug=DEBUG)
