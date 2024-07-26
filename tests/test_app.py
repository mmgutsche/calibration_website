import json
import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from app import app
from app import calculate_score


def test_index():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_get_questions():
    client = app.test_client()
    response = client.get("/questions")
    assert response.status_code == 200
    questions = json.loads(response.data)
    assert len(questions) == 10


def test_submit_invalid_input():
    client = app.test_client()
    response = client.post("/submit", json={})
    assert response.status_code == 400


def test_submit_invalid_format():
    client = app.test_client()
    response = client.post("/submit", json={"questions": [1, 2, 3], "answers": {}})
    assert response.status_code == 400


questions = [
    {"question": "What is the capital of France?", "answer": 10},
    {"question": "What is 2+2?", "answer": 4},
    {"question": "What is the boiling point of water in Celsius?", "answer": 100},
    {"question": "What is the capital of Germany?", "answer": 20},
]


def test_submit_invalid_answer_format():
    client = app.test_client()
    response = client.post(
        "/submit",
        json={
            "questions": [{"question": "Q1", "answer": 5}],
            "answers": {"lower_0": "a", "upper_0": "b"},
        },
    )
    assert response.status_code == 400
    assert b"Invalid answer format" in response.data


def test_submit_valid_input():
    client = app.test_client()
    response = client.post(
        "/submit",
        json={
            "questions": [{"question": "Q1", "answer": 5}],
            "answers": {"lower_0": 0, "upper_0": 10},
        },
    )
    assert response.status_code == 200
    result = json.loads(response.data)
    assert "score" in result
    assert "detailed_results" in result


def test_calculate_score_all_correct():
    answers = {
        "lower_0": 5,
        "upper_0": 15,
        "lower_1": 3,
        "upper_1": 5,
        "lower_2": 95,
        "upper_2": 105,
        "lower_3": 15,
        "upper_3": 25,
    }
    score, details = calculate_score(questions, answers)
    assert score == 100
    assert all(detail["correct"] for detail in details)


def test_calculate_score_all_incorrect():
    answers = {
        "lower_0": 15,
        "upper_0": 20,
        "lower_1": 5,
        "upper_1": 10,
        "lower_2": 105,
        "upper_2": 110,
        "lower_3": 25,
        "upper_3": 30,
    }
    score, details = calculate_score(questions, answers)
    assert score == 0
    assert not any(detail["correct"] for detail in details)


def test_calculate_score_some_correct():
    answers = {
        "lower_0": 5,
        "upper_0": 15,  # Correct
        "lower_1": 0,
        "upper_1": 3,  # Incorrect
        "lower_2": 90,
        "upper_2": 95,  # Incorrect
        "lower_3": 15,
        "upper_3": 25,  # Correct
    }
    score, details = calculate_score(questions, answers)
    assert score == 50
    assert details[0]["correct"]
    assert not details[1]["correct"]
    assert not details[2]["correct"]
    assert details[3]["correct"]


def test_calculate_score_partial_overlap():
    answers = {
        "lower_0": 5,
        "upper_0": 10,  # Correct (boundary)
        "lower_1": 3,
        "upper_1": 4,  # Correct (boundary)
        "lower_2": 100,
        "upper_2": 110,  # Correct (boundary)
        "lower_3": 10,
        "upper_3": 15,  # Incorrect
    }
    score, details = calculate_score(questions, answers)
    assert score == 75
    assert details[0]["correct"]
    assert details[1]["correct"]
    assert details[2]["correct"]
    assert not details[3]["correct"]
