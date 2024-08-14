from fabric import Connection, task
from invoke import Responder
from datetime import datetime
import getpass

# Variables
SERVER_USER = "mgutsche"
SERVER_IP = "188.245.88.101"
GIT_REPO = "git@github.com:mmgutsche/calibration_website.git"
TARGET_DIR = "/var/www/calibration_website"
LOG_FILE = "/var/www/calibration_website/deployment.log"
ENV_FILE = f"{TARGET_DIR}/.env"
VENV_DIR = f"{TARGET_DIR}/venv"

"""
Quick usage guide:
- Run `fab deploy` to deploy the latest changes from the Git repository.
- Run `fab restart-service` to restart the systemd service.
- Run `fab check-status` to check the status of the systemd service.
- Run `fab clean-venv` to clean and recreate the virtual environment.

"""


def get_sudo_responder(sudo_password):
    return Responder(
        pattern=r"\[sudo\] password:",
        response=f"{sudo_password}\n",
    )


def log_to_file(conn, message):
    """Logs a single line message to the server log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.run(f"echo '{message} at {timestamp}' >> {LOG_FILE}")


@task
def deploy(c):
    # SSH connection
    conn = Connection(host=SERVER_IP, user=SERVER_USER)

    print("Starting deployment script...")

    # Git operations, dependency installation, and environment file management
    with conn.cd(TARGET_DIR):
        print("Pulling the latest changes from the Git repository...")
        conn.run("git pull origin main")
        print("Git pull completed.")

        # Check for .env file and create it if it doesn't exist
        result = conn.run(
            f"if [ ! -f '{ENV_FILE}' ]; then echo '1'; else echo '0'; fi", hide=True
        ).stdout.strip()
        if result == "1":
            print(".env file not found. Creating .env file...")
            secret_key = conn.run("openssl rand -hex 32", hide=True).stdout.strip()
            env_content = f"""
            # Environment variables for the Calibration Website
            SECRET_KEY={secret_key}
            DATABASE_URL=sqlite:///./app.db  # Adjust this if using a different database
            DEBUG=False  # Set to False in production
            """
            conn.run(f"echo '{env_content}' > {ENV_FILE}")
            print(".env file created with default settings.")
        else:
            print(".env file already exists. Skipping creation.")

        # Dependency installation using the virtual environment's pip
        print("Installing dependencies from requirements.txt...")
        conn.run(f"{TARGET_DIR}/venv/bin/pip install -r requirements.txt")
        print("Dependencies installed.")

    # Logging deployment details
    print("Logging deployment details...")
    deployment_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.run(f"echo 'Deployment successful on: {deployment_time}' >> {LOG_FILE}")
    print("Deployment logged.")

    print("Deployment script executed successfully.")


@task
def restart_service(c):
    # SSH connection
    conn = Connection(host=SERVER_IP, user=SERVER_USER)

    # Handle sudo password
    sudo_password = getpass.getpass("Enter your sudo password: ")
    sudo_responder = get_sudo_responder(sudo_password)

    # Restarting the systemd service
    print("Restarting the systemd service...")
    try:

        conn.sudo(
            "sudo systemctl daemon-reload",
            pty=True,
            watchers=[sudo_responder],
        )

        conn.sudo(
            "systemctl restart calibration_website.service",
            pty=True,
            watchers=[sudo_responder],
        )
        print("Systemd service restarted.")
    except Exception as e:
        print(f"Failed to restart service: {e}")
        conn.run(
            f"echo 'Service restart failed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}' >> {LOG_FILE}"
        )
        return

    # Logging service restart details
    print("Logging service restart details...")
    restart_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.run(f"echo 'Service restarted successfully on: {restart_time}' >> {LOG_FILE}")
    print("Service restart logged.")

    print("Service restart script executed successfully.")


def fetch_service_logs(conn, sudo_responder):
    print("Fetching service logs...")
    logs = conn.sudo(
        "journalctl -u calibration_website.service --no-pager -n 50",
        hide=True,
        watchers=[sudo_responder],
    ).stdout.strip()
    print(f"Service Logs:\n{logs}")
    return logs


def fetch_service_status_details(conn, sudo_responder):
    print("Fetching detailed service status...")
    status_details = conn.sudo(
        "systemctl status calibration_website.service --no-pager",
        hide=True,
        watchers=[sudo_responder],
    ).stdout.strip()
    print(f"Service Status Details:\n{status_details}")
    return status_details


@task
def clean_venv(c):
    """Task to clean and recreate the virtual environment."""
    conn = Connection(host=SERVER_IP, user=SERVER_USER)

    # Remove the existing virtual environment
    print("Removing existing virtual environment...")
    conn.run(f"rm -rf {VENV_DIR}")
    print("Existing virtual environment removed.")

    # Create a new virtual environment
    print("Creating a new virtual environment...")
    conn.run(f"python3 -m venv {VENV_DIR}")
    print("New virtual environment created.")

    log_to_file(conn, "Virtual environment cleaned and recreated.")


@task
def check_status(c):
    # SSH connection
    conn = Connection(host=SERVER_IP, user=SERVER_USER)

    # Handle sudo password
    sudo_password = getpass.getpass("Enter your sudo password: ")
    sudo_responder = get_sudo_responder(sudo_password)

    # Checking the status of the service
    print("Checking the status of the systemd service...")
    try:
        status_result = conn.sudo(
            "systemctl is-active calibration_website.service",
            hide=True,
            warn=True,
            watchers=[sudo_responder],
        ).stdout.strip()

        if status_result == "active":
            print("Service is running successfully.")
            log_to_file(conn, "Service is running successfully.")
        elif status_result == "inactive":
            print("Service is inactive.")
            log_to_file(conn, "Service is inactive.")
        elif status_result == "failed":
            print("Service has failed.")
            log_to_file(conn, "Service has failed.")

            # Fetch logs and detailed status
            fetch_service_logs(conn, sudo_responder)
            fetch_service_status_details(conn, sudo_responder)
        else:
            print(f"Unexpected service status: {status_result}")
            log_to_file(conn, f"Unexpected service status: {status_result}")

    except Exception as e:
        print(f"Error checking service status: {e}")
        log_to_file(conn, "Error checking service status.")

    print("Status check completed.")
