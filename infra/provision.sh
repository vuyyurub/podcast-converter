#!/bin/bash
sudo apt update -y
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
