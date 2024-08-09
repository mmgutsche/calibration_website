document.addEventListener('DOMContentLoaded', () => {
    // Add event listener for deleting profile
    document.getElementById('delete-profile')?.addEventListener('click', async function (event) {
        event.preventDefault();

        if (!confirm('Are you sure you want to delete your profile? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch('/profile', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                alert('Profile deleted successfully!');
                setTimeout(() => {
                    window.location.href = "/"; // Redirect to home page on success
                }, 2000); // Delay to show the message
            } else {
                const error = await response.json();
                alert(`Error: ${error.detail}`);
            }
        } catch (error) {
            console.error('Error during fetch:', error);
            alert('An unexpected error occurred.');
        }
    });
});
