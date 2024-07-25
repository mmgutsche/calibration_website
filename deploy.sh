#!/bin/bash

# Variables
SERVER_USER=mgutsche
SERVER_IP=188.245.88.101
GIT_REPO=git@github.com:mmgutsche/calibration_website.git
TARGET_DIR=/var/www/calibration_website
LOG_FILE=/var/www/calibration_website/deployment.log

# SSH into the server and execute updates
ssh $SERVER_USER@$SERVER_IP << 'EOF'

# Activate the Python virtual environment
source $TARGET_DIR/venv/bin/activate

# Change to the target directory
cd $TARGET_DIR

# Pull the latest changes from the Git main branch
git pull origin main

# Install any updated dependencies
pip install -r requirements.txt

# Optionally, perform other updates like database migrations

# Restart the systemd service to reflect changes
sudo systemctl restart calibration_website.service

# Log the deployment time and date
echo "Deployed on: $(date)" >> $LOG_FILE

# Deactivate the virtual environment
deactivate

EOF

echo "Deployment script executed successfully."
