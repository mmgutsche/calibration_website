from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    make_response,
    redirect,
    url_for,
)
import json
import random
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime

app = Flask(__name__)

# Configure rate limiter
limiter = Limiter(get_remote_address, app=app)

# Load questions from a JSON file
with open("questions.json", "r") as f:
    questions = json.load(f)


@app.route("/")
def index():
    return render_template("index.html")


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
    if not data or "questions" not in data or "answers" not in data:
        return jsonify({"error": "Invalid input data"}), 400

    selected_questions = data.get("questions")
    answers = data.get("answers")

    if not isinstance(selected_questions, list) or not isinstance(answers, dict):
        return jsonify({"error": "Invalid selected questions or answers"}), 400

    for i, _ in enumerate(selected_questions):
        lower = answers.get(f"lower_{i}")
        upper = answers.get(f"upper_{i}")

        try:
            lower = float(lower)
            upper = float(upper)
        except ValueError:
            return jsonify({"error": "Invalid answer format"}), 400

    return None


def handle_cookie_consent(request, test_result, score, detailed_results):
    cookie_consent = request.cookies.get("cookieConsent")
    if cookie_consent == "true":
        existing_results = request.cookies.get("test_results")
        try:
            if existing_results:
                test_results = json.loads(existing_results)
            else:
                test_results = []
        except (json.JSONDecodeError, TypeError):
            test_results = []

        test_results.append(test_result)

        resp = make_response(
            jsonify({"score": score, "detailed_results": detailed_results})
        )
        resp.set_cookie("test_results", json.dumps(test_results))
        return resp
    else:
        return jsonify({"score": score, "detailed_results": detailed_results})


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
    app.run(debug=False)
