from flask import Flask, request, jsonify, render_template
import json
import random

app = Flask(__name__)

# Load questions from a JSON file
with open('questions.json', 'r') as f:
    questions = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questions')
def get_questions():
    random_questions = random.sample(questions, 10)
    return jsonify(random_questions)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    selected_questions = data.get('questions')
    answers = data.get('answers')
    score, detailed_results = calculate_score(selected_questions, answers)    
    return jsonify({'score': score, 'detailed_results': detailed_results})

def calculate_score(selected_questions, answers):
    correct_count = 0
    detailed_results = []
    for i, q in enumerate(selected_questions):
        lower = float(answers.get(f'lower_{i}'))
        upper = float(answers.get(f'upper_{i}'))
        correct = lower <= q['answer'] <= upper
        detailed_results.append({
            'question': q['question'],
            'correct': correct,
            'correct_answer': q['answer'],
            'lower_bound': lower,
            'upper_bound': upper
        })
        if correct:
            correct_count += 1
    score = round((correct_count / len(selected_questions)) * 100)
    return score, detailed_results

if __name__ == '__main__':
    app.run(debug=True)
