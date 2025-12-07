#!/bin/bash

echo "=========================================="
echo "Setup Auto-Start StreamLive"
echo "=========================================="
echo ""

# Get current directory and user
CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)

echo "Installing as user: $CURRENT_USER"
echo "Directory: $CURRENT_DIR"
echo ""

# 1. Create systemd service (better than supervisor)
echo "[1] Creating systemd service..."

sudo tee /etc/systemd/system/streamlive.service > /dev/null <<EOF
[Unit]
Description=StreamLive Application
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$CURRENT_DIR/venv/bin/gunicorn -w 2 --timeout 300 --graceful-timeout 300 -b 0.0.0.0:5000 app:app
Restart=always
RestartSec=10
StandardOutput=append:/var/log/streamlive.out.log
StandardError=append:/var/log/streamlive.err.log

# Prevent zombie processes
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF

# 2. Create log files
echo "[2] Creating log files..."
sudo touch /var/log/streamlive.out.log
sudo touch /var/log/streamlive.err.log
sudo chown $CURRENT_USER:$CURRENT_USER /var/log/streamlive.out.log
sudo chown $CURRENT_USER:$CURRENT_USER /var/log/streamlive.err.log

# 3. Reload systemd
echo "[3] Reloading systemd..."
sudo systemctl daemon-reload

# 4. Enable auto-start
echo "[4] Enabling auto-start..."
sudo systemctl enable streamlive

# 5. Start service
echo "[5] Starting service..."
sudo systemctl start streamlive

# 6. Check status
echo ""
echo "=========================================="
echo "Status:"
echo "=========================================="
sudo systemctl status streamlive --no-pager

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Commands:"
echo "  Start:   sudo systemctl start streamlive"
echo "  Stop:    sudo systemctl stop streamlive"
echo "  Restart: sudo systemctl restart streamlive"
echo "  Status:  sudo systemctl status streamlive"
echo "  Logs:    sudo journalctl -u streamlive -f"
echo ""
echo "Application will auto-start on server reboot!"
echo ""
