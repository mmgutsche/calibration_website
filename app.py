from flask import Flask, request, jsonify, render_template
import json
import random
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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
    if not data or "questions" not in data or "answers" not in data:
        return jsonify({"error": "Invalid input data"}), 400

    selected_questions = data.get("questions")
    answers = data.get("answers")

    # Validate selected questions and answers
    if not isinstance(selected_questions, list) or not isinstance(answers, dict):
        return jsonify({"error": "Invalid selected questions or answers"}), 400

    # Validate answer format
    for i, q in enumerate(selected_questions):
        lower = answers.get(f"lower_{i}")
        upper = answers.get(f"upper_{i}")

        if not isinstance(lower, (int, float)) or not isinstance(upper, (int, float)):
            return jsonify({"error": "Invalid answer format"}), 400

    # Calculate score and detailed results
    score, detailed_results = calculate_score(selected_questions, answers)
    return jsonify({"score": score, "detailed_results": detailed_results})


def calculate_score(selected_questions, answers):
    correct_count = 0
    detailed_results = []
    for i, q in enumerate(selected_questions):
        lower = float(answers.get(f"lower_{i}"))
        upper = float(answers.get(f"upper_{i}"))
        correct = lower <= q["answer"] <= upper
        detailed_results.append(
            {
                "question": q["question"],
                "correct": correct,
                "correct_answer": q["answer"],
                "lower_bound": lower,
                "upper_bound": upper,
            }
        )
        if correct:
            correct_count += 1
    score = round((correct_count / len(selected_questions)) * 100)
    return score, detailed_results


if __name__ == "__main__":
    app.run(debug=False)
