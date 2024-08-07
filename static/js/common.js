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
    setTimeout(() => {
        $('#message').fadeOut();
        messageDiv.classList.add('d-none');
    }, 5000); // Auto-hide message after 5 seconds
}

function displayError(message) {
    const errorBanner = document.getElementById('errorBanner');
    errorBanner.innerText = message;
    errorBanner.classList.remove('d-none');
    setTimeout(() => {
        $('#errorBanner').fadeOut();
        errorBanner.classList.add('d-none');
    }, 5000); // Auto-hide error after 5 seconds
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
