#!/bin/bash

echo "=== YouTube Live Stream Scheduler Setup (Web Version) ==="

# Update system
echo "Updating system..."
sudo apt-get update

# Install FFmpeg
echo "Installing FFmpeg..."
sudo apt-get install -y ffmpeg

# Install Python3 dan pip
echo "Installing Python3 and pip..."
sudo apt-get install -y python3 python3-pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Make scripts executable
chmod +x app.py
chmod +x stream.py

echo ""
echo "=== Setup selesai! ==="
echo ""
echo "Pilih mode:"
echo ""
echo "1. WEB VERSION (Recommended):"
echo "   python3 app.py"
echo "   Akses: http://localhost:5000"
echo "   Atau: http://YOUR_SERVER_IP:5000"
echo ""
echo "2. CLI VERSION:"
echo "   python3 stream.py"
echo ""
echo "Untuk jalankan di background:"
echo "   nohup python3 app.py > app.log 2>&1 &"
echo ""
