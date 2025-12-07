# 🎥 StreamLive - Complete Guide

**Version:** 2.1.0  
**Last Updated:** December 7, 2025

---

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Features Overview](#features-overview)
5. [User Management](#user-management)
6. [Advanced Features](#advanced-features)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)
9. [Security](#security)

---

## 🌟 Introduction

StreamLive is an advanced streaming platform that allows you to manage YouTube Live streams with automation, multi-platform support, and comprehensive analytics.

### Key Capabilities
- ✅ User authentication & management
- ✅ Video library management
- ✅ Multi-channel streaming
- ✅ Automated scheduling
- ✅ Stream health monitoring
- ✅ Multi-platform streaming (YouTube, Facebook, Twitch)
- ✅ Video playlist management
- ✅ Advanced analytics dashboard

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
# Basic migration
python migrate_database.py

# Advanced features migration
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

**⚠️ IMPORTANT:** Change the default password immediately after first login!

---

## 📦 Installation

### System Requirements

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

### Step-by-Step Installation

#### 1. Clone Repository
```bash
git clone <repository-url>
cd streamlive
```

#### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies:**
- Flask==3.0.0
- Flask-SQLAlchemy==3.1.1
- Flask-Login==0.6.3
- APScheduler==3.10.4
- bcrypt==4.1.2
- gdown==5.1.0
- pytz==2024.1
- psutil==5.9.6

#### 3. Install FFmpeg

**Windows:**
```bash
# Download from https://ffmpeg.org/download.html
# Add to PATH
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

#### 4. Initialize Database
```bash
python migrate_database.py
python migrate_advanced_features.py
```

#### 5. Start Server
```bash
python app.py
```

---

## 🎯 Features Overview

### Core Features

#### 1. Video Library Management
- Upload videos manually
- Download from Google Drive
- Scan local folder
- Auto-detect metadata (duration, resolution, size)
- Track usage statistics

#### 2. Channel Management
- Multiple channels support
- Individual channel configuration
- Start/stop per channel
- Encoding settings (copy/encode mode)
- Campaign date ranges

#### 3. System Monitoring
- Real-time status
- CPU/Memory/Disk usage
- Stream logs
- Session history
- Statistics dashboard

### Advanced Features

#### 4. Automated Scheduler ⏰
- Cron-like scheduling
- Day-of-week selection
- Auto start/stop streams
- Multiple tasks per channel

#### 5. Stream Health Monitoring 🏥
- Real-time FPS tracking
- Bitrate monitoring
- Dropped frames detection
- CPU/Memory usage
- Health status alerts

#### 6. Multi-Platform Streaming 📡
- Stream to multiple platforms simultaneously
- YouTube, Facebook, Twitch support
- Custom RTMP servers
- Platform priority system

#### 7. Video Playlist Management 🎵
- Create playlists
- Sequential/Shuffle/Random playback
- Weighted selection
- Content rotation

#### 8. Advanced Analytics 📊
- Channel performance metrics
- Peak hours analysis
- Video usage statistics
- Success rate tracking
- Export reports

---

## 👥 User Management

### Default Admin Account

**First Login:**
- Username: `admin`
- Password: `admin123`

The default credentials are only shown on the login page when the password hasn't been changed.

### Creating Users

1. Login as admin
2. Click "👥 Users" in sidebar
3. Click "➕ Add New User"
4. Fill in details:
   - Username (required)
   - Password (required, min 6 characters)
   - Email (optional)
   - Admin role (checkbox)
   - Active status (checkbox)
5. Click "💾 Create User"

### User Roles

**Admin Users:**
- Full system access
- User management
- All features available

**Regular Users:**
- Stream management
- Video library
- View analytics
- No user management

### Security Features

- ✅ Password hashing (bcrypt)
- ✅ Session management
- ✅ Login required for all routes
- ✅ Admin-only features protected
- ✅ Self-protection (can't delete yourself)
- ✅ Last admin protection

---

## 🚀 Advanced Features

### 1. Automated Scheduler

#### Creating a Scheduled Task

**Via UI:**
1. Click "⏰ Scheduler" in sidebar
2. Click "➕ Add Scheduled Task"
3. Select channel
4. Choose task type (Start/Stop)
5. Set time (HH:MM)
6. Select days of week
7. Click "💾 Create"

**Via API:**
```bash
POST /api/scheduled-tasks
{
  "channel_id": 1,
  "task_type": "start",
  "scheduled_time": "08:00",
  "days_of_week": "0,1,2,3,4"
}
```

**Days of Week:**
- 0 = Monday
- 1 = Tuesday
- 2 = Wednesday
- 3 = Thursday
- 4 = Friday
- 5 = Saturday
- 6 = Sunday

#### Example Schedules

**Weekday Streaming (Mon-Fri, 8 AM - 6 PM):**
```json
// Start task
{
  "channel_id": 1,
  "task_type": "start",
  "scheduled_time": "08:00",
  "days_of_week": "0,1,2,3,4"
}

// Stop task
{
  "channel_id": 1,
  "task_type": "stop",
  "scheduled_time": "18:00",
  "days_of_week": "0,1,2,3,4"
}
```

**24/7 Streaming:**
```json
{
  "channel_id": 1,
  "task_type": "start",
  "scheduled_time": "00:00",
  "days_of_week": "0,1,2,3,4,5,6"
}
```

---

### 2. Stream Health Monitoring

#### Metrics Tracked
- **FPS** (Frames Per Second)
- **Bitrate** (kbps)
- **Dropped Frames**
- **CPU Usage** (%)
- **Memory Usage** (%)
- **Status** (healthy/warning/critical)

#### Health Status Levels

| Status | Condition | Action |
|--------|-----------|--------|
| 🟢 Healthy | Normal operation | None |
| 🟡 Warning | Dropped frames > 50 OR CPU > 70% | Log warning |
| 🔴 Critical | Dropped frames > 100 OR CPU > 90% | Alert + Log |

#### Viewing Health Data

**Via API:**
```bash
GET /api/health/{session_id}
```

**Response:**
```json
{
  "health_checks": [
    {
      "timestamp": "2025-12-07T10:30:00",
      "fps": 30.0,
      "bitrate_kbps": 4000.0,
      "dropped_frames": 5,
      "cpu_usage": 45.2,
      "memory_usage": 32.1,
      "status": "healthy"
    }
  ]
}
```

---

### 3. Multi-Platform Streaming

#### Supported Platforms

| Platform | RTMP URL |
|----------|----------|
| YouTube | `rtmp://a.rtmp.youtube.com/live2/` |
| Facebook | `rtmps://live-api-s.facebook.com:443/rtmp/` |
| Twitch | `rtmp://live.twitch.tv/app/` |
| Custom | Your custom RTMP server |

#### Adding a Platform

**Via UI:**
1. Click "📡 Platforms" in sidebar
2. Click "➕ Add Platform Destination"
3. Select channel
4. Choose platform (RTMP URL auto-fills)
5. Enter stream key
6. Set priority (optional)
7. Click "💾 Add"

**Via API:**
```bash
POST /api/platforms
{
  "channel_id": 1,
  "platform_name": "youtube",
  "rtmp_url": "rtmp://a.rtmp.youtube.com/live2/",
  "stream_key": "your-stream-key",
  "priority": 1
}
```

#### Example: Stream to Multiple Platforms

```bash
# Add YouTube
POST /api/platforms
{
  "channel_id": 1,
  "platform_name": "youtube",
  "rtmp_url": "rtmp://a.rtmp.youtube.com/live2/",
  "stream_key": "youtube-key",
  "priority": 1
}

# Add Facebook
POST /api/platforms
{
  "channel_id": 1,
  "platform_name": "facebook",
  "rtmp_url": "rtmps://live-api-s.facebook.com:443/rtmp/",
  "stream_key": "facebook-key",
  "priority": 2
}

# Add Twitch
POST /api/platforms
{
  "channel_id": 1,
  "platform_name": "twitch",
  "rtmp_url": "rtmp://live.twitch.tv/app/",
  "stream_key": "twitch-key",
  "priority": 3
}
```

---

### 4. Video Playlist Management

#### Playback Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| Sequential | Play videos in order | Episodic content |
| Shuffle | Random without immediate repeat | Variety shows |
| Random | Weighted random selection | Promotional content |

#### Creating a Playlist

**Via UI:**
1. Click "🎵 Playlists" in sidebar
2. Click "➕ Create Playlist"
3. Enter name and description
4. Select playback mode
5. Click "💾 Create"

**Via API:**
```bash
POST /api/playlists
{
  "name": "Morning Shows",
  "description": "Morning content rotation",
  "playback_mode": "sequential"
}
```

#### Adding Videos to Playlist

```bash
POST /api/playlists/{playlist_id}/videos
{
  "video_id": 5,
  "weight": 1
}
```

**Weight:** Used in `random` mode. Higher weight = more likely to play.

---

### 5. Advanced Analytics

#### Available Metrics

**Channel Analytics:**
- Total sessions
- Total duration
- Success rate
- Average session duration
- Uptime percentage

**Peak Hours:**
- Hour-by-hour breakdown
- Session count per hour
- Top 5 peak hours

**Video Performance:**
- Most used videos
- Usage count
- Total duration per video

#### Viewing Analytics

**Via UI:**
1. Click "📊 Analytics" in sidebar
2. Select channel (or "All Channels")
3. Choose date range (7/30/90 days)
4. View metrics
5. Click "📥 Export" to download

**Via API:**
```bash
# Channel analytics
GET /api/analytics/channel/{channel_id}?days=30

# Peak hours
GET /api/analytics/peak-hours?channel_id=1&days=30

# Video performance
GET /api/analytics/video-performance?days=30

# Export report
GET /api/analytics/export?type=channel&channel_id=1&days=30&format=json
```

---

## 🔌 API Reference

### Authentication
All API endpoints require authentication via Flask-Login session.

### Channels

```bash
GET    /api/channels              # List all channels
POST   /api/channels              # Create channel
GET    /api/channels/{id}         # Get channel
PUT    /api/channels/{id}         # Update channel
DELETE /api/channels/{id}         # Delete channel
POST   /api/start/{id}            # Start streaming
POST   /api/stop/{id}             # Stop streaming
POST   /api/stop-all              # Stop all streams
```

### Videos

```bash
GET    /api/videos                # List all videos
POST   /api/videos                # Add video
GET    /api/videos/{id}           # Get video
PUT    /api/videos/{id}           # Update video
DELETE /api/videos/{id}           # Delete video
POST   /api/videos/upload         # Upload video
POST   /api/videos/scan           # Scan folder
POST   /api/videos/download-gdrive # Download from GDrive
```

### Playlists

```bash
GET    /api/playlists             # List playlists
POST   /api/playlists             # Create playlist
GET    /api/playlists/{id}        # Get playlist
DELETE /api/playlists/{id}        # Delete playlist
POST   /api/playlists/{id}/videos # Add video to playlist
DELETE /api/playlists/{id}/videos # Remove video from playlist
```

### Scheduler

```bash
GET    /api/scheduled-tasks       # List tasks
POST   /api/scheduled-tasks       # Create task
DELETE /api/scheduled-tasks/{id}  # Delete task
```

### Platforms

```bash
GET    /api/platforms             # List platforms
POST   /api/platforms             # Add platform
DELETE /api/platforms/{id}        # Delete platform
```

### Analytics

```bash
GET /api/analytics/channel/{id}        # Channel analytics
GET /api/analytics/peak-hours          # Peak hours
GET /api/analytics/video-performance   # Video stats
GET /api/analytics/export              # Export report
```

### Users (Admin Only)

```bash
GET    /api/users                 # List users
POST   /api/users                 # Create user
GET    /api/users/{id}            # Get user
PUT    /api/users/{id}            # Update user
DELETE /api/users/{id}            # Delete user
```

### System

```bash
GET /api/status                   # System status
GET /api/logs                     # System logs
GET /api/stats                    # Statistics
GET /api/history                  # Stream history
GET /api/system/metrics           # System metrics
GET /api/health/{session_id}      # Health metrics
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Migration Fails
```bash
# Check database
ls -la instance/streaming.db

# Backup and retry
cp instance/streaming.db instance/streaming.db.backup
python migrate_database.py
python migrate_advanced_features.py
```

#### 2. Scheduler Not Working
```bash
# Check if APScheduler is installed
pip install APScheduler==3.10.4

# Restart application
python app.py
```

#### 3. Stream Won't Start
- Check if video file exists
- Verify RTMP URL and stream key
- Check FFmpeg is installed: `ffmpeg -version`
- Review logs: Click "📝 System Logs"

#### 4. Health Monitoring No Data
- Wait 30 seconds after stream starts
- Check database: `SELECT * FROM stream_health LIMIT 5;`
- Verify stream is actually running

#### 5. Multi-Platform Fails
- Verify RTMP URLs are correct
- Test each platform individually
- Check stream keys are valid
- Review firewall/network settings

#### 6. Analytics Showing Zero
- Check date range (default 30 days)
- Verify sessions exist in database
- Ensure channel_id is correct
- Wait for data to accumulate

#### 7. Can't Login
- Verify username and password
- Check if user is active
- Clear browser cookies
- Check database: `SELECT * FROM users;`

---

## 🔒 Security

### Built-in Security Features

- ✅ Password hashing with bcrypt
- ✅ Session management with Flask-Login
- ✅ Login required for all routes
- ✅ Admin-only features protected
- ✅ Stream keys masked in API responses
- ✅ CSRF protection
- ✅ SQL injection prevention (SQLAlchemy)

### Security Best Practices

#### 1. Change Default Password
```
1. Login with admin/admin123
2. Go to Users section
3. Edit admin user
4. Set strong password
5. Logout and login with new password
```

#### 2. Use Strong Passwords
- Minimum 12 characters
- Mix uppercase, lowercase, numbers, symbols
- Don't reuse passwords
- Use password manager

#### 3. Regular Updates
- Update dependencies regularly
- Monitor security advisories
- Keep FFmpeg updated
- Update Python version

#### 4. Network Security
- Use HTTPS in production
- Configure firewall
- Restrict access by IP (optional)
- Use VPN for remote access

#### 5. Backup Regularly
```bash
# Backup database
cp instance/streaming.db backups/streaming_$(date +%Y%m%d).db

# Backup videos
tar -czf backups/videos_$(date +%Y%m%d).tar.gz videos/
```

#### 6. Monitor Access
- Review user activity logs
- Check last login times
- Deactivate unused accounts
- Audit admin actions

### Production Deployment

#### 1. Use Production Server
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 2. Use HTTPS
```bash
# Install certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com
```

#### 3. Configure Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 4. Set Environment Variables
```bash
export SECRET_KEY='your-secret-key-here'
export DATABASE_URL='sqlite:///production.db'
export FLASK_ENV='production'
```

---

## 📚 Additional Resources

### Documentation Files
- `README.md` - Project overview
- `CHANGELOG.md` - Version history
- `FEATURE_SUGGESTIONS.md` - Future enhancements

### Migration Scripts
- `migrate_database.py` - Basic database setup
- `migrate_advanced_features.py` - Advanced features setup

### Configuration
- `requirements.txt` - Python dependencies
- `setup.sh` - Setup script (Linux/Mac)

---

## 💡 Tips & Best Practices

### For Content Creators

1. **Start Small**
   - Begin with one channel
   - Test with short videos
   - Gradually add features

2. **Use Playlists**
   - Create themed playlists
   - Rotate content automatically
   - Keep viewers engaged

3. **Monitor Analytics**
   - Check peak hours
   - Optimize schedule
   - Track video performance

4. **Automate Everything**
   - Set up schedules
   - Use multi-platform
   - Let system run 24/7

### For Developers

1. **Code Organization**
   - Keep modules separate
   - Follow naming conventions
   - Comment complex logic

2. **Error Handling**
   - Always handle exceptions
   - Provide user feedback
   - Log errors properly

3. **Testing**
   - Test each feature
   - Check edge cases
   - Verify API responses

4. **Performance**
   - Monitor resource usage
   - Optimize database queries
   - Cache when possible

---

## 🎉 Success Stories

### Example 1: Music Channel
- **Before:** Manual streaming 8 hours/day
- **After:** 24/7 automated with playlists
- **Result:** 3x more viewers, zero manual work

### Example 2: Business Channel
- **Before:** YouTube only, manual schedule
- **After:** YouTube + Facebook + Twitch, automated
- **Result:** 5x reach, professional quality

### Example 3: Content Creator
- **Before:** No analytics, guessing best times
- **After:** Data-driven scheduling
- **Result:** 2x engagement, optimized content

---

## 📞 Support

### Getting Help

1. Check this documentation
2. Review troubleshooting section
3. Check GitHub issues
4. Contact support team

### Reporting Bugs

Include:
- Error message
- Steps to reproduce
- System information
- Log files

### Feature Requests

Include:
- Use case description
- Expected behavior
- Benefits
- Priority level

---

## 🎯 What's Next?

### Immediate Steps
1. ✅ Install and setup
2. ✅ Change default password
3. ✅ Add your first video
4. ✅ Create a channel
5. ✅ Start streaming

### Short-term Goals
1. Set up automated schedules
2. Add multiple platforms
3. Create playlists
4. Monitor analytics

### Long-term Vision
1. Scale to multiple channels
2. Optimize based on data
3. Automate everything
4. Grow your audience

---

**Version:** 2.1.0  
**Status:** Production Ready ✅  
**Last Updated:** December 7, 2025  
**Author:** StreamLive Team

**Happy Streaming! 🎥✨**
