# 🎥 StreamLive - Advanced Streaming Platform

**Version 2.1.0** - Professional streaming automation platform with multi-platform support and comprehensive analytics.

## ✨ Features

### Core Features
- ✅ **User Authentication** - Secure login with role-based access
- ✅ **Video Library** - Upload, download from GDrive, or scan local files
- ✅ **Multi-Channel** - Manage multiple streaming channels
- ✅ **Web Dashboard** - Professional admin interface
- ✅ **Real-time Monitoring** - System metrics and stream logs

### Advanced Features (NEW!)
- ✅ **Automated Scheduler** - Schedule streams with cron-like precision
- ✅ **Health Monitoring** - Real-time FPS, bitrate, and performance tracking
- ✅ **Multi-Platform** - Stream to YouTube, Facebook, Twitch simultaneously
- ✅ **Playlist Management** - Create playlists with multiple playback modes
- ✅ **Advanced Analytics** - Comprehensive performance metrics and reports

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python migrate_database.py
python migrate_advanced_features.py
```

### 3. Start Application
```bash
python app.py
```

### 4. Access Dashboard
```
http://localhost:5000
```

### 5. Login
```
Username: admin
Password: admin123
```

**⚠️ Change the default password immediately after first login!**

## 📖 Documentation

**Complete Guide:** [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)

This comprehensive guide includes:
- Installation instructions
- Feature documentation
- API reference
- Troubleshooting
- Security best practices
- Usage examples

## 📋 System Requirements

**Minimum:**
- Python 3.8+
- 2GB RAM
- 10GB disk space
- FFmpeg installed

**Recommended:**
- Python 3.10+
- 4GB RAM
- 50GB disk space
- Dedicated server

## 🎯 Key Features Explained

### Automated Scheduler
Schedule streams to start/stop automatically based on time and day of week.

### Health Monitoring
Track FPS, bitrate, dropped frames, CPU/Memory usage in real-time.

### Multi-Platform Streaming
Stream to YouTube, Facebook, and Twitch simultaneously from one source.

### Playlist Management
Create playlists with sequential, shuffle, or weighted random playback.

### Advanced Analytics
View channel performance, peak hours, video statistics, and export reports.

## 🔒 Security

- Password hashing with bcrypt
- Session management with Flask-Login
- Admin-only features protected
- Stream keys masked in API responses

## ☁️ Cloud Deployment

### Quick Cloud Setup
```bash
chmod +x deploy.sh
./deploy.sh
```

See [QUICK_CLOUD_SETUP.md](QUICK_CLOUD_SETUP.md) for 10-minute setup guide.

### Supported Platforms
- ✅ AWS EC2
- ✅ Google Cloud Platform
- ✅ DigitalOcean
- ✅ Azure
- ✅ Heroku

See [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) for platform-specific guides.

## 📚 Additional Documentation

- `COMPLETE_GUIDE.md` - Comprehensive documentation
- `CLOUD_DEPLOYMENT.md` - Cloud deployment guide
- `QUICK_CLOUD_SETUP.md` - Quick cloud setup
- `CHANGELOG.md` - Version history
- `FEATURE_SUGGESTIONS.md` - Future enhancements
- `PROJECT_STRUCTURE.md` - Code organization

## 🐛 Troubleshooting

See the [Troubleshooting section](COMPLETE_GUIDE.md#troubleshooting) in the Complete Guide.

## 📞 Support

For issues, questions, or feature requests, please refer to the Complete Guide or contact the support team
del streaming.db

# Linux/Mac
rm streaming.db
```

Lihat [MIGRATION.md](MIGRATION.md) untuk detail lengkap.

## Panduan Penggunaan

### 1. Tambah Video ke Library

Ada 2 cara menambah video:

**A. Download dari Google Drive:**
1. Klik "⬇️ Download dari GDrive"
2. Masukkan judul video
3. Masukkan nama file (contoh: video.mp4)
4. Masukkan Google Drive File ID
   - Dari link: `https://drive.google.com/file/d/1ABC123XYZ/view`
   - Ambil bagian `1ABC123XYZ`
5. Klik Download

**B. Tambah Manual (jika sudah upload via FTP/SSH):**
1. Klik "➕ Tambah Video"
2. Masukkan judul video
3. Masukkan nama file
4. Masukkan path file (contoh: ./videos/video.mp4)
5. Klik Simpan

### 2. Buat Channel Streaming

1. Klik "➕ Tambah Channel"
2. Isi form:
   - **Nama Channel**: Nama untuk identifikasi
   - **YouTube Stream Key**: Dari YouTube Studio > Go Live > Stream
   - **Pilih Video**: Pilih dari video library
   - **Tanggal Mulai Campaign**: (Opsional) Kapan campaign dimulai
   - **Tanggal Selesai Campaign**: (Opsional) Kapan campaign berakhir
   - **Waktu Mulai/Selesai (Harian)**: Jam streaming setiap hari
   - **Timezone**: Sesuaikan zona waktu
