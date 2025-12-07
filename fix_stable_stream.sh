#!/bin/bash

echo "=========================================="
echo "Fix Stable Streaming"
echo "=========================================="

# 1. Kill semua process FFmpeg dan Gunicorn
echo "[1] Stopping all processes..."
pkill -9 ffmpeg
pkill -9 gunicorn
sleep 3

# 2. Clean up zombie processes
echo "[2] Cleaning zombie processes..."
ps aux | grep defunct | awk '{print $2}' | xargs -r sudo kill -9 2>/dev/null
sleep 2

# 3. Check internet speed
echo "[3] Testing internet connection..."
ping -c 5 a.rtmp.youtube.com | tail -1

# 4. Restart application dengan timeout protection
echo "[4] Starting application with stability improvements..."
cd ~/streamlive
source venv/bin/activate

# Set ulimit untuk prevent resource issues
ulimit -n 4096

# Start gunicorn dengan timeout lebih tinggi
nohup gunicorn -w 2 --timeout 300 --graceful-timeout 300 -b 0.0.0.0:5000 app:app > /tmp/streamlive.log 2>&1 &

sleep 5

# 5. Check if running
echo "[5] Checking application status..."
ps aux | grep gunicorn | grep -v grep

echo ""
echo "=========================================="
echo "Done! Application restarted."
echo "=========================================="
echo ""
echo "Now:"
echo "1. Wait 10 seconds"
echo "2. Go to dashboard and start stream"
echo "3. Monitor with: tail -f /tmp/streamlive.log"
echo ""
echo "If stream still stops, the issue is:"
echo "- Internet upload speed too slow"
echo "- YouTube rejecting the stream"
echo "- Video bitrate too high"
echo ""
