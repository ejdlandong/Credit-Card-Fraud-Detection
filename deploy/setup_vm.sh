#!/bin/bash
set -e

echo "Setting up server environment..."

# Update packages and install Docker
sudo apt-get update
sudo apt-get install -y docker.io curl git

# Enable and start Docker
sudo systemctl enable docker
sudo systemctl start docker

# Configure UFW Firewall (Allow only SSH and Port 8000)
sudo ufw allow 22/tcp
sudo ufw allow 8000/tcp
sudo ufw --force enable

echo "VM environment setup complete!"