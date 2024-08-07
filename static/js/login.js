document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;

            try {
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
                    setTimeout(() => {
                        window.location.href = data.redirect_url; // Redirect to the original or main page
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
});
