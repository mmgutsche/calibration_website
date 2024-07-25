#!/bin/bash

# Variables
SERVER_USER=mgutsche
SERVER_IP=188.245.88.101

# SSH into the server and execute updates with forced TTY allocation
ssh -T $SERVER_USER@$SERVER_IP <<'EOF'
# Set shell options for better debugging

echo "Starting deployment script..."
echo "Environment variables being used:"
GIT_REPO="git@github.com:mmgutsche/calibration_website.git"
TARGET_DIR="/var/www/calibration_website"
LOG_FILE="/var/www/calibration_website/deployment.log"

# Check the directory and activate the virtual environment
echo "Changing directory to \$TARGET_DIR and activating the virtual environment..."
cd ${TARGET_DIR}
source ${TARGET_DIR}/venv/bin/activate
echo "Virtual environment activated."

# Git operations
echo "Pulling the latest changes from the Git repository..."
git pull origin main
echo "Git pull completed."

# Dependency installation
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
echo "Dependencies installed."

# Optionally, perform other updates like database migrations
# echo "Performing database migrations..."
# python manage.py migrate

# Systemd service restart
echo "Restarting the systemd service..."
sudo systemctl restart calibration_website.service
echo "Systemd service restarted."

# Logging deployment details
echo "Logging deployment details..."
echo "Deployed on: \$(date)" >> "\${LOG_FILE}"
echo "Deployment logged."

# Deactivate the virtual environment
echo "Deactivating the virtual environment..."
deactivate
echo "Virtual environment deactivated."

echo "Deployment script executed successfully."
EOF

echo "Deployment script completed."
