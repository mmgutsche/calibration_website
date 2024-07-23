document.addEventListener('DOMContentLoaded', () => {
    let selectedQuestions = [];

    fetch('/questions')
        .then(response => response.json())
        .then(questions => {
            selectedQuestions = questions;
            const container = document.getElementById('questionsContainer');
            questions.forEach((q, index) => {
                const questionHtml = `
                    <div class="row mb-3 question-row" data-index="${index}">
                        <div class="col-md-4">
                            <label>${q.question}</label>
                        </div>
                        <div class="col-md-2">
                            <input type="text" name="lower_${index}" class="form-control number-input" placeholder="Lower bound">
                        </div>
                        <div class="col-md-2">
                            <input type="text" name="upper_${index}" class="form-control number-input" placeholder="Upper bound">
                        </div>
                        <div class="col-md-4 correct-answer d-none">
                            <span class="text-success">Correct answer: ${q.answer}</span>
                        </div>
                    </div>
                `;
                container.innerHTML += questionHtml;
            });

            // Initialize Cleave.js on number input fields
            document.querySelectorAll('.number-input').forEach(input => {
                new Cleave(input, {
                    numeral: true,
                    numeralThousandsGroupStyle: 'thousand'
                });
            });
        })
        .catch(error => {
            displayError(`Error fetching questions: ${error.message}`);
        });

    document.getElementById('calibrationForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(this);
        let allFieldsFilled = true;
        let answers = {};

        // Check if all fields are filled
        for (let [key, value] of formData.entries()) {
            if (value === "") {
                allFieldsFilled = false;
                break;
            }
            // Remove thousands separators before sending to the server
            answers[key] = value.replace(/,/g, '');
        }

        if (!allFieldsFilled) {
            displayError('Please fill out all fields before submitting.');
        } else {
            // Hide error banner if previously shown
            hideError();

            // Submit the form data
            fetch('/submit', {
                method: 'POST',
                body: JSON.stringify({ questions: selectedQuestions, answers: answers }),
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(result => {
                if (result.error) {
                    displayError(result.error);
                } else {
                    document.getElementById('result').innerText = `Your calibration score is: ${result.score}%`;

                    // Show correct answers
                    result.detailed_results.forEach((item, index) => {
                        const questionRow = document.querySelector(`.question-row[data-index="${index}"]`);
                        const correctAnswerDiv = questionRow.querySelector('.correct-answer');
                        correctAnswerDiv.classList.remove('d-none');
                        if (!item.correct) {
                            correctAnswerDiv.classList.add('text-danger');
                            correctAnswerDiv.querySelector('span').classList.remove('text-success');
                        }
                    });
                }
            })
            .catch(error => {
                displayError(`Error submitting answers: ${error.message}`);
            });
        }
    });

    function displayError(message) {
        const errorBanner = document.getElementById('errorBanner');
        errorBanner.innerText = message;
        errorBanner.classList.remove('d-none');
    }

    function hideError() {
        const errorBanner = document.getElementById('errorBanner');
        errorBanner.classList.add('d-none');
        errorBanner.innerText = '';
    }
});
