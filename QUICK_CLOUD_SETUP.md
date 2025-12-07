# ⚡ Quick Cloud Setup

Get StreamLive running on cloud in 10 minutes!

---

## 🚀 One-Command Setup

```bash
# Clone repository
git clone <your-repo-url>
cd streamlive

# Run deployment script
chmod +x deploy.sh
./deploy.sh
```

This will:
- ✅ Update system
- ✅ Install Python, FFmpeg, Nginx, Supervisor
- ✅ Install dependencies
- ✅ Run migrations

---

## 📝 Manual Setup (5 Steps)

### 1. Install Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip ffmpeg nginx supervisor -y
```

### 2. Setup Application
```bash
cd streamlive
pip3 install -r requirements.txt
pip3 install gunicorn
python3 migrate_database.py
python3 migrate_advanced_features.py
```

### 3. Configure Supervisor
```bash
sudo cp configs/supervisor.conf /etc/supervisor/conf.d/streamlive.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start streamlive
```

### 4. Configure Nginx
```bash
sudo cp configs/nginx.conf /etc/nginx/sites-available/streamlive
sudo ln -s /etc/nginx/sites-available/streamlive /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Setup SSL (Optional)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## ✅ Verify Installation

```bash
# Check if application is running
sudo supervisorctl status streamlive

# Check Nginx
sudo systemctl status nginx

# Test application
curl http://localhost:5000

# View logs
sudo tail -f /var/log/streamlive.out.log
```

---

## 🌐 Access Your Application

```
http://your-server-ip
or
http://your-domain.com
```

**Login:**
- Username: `admin`
- Password: `admin123`

**⚠️ Change password immediately!**

---

## 🔧 Common Commands

```bash
# Restart application
sudo supervisorctl restart streamlive

# View logs
sudo tail -f /var/log/streamlive.out.log
sudo tail -f /var/log/streamlive.err.log

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo supervisorctl status
sudo systemctl status nginx
```

---

## 🐛 Troubleshooting

**Application won't start?**
```bash
sudo supervisorctl tail streamlive stderr
```

**Can't access from browser?**
```bash
# Check firewall
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

**FFmpeg not found?**
```bash
sudo apt install ffmpeg -y
ffmpeg -version
```

---

## 📚 Full Documentation

See [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) for:
- Platform-specific guides (AWS, GCP, Azure, etc.)
- Advanced configuration
- Security hardening
- Performance optimization
- Monitoring setup

---

**Need Help?** Check [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)
