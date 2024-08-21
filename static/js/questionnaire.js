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
                        <input type="text" name="lower_${index}" class="form-control number-input" placeholder="e.g., -1.5e-7">
                    </div>
                    <div class="col-md-2">
                        <input type="text" name="upper_${index}" class="form-control number-input" placeholder="e.g., 3.2e9">
                    </div>
                    <div class="col-md-4 result-container d-none">
                        <!-- Result will be dynamically inserted here -->
                    </div>
                    <div class="col-md-12 mt-2">
                        <button type="button" class="btn btn-link toggle-notes">Add Notes</button>
                        <textarea name="note_${index}" class="form-control note-input d-none" placeholder="Add your notes here (this will not be submitted)" rows="1"></textarea>
                    </div>
                </div>
            `;
                container.innerHTML += questionHtml;
            });

            // Add event listener for toggling the note field
            document.querySelectorAll('.toggle-notes').forEach(button => {
                button.addEventListener('click', function () {
                    const textarea = this.nextElementSibling;
                    if (textarea.classList.contains('d-none')) {
                        textarea.classList.remove('d-none');
                        this.textContent = 'Hide Notes';
                        textarea.focus(); // Optional: focus the textarea when expanded
                    } else {
                        textarea.classList.add('d-none');
                        this.textContent = 'Add Notes';
                    }
                });
            });

            // Add event listener for expanding textareas
            document.querySelectorAll('.note-input').forEach(textarea => {
                textarea.addEventListener('input', function () {
                    this.style.height = 'auto'; // Reset the height
                    this.style.height = this.scrollHeight + 'px'; // Set the height to match the content
                });
            });

            document.querySelectorAll('.number-input').forEach(input => {
                input.addEventListener('input', function () {
                    try {
                        const number = new BigNumber(this.value);
                        if (!number.isNaN() && number.isFinite()) { // Check if number is finite
                            this.classList.remove('is-invalid');
                            this.classList.add('is-valid');
                        } else {
                            this.classList.add('is-invalid');
                            this.classList.remove('is-valid');
                        }
                    } catch (e) {
                        this.classList.add('is-invalid');
                        this.classList.remove('is-valid');
                    }
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

        // Check if all fields are filled (excluding notes)
        for (let [key, value] of formData.entries()) {
            if (key.startsWith('note_')) continue; // Skip notes
            if (value === "") {
                allFieldsFilled = false;
                break;
            }
            // Parse and validate using BigNumber to handle all numeric formats including scientific notation
            const number = new BigNumber(value.replace(/,/g, '')); // Clean up commas for thousand separators

            if (number.isNaN() || !number.isFinite()) {
                displayError(`Invalid number: ${value}`);
                return;
            }

            // Store the numeric value as a string to preserve any formatting (like scientific notation)
            answers[key] = number.toString();
        }

        if (!allFieldsFilled) {
            displayError('Please fill out all fields before submitting.');
        } else {
            // Hide error banner if previously shown
            hideError();

            // Submit the form data (excluding notes)
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
        console.log('Displaying results:', result);
        // Disable all input fields in the form
        document.querySelectorAll('#calibrationForm input').forEach(input => {
            input.disabled = true;
        });

        // Disable all note fields
        document.querySelectorAll('#calibrationForm .note-input').forEach(input => {
            input.disabled = true;
        });

        // Hide the submit button
        document.querySelector('#calibrationForm button[type="submit"]').style.display = 'none';

        // Display the total score in the new section
        const scoreContainer = document.getElementById('totalScore');
        scoreContainer.textContent = `Total Score: ${result.score}%`;

        // Make the results summary section visible
        document.getElementById('resultsSummary').classList.remove('d-none');


        result.detailed_results.forEach((item, index) => {
            const resultContainer = document.querySelector(`.question-row[data-index="${index}"] .result-container`);
            if (resultContainer === null) {
                console.error('No result container found for index:', index);
                return; // Skip this iteration if no container is found
            }
            // Determine the color based on whether the answer was correct
            const colorClass = item.correct ? 'text-success' : 'text-danger';


            // Format the correct answer and user's bounds
            const formattedAnswer = formatNumber(item.correct_answer);
            const formattedLowerBound = formatNumber(item.lower_bound);
            const formattedUpperBound = formatNumber(item.upper_bound);

            // Select the input fields corresponding to the current question
            const lowerBoundInput = document.querySelector(`input[name="lower_${index}"]`);
            const upperBoundInput = document.querySelector(`input[name="upper_${index}"]`);

            // Update the form fields with the formatted bounds if the inputs are found
            if (lowerBoundInput && upperBoundInput) {
                lowerBoundInput.value = formattedLowerBound;
                upperBoundInput.value = formattedUpperBound;
            } else {
                console.error('Input fields not found for index:', index);
            }
            // Insert the result text with appropriate color
            resultContainer.innerHTML = `<span class="${colorClass}">${formattedAnswer}</span>`;
            resultContainer.classList.remove('d-none');
        });
    }


    function hideError() {
        const errorBanner = document.getElementById('errorBanner');
        errorBanner.classList.add('d-none');
        errorBanner.innerText = '';
    }
});


function formatNumber(num) {
    const absNum = Math.abs(num);

    // Use Intl.NumberFormat for most formatting
    const formatter = new Intl.NumberFormat(undefined, {
        notation: absNum < 1e-2 || absNum >= 1e6 ? 'scientific' : 'standard',
        maximumFractionDigits: 2,
    });

    return formatter.format(num);
}