#!/bin/bash

echo "=========================================="
echo "Fix Streaming Issues"
echo "=========================================="
echo ""

# Kill zombie FFmpeg processes
echo "[1] Cleaning up zombie processes..."
sudo pkill -9 ffmpeg 2>/dev/null
sleep 2

# Check system resources
echo "[2] Checking system resources..."
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}'
echo ""
echo "Memory Usage:"
free -h | grep Mem | awk '{print $3 "/" $2}'
echo ""
echo "Disk Space:"
df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}'
echo ""

# Check network
echo "[3] Testing network to YouTube..."
ping -c 3 a.rtmp.youtube.com 2>/dev/null || echo "Cannot reach YouTube RTMP server"
echo ""

# Check video file
echo "[4] Checking video file..."
VIDEO_FILE=$(ls -1 videos/*.mp4 | head -1)
if [ -f "$VIDEO_FILE" ]; then
    echo "Video found: $VIDEO_FILE"
    echo "Video info:"
    ffprobe -v error -show_entries format=duration,size,bit_rate -show_entries stream=codec_name,width,height,r_frame_rate -of default=noprint_wrappers=1 "$VIDEO_FILE" 2>/dev/null | head -10
else
    echo "No video file found!"
fi
echo ""

echo "=========================================="
echo "Recommendations:"
echo "=========================================="
echo ""
echo "1. Use COPY mode (no re-encoding) for better stability"
echo "2. If using ENCODE mode, use these settings:"
echo "   - Bitrate: 2500k (for 720p) or 4000k (for 1080p)"
echo "   - FPS: 30"
echo "   - Preset: veryfast or ultrafast"
echo ""
echo "3. Check your internet upload speed:"
echo "   - Minimum: 5 Mbps for 720p"
echo "   - Recommended: 10+ Mbps for 1080p"
echo ""
echo "4. Monitor logs while streaming:"
echo "   tail -f /tmp/streamlive.log"
echo ""
