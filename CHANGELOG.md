# Changelog

## Version 2.1.0 - Advanced Features (2025-12-07)

### 🚀 Major Features Added

#### 1. Automated Scheduler ⏰
- Background task scheduler using APScheduler
- Cron-like scheduling with day-of-week selection
- Automatic start/stop of streams
- Database-persisted tasks
- API endpoints for task management

#### 2. Stream Health Monitoring 🏥
- Real-time health metrics tracking
- FPS, bitrate, and dropped frames monitoring
- CPU and memory usage tracking
- Health status levels (healthy/warning/critical)
- Automatic alerts on critical status
- 30-second monitoring intervals

#### 3. Multi-Platform Streaming 📡
- Simultaneous streaming to multiple platforms
- Support for YouTube, Facebook, Twitch
- Custom RTMP server support
- Platform priority system
- Independent process management

#### 4. Video Playlist Management 🎬
- Create and manage video playlists
- Multiple playback modes (sequential, shuffle, random)
- Weighted random selection
- Video ordering and reordering
- Playlist-to-channel assignment

#### 5. Advanced Analytics Dashboard 📊
- Channel performance analytics
- Peak hours analysis
- Video performance tracking
- Success rate calculations
- Uptime percentage
- Export functionality (JSON/CSV)

### 📦 New Database Tables
- `playlists` - Video playlist definitions
- `playlist_items` - Videos in playlists
- `stream_health` - Health monitoring data
- `scheduled_tasks` - Automated scheduler tasks
- `platform_destinations` - Multi-platform streaming configs

### 🔌 New API Endpoints (15)
- Playlist management (5 endpoints)
- Scheduled tasks (3 endpoints)
- Platform destinations (3 endpoints)
- Health monitoring (1 endpoint)
- Analytics (4 endpoints)

### 📚 Documentation Added
- `ADVANCED_FEATURES_GUIDE.md` - Comprehensive feature guide
- `QUICK_START_ADVANCED.md` - Quick start guide
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details

### 🔧 Files Added/Modified
- **New:** `advanced_features.py` (500+ lines)
- **New:** `migrate_advanced_features.py`
- **Modified:** `database.py` (5 new models)
- **Modified:** `app.py` (15+ new routes)

---

## Version 2.0.0 - Video Library & Multiple Streaming

### ✨ New Features
- **Video Library Management**: Kelola semua video di satu tempat
  - Upload video manual atau download dari Google Drive
  - Auto-detect video metadata (duration, resolution, file size)
  - Track usage statistics per video
  - Prevent deletion jika video sedang digunakan

- **Multiple Streaming Support**: Stream ke banyak channel sekaligus
  - Setiap channel punya konfigurasi independent
  - Start/stop individual per channel
  - Monitor semua channel dalam 1 dashboard

- **Database Integration**: SQLite database untuk persistent storage
  - Video library dengan metadata lengkap
  - Channel configurations
  - Streaming sessions history
  - Logs dengan level (INFO, WARNING, ERROR)
  - Daily statistics

### 🔧 Improvements
- Simplified channel creation (pilih video dari library)
- Better error handling dan validation
- Real-time status updates
- Usage tracking per video
- Cleaner UI dengan modal dialogs

### 🗑️ Removed
- Per-channel Google Drive download (sekarang via Video Library)
- Single stream limitation
- File-based configuration (sekarang database)

## Version 1.0.0 - Initial Release

### Features
- Basic YouTube live streaming
- Google Drive integration
- Schedule-based streaming
- Web interface
- CLI version
- Single channel support
