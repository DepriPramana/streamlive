#!/bin/bash

# StreamLive Cloud Deployment Script
# Version: 2.1.0

set -e

echo "=========================================="
echo "StreamLive Cloud Deployment"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run as root${NC}"
    exit 1
fi

# Update system
echo -e "${GREEN}[1/8] Updating system...${NC}"
sudo apt update && sudo apt upgrade -y

# Install Python and pip
echo -e "${GREEN}[2/8] Installing Python and pip...${NC}"
sudo apt install python3 python3-pip python3-venv -y

# Install FFmpeg
echo -e "${GREEN}[3/8] Installing FFmpeg...${NC}"
sudo apt install ffmpeg -y

# Install Nginx
echo -e "${GREEN}[4/8] Installing Nginx...${NC}"
sudo apt install nginx -y

# Install Supervisor
echo -e "${GREEN}[5/8] Installing Supervisor...${NC}"
sudo apt install supervisor -y

# Create virtual environment
echo -e "${GREEN}[6/8] Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo -e "${GREEN}[7/8] Installing Python dependencies...${NC}"
pip install -r requirements.txt
pip install gunicorn

# Run migrations
echo -e "${GREEN}[8/8] Running database migrations...${NC}"
python migrate_database.py
python migrate_advanced_features.py

echo ""
echo -e "${GREEN}=========================================="
echo "Installation Complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Configure Supervisor: sudo nano /etc/supervisor/conf.d/streamlive.conf"
echo "2. Configure Nginx: sudo nano /etc/nginx/sites-available/streamlive"
echo "3. Start application: sudo supervisorctl start streamlive"
echo ""
echo "See CLOUD_DEPLOYMENT.md for detailed instructions"
echo ""
