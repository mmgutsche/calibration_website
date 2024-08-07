document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('register-form')?.addEventListener('submit', async function (event) {
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

    // Show Password Toggle
    document.getElementById('show-password').addEventListener('click', function () {
        var passwordFields = [
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

    // Password Strength Indicator
    document.getElementById('register-password').addEventListener('input', function () {
        var strength = document.getElementById('password-strength');
        var password = this.value;
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

    document.getElementById('login-form')?.addEventListener('submit', async function (event) {
        event.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        const response = await fetch('/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            displayMessage('Logged in successfully!');
            updateNavigation(true, username);
            window.location.href = data.redirect_url; // Redirect to the original or main page
        } else {
            const error = await response.json();
            displayError(`Error: ${error.detail}`);
        }
    });

    document.getElementById('logout-link')?.addEventListener('click', async function (event) {
        event.preventDefault();

        const response = await fetch('/logout', {
            method: 'GET',
        });

        if (response.ok) {
            displayMessage('Logged out successfully!');
            updateNavigation(false);
            window.location.href = "/"; // Redirect to home page on logout
        } else {
            displayError('Logout failed!');
        }
    });

    function updateNavigation(isAuthenticated, username = "") {
        console.log("Updating navigation, isAuthenticated:", isAuthenticated, "username:", username);
        const loginLink = document.getElementById('login-link');
        const registerLink = document.getElementById('register-link');
        const profileLink = document.getElementById('profile-link');
        const profileLinkText = document.getElementById('profile-link-text'); // Add this line
        const logoutLink = document.getElementById('logout-link');
        const logoutLinkText = document.getElementById('logout-link-text'); // Add this line

        if (isAuthenticated) {
            loginLink.classList.add('d-none');
            registerLink.classList.add('d-none');
            profileLink.classList.remove('d-none');
            logoutLink.classList.remove('d-none');
            profileLinkText.textContent = `Profile (${username})`; // Update profile link text
            logoutLinkText.textContent = `Log out`; // Update logout link text
        } else {
            loginLink.classList.remove('d-none');
            registerLink.classList.remove('d-none');
            profileLink.classList.add('d-none');
            logoutLink.classList.add('d-none');
            profileLinkText.textContent = "Profile"; // Reset profile link text
            logoutLinkText.textContent = "Log out"; // Reset logout link text
        }
    }

    function displayMessage(message) {
        const messageDiv = document.getElementById('message');
        messageDiv.innerText = message;
        messageDiv.classList.remove('d-none');
        setTimeout(() => $('#message').fadeOut(), 5000); // Auto-hide message after 5 seconds
    }

    function displayError(message) {
        const errorBanner = document.getElementById('errorBanner');
        errorBanner.innerText = message;
        errorBanner.classList.remove('d-none');
        setTimeout(() => $('#errorBanner').fadeOut(), 5000); // Auto-hide error after 5 seconds
    }

    window.onload = function () {
        console.log("Checking authentication status on page load");
        fetch('/check-auth')
            .then(response => response.json())
            .then(data => {
                console.log("Authentication status:", data.is_authenticated, "username:", data.username);
                updateNavigation(data.is_authenticated, data.username);
            })
            .catch(error => {
                console.error('Error checking authentication status:', error);
            });
    };
});
