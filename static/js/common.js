function updateNavigation(isAuthenticated, username = "") {
    console.log("Updating navigation, isAuthenticated:", isAuthenticated, "username:", username);
    const profileLink = document.getElementById('profile-link');
    const profileLinkText = document.getElementById('profile-link-text');
    const logoutLink = document.getElementById('logout-link');
    const logoutLinkText = document.getElementById('logout-link-text');
    const userGreeting = document.getElementById('user-greeting');
    const usernameDisplay = document.getElementById('username-display');
    const loginPrompt = document.getElementById('login-prompt');

    if (isAuthenticated) {
        // Hide login prompt and show user-related links and greeting
        loginPrompt.classList.add('d-none');
        profileLink.classList.remove('d-none');
        logoutLink.classList.remove('d-none');
        userGreeting.classList.remove('d-none');
        profileLinkText.textContent = `Profile (${username})`;
        logoutLinkText.textContent = `Log out`;
        usernameDisplay.textContent = username;
    } else {
        // Show login prompt and hide user-related links and greeting
        loginPrompt.classList.remove('d-none');
        profileLink.classList.add('d-none');
        logoutLink.classList.add('d-none');
        userGreeting.classList.add('d-none');
        usernameDisplay.textContent = "";
    }
}

document.addEventListener('DOMContentLoaded', () => {
    checkAuthOnLoad();
});

function checkAuthOnLoad() {
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
}

function displayMessage(message) {
    const messageDiv = document.getElementById('message');
    messageDiv.innerText = message;
    messageDiv.classList.remove('d-none');
    setTimeout(() => {
        messageDiv.classList.add('d-none');
    }, 5000); // Hide the message after 5 seconds
}

function displayError(message) {
    const errorBanner = document.getElementById('errorBanner');
    errorBanner.innerText = message;
    errorBanner.classList.remove('d-none');
    setTimeout(() => {
        errorBanner.classList.add('d-none');
    }, 5000); // Hide the error after 5 seconds
}
