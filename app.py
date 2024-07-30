import os
import json
import random


from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    make_response,
    send_from_directory,
    redirect,
    url_for,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


from datetime import datetime

import logging

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("DEBUG", "False").lower() in [
    "true",
    "1",
]  # This converts the DEBUG environment variable to a boolean

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Configure rate limiter
limiter = Limiter(get_remote_address, app=app)

# Load questions from a JSON file
with open("questions.json", "r") as f:
    questions = json.load(f)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/questions")
@limiter.limit("10/minute")  # Limit the rate to 10 requests per minute
def get_questions():
    random_questions = random.sample(questions, 10)
    return jsonify(random_questions)


@app.route("/submit", methods=["POST"])
@limiter.limit("5/minute")  # Limit the rate to 5 requests per minute
def submit():
    data = request.json

    # Validate input data
    error_response = validate_input_data(data)
    if error_response:
        return error_response

    selected_questions = data.get("questions")
    answers = data.get("answers")

    # Calculate score and detailed results
    score, detailed_results = calculate_score(selected_questions, answers)

    # Create a new test result entry
    test_result = {"date": datetime.now().isoformat(), "score": score}

    # Handle storing the test result in cookies if consent is given
    return handle_cookie_consent(request, test_result, score, detailed_results)


def validate_input_data(data):
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if "questions" not in data or "answers" not in data:
        return jsonify({"error": "Questions or answers missing"}), 400
    if not isinstance(data["questions"], list) or not isinstance(data["answers"], dict):
        return jsonify({"error": "Incorrect data types for questions or answers"}), 400

    for i, question in enumerate(data["questions"]):
        if f"lower_{i}" not in data["answers"] or f"upper_{i}" not in data["answers"]:
            return jsonify({"error": f"Bounds for question {i} not provided"}), 400
        try:
            float(data["answers"][f"lower_{i}"])
            float(data["answers"][f"upper_{i}"])
        except ValueError:
            return (
                jsonify({"error": f"Non-numeric bounds provided for question {i}"}),
                400,
            )

    return None


@app.before_request
def check_cookies():
    if "test_results" in request.cookies:
        try:
            json.loads(request.cookies["test_results"])
        except json.JSONDecodeError:
            response = make_response(
                jsonify({"error": "Invalid cookie data, reset required"}), 400
            )
            response.set_cookie("test_results", "", expires=0, path="/")
            return response


def handle_cookie_consent(request, test_result, score, detailed_results):
    cookie_consent = request.cookies.get("cookieConsent")
    app.logger.info(f"Cookie consent: {cookie_consent}")
    resp = make_response(
        jsonify({"score": score, "detailed_results": detailed_results})
    )

    if cookie_consent == "true":
        existing_results = request.cookies.get("test_results")
        try:
            test_results = json.loads(existing_results) if existing_results else []
            app.logger.debug(f"Existing test results: {test_results}")

        except json.JSONDecodeError:
            app.logger.info("Malformed JSON detected, resetting cookie.")
            resp.set_cookie("test_results", "", expires=0, path="/")
            return resp  # Early return to skip processing with bad data
        # Process and store new test result
        test_results.append(test_result)
        test_results = test_results[-10:]  # Keep only the last 10 entries
        json_data = json.dumps(test_results)
        app.logger.debug(f"Serialized JSON for cookie: {json_data}")
        # Decide settings based on environment
        cookie_settings = {"samesite": "Lax" if DEBUG else "None", "secure": not DEBUG}

        # Reset and set the new cookie data
        resp.set_cookie(
            "test_results",
            json_data,
            max_age=3600 * 24 * 365,
            path="/",
            **cookie_settings,
        )

    return resp


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


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Too many requests. Please wait and try again later."), 429


if __name__ == "__main__":
    # showing different logging levels
    app.run(debug=DEBUG)
