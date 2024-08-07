document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            const username = document.getElementById('register-username').value;
            const password = document.getElementById('register-password').value;
            const confirmPassword = document.getElementById('register-confirm-password').value;
            const email = document.getElementById('register-email').value;
            const first_name = document.getElementById('register-first-name').value || null;
            const last_name = document.getElementById('register-last-name').value || null;
            const date_of_birth = document.getElementById('register-date-of-birth').value || null;

            // Check if password and confirm password match
            if (password !== confirmPassword) {
                displayError('Passwords do not match!');
                return;
            }

            // Check if email is valid
            if (!email.includes('@')) {
                displayError('Invalid email!');
                return;
            }

            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password, email, first_name, last_name, date_of_birth }),
                });

                if (response.ok) {
                    displayMessage('User registered successfully!');
                    setTimeout(() => {
                        window.location.href = "/login"; // Redirect to login page on success
                    }, 2000); // Delay to show the message
                } else if (response.status === 409) {
                    displayError('Username already registered! Redirecting to login...');
                    setTimeout(() => {
                        window.location.href = "/login"; // Redirect to login page if user already registered
                    }, 2000); // Delay to show the message
                } else {
                    const error = await response.json();
                    displayError(`Error: ${error.detail}`);
                }
            } catch (error) {
                console.error('Error during fetch:', error);
                displayError('An unexpected error occurred.');
            }
        });
    }

    // Show Password Toggle
    const showPasswordToggle = document.getElementById('show-password');
    if (showPasswordToggle) {
        showPasswordToggle.addEventListener('click', function () {
            const passwordFields = [
                document.getElementById('register-password'),
                document.getElementById('register-confirm-password')
            ];
            passwordFields.forEach(field => {
                if (field.type === 'password') {
                    field.type = 'text';
                } else {
                    field.type = 'password';
                }
            });
        });
    }

    // Password Strength Indicator
    const passwordField = document.getElementById('register-password');
    if (passwordField) {
        passwordField.addEventListener('input', function () {
            const strength = document.getElementById('password-strength');
            const password = this.value;
            if (password.length < 8) {
                strength.textContent = 'Weak';
                strength.style.color = 'red';
            } else if (password.length >= 8 && password.length < 12) {
                strength.textContent = 'Moderate';
                strength.style.color = 'orange';
            } else {
                strength.textContent = 'Strong';
                strength.style.color = 'green';
            }
        });
    }
});
