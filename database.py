#!/usr/bin/env python3
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()

class StreamChannel(db.Model):
    """Model untuk menyimpan channel streaming"""
    __tablename__ = 'stream_channels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    stream_key = db.Column(db.String(255), nullable=False)
    rtmp_url = db.Column(db.String(255), default='rtmp://a.rtmp.youtube.com/live2/')
    gdrive_file_id = db.Column(db.String(255))
    video_path = db.Column(db.String(255))
    start_time = db.Column(db.String(10), default='08:00')
    end_time = db.Column(db.String(10), default='20:00')
    start_date = db.Column(db.Date, nullable=True)  # Tanggal mulai campaign
    end_date = db.Column(db.Date, nullable=True)    # Tanggal selesai campaign
    timezone = db.Column(db.String(50), default='Asia/Jakarta')
    
    # Advanced settings
    encoding_mode = db.Column(db.String(20), default='copy')  # copy, encode
    bitrate = db.Column(db.String(20), default='4000k')
    fps = db.Column(db.Integer, default=30)
    preset = db.Column(db.String(20), default='veryfast')  # ultrafast, veryfast, fast, medium
    
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'stream_key': self.stream_key,
            'rtmp_url': self.rtmp_url,
            'gdrive_file_id': self.gdrive_file_id,
            'video_path': self.video_path,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'timezone': self.timezone,
            'encoding_mode': self.encoding_mode,
            'bitrate': self.bitrate,
            'fps': self.fps,
            'preset': self.preset,
            'enabled': self.enabled
        }

class StreamSession(db.Model):
    """Model untuk menyimpan history streaming session"""
    __tablename__ = 'stream_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('stream_channels.id'), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, default=0)
    video_file = db.Column(db.String(255))
    status = db.Column(db.String(50))  # started, stopped, error
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    channel = db.relationship('StreamChannel', backref='sessions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'channel_name': self.channel.name if self.channel else 'Unknown',
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'duration_formatted': self.format_duration(),
            'video_file': self.video_file,
            'status': self.status,
            'error_message': self.error_message
        }
    
    def format_duration(self):
        if not self.duration_seconds:
            return "0s"
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

class StreamLog(db.Model):
    """Model untuk menyimpan logs"""
    __tablename__ = 'stream_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    level = db.Column(db.String(20), default='INFO')  # INFO, WARNING, ERROR
    message = db.Column(db.Text, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('stream_sessions.id'), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'message': self.message,
            'session_id': self.session_id
        }

class Configuration(db.Model):
    """Model untuk menyimpan konfigurasi"""
    __tablename__ = 'configurations'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'updated_at': self.updated_at.isoformat()
        }

class VideoLibrary(db.Model):
    """Model untuk menyimpan video library"""
    __tablename__ = 'video_library'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size_mb = db.Column(db.Float, default=0)
    duration_seconds = db.Column(db.Integer, default=0)
    resolution = db.Column(db.String(20))  # 1920x1080, 1280x720, etc
    gdrive_file_id = db.Column(db.String(255))
    source = db.Column(db.String(50))  # gdrive, upload, url
    thumbnail_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    usage_count = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size_mb': round(self.file_size_mb, 2),
            'duration_seconds': self.duration_seconds,
            'duration_formatted': self.format_duration(),
            'resolution': self.resolution,
            'gdrive_file_id': self.gdrive_file_id,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count
        }
    
    def format_duration(self):
        if not self.duration_seconds:
            return "Unknown"
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

