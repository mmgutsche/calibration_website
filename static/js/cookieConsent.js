// cookieConsent.js

function checkCookie() {
    if (!localStorage.getItem('cookieConsent')) {
        document.getElementById('cookieConsent').style.display = 'block';
    }
}

function acceptCookies() {
    localStorage.setItem('cookieConsent', 'true');
    document.cookie = "cookieConsent=true; path=/";
    document.getElementById('cookieConsent').style.display = 'none';
    location.reload();
}

function declineCookies() {
    localStorage.setItem('cookieConsent', 'false');
    document.cookie = "cookieConsent=false; path=/";
    document.getElementById('cookieConsent').style.display = 'none';
    location.reload();
}

function deleteCookies() {
    document.cookie = "last_test=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "last_score=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    location.reload();
}

window.onload = checkCookie;
