#!/bin/bash

# Update and install Docker + Docker Compose
sudo apt update -y
sudo apt install -y docker.io docker-compose

# Add ubuntu user to Docker group (no need to relogin for current session)
sudo usermod -aG docker ubuntu
newgrp docker  # Apply group changes immediately

# Fetch your application code (example using Git)
sudo -u ubuntu git clone https://github.com/vuyyurub/podcast-converter.git /home/ubuntu/app

# Navigate to app directory and start containers
cd /home/ubuntu/app
sudo docker-compose up -d --build

# Optional: Verify containers are running
sudo docker ps