class User(db.Model):
    """Model untuk user authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    # Flask-Login required methods
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

class StreamStats(db.Model):
    """Model untuk statistik streaming"""
    __tablename__ = 'stream_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    total_sessions = db.Column(db.Integer, default=0)
    total_duration_seconds = db.Column(db.Integer, default=0)
    successful_streams = db.Column(db.Integer, default=0)
    failed_streams = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'total_sessions': self.total_sessions,
            'total_duration_seconds': self.total_duration_seconds,
            'total_duration_formatted': self.format_duration(),
            'successful_streams': self.successful_streams,
            'failed_streams': self.failed_streams
        }
    
    def format_duration(self):
        if not self.total_duration_seconds:
            return "0s"
        hours = self.total_duration_seconds // 3600
        minutes = (self.total_duration_seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

class Playlist(db.Model):
    """Model untuk video playlist"""
    __tablename__ = 'playlists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    playback_mode = db.Column(db.String(20), default='sequential')  # sequential, shuffle, random
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'playback_mode': self.playback_mode,
            'video_count': len(self.items),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PlaylistItem(db.Model):
    """Model untuk item dalam playlist"""
    __tablename__ = 'playlist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video_library.id'), nullable=False)
    order_index = db.Column(db.Integer, default=0)
    weight = db.Column(db.Integer, default=1)  # For weighted random selection
    
    playlist = db.relationship('Playlist', backref='items')
    video = db.relationship('VideoLibrary')
    
    def to_dict(self):
        return {
            'id': self.id,
            'playlist_id': self.playlist_id,
            'video_id': self.video_id,
            'video': self.video.to_dict() if self.video else None,
            'order_index': self.order_index,
            'weight': self.weight
        }

class StreamHealth(db.Model):
    """Model untuk monitoring stream health"""
    __tablename__ = 'stream_health'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('stream_sessions.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    fps = db.Column(db.Float)
    bitrate_kbps = db.Column(db.Float)
    dropped_frames = db.Column(db.Integer, default=0)
    cpu_usage = db.Column(db.Float)
    memory_usage = db.Column(db.Float)
    status = db.Column(db.String(20), default='healthy')  # healthy, warning, critical
    
    session = db.relationship('StreamSession', backref='health_checks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'fps': self.fps,
            'bitrate_kbps': self.bitrate_kbps,
            'dropped_frames': self.dropped_frames,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'status': self.status
        }

class ScheduledTask(db.Model):
    """Model untuk automated scheduler"""
    __tablename__ = 'scheduled_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('stream_channels.id'), nullable=False)
    task_type = db.Column(db.String(20), nullable=False)  # start, stop
    scheduled_time = db.Column(db.Time, nullable=False)
    days_of_week = db.Column(db.String(50))  # 0,1,2,3,4,5,6 (Mon-Sun)
    enabled = db.Column(db.Boolean, default=True)
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    
    channel = db.relationship('StreamChannel', backref='scheduled_tasks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'channel_name': self.channel.name if self.channel else 'Unknown',
            'task_type': self.task_type,
            'scheduled_time': self.scheduled_time.strftime('%H:%M') if self.scheduled_time else None,
            'days_of_week': self.days_of_week,
            'enabled': self.enabled,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None
        }

class PlatformDestination(db.Model):
    """Model untuk multi-platform streaming destinations"""
    __tablename__ = 'platform_destinations'
    
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('stream_channels.id'), nullable=False)
    platform_name = db.Column(db.String(50), nullable=False)  # youtube, facebook, twitch, custom
    rtmp_url = db.Column(db.String(255), nullable=False)
    stream_key = db.Column(db.String(255), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=0)  # Higher priority streams first
    
    channel = db.relationship('StreamChannel', backref='destinations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'platform_name': self.platform_name,
            'rtmp_url': self.rtmp_url,
            'stream_key': '***' + self.stream_key[-4:] if self.stream_key else '',  # Masked
            'enabled': self.enabled,
            'priority': self.priority
        }

def init_db(app):
    """Initialize database"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("Database initialized!")
        
        # Create default admin user if not exists
        from werkzeug.security import generate_password_hash
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                email='admin@streamlive.local',
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created!")
            print("Username: admin")
            print("Password: admin123")
            print("⚠️  PLEASE CHANGE THE PASSWORD AFTER FIRST LOGIN!")
