#!/bin/bash

echo "=========================================="
echo "StreamLive - Complete System Check"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}[1] Checking FFmpeg...${NC}"
ffmpeg -version 2>&1 | head -1
echo ""

echo -e "${GREEN}[2] Checking Application Status...${NC}"
ps aux | grep -E "gunicorn|python.*app.py" | grep -v grep
echo ""

echo -e "${GREEN}[3] Checking Port 5000...${NC}"
sudo netstat -tulpn | grep 5000
echo ""

echo -e "${GREEN}[4] Checking Nginx Status...${NC}"
sudo systemctl status nginx --no-pager | head -5
echo ""

echo -e "${GREEN}[5] Checking Video Files...${NC}"
ls -lh videos/ 2>/dev/null || echo "No videos folder"
echo ""

echo -e "${GREEN}[6] Checking Database...${NC}"
ls -lh instance/streaming.db 2>/dev/null || echo "No database"
echo ""

echo -e "${GREEN}[7] Last 20 Error Logs...${NC}"
echo "--- Application Errors ---"
sudo tail -20 /var/log/streamlive.err.log 2>/dev/null || tail -20 /tmp/streamlive.log 2>/dev/null || echo "No error logs found"
echo ""

echo -e "${GREEN}[8] Last 10 Application Logs...${NC}"
sudo tail -10 /var/log/streamlive.out.log 2>/dev/null || echo "No output logs"
echo ""

echo -e "${GREEN}[9] Checking FFmpeg Processes...${NC}"
ps aux | grep ffmpeg | grep -v grep || echo "No FFmpeg processes running"
echo ""

echo -e "${GREEN}[10] Checking API Status...${NC}"
curl -s http://localhost:5000/api/status | python3 -m json.tool 2>/dev/null || echo "API not responding"
echo ""

echo -e "${GREEN}[11] Checking Firewall...${NC}"
sudo ufw status | grep -E "5000|80|443"
echo ""

echo -e "${GREEN}[12] Checking Disk Space...${NC}"
df -h | grep -E "Filesystem|/$"
echo ""

echo "=========================================="
echo "Check Complete!"
echo "=========================================="
echo ""
echo "Untuk test start stream manual:"
echo "  curl -X POST http://localhost:5000/api/start/1"
echo ""
echo "Untuk lihat log real-time:"
echo "  sudo tail -f /var/log/streamlive.err.log"
echo ""