3. Klik Simpan

**Advanced Settings (Opsional):**
- **Copy Mode** (Default): Stream video asli tanpa re-encode
  - ✅ Cepat & hemat CPU
  - ✅ Kualitas sama dengan video asli
  - ✅ Recommended untuk video yang sudah di-encode dengan baik
  
- **Encode Mode**: Re-encode video dengan custom settings
  - Custom bitrate (contoh: 4000k untuk 1080p)
  - Custom FPS (24, 30, 60)
  - Custom preset (ultrafast, veryfast, fast, medium)
  - ⚠️ Butuh CPU lebih tinggi

**Contoh Scheduling:**
- Campaign: 1 Jan 2025 - 31 Jan 2025
- Waktu Harian: 08:00 - 20:00
- Mode: Copy (gunakan video asli 1080p 4000k CBR 30fps)
- Artinya: Stream setiap hari dari jam 8 pagi - 8 malam, hanya selama bulan Januari 2025

### 3. Mulai Streaming

- Klik "▶️ Start" pada channel yang ingin distream
- Atau bisa start multiple channel sekaligus
- Monitor status real-time di dashboard

### 4. Stop Streaming

- Klik "⏹️ Stop" pada channel yang berjalan
- Atau "⏹️ Stop Semua" untuk stop semua channel

## Cara Pakai

### Mode 1: Web Interface (Recommended)

#### Jalankan web server:
```bash
python3 app.py
```

#### Akses dari browser:
- Local: `http://localhost:5000`
- Remote: `http://YOUR_SERVER_IP:5000`

#### Jalankan di background:
```bash
nohup python3 app.py > app.log 2>&1 &
```

#### Stop web server:
```bash
pkill -f app.py
```

### Mode 2: CLI Version

#### Jalankan langsung:
```bash
python3 stream.py
```

#### Jalankan di background:
```bash
nohup python3 stream.py > stream.log 2>&1 &
```

#### Stop streaming:
```bash
pkill -f stream.py
```

## Systemd Service (Auto-start saat boot)

Buat file `/etc/systemd/system/youtube-stream.service`:

```ini
[Unit]
Description=YouTube Live Stream Web Interface
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/youtube-livestream-scheduler
ExecStart=/usr/bin/python3 /path/to/youtube-livestream-scheduler/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable dan start:
```bash
sudo systemctl enable youtube-stream
sudo systemctl start youtube-stream
sudo systemctl status youtube-stream
```

Buat file `/etc/systemd/system/youtube-stream.service`:

```ini
[Unit]
Description=YouTube Live Stream Scheduler
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/youtube-livestream-scheduler
ExecStart=/usr/bin/python3 /path/to/youtube-livestream-scheduler/stream.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable dan start:
```bash
sudo systemctl enable youtube-stream
sudo systemctl start youtube-stream
sudo systemctl status youtube-stream
```

## Tips Optimasi

### Untuk VPS dengan RAM kecil:
- Gunakan bitrate lebih rendah (1500k untuk 480p)
- Gunakan preset `ultrafast` di FFmpeg

### Untuk koneksi internet lambat:
- Turunkan bitrate ke 1000k-1500k
- Gunakan resolusi 480p

### Monitoring resource:
```bash
htop  # Monitor CPU/RAM
iftop # Monitor bandwidth
```

## Troubleshooting

### Video tidak download:
- Pastikan Google Drive link sudah public
- Check file_id sudah benar

### Stream tidak jalan:
- Pastikan stream key benar
- Check YouTube Studio apakah live stream sudah enabled
- Pastikan FFmpeg terinstall: `ffmpeg -version`

### Stream terputus-putus:
- Turunkan bitrate
- Check koneksi internet: `speedtest-cli`

## Resource Usage

Program ini sangat ringan:
- RAM: ~50-100 MB per stream
- CPU: 
  - **Copy Mode**: 5-15% per stream (sangat ringan)
  - **Encode Mode**: 20-50% per stream (tergantung preset)
- Bandwidth: Sesuai bitrate video (4000k = ~4 Mbps upload per stream)
- Storage: Tergantung ukuran video

**Rekomendasi:**
- Untuk VPS dengan CPU terbatas: Gunakan Copy Mode
- Video sudah 1080p 4000k CBR 30fps: Gunakan Copy Mode
- Perlu resize/adjust quality: Gunakan Encode Mode

## Fitur Database

Semua data tersimpan di SQLite database (`streaming.db`):
- **Video Library**: Semua video dengan metadata
- **Channels**: Konfigurasi semua channel
- **Stream Sessions**: History streaming
- **Logs**: Semua aktivitas
- **Statistics**: Statistik harian

## Multiple Streaming

Aplikasi support streaming ke multiple channel sekaligus:
- Setiap channel bisa pakai video berbeda
- Jadwal streaming berbeda per channel
- Bitrate & quality berbeda per channel
- Monitor semua channel dalam 1 dashboard

## License
MIT
