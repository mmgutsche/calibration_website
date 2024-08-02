document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('register-form').addEventListener('submit', async function (event) {
        event.preventDefault();
        const username = document.getElementById('register-username').value;
        const password = document.getElementById('register-password').value;

        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            displayMessage('User registered successfully!');
            $('#registerModal').modal('hide'); // Close the modal on success
        } else {
            const error = await response.json();
            displayError(`Error: ${error.detail}`);
        }
    });

    document.getElementById('login-form').addEventListener('submit', async function (event) {
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
            $('#loginModal').modal('hide'); // Close the modal on success
            updateNavigation(true);
        } else {
            const error = await response.json();
            displayError(`Error: ${error.detail}`);
        }
    });

    document.getElementById('logout-link').addEventListener('click', async function (event) {
        event.preventDefault();

        const response = await fetch('/logout', {
            method: 'GET',
        });

        if (response.ok) {
            displayMessage('Logged out successfully!');
            updateNavigation(false);
        } else {
            displayError('Logout failed!');
        }
    });

    function updateNavigation(isAuthenticated) {
        const loginLink = document.getElementById('login-link');
        const registerLink = document.getElementById('register-link');
        const profileLink = document.getElementById('profile-link');
        const logoutLink = document.getElementById('logout-link');

        if (isAuthenticated) {
            loginLink.classList.add('d-none');
            registerLink.classList.add('d-none');
            profileLink.classList.remove('d-none');
            logoutLink.classList.remove('d-none');
        } else {
            loginLink.classList.remove('d-none');
            registerLink.classList.remove('d-none');
            profileLink.classList.add('d-none');
            logoutLink.classList.add('d-none');
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
        // Check if the user is authenticated on page load
        fetch('/check-auth')
            .then(response => response.json())
            .then(data => {
                updateNavigation(data.is_authenticated);
            })
            .catch(error => {
                console.error('Error checking authentication status:', error);
            });
    };
});
