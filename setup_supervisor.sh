#!/bin/bash

# Setup Supervisor untuk StreamLive
echo "=========================================="
echo "Setup Supervisor untuk StreamLive"
echo "=========================================="

# Get current directory
CURRENT_DIR=$(pwd)
USER=$(whoami)

# Create supervisor config
echo "Creating supervisor configuration..."
sudo tee /etc/supervisor/conf.d/streamlive.conf > /dev/null <<EOF
[program:streamlive]
directory=$CURRENT_DIR
command=$CURRENT_DIR/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
user=$USER
autostart=true
autorestart=true
stderr_logfile=/var/log/streamlive.err.log
stdout_logfile=/var/log/streamlive.out.log
environment=PATH="$CURRENT_DIR/venv/bin"
EOF

# Create log files
echo "Creating log files..."
sudo touch /var/log/streamlive.err.log
sudo touch /var/log/streamlive.out.log
sudo chown $USER:$USER /var/log/streamlive.err.log
sudo chown $USER:$USER /var/log/streamlive.out.log

# Reload supervisor
echo "Reloading supervisor..."
sudo supervisorctl reread
sudo supervisorctl update

# Start streamlive
echo "Starting streamlive..."
sudo supervisorctl start streamlive

# Check status
echo ""
echo "=========================================="
echo "Status:"
echo "=========================================="
sudo supervisorctl status streamlive

echo ""
echo "Jika masih error, cek log dengan:"
echo "sudo tail -f /var/log/streamlive.err.log"
