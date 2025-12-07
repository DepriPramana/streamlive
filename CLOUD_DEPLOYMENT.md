# ☁️ Cloud Deployment Guide

Complete guide for deploying StreamLive on various cloud platforms.

---

## 📋 Table of Contents

1. [AWS EC2](#aws-ec2)
2. [Google Cloud Platform](#google-cloud-platform)
3. [DigitalOcean](#digitalocean)
4. [Azure](#azure)
5. [Heroku](#heroku)
6. [General Setup](#general-setup)

---

## 🚀 AWS EC2

### Step 1: Launch EC2 Instance

1. **Login to AWS Console**
   - Go to EC2 Dashboard
   - Click "Launch Instance"

2. **Choose AMI**
   - Select "Ubuntu Server 22.04 LTS"
   - 64-bit (x86)

3. **Choose Instance Type**
   - Minimum: t2.medium (2 vCPU, 4GB RAM)
   - Recommended: t2.large (2 vCPU, 8GB RAM)

4. **Configure Security Group**
   ```
   Type: SSH, Port: 22, Source: Your IP
   Type: HTTP, Port: 80, Source: 0.0.0.0/0
   Type: HTTPS, Port: 443, Source: 0.0.0.0/0
   Type: Custom TCP, Port: 5000, Source: 0.0.0.0/0
   ```

5. **Add Storage**
   - Minimum: 20GB
   - Recommended: 50GB+ for videos

6. **Launch & Download Key Pair**
   - Save `.pem` file securely

### Step 2: Connect to Instance

```bash
# Set permissions
chmod 400 your-key.pem

# Connect
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Step 3: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python & pip
sudo apt install python3 python3-pip -y

# Install FFmpeg
sudo apt install ffmpeg -y

# Install Git
sudo apt install git -y
```

### Step 4: Deploy Application

```bash
# Clone repository
git clone <your-repo-url>
cd streamlive

# Install Python dependencies
pip3 install -r requirements.txt

# Run migrations
python3 migrate_database.py
python3 migrate_advanced_features.py

# Test run
python3 app.py
```

### Step 5: Setup Production Server

```bash
# Install Gunicorn
pip3 install gunicorn

# Install Nginx
sudo apt install nginx -y

# Install Supervisor (for process management)
sudo apt install supervisor -y
```

### Step 6: Configure Gunicorn

Create `/etc/supervisor/conf.d/streamlive.conf`:

```ini
[program:streamlive]
directory=/home/ubuntu/streamlive
command=/usr/local/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/streamlive.err.log
stdout_logfile=/var/log/streamlive.out.log
```

```bash
# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start streamlive
```

### Step 7: Configure Nginx

Create `/etc/nginx/sites-available/streamlive`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 2G;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/streamlive /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 8: Setup SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## 🌐 Google Cloud Platform

### Step 1: Create VM Instance

1. **Go to Compute Engine**
   - Click "Create Instance"

2. **Configure Instance**
   - Name: streamlive-server
   - Region: Choose nearest
   - Machine type: e2-medium (2 vCPU, 4GB)
   - Boot disk: Ubuntu 22.04 LTS, 50GB

3. **Firewall**
   - Allow HTTP traffic
   - Allow HTTPS traffic

4. **Create**

### Step 2: Setup Firewall Rules

```bash
# Create firewall rule for port 5000
gcloud compute firewall-rules create allow-streamlive \
    --allow tcp:5000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow StreamLive"
```

### Step 3: Connect via SSH

```bash
# From GCP Console, click "SSH" button
# Or use gcloud CLI
gcloud compute ssh streamlive-server
```

### Step 4: Follow AWS Steps 3-8

Same installation and configuration steps as AWS.

---

## 💧 DigitalOcean

### Step 1: Create Droplet

1. **Login to DigitalOcean**
2. **Create Droplet**
   - Image: Ubuntu 22.04 LTS
   - Plan: Basic ($12/month - 2GB RAM)
   - Datacenter: Choose nearest
   - Add SSH key

### Step 2: Connect

```bash
ssh root@your-droplet-ip
```

### Step 3: Initial Setup

```bash
# Create user
adduser streamlive
usermod -aG sudo streamlive

# Switch to user
su - streamlive
```

### Step 4: Follow AWS Steps 3-8

Same installation and configuration steps.

---

## ☁️ Azure

### Step 1: Create Virtual Machine

1. **Go to Azure Portal**
2. **Create VM**
   - Image: Ubuntu Server 22.04 LTS
   - Size: Standard_B2s (2 vCPU, 4GB)
   - Authentication: SSH public key

3. **Networking**
   - Allow ports: 22, 80, 443, 5000

### Step 2: Connect

```bash
ssh azureuser@your-vm-ip
```

### Step 3: Follow AWS Steps 3-8

Same installation and configuration steps.

---

## 🎯 Heroku

### Step 1: Prepare Application

Create `Procfile`:
```
web: gunicorn app:app
```

Create `runtime.txt`:
```
python-3.10.12
```

### Step 2: Deploy

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create your-app-name

# Add buildpack for FFmpeg
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git

# Deploy
git push heroku main

# Run migrations
heroku run python migrate_database.py
heroku run python migrate_advanced_features.py

# Open app
heroku open
```

**Note:** Heroku has limitations:
- Ephemeral filesystem (videos won't persist)
- Use external storage (S3, GCS) for videos
- Limited to 512MB RAM on free tier

---

## 🔧 General Setup

### Environment Variables

Create `.env` file:
```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///streaming.db
FLASK_ENV=production
```

Load in app:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Systemd Service (Alternative to Supervisor)

Create `/etc/systemd/system/streamlive.service`:

```ini
[Unit]
Description=StreamLive Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/streamlive
ExecStart=/usr/local/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable streamlive
sudo systemctl start streamlive
sudo systemctl status streamlive
```

### Monitoring

```bash
# View logs
sudo tail -f /var/log/streamlive.out.log
sudo tail -f /var/log/streamlive.err.log

# Check status
sudo supervisorctl status streamlive
# or
sudo systemctl status streamlive
```

### Backup Script

Create `backup.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp instance/streaming.db $BACKUP_DIR/streaming_$DATE.db

# Backup videos (optional)
tar -czf $BACKUP_DIR/videos_$DATE.tar.gz videos/

# Keep only last 7 days
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
chmod +x backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
0 2 * * * /home/ubuntu/streamlive/backup.sh
```

---

## 🔒 Security Checklist

- [ ] Change default admin password
- [ ] Setup firewall (ufw)
- [ ] Enable SSL/HTTPS
- [ ] Use strong SECRET_KEY
- [ ] Disable debug mode
- [ ] Setup automatic backups
- [ ] Configure fail2ban
- [ ] Keep system updated
- [ ] Use non-root user
- [ ] Restrict SSH access

### Setup UFW Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Install Fail2ban

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📊 Performance Optimization

### 1. Use CDN for Static Files

Configure Nginx to cache static files:
```nginx
location /static/ {
    alias /home/ubuntu/streamlive/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 2. Database Optimization

```bash
# For production, consider PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Update DATABASE_URL
DATABASE_URL=postgresql://user:pass@localhost/streamlive
```

### 3. Redis for Caching

```bash
sudo apt install redis-server -y
pip3 install redis flask-caching
```

---

## 🐛 Troubleshooting

### Application Won't Start

```bash
# Check logs
sudo tail -f /var/log/streamlive.err.log

# Check if port is in use
sudo netstat -tulpn | grep 5000

# Restart service
sudo supervisorctl restart streamlive
```

### FFmpeg Not Found

```bash
# Install FFmpeg
sudo apt install ffmpeg -y

# Verify installation
ffmpeg -version
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R ubuntu:ubuntu /home/ubuntu/streamlive

# Fix permissions
chmod +x app.py
```

### Out of Memory

```bash
# Check memory
free -h

# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📞 Support

For deployment issues:
1. Check logs first
2. Verify all dependencies installed
3. Check firewall rules
4. Test locally before deploying
5. Contact support if needed

---

**Last Updated:** December 7, 2025  
**Version:** 2.1.0
