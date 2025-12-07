#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import subprocess
import os
from datetime import datetime, date, timedelta
import pytz
import gdown
import threading
import signal
import psutil
from functools import wraps
from database import db, init_db, StreamSession, StreamLog, Configuration, StreamStats, StreamChannel, VideoLibrary, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'streamlive-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///streaming.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB max upload

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database
init_db(app)

from streaming_service import streaming_service

class StreamManager:
    def __init__(self):
        # Use new streaming service
        self.streaming_service = streaming_service
        self.processes = {}  # Kept for compatibility
        self.running_channels = {}  # Kept for compatibility
        self.log_messages = []
        
    # Config methods removed - all configuration now in database
    
    def add_log(self, message, level='INFO', session_id=None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        if len(self.log_messages) > 100:
            self.log_messages.pop(0)
        print(log_entry)
        
        # Save to database
        try:
            log = StreamLog(
                timestamp=datetime.utcnow(),
                level=level,
                message=message,
                session_id=session_id
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            print(f"Error saving log to DB: {e}")
    

    
    def is_streaming_time(self, channel):
        tz = pytz.timezone(channel.timezone)
        now = datetime.now(tz)
        current_date = now.date()
        current_time = now.time()
        
        # Check date range
        if channel.start_date and current_date < channel.start_date:
            return False
        if channel.end_date and current_date > channel.end_date:
            return False
        
        # Check time range
        start = datetime.strptime(channel.start_time, '%H:%M').time()
        end = datetime.strptime(channel.end_time, '%H:%M').time()
        
        if start <= end:
            return start <= current_time <= end
        else:
            return current_time >= start or current_time <= end
    
    def start_stream(self, channel_id):
        # Use new streaming service with auto-retry
        success, message = self.streaming_service.start_stream(channel_id)
        
        # Update compatibility attributes
        if success:
            self.running_channels = dict(self.streaming_service.running_channels)
            self.processes = dict(self.streaming_service.active_streams)
        
        return success, message
    
    def start_stream_old(self, channel_id):
        # Old implementation (kept as backup)
        channel = StreamChannel.query.get(channel_id)
        if not channel:
            return False, "Channel tidak ditemukan"
        
        if channel_id in self.running_channels:
            return False, f"Stream untuk {channel.name} sudah berjalan"
        
        if not channel.video_path or not os.path.exists(channel.video_path):
            return False, f"Video tidak ditemukan untuk {channel.name}! Pilih video dari library."
        
        # Update video usage stats
        video = VideoLibrary.query.filter_by(file_path=channel.video_path).first()
        if video:
            video.usage_count += 1
            video.last_used = datetime.utcnow()
            db.session.commit()
        
        rtmp_url = channel.rtmp_url + channel.stream_key
        
        # Build FFmpeg command based on encoding mode
        if channel.encoding_mode == 'copy':
            # Copy mode - streaming video asli tanpa re-encode (cepat & hemat CPU)
            cmd = [
                'ffmpeg',
                '-re',
                '-stream_loop', '-1',
                '-i', channel.video_path,
                '-c:v', 'copy',  # Copy video codec
                '-c:a', 'copy',  # Copy audio codec
                '-f', 'flv',
                rtmp_url
            ]
        else:
            # Encode mode - re-encode dengan custom settings
            cmd = [
                'ffmpeg',
                '-re',
                '-stream_loop', '-1',
                '-i', channel.video_path,
                '-c:v', 'libx264',
                '-preset', channel.preset,
                '-b:v', channel.bitrate,
                '-maxrate', channel.bitrate,
                '-bufsize', str(int(channel.bitrate.replace('k', '')) * 2) + 'k',
                '-r', str(channel.fps),  # FPS
                '-pix_fmt', 'yuv420p',
                '-g', str(channel.fps * 2),  # Keyframe interval
                '-c:a', 'aac',
                '-b:a', '128k',
                '-ar', '44100',
                '-f', 'flv',
                rtmp_url
            ]
        
        try:
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Create session in database
            session = StreamSession(
                channel_id=channel_id,
                start_time=datetime.utcnow(),
                video_file=channel.video_path,
                status='started'
            )
            db.session.add(session)
            db.session.commit()
            
            self.processes[channel_id] = process
            self.running_channels[channel_id] = session.id
            
            self.add_log(f"Streaming dimulai untuk {channel.name}!", "INFO", session.id)
            self.update_daily_stats()
            return True, f"Streaming {channel.name} berhasil dimulai"
        except Exception as e:
            self.add_log(f"Error start stream {channel.name}: {e}", "ERROR")
            return False, str(e)
    
    def stop_stream(self, channel_id):
        # Use new streaming service
        success, message = self.streaming_service.stop_stream(channel_id)
        
        # Update compatibility attributes
        self.running_channels = dict(self.streaming_service.running_channels)
        self.processes = dict(self.streaming_service.active_streams)
        
        return success, message
    
    def stop_stream_old(self, channel_id):
        # Old implementation (kept as backup)
        if channel_id not in self.running_channels:
            return False, "Stream tidak berjalan"
        
        channel = StreamChannel.query.get(channel_id)
        process = self.processes.get(channel_id)
        session_id = self.running_channels.get(channel_id)
        
        if process:
            self.add_log(f"Menghentikan streaming {channel.name}...", "INFO", session_id)
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            # Update session in database
            try:
                session = StreamSession.query.get(session_id)
                if session:
                    session.end_time = datetime.utcnow()
                    session.duration_seconds = int((session.end_time - session.start_time).total_seconds())
                    session.status = 'stopped'
                    db.session.commit()
                    self.update_daily_stats()
            except Exception as e:
                print(f"Error updating session: {e}")
            
            del self.processes[channel_id]
            del self.running_channels[channel_id]
            self.add_log(f"Streaming {channel.name} dihentikan", "INFO", session_id)
            return True, f"Streaming {channel.name} berhasil dihentikan"
        return False, "Tidak ada proses streaming"
    
    def stop_all_streams(self):
        """Stop semua streaming yang berjalan"""
        channel_ids = list(self.running_channels.keys())
        for channel_id in channel_ids:
            self.stop_stream(channel_id)
        return True, "Semua streaming dihentikan"
    
    def update_daily_stats(self):
        """Update statistik harian"""
        try:
            today = date.today()
            stats = StreamStats.query.filter_by(date=today).first()
            
            if not stats:
                stats = StreamStats(date=today)
                db.session.add(stats)
            
            # Count sessions for today
            sessions = StreamSession.query.filter(
                db.func.date(StreamSession.start_time) == today
            ).all()
            
            stats.total_sessions = len(sessions)
            stats.successful_streams = len([s for s in sessions if s.status == 'stopped'])
            stats.failed_streams = len([s for s in sessions if s.status == 'error'])
            stats.total_duration_seconds = sum([s.duration_seconds or 0 for s in sessions])
            
            db.session.commit()
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def get_status(self):
        # Sync with streaming service
        self.running_channels = dict(self.streaming_service.running_channels)
        self.processes = dict(self.streaming_service.active_streams)
        
        channels = StreamChannel.query.filter_by(enabled=True).all()
        channel_statuses = []
        
        for channel in channels:
            video_exists = os.path.exists(channel.video_path) if channel.video_path else False
            video_size = 0
            if video_exists:
                video_size = os.path.getsize(channel.video_path) / (1024 * 1024)
            
            # Check if really running (double check)
            is_running = self.streaming_service.is_stream_active(channel.id)
            
            channel_statuses.append({
                "id": channel.id,
                "name": channel.name,
                "running": is_running,
                "video_exists": video_exists,
                "video_size_mb": round(video_size, 2),
                "is_streaming_time": self.is_streaming_time(channel),
                "current_time": datetime.now(pytz.timezone(channel.timezone)).strftime('%H:%M:%S'),
                "schedule": f"{channel.start_time} - {channel.end_time}"
            })
        
        return {
            "channels": channel_statuses,
            "total_running": len(self.streaming_service.active_streams),
            "total_channels": len(channels)
        }

# Global stream manager
stream_manager = StreamManager()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Check if default admin password is still in use
    show_default_credentials = False
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user and check_password_hash(admin_user.password_hash, 'admin123'):
        show_default_credentials = True
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Your account has been deactivated.', 'error')
                return render_template('login.html', show_default_credentials=show_default_credentials)
            
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', show_default_credentials=show_default_credentials)

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

# Admin-only decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({"success": False, "message": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/users', methods=['GET', 'POST'])
@login_required
@admin_required
def api_users():
    """Get all users or create new user (admin only)"""
    if request.method == 'POST':
        data = request.json
        
        # Validate required fields
        if not data.get('username') or not data.get('password'):
            return jsonify({"success": False, "message": "Username and password are required"})
        
        # Check if username already exists
        existing = User.query.filter_by(username=data['username']).first()
        if existing:
            return jsonify({"success": False, "message": "Username already exists"})
        
        # Create new user
        user = User(
            username=data['username'],
            password_hash=generate_password_hash(data['password']),
            email=data.get('email', ''),
            is_admin=data.get('is_admin', False),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": f"User {data['username']} created successfully",
            "user": user.to_dict()
        })
    
    # GET - return all users
    users = User.query.all()
    return jsonify({"users": [u.to_dict() for u in users]})

@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
@admin_required
def api_user(user_id):
    """Get, update, or delete specific user (admin only)"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'DELETE':
        # Prevent deleting yourself
        if user.id == current_user.id:
            return jsonify({"success": False, "message": "Cannot delete your own account"})
        
        # Prevent deleting the last admin
        if user.is_admin:
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count <= 1:
                return jsonify({"success": False, "message": "Cannot delete the last admin user"})
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True, "message": f"User {user.username} deleted"})
    
    if request.method == 'PUT':
        data = request.json
        
        # Update username if provided and not duplicate
        if 'username' in data and data['username'] != user.username:
            existing = User.query.filter_by(username=data['username']).first()
            if existing:
                return jsonify({"success": False, "message": "Username already exists"})
            user.username = data['username']
        
        # Update password if provided
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])
        
        # Update other fields
        if 'email' in data:
            user.email = data['email']
        
        if 'is_active' in data:
            # Prevent deactivating yourself
            if user.id == current_user.id and not data['is_active']:
                return jsonify({"success": False, "message": "Cannot deactivate your own account"})
            user.is_active = data['is_active']
        
        if 'is_admin' in data:
            # Prevent removing admin from yourself
            if user.id == current_user.id and not data['is_admin']:
                return jsonify({"success": False, "message": "Cannot remove admin role from your own account"})
            
            # Prevent removing the last admin
            if user.is_admin and not data['is_admin']:
                admin_count = User.query.filter_by(is_admin=True).count()
                if admin_count <= 1:
                    return jsonify({"success": False, "message": "Cannot remove admin role from the last admin"})
            
            user.is_admin = data['is_admin']
        
        db.session.commit()
        return jsonify({"success": True, "message": "User updated successfully", "user": user.to_dict()})
    
    return jsonify({"user": user.to_dict()})

@app.route('/')
@login_required
def index():
    """Professional admin dashboard"""
    return render_template('admin.html', user=current_user)

@app.route('/simple')
@login_required
def simple():
    """Simple view (old version)"""
    return render_template('index.html', user=current_user)

@app.route('/api/status')
def api_status():
    return jsonify(stream_manager.get_status())

@app.route('/api/logs')
def api_logs():
    # Get from database
    logs = StreamLog.query.order_by(StreamLog.timestamp.desc()).limit(50).all()
    db_logs = [log.to_dict() for log in reversed(logs)]
    return jsonify({"logs": stream_manager.log_messages[-50:], "db_logs": db_logs})



@app.route('/api/channels', methods=['GET', 'POST'])
def api_channels():
    if request.method == 'POST':
        data = request.json
        # Validate video path
        video_path = data.get('video_path', '')
        if not video_path:
            return jsonify({"success": False, "message": "Video path tidak boleh kosong"})
        
        if not os.path.exists(video_path):
            return jsonify({"success": False, "message": "Video file tidak ditemukan"})
        
        # Parse dates
        start_date = None
        end_date = None
        if data.get('start_date'):
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except:
                pass
        if data.get('end_date'):
            try:
                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            except:
                pass
        
        # Validate dates
        if start_date and end_date and start_date > end_date:
            return jsonify({"success": False, "message": "Tanggal mulai tidak boleh lebih besar dari tanggal selesai"})
        
        channel = StreamChannel(
            name=data['name'],
            stream_key=data['stream_key'],
            rtmp_url=data.get('rtmp_url', 'rtmp://a.rtmp.youtube.com/live2/'),
            video_path=video_path,
            start_date=start_date,
            end_date=end_date,
            start_time=data.get('start_time', '08:00'),
            end_time=data.get('end_time', '20:00'),
            timezone=data.get('timezone', 'Asia/Jakarta'),
            encoding_mode=data.get('encoding_mode', 'copy'),
            bitrate=data.get('bitrate', '4000k'),
            fps=data.get('fps', 30),
            preset=data.get('preset', 'veryfast'),
            enabled=data.get('enabled', True)
        )
        db.session.add(channel)
        db.session.commit()
        return jsonify({"success": True, "message": "Channel ditambahkan", "channel": channel.to_dict()})
    
    channels = StreamChannel.query.all()
    return jsonify({"channels": [c.to_dict() for c in channels]})

@app.route('/api/channels/<int:channel_id>', methods=['GET', 'PUT', 'DELETE'])
def api_channel(channel_id):
    channel = StreamChannel.query.get_or_404(channel_id)
    
    if request.method == 'DELETE':
        if channel_id in stream_manager.running_channels:
            return jsonify({"success": False, "message": "Stop streaming dulu!"})
        db.session.delete(channel)
        db.session.commit()
        return jsonify({"success": True, "message": "Channel dihapus"})
    
    if request.method == 'PUT':
        data = request.json
        for key, value in data.items():
            if hasattr(channel, key):
                setattr(channel, key, value)
        db.session.commit()
        return jsonify({"success": True, "message": "Channel diupdate", "channel": channel.to_dict()})
    
    return jsonify({"channel": channel.to_dict()})



@app.route('/api/start/<int:channel_id>', methods=['POST'])
def api_start(channel_id):
    success, message = stream_manager.start_stream(channel_id)
    return jsonify({"success": success, "message": message})

@app.route('/api/stop/<int:channel_id>', methods=['POST'])
def api_stop(channel_id):
    success, message = stream_manager.stop_stream(channel_id)
    return jsonify({"success": success, "message": message})

@app.route('/api/stop-all', methods=['POST'])
def api_stop_all():
    success, message = stream_manager.stop_all_streams()
    return jsonify({"success": success, "message": message})

def get_video_metadata(file_path):
    """Get video metadata using ffprobe"""
    metadata = {
        'duration_seconds': 0,
        'resolution': None,
        'file_size_mb': 0
    }
    
    try:
        if os.path.exists(file_path):
            metadata['file_size_mb'] = os.path.getsize(file_path) / (1024 * 1024)
            
            result = subprocess.run([
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-show_entries', 'stream=width,height',
                '-of', 'json',
                file_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                import json as json_lib
                data = json_lib.loads(result.stdout)
                if 'format' in data and 'duration' in data['format']:
                    metadata['duration_seconds'] = int(float(data['format']['duration']))
                if 'streams' in data and len(data['streams']) > 0:
                    stream = data['streams'][0]
                    if 'width' in stream and 'height' in stream:
                        metadata['resolution'] = f"{stream['width']}x{stream['height']}"
    except Exception as e:
        print(f"Error getting video metadata: {e}")
    
    return metadata

@app.route('/api/videos', methods=['GET', 'POST'])
def api_videos():
    """Get all videos or add new video"""
    if request.method == 'POST':
        data = request.json
        
        # Check if video already exists
        existing = VideoLibrary.query.filter_by(filename=data['filename']).first()
        if existing:
            return jsonify({"success": False, "message": "Video dengan filename ini sudah ada"})
        
        video = VideoLibrary(
            title=data['title'],
            filename=data['filename'],
            file_path=data['file_path'],
            gdrive_file_id=data.get('gdrive_file_id', ''),
            source=data.get('source', 'manual')
        )
        
        # Get file metadata
        metadata = get_video_metadata(data['file_path'])
        video.file_size_mb = metadata['file_size_mb']
        video.duration_seconds = metadata['duration_seconds']
        video.resolution = metadata['resolution']
        
        db.session.add(video)
        db.session.commit()
        return jsonify({"success": True, "message": "Video ditambahkan ke library", "video": video.to_dict()})
    
    # GET - return all videos
    videos = VideoLibrary.query.order_by(VideoLibrary.created_at.desc()).all()
    return jsonify({"videos": [v.to_dict() for v in videos]})

@app.route('/api/videos/<int:video_id>', methods=['GET', 'PUT', 'DELETE'])
def api_video(video_id):
    """Get, update, or delete specific video"""
    video = VideoLibrary.query.get_or_404(video_id)
    
    if request.method == 'DELETE':
        # Check if video is being used by any channel
        channels_using = StreamChannel.query.filter_by(video_path=video.file_path).all()
        if channels_using:
            channel_names = [c.name for c in channels_using]
            return jsonify({
                "success": False, 
                "message": f"Video digunakan oleh channel: {', '.join(channel_names)}"
            })
        
        # Delete file if exists
        if os.path.exists(video.file_path):
            try:
                os.remove(video.file_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
        
        db.session.delete(video)
        db.session.commit()
        return jsonify({"success": True, "message": "Video dihapus dari library"})
    
    if request.method == 'PUT':
        data = request.json
        for key, value in data.items():
            if hasattr(video, key) and key not in ['id', 'created_at']:
                setattr(video, key, value)
        db.session.commit()
        return jsonify({"success": True, "message": "Video diupdate", "video": video.to_dict()})
    
    return jsonify({"video": video.to_dict()})

@app.route('/api/videos/upload', methods=['POST'])
def api_video_upload():
    """Upload video file"""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No file provided"}), 400
        
        file = request.files['file']
        title = request.form.get('title', 'Untitled Video')
        
        if file.filename == '':
            return jsonify({"success": False, "message": "No file selected"}), 400
        
        # Create videos directory if not exists
        os.makedirs('./videos', exist_ok=True)
        
        # Generate safe filename
        import re
        safe_filename = re.sub(r'[^\w\s.-]', '', file.filename)
        safe_filename = safe_filename.replace(' ', '_')
        
        # Check if filename already exists
        counter = 1
        original_filename = safe_filename
        while os.path.exists(f"./videos/{safe_filename}"):
            name, ext = os.path.splitext(original_filename)
            safe_filename = f"{name}_{counter}{ext}"
            counter += 1
        
        file_path = f"./videos/{safe_filename}"
        
        # Save file
        file.save(file_path)
        stream_manager.add_log(f"Video uploaded: {safe_filename}", "INFO")
        
        # Add to library
        video = VideoLibrary(
            title=title,
            filename=safe_filename,
            file_path=file_path,
            source='upload'
        )
        
        # Get metadata
        metadata = get_video_metadata(file_path)
        video.file_size_mb = metadata['file_size_mb']
        video.duration_seconds = metadata['duration_seconds']
        video.resolution = metadata['resolution']
        
        db.session.add(video)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": f"Video berhasil diupload: {safe_filename}",
            "video": video.to_dict()
        })
    except Exception as e:
        stream_manager.add_log(f"Error upload video: {e}", "ERROR")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/videos/scan', methods=['POST'])
def api_video_scan():
    """Scan ./videos folder and add unregistered videos to library"""
    try:
        videos_dir = './videos'
        if not os.path.exists(videos_dir):
            os.makedirs(videos_dir)
            return jsonify({"success": True, "message": "Folder videos dibuat", "found": 0, "added": 0})
        
        # Video extensions
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm', '.m4v']
        
        found_files = []
        for filename in os.listdir(videos_dir):
            file_path = os.path.join(videos_dir, filename)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(filename)
                if ext.lower() in video_extensions:
                    found_files.append((filename, file_path))
        
        added_count = 0
        for filename, file_path in found_files:
            # Check if already in library
            existing = VideoLibrary.query.filter_by(filename=filename).first()
            if not existing:
                # Add to library
                video = VideoLibrary(
                    title=filename.rsplit('.', 1)[0],  # Remove extension
                    filename=filename,
                    file_path=file_path,
                    source='scan'
                )
                
                # Get metadata
                metadata = get_video_metadata(file_path)
                video.file_size_mb = metadata['file_size_mb']
                video.duration_seconds = metadata['duration_seconds']
                video.resolution = metadata['resolution']
                
                db.session.add(video)
                added_count += 1
        
        db.session.commit()
        stream_manager.add_log(f"Scan completed: {len(found_files)} found, {added_count} added", "INFO")
        
        return jsonify({
            "success": True,
            "message": "Scan selesai",
            "found": len(found_files),
            "added": added_count
        })
    except Exception as e:
        stream_manager.add_log(f"Error scanning videos: {e}", "ERROR")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/videos/download-gdrive', methods=['POST'])
def api_video_download_gdrive():
    """Download video from Google Drive to library"""
    data = request.json
    
    def download_thread():
        try:
            # Create videos directory if not exists
            os.makedirs('./videos', exist_ok=True)
            
            filename = data.get('filename', f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
            file_path = f"./videos/{filename}"
            
            stream_manager.add_log(f"Downloading {data['title']} dari Google Drive...", "INFO")
            
            url = f"https://drive.google.com/uc?id={data['gdrive_file_id']}"
            gdown.download(url, file_path, quiet=False)
            
            # Add to library
            video = VideoLibrary(
                title=data['title'],
                filename=filename,
                file_path=file_path,
                gdrive_file_id=data['gdrive_file_id'],
                source='gdrive'
            )
            
            # Get metadata
            metadata = get_video_metadata(file_path)
            video.file_size_mb = metadata['file_size_mb']
            video.duration_seconds = metadata['duration_seconds']
            video.resolution = metadata['resolution']
            
            db.session.add(video)
            db.session.commit()
            
            stream_manager.add_log(f"Download selesai: {data['title']}", "INFO")
        except Exception as e:
            stream_manager.add_log(f"Error download: {e}", "ERROR")
    
    thread = threading.Thread(target=download_thread)
    thread.start()
    return jsonify({"success": True, "message": "Download dimulai"})



@app.route('/api/history')
def api_history():
    """Get streaming history"""
    limit = request.args.get('limit', 20, type=int)
    sessions = StreamSession.query.order_by(StreamSession.start_time.desc()).limit(limit).all()
    return jsonify({"sessions": [s.to_dict() for s in sessions]})

@app.route('/api/stats')
def api_stats():
    """Get statistics"""
    days = request.args.get('days', 7, type=int)
    stats = StreamStats.query.order_by(StreamStats.date.desc()).limit(days).all()
    
    # Overall stats
    total_sessions = StreamSession.query.count()
    total_duration = db.session.query(db.func.sum(StreamSession.duration_seconds)).scalar() or 0
    
    return jsonify({
        "daily_stats": [s.to_dict() for s in reversed(stats)],
        "total_sessions": total_sessions,
        "total_duration_seconds": total_duration
    })

@app.route('/api/system/metrics')
def api_system_metrics():
    """Get system metrics (CPU, Memory, Disk)"""
    try:
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory Usage
        memory = psutil.virtual_memory()
        memory_total = memory.total / (1024 ** 3)  # GB
        memory_used = memory.used / (1024 ** 3)    # GB
        memory_percent = memory.percent
        
        # Disk Usage
        disk = psutil.disk_usage('/')
        disk_total = disk.total / (1024 ** 3)  # GB
        disk_used = disk.used / (1024 ** 3)    # GB
        disk_percent = disk.percent
        
        # Network (optional)
        net_io = psutil.net_io_counters()
        
        return jsonify({
            "success": True,
            "cpu": {
                "percent": round(cpu_percent, 1),
                "count": cpu_count,
                "per_cpu": psutil.cpu_percent(interval=0.1, percpu=True)
            },
            "memory": {
                "total_gb": round(memory_total, 2),
                "used_gb": round(memory_used, 2),
                "available_gb": round(memory.available / (1024 ** 3), 2),
                "percent": round(memory_percent, 1)
            },
            "disk": {
                "total_gb": round(disk_total, 2),
                "used_gb": round(disk_used, 2),
                "free_gb": round(disk.free / (1024 ** 3), 2),
                "percent": round(disk_percent, 1)
            },
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ===================================
# ADVANCED FEATURES API ROUTES
# ===================================

# Import advanced features
from advanced_features import (
    AutomatedScheduler, StreamHealthMonitor, PlaylistManager,
    MultiPlatformStreamer, AdvancedAnalytics
)
from database import Playlist, PlaylistItem, ScheduledTask, PlatformDestination, StreamHealth

# Initialize advanced features
automated_scheduler = None
health_monitor = None
playlist_manager = PlaylistManager()
multi_platform = None
analytics = AdvancedAnalytics()

def init_advanced_features():
    """Initialize advanced features after app starts"""
    global automated_scheduler, health_monitor, multi_platform
    automated_scheduler = AutomatedScheduler(stream_manager)
    health_monitor = StreamHealthMonitor(stream_manager)
    multi_platform = MultiPlatformStreamer(stream_manager)

# --- Playlist Management ---
@app.route('/api/playlists', methods=['GET', 'POST'])
@login_required
def api_playlists():
    """Get all playlists or create new one"""
    if request.method == 'POST':
        data = request.json
        playlist = playlist_manager.create_playlist(
            name=data['name'],
            description=data.get('description', ''),
            playback_mode=data.get('playback_mode', 'sequential')
        )
        return jsonify({"success": True, "playlist": playlist.to_dict()})
    
    playlists = Playlist.query.all()
    return jsonify({"playlists": [p.to_dict() for p in playlists]})

@app.route('/api/playlists/<int:playlist_id>', methods=['GET', 'DELETE'])
@login_required
def api_playlist(playlist_id):
    """Get or delete specific playlist"""
    playlist = Playlist.query.get_or_404(playlist_id)
    
    if request.method == 'DELETE':
        db.session.delete(playlist)
        db.session.commit()
        return jsonify({"success": True, "message": "Playlist deleted"})
    
    items = PlaylistItem.query.filter_by(playlist_id=playlist_id)\
        .order_by(PlaylistItem.order_index).all()
    
    return jsonify({
        "playlist": playlist.to_dict(),
        "items": [item.to_dict() for item in items]
    })

@app.route('/api/playlists/<int:playlist_id>/videos', methods=['POST', 'DELETE'])
@login_required
def api_playlist_videos(playlist_id):
    """Add or remove video from playlist"""
    if request.method == 'POST':
        data = request.json
        item = playlist_manager.add_video_to_playlist(
            playlist_id=playlist_id,
            video_id=data['video_id'],
            weight=data.get('weight', 1)
        )
        return jsonify({"success": True, "item": item.to_dict()})
    
    if request.method == 'DELETE':
        data = request.json
        playlist_manager.remove_video_from_playlist(playlist_id, data['video_id'])
        return jsonify({"success": True, "message": "Video removed from playlist"})

# --- Scheduled Tasks ---
@app.route('/api/scheduled-tasks', methods=['GET', 'POST'])
@login_required
def api_scheduled_tasks():
    """Get all scheduled tasks or create new one"""
    if request.method == 'POST':
        data = request.json
        from datetime import time as dt_time
        scheduled_time = dt_time.fromisoformat(data['scheduled_time'])
        
        task = automated_scheduler.create_task(
            channel_id=data['channel_id'],
            task_type=data['task_type'],
            scheduled_time=scheduled_time,
            days_of_week=data.get('days_of_week', '0,1,2,3,4,5,6')
        )
        return jsonify({"success": True, "task": task.to_dict()})
    
    tasks = ScheduledTask.query.all()
    return jsonify({"tasks": [t.to_dict() for t in tasks]})

@app.route('/api/scheduled-tasks/<int:task_id>', methods=['DELETE'])
@login_required
def api_scheduled_task(task_id):
    """Delete scheduled task"""
    automated_scheduler.remove_task(task_id)
    return jsonify({"success": True, "message": "Task deleted"})

# --- Platform Destinations ---
@app.route('/api/platforms', methods=['GET', 'POST'])
@login_required
def api_platforms():
    """Get all platform destinations or create new one"""
    if request.method == 'POST':
        data = request.json
        platform = PlatformDestination(
            channel_id=data['channel_id'],
            platform_name=data['platform_name'],
            rtmp_url=data['rtmp_url'],
            stream_key=data['stream_key'],
            enabled=data.get('enabled', True),
            priority=data.get('priority', 0)
        )
        db.session.add(platform)
        db.session.commit()
        return jsonify({"success": True, "platform": platform.to_dict()})
    
    channel_id = request.args.get('channel_id', type=int)
    query = PlatformDestination.query
    if channel_id:
        query = query.filter_by(channel_id=channel_id)
    
    platforms = query.all()
    return jsonify({"platforms": [p.to_dict() for p in platforms]})

@app.route('/api/platforms/<int:platform_id>', methods=['DELETE'])
@login_required
def api_platform(platform_id):
    """Delete platform destination"""
    platform = PlatformDestination.query.get_or_404(platform_id)
    db.session.delete(platform)
    db.session.commit()
    return jsonify({"success": True, "message": "Platform deleted"})

# --- Stream Health ---
@app.route('/api/health/<int:session_id>')
@login_required
def api_stream_health(session_id):
    """Get health metrics for a session"""
    health_checks = StreamHealth.query.filter_by(session_id=session_id)\
        .order_by(StreamHealth.timestamp.desc()).limit(50).all()
    
    return jsonify({
        "health_checks": [h.to_dict() for h in health_checks]
    })

# --- Analytics ---
@app.route('/api/analytics/channel/<int:channel_id>')
@login_required
def api_channel_analytics(channel_id):
    """Get analytics for a channel"""
    days = request.args.get('days', 30, type=int)
    data = analytics.get_channel_analytics(channel_id, days)
    return jsonify(data)

@app.route('/api/analytics/peak-hours')
@login_required
def api_peak_hours():
    """Get peak streaming hours"""
    channel_id = request.args.get('channel_id', type=int)
    days = request.args.get('days', 30, type=int)
    data = analytics.get_peak_hours(channel_id, days)
    return jsonify(data)

@app.route('/api/analytics/video-performance')
@login_required
def api_video_performance():
    """Get video performance metrics"""
    days = request.args.get('days', 30, type=int)
    data = analytics.get_video_performance(days)
    return jsonify(data)

@app.route('/api/analytics/export')
@login_required
def api_export_analytics():
    """Export analytics report"""
    report_type = request.args.get('type', 'channel')
    format_type = request.args.get('format', 'json')
    channel_id = request.args.get('channel_id', type=int)
    days = request.args.get('days', 30, type=int)
    
    kwargs = {'days': days}
    if channel_id:
        kwargs['channel_id'] = channel_id
    
    data = analytics.export_report(report_type, format_type, **kwargs)
    
    if format_type == 'json':
        return jsonify({"data": data})
    else:
        return data

def signal_handler(sig, frame):
    print("\nShutting down...")
    if automated_scheduler:
        automated_scheduler.shutdown()
    stream_manager.stop_all_streams()
    os._exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("🎥 StreamLive - Advanced Streaming Platform")
    print("=" * 60)
    print("\n✨ Features Enabled:")
    print("  ✅ User Authentication & Management")
    print("  ✅ Video Library Management")
    print("  ✅ Channel Management")
    print("  ✅ Automated Scheduler")
    print("  ✅ Stream Health Monitoring")
    print("  ✅ Multi-Platform Streaming")
    print("  ✅ Video Playlist Management")
    print("  ✅ Advanced Analytics Dashboard")
    print("\n🌐 Access:")
    print("  Local:   http://localhost:5000")
    print("  Network: http://YOUR_SERVER_IP:5000")
    print("\n⚙️  Initializing advanced features...")
    
    # Initialize advanced features
    with app.app_context():
        init_advanced_features()
        print("  ✅ Automated Scheduler started")
        print("  ✅ Health Monitor ready")
        print("  ✅ Multi-Platform Streamer ready")
        print("  ✅ Analytics Engine ready")
    
    print("\n🚀 Server starting...")
    print("Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
