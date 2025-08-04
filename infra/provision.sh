#!/bin/bash
sudo yum update -y
sudo yum install -y docker git
sudo systemctl enable docker
sudo systemctl start docker
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo usermod -aG docker ec2-user
sudo -u ec2-user git clone https://github.com/vuyyurub/podcast-converter.git /home/ec2-user/app
cd /home/ec2-user/app
sudo docker-compose up -d --build
