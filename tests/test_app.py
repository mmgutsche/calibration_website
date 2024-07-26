import json
import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from app import app


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
    assert b"Invalid input data" in response.data


def test_submit_invalid_format():
    client = app.test_client()
    response = client.post("/submit", json={"questions": [1, 2, 3], "answers": {}})
    assert response.status_code == 400


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
