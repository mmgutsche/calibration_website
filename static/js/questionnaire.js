document.addEventListener('DOMContentLoaded', () => {
    console.log("questionnaire.js loaded"); // Debugging statement

    let selectedQuestions = [];

    fetch('/questions')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.statusText}`);
            }
            return response.json();
        })
        .then(questions => {
            console.log("Questions fetched:", questions); // Debugging statement
            selectedQuestions = questions;
            const container = document.getElementById('questionsContainer');
            questions.forEach((q, index) => {
                const questionHtml = `
                    <div class="row mb-3 question-row" data-index="${index}">
                        <div class="col-md-4">
                            <label>${q.question}</label>
                        </div>
                        <div class="col-md-2">
                            <input type="number" name="lower_${index}" class="form-control number-input" placeholder="Lower bound">
                        </div>
                        <div class="col-md-2">
                            <input type="number" name="upper_${index}" class="form-control number-input" placeholder="Upper bound">
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
            console.error(`Error fetching questions: ${error.message}`); // Debugging statement
            displayError(`Error fetching questions: ${error.message}`);
        });

    document.getElementById('calibrationForm').addEventListener('submit', function (event) {
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
            // Ensure all values are numbers
            let numberValue = parseFloat(value.replace(/,/g, ''));
            if (isNaN(numberValue)) {
                displayError(`Invalid number: ${value}`);
                return;
            }
            answers[key] = numberValue;
        }

        if (!allFieldsFilled) {
            displayError('Please fill out all fields before submitting.');
        } else {
            // Hide error banner if previously shown
            hideError();

            // Submit the form data
            console.log('Submitting answers:', answers); // Debugging statement
            fetch('/submit', {
                method: 'POST',
                body: JSON.stringify({ questions: selectedQuestions, answers: answers }),
                headers: {
                    'Content-Type': 'application/json'
                }
            })
                .then(response => {
                    console.log('Received response:', response); // Debugging statement
                    return response.json();
                })
                .then(result => {
                    console.log('Processed result:', result); // Debugging statement
                    if (result.error) {
                        displayError(result.error);
                    } else {
                        console.log('Displaying result:', result); // Debugging statement
                        // Display results on the same page
                        displayResults(result);
                    }
                })
                .catch(error => {
                    console.error(`Error submitting answers: ${error.message}`, error); // Debugging statement
                    displayError(`Error submitting answers: ${error.message}`);
                });
        }
    });

    function displayResults(result) {
        const formContainer = document.getElementById('calibrationForm'); // Place this in the global scope or within each function that needs it
        const resultContainer = document.getElementById('result');
        resultContainer.innerHTML = ''; // Clear previous results
        result.detailed_results.forEach((item) => {
            const cardClass = item.correct ? 'bg-success text-white' : 'bg-danger text-white';
            const cardHtml = `
            <div class="col-lg-4 col-md-6 col-12 mb-3"> <!-- Different sizes for different screens -->
                <div class="card ${cardClass}">
                    <div class="card-body">
                        <h5 class="card-title">${item.question}</h5>
                        <p class="card-text">Your Guess Range: ${item.lower_bound} to ${item.upper_bound}</p>
                        <p class="card-text">Correct Answer: ${item.correct_answer}</p>
                    </div>
                </div>
            </div>
            `;
            resultContainer.innerHTML += cardHtml;
        });

        resultContainer.classList.remove('d-none');
        formContainer.classList.add('d-none'); // Hide the form
    }

    function displayError(message) {
        console.error(message); // Debugging statement
        const errorBanner = document.getElementById('errorBanner');
        errorBanner.innerText = message;
        errorBanner.classList.remove('d-none');
        setTimeout(() => $('#errorBanner').fadeOut(), 5000); // Auto-hide error after 5 seconds
    }

    function hideError() {
        const errorBanner = document.getElementById('errorBanner');
        errorBanner.classList.add('d-none');
        errorBanner.innerText = '';
    }

    function displayMessage(message) {
        console.log(message); // Debugging statement
        const messageDiv = document.getElementById('message');
        messageDiv.innerText = message;
        messageDiv.classList.remove('d-none');
        setTimeout(() => $('#message').fadeOut(), 5000); // Auto-hide message after 5 seconds
    }
});
