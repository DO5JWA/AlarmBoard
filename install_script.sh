#!/bin/bash

# Update and upgrade system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip

# Install necessary Python packages
pip3 install flask flask-socketio gtts meshtastic

# Install node.js and npm (for socket.io and axios)
curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt install -y nodejs

# Install necessary JavaScript packages
sudo npm install axios socket.io

# Install Leaflet for map display
sudo npm install leaflet

# Create directories for logs and static files
mkdir -p logs
mkdir -p static/bilder

# Download Leaflet CSS and JS files (if not already available)
sudo wget https://unpkg.com/leaflet@1.7.1/dist/leaflet.js -P static
sudo wget https://unpkg.com/leaflet@1.7.1/dist/leaflet.css -P static

# Set permissions for web server access to static files
sudo chmod -R 755 static

# Provide instructions to run the Flask app
echo "Installation completed!"
echo "To start the application, run: python3 app.py"
