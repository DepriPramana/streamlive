# 🔧 Troubleshooting - Bahasa Indonesia

## Error: "no such process" di Supervisor

### Solusi 1: Setup Supervisor Manual

```bash
# 1. Buat konfigurasi supervisor
sudo nano /etc/supervisor/conf.d/streamlive.conf
```

Isi dengan (ganti `/home/ipramana/streamlive` dengan path Anda):

```ini
[program:streamlive]
directory=/home/ipramana/streamlive
command=/home/ipramana/streamlive/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
user=ipramana
autostart=true
autorestart=true
stderr_logfile=/var/log/streamlive.err.log
stdout_logfile=/var/log/streamlive.out.log
environment=PATH="/home/ipramana/streamlive/venv/bin"
```

```bash
# 2. Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update

# 3. Start aplikasi
sudo supervisorctl start streamlive

# 4. Cek status
sudo supervisorctl status streamlive
```

### Solusi 2: Jalankan Langsung (Tanpa Supervisor)

Jika supervisor bermasalah, jalankan langsung:

```bash
# Aktifkan virtual environment
source venv/bin/activate

# Jalankan dengan gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Atau jalankan development server:

```bash
python3 app.py
```

### Solusi 3: Gunakan Systemd (Alternatif Supervisor)

```bash
# 1. Buat service file
sudo nano /etc/systemd/system/streamlive.service
```

Isi dengan:

```ini
[Unit]
Description=StreamLive Application
After=network.target

[Service]
Type=simple
User=ipramana
WorkingDirectory=/home/ipramana/streamlive
Environment="PATH=/home/ipramana/streamlive/venv/bin"
ExecStart=/home/ipramana/streamlive/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 2. Reload systemd
sudo systemctl daemon-reload

# 3. Enable dan start service
sudo systemctl enable streamlive
sudo systemctl start streamlive

# 4. Cek status
sudo systemctl status streamlive
```

---

## Cek Log Error

```bash
# Log aplikasi
sudo tail -f /var/log/streamlive.err.log

# Log supervisor
sudo tail -f /var/log/supervisor/supervisord.log

# Log systemd (jika pakai systemd)
sudo journalctl -u streamlive -f
```

---

## Cek Apakah Port 5000 Sudah Dipakai

```bash
# Cek port
sudo netstat -tulpn | grep 5000

# Atau
sudo lsof -i :5000

# Jika ada proses, kill dulu
sudo kill -9 <PID>
```

---

## Cek Virtual Environment

```bash
# Pastikan venv ada
ls -la venv/

# Jika tidak ada, buat ulang
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

---

## Cek Gunicorn Terinstall

```bash
# Aktifkan venv
source venv/bin/activate

# Cek gunicorn
which gunicorn
gunicorn --version

# Jika tidak ada, install
pip install gunicorn
```

---

## Test Aplikasi Manual

```bash
# Aktifkan venv
source venv/bin/activate

# Test dengan Flask development server
python3 app.py

# Jika jalan, berarti aplikasi OK
# Tekan Ctrl+C untuk stop
```

---

## Setup Nginx (Setelah Aplikasi Jalan)

```bash
# 1. Buat konfigurasi nginx
sudo nano /etc/nginx/sites-available/streamlive
```

Isi dengan:

```nginx
server {
    listen 80;
    server_name _;  # Ganti dengan domain Anda

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    client_max_body_size 2G;
}
```

```bash
# 2. Enable site
sudo ln -s /etc/nginx/sites-available/streamlive /etc/nginx/sites-enabled/

# 3. Test konfigurasi
sudo nginx -t

# 4. Restart nginx
sudo systemctl restart nginx
```

---

## Akses Aplikasi

Setelah semua jalan:

```
# Langsung ke aplikasi (tanpa nginx)
http://your-server-ip:5000

# Lewat nginx
http://your-server-ip
```

**Login:**
- Username: `admin`
- Password: `admin123`

---

## Command Berguna

```bash
# Restart aplikasi (supervisor)
sudo supervisorctl restart streamlive

# Restart aplikasi (systemd)
sudo systemctl restart streamlive

# Restart nginx
sudo systemctl restart nginx

# Cek status semua
sudo supervisorctl status
sudo systemctl status nginx
sudo systemctl status streamlive

# Lihat log real-time
sudo tail -f /var/log/streamlive.err.log
sudo tail -f /var/log/streamlive.out.log
```

---

## Jika Masih Error

1. **Cek Python version:**
   ```bash
   python3 --version  # Harus 3.8+
   ```

2. **Cek FFmpeg:**
   ```bash
   ffmpeg -version
   # Jika tidak ada:
   sudo apt install ffmpeg -y
   ```

3. **Cek permissions:**
   ```bash
   ls -la
   # Pastikan file bisa diakses user Anda
   ```

4. **Reinstall dependencies:**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt --force-reinstall
   ```

5. **Cek database:**
   ```bash
   ls -la instance/
   # Pastikan streaming.db ada
   
   # Jika tidak ada, run migration
   python3 migrate_database.py
   python3 migrate_advanced_features.py
   ```

---

## Kontak Support

Jika masih bermasalah, kirim informasi berikut:

1. Output dari: `sudo supervisorctl status`
2. Output dari: `sudo tail -20 /var/log/streamlive.err.log`
3. Output dari: `python3 --version`
4. Output dari: `which gunicorn`
5. Screenshot error

---

**Semoga membantu!** 🚀
