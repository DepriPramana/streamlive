#!/usr/bin/env python3
"""
Robust Streaming Service with Auto-Retry and Better Error Handling
Based on Node.js streaming service
"""

import subprocess
import threading
import time
import os
import signal
from datetime import datetime
from database import db, StreamChannel, StreamSession, StreamLog, VideoLibrary

class StreamingService:
    def __init__(self):
        self.active_streams = {}  # {channel_id: process}
        self.running_channels = {}  # {channel_id: session_id}
        self.stream_logs = {}  # {channel_id: [logs]}
        self.stream_retry_count = {}  # {channel_id: retry_count}
        self.manually_stopping = set()  # Set of channel_ids being manually stopped
        self.MAX_RETRY_ATTEMPTS = 3
        self.MAX_LOG_LINES = 100
        self.monitor_threads = {}  # {channel_id: thread}
        
    def add_stream_log(self, channel_id, message, level='INFO'):
        """Add log entry for stream"""
        if channel_id not in self.stream_logs:
            self.stream_logs[channel_id] = []
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'level': level
        }
        
        self.stream_logs[channel_id].append(log_entry)
        
        # Keep only last MAX_LOG_LINES
        if len(self.stream_logs[channel_id]) > self.MAX_LOG_LINES:
            self.stream_logs[channel_id].pop(0)
        
        # Also save to database
        try:
            session_id = self.running_channels.get(channel_id)
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
    
    def build_ffmpeg_command(self, channel):
        """Build FFmpeg command with reconnection parameters"""
        rtmp_url = channel.rtmp_url + channel.stream_key
        
        # Base command with reconnection logic
        base_args = [
            'ffmpeg',
            '-loglevel', 'error',
            '-re',
            '-stream_loop', '-1',
            '-i', channel.video_path,
        ]
        
        # Encoding settings
        if channel.encoding_mode == 'copy':
            encoding_args = [
                '-c:v', 'copy',
                '-c:a', 'copy',
            ]
        else:
            bitrate_num = int(channel.bitrate.replace('k', ''))
            encoding_args = [
                '-c:v', 'libx264',
                '-preset', channel.preset,
                '-b:v', channel.bitrate,
                '-maxrate', f'{int(bitrate_num * 1.5)}k',
                '-bufsize', f'{bitrate_num * 2}k',
                '-r', str(channel.fps),
                '-pix_fmt', 'yuv420p',
                '-g', str(channel.fps * 2),
                '-c:a', 'aac',
                '-b:a', '128k',
                '-ar', '44100',
            ]
        
        # Output settings with reconnection
        output_args = [
            '-f', 'flv',
            '-reconnect', '1',
            '-reconnect_streamed', '1',
            '-reconnect_delay_max', '5',
            rtmp_url
        ]
        
        return base_args + encoding_args + output_args
    
    def monitor_stream(self, channel_id, process):
        """Monitor stream process and handle errors"""
        channel = StreamChannel.query.get(channel_id)
        
        while True:
            # Check if process is still running
            poll = process.poll()
            
            if poll is not None:
                # Process ended
                print(f"[StreamingService] Stream {channel_id} ended with code {poll}")
                self.add_stream_log(channel_id, f"Stream ended with code {poll}", 'WARNING')
                
                # Check if manually stopped
                if channel_id in self.manually_stopping:
                    self.add_stream_log(channel_id, "Stream was manually stopped", 'INFO')
                    self.manually_stopping.discard(channel_id)
                    self.cleanup_stream(channel_id)
                    break
                
                # Auto-retry logic
                retry_count = self.stream_retry_count.get(channel_id, 0)
                
                if retry_count < self.MAX_RETRY_ATTEMPTS:
                    self.stream_retry_count[channel_id] = retry_count + 1
                    self.add_stream_log(
                        channel_id,
                        f"FFmpeg crashed. Attempting restart #{retry_count + 1}",
                        'WARNING'
                    )
                    
                    # Wait before retry
                    time.sleep(5)
                    
                    # Retry
                    try:
                        self.cleanup_stream(channel_id, keep_session=True)
                        success, message = self.start_stream(channel_id)
                        
                        if success:
                            self.add_stream_log(channel_id, "Stream restarted successfully", 'INFO')
                        else:
                            self.add_stream_log(channel_id, f"Failed to restart: {message}", 'ERROR')
                            self.cleanup_stream(channel_id)
                    except Exception as e:
                        self.add_stream_log(channel_id, f"Error during restart: {e}", 'ERROR')
                        self.cleanup_stream(channel_id)
                else:
                    self.add_stream_log(
                        channel_id,
                        f"Maximum retry attempts ({self.MAX_RETRY_ATTEMPTS}) reached",
                        'ERROR'
                    )
                    self.cleanup_stream(channel_id)
                
                break
            
            # Sleep before next check
            time.sleep(2)
    
    def start_stream(self, channel_id):
        """Start streaming with auto-retry support"""
        try:
            # Reset retry count
            self.stream_retry_count[channel_id] = 0
            
            # Check if already streaming
            if channel_id in self.active_streams:
                return False, "Stream is already active"
            
            # Get channel
            channel = StreamChannel.query.get(channel_id)
            if not channel:
                return False, "Channel not found"
            
            # Check video exists
            if not channel.video_path or not os.path.exists(channel.video_path):
                return False, "Video file not found"
            
            # Build FFmpeg command
            cmd = self.build_ffmpeg_command(channel)
            
            self.add_stream_log(channel_id, f"Starting stream: {' '.join(cmd)}", 'INFO')
            
            # Start FFmpeg process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            # Create session
            session = StreamSession(
                channel_id=channel_id,
                start_time=datetime.utcnow(),
                video_file=channel.video_path,
                status='started'
            )
            db.session.add(session)
            db.session.commit()
            
            # Store process and session
            self.active_streams[channel_id] = process
            self.running_channels[channel_id] = session.id
            
            # Start monitoring thread
            monitor_thread = threading.Thread(
                target=self.monitor_stream,
                args=(channel_id, process),
                daemon=True
            )
            monitor_thread.start()
            self.monitor_threads[channel_id] = monitor_thread
            
            self.add_stream_log(channel_id, f"Stream started successfully for {channel.name}", 'INFO')
            
            return True, f"Streaming {channel.name} started successfully"
            
        except Exception as e:
            self.add_stream_log(channel_id, f"Error starting stream: {e}", 'ERROR')
            return False, str(e)
    
    def stop_stream(self, channel_id):
        """Stop streaming"""
        try:
            if channel_id not in self.active_streams:
                return False, "Stream is not active"
            
            self.add_stream_log(channel_id, "Stopping stream...", 'INFO')
            
            # Mark as manually stopping
            self.manually_stopping.add(channel_id)
            
            # Get process
            process = self.active_streams.get(channel_id)
            
            if process:
                try:
                    # Send SIGTERM
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    else:
                        process.terminate()
                    
                    # Wait for process to end
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # Force kill if not terminated
                        if os.name != 'nt':
                            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                        else:
                            process.kill()
                except Exception as e:
                    self.add_stream_log(channel_id, f"Error killing process: {e}", 'ERROR')
            
            # Cleanup
            self.cleanup_stream(channel_id)
            
            self.add_stream_log(channel_id, "Stream stopped successfully", 'INFO')
            
            return True, "Stream stopped successfully"
            
        except Exception as e:
            self.manually_stopping.discard(channel_id)
            self.add_stream_log(channel_id, f"Error stopping stream: {e}", 'ERROR')
            return False, str(e)
    
    def cleanup_stream(self, channel_id, keep_session=False):
        """Cleanup stream resources"""
        try:
            # Remove from active streams
            if channel_id in self.active_streams:
                del self.active_streams[channel_id]
            
            # Update session
            if not keep_session and channel_id in self.running_channels:
                session_id = self.running_channels[channel_id]
                session = StreamSession.query.get(session_id)
                
                if session:
                    session.end_time = datetime.utcnow()
                    session.duration_seconds = int((session.end_time - session.start_time).total_seconds())
                    session.status = 'stopped'
                    db.session.commit()
                
                del self.running_channels[channel_id]
            
            # Remove from manually stopping set
            self.manually_stopping.discard(channel_id)
            
        except Exception as e:
            print(f"Error cleaning up stream {channel_id}: {e}")
    
    def stop_all_streams(self):
        """Stop all active streams"""
        channel_ids = list(self.active_streams.keys())
        for channel_id in channel_ids:
            self.stop_stream(channel_id)
        return True, "All streams stopped"
    
    def get_stream_logs(self, channel_id):
        """Get logs for a stream"""
        return self.stream_logs.get(channel_id, [])
    
    def is_stream_active(self, channel_id):
        """Check if stream is active"""
        return channel_id in self.active_streams
    
    def get_active_streams(self):
        """Get list of active stream IDs"""
        return list(self.active_streams.keys())

# Global instance
streaming_service = StreamingService()
