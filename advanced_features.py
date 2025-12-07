#!/usr/bin/env python3
"""
Advanced Features Module for StreamLive
Implements: Automated Scheduler, Stream Health Monitoring, Multi-Platform Streaming,
Video Playlist Management, and Advanced Analytics
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time, timedelta
import threading
import time as time_module
import re
import random
from database import db, ScheduledTask, StreamHealth, Playlist, PlaylistItem, PlatformDestination, StreamChannel, VideoLibrary, StreamSession, StreamStats
import psutil
import os

class AutomatedScheduler:
    """Automated task scheduler for starting/stopping streams"""
    
    def __init__(self, stream_manager):
        self.stream_manager = stream_manager
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.load_scheduled_tasks()
    
    def load_scheduled_tasks(self):
        """Load all scheduled tasks from database"""
        tasks = ScheduledTask.query.filter_by(enabled=True).all()
        for task in tasks:
            self.add_task_to_scheduler(task)
    
    def add_task_to_scheduler(self, task):
        """Add a task to APScheduler"""
        try:
            # Parse days of week
            days = task.days_of_week.split(',') if task.days_of_week else ['0','1','2','3','4','5','6']
            days_map = {'0': 'mon', '1': 'tue', '2': 'wed', '3': 'thu', '4': 'fri', '5': 'sat', '6': 'sun'}
            day_of_week = ','.join([days_map[d] for d in days if d in days_map])
            
            # Create cron trigger
            trigger = CronTrigger(
                hour=task.scheduled_time.hour,
                minute=task.scheduled_time.minute,
                day_of_week=day_of_week
            )
            
            # Add job
            job_id = f"task_{task.id}"
            self.scheduler.add_job(
                func=self.execute_task,
                trigger=trigger,
                args=[task.id],
                id=job_id,
                replace_existing=True
            )
            
            print(f"✅ Scheduled task {task.id}: {task.task_type} channel {task.channel_id} at {task.scheduled_time}")
        except Exception as e:
            print(f"❌ Error scheduling task {task.id}: {e}")
    
    def execute_task(self, task_id):
        """Execute a scheduled task"""
        try:
            task = ScheduledTask.query.get(task_id)
            if not task or not task.enabled:
                return
            
            if task.task_type == 'start':
                success, message = self.stream_manager.start_stream(task.channel_id)
            elif task.task_type == 'stop':
                success, message = self.stream_manager.stop_stream(task.channel_id)
            else:
                return
            
            # Update last run
            task.last_run = datetime.utcnow()
            db.session.commit()
            
            self.stream_manager.add_log(
                f"Scheduled task executed: {task.task_type} channel {task.channel_id} - {message}",
                "INFO" if success else "ERROR"
            )
        except Exception as e:
            print(f"❌ Error executing task {task_id}: {e}")
    
    def create_task(self, channel_id, task_type, scheduled_time, days_of_week='0,1,2,3,4,5,6'):
        """Create a new scheduled task"""
        task = ScheduledTask(
            channel_id=channel_id,
            task_type=task_type,
            scheduled_time=scheduled_time,
            days_of_week=days_of_week,
            enabled=True
        )
        db.session.add(task)
        db.session.commit()
        
        self.add_task_to_scheduler(task)
        return task
    
    def remove_task(self, task_id):
        """Remove a scheduled task"""
        try:
            job_id = f"task_{task_id}"
            self.scheduler.remove_job(job_id)
        except:
            pass
        
        task = ScheduledTask.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
    
    def shutdown(self):
        """Shutdown scheduler"""
        self.scheduler.shutdown()


class StreamHealthMonitor:
    """Monitor stream health and performance"""
    
    def __init__(self, stream_manager):
        self.stream_manager = stream_manager
        self.monitoring = {}  # {channel_id: thread}
        self.stop_flags = {}  # {channel_id: stop_event}
    
    def start_monitoring(self, channel_id, session_id):
        """Start monitoring a stream"""
        if channel_id in self.monitoring:
            return
        
        stop_event = threading.Event()
        self.stop_flags[channel_id] = stop_event
        
        thread = threading.Thread(
            target=self._monitor_loop,
            args=(channel_id, session_id, stop_event),
            daemon=True
        )
        thread.start()
        self.monitoring[channel_id] = thread
    
    def stop_monitoring(self, channel_id):
        """Stop monitoring a stream"""
        if channel_id in self.stop_flags:
            self.stop_flags[channel_id].set()
            del self.stop_flags[channel_id]
        if channel_id in self.monitoring:
            del self.monitoring[channel_id]
    
    def _monitor_loop(self, channel_id, session_id, stop_event):
        """Monitoring loop"""
        while not stop_event.is_set():
            try:
                # Get process info
                process = self.stream_manager.processes.get(channel_id)
                if not process:
                    break
                
                # Get system metrics
                try:
                    proc = psutil.Process(process.pid)
                    cpu_usage = proc.cpu_percent(interval=1)
                    memory_usage = proc.memory_percent()
                except:
                    cpu_usage = 0
                    memory_usage = 0
                
                # Parse FFmpeg output for stream stats
                fps, bitrate, dropped_frames = self._parse_ffmpeg_stats(process)
                
                # Determine health status
                status = 'healthy'
                if dropped_frames > 100 or cpu_usage > 90:
                    status = 'critical'
                elif dropped_frames > 50 or cpu_usage > 70:
                    status = 'warning'
                
                # Save health check
                health = StreamHealth(
                    session_id=session_id,
                    fps=fps,
                    bitrate_kbps=bitrate,
                    dropped_frames=dropped_frames,
                    cpu_usage=cpu_usage,
                    memory_usage=memory_usage,
                    status=status
                )
                db.session.add(health)
                db.session.commit()
                
                # Alert if critical
                if status == 'critical':
                    self.stream_manager.add_log(
                        f"⚠️ Stream health critical for channel {channel_id}: CPU {cpu_usage}%, Dropped frames: {dropped_frames}",
                        "WARNING",
                        session_id
                    )
                
                # Wait before next check
                time_module.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error in health monitoring: {e}")
                time_module.sleep(30)
    
    def _parse_ffmpeg_stats(self, process):
        """Parse FFmpeg output for statistics"""
        # This is a simplified version - in production, you'd parse stderr output
        fps = 30.0  # Default
        bitrate = 4000.0  # Default
        dropped_frames = 0
        
        # TODO: Implement actual FFmpeg stats parsing from stderr
        # For now, return defaults
        return fps, bitrate, dropped_frames


class PlaylistManager:
    """Manage video playlists"""
    
    def __init__(self):
        pass
    
    def create_playlist(self, name, description='', playback_mode='sequential'):
        """Create a new playlist"""
        playlist = Playlist(
            name=name,
            description=description,
            playback_mode=playback_mode
        )
        db.session.add(playlist)
        db.session.commit()
        return playlist
    
    def add_video_to_playlist(self, playlist_id, video_id, order_index=None, weight=1):
        """Add a video to playlist"""
        if order_index is None:
            # Get max order index
            max_order = db.session.query(db.func.max(PlaylistItem.order_index))\
                .filter_by(playlist_id=playlist_id).scalar() or 0
            order_index = max_order + 1
        
        item = PlaylistItem(
            playlist_id=playlist_id,
            video_id=video_id,
            order_index=order_index,
            weight=weight
        )
        db.session.add(item)
        db.session.commit()
        return item
    
    def remove_video_from_playlist(self, playlist_id, video_id):
        """Remove a video from playlist"""
        item = PlaylistItem.query.filter_by(
            playlist_id=playlist_id,
            video_id=video_id
        ).first()
        if item:
            db.session.delete(item)
            db.session.commit()
    
    def get_next_video(self, playlist_id, current_video_id=None):
        """Get next video in playlist based on playback mode"""
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return None
        
        items = PlaylistItem.query.filter_by(playlist_id=playlist_id)\
            .order_by(PlaylistItem.order_index).all()
        
        if not items:
            return None
        
        if playlist.playback_mode == 'sequential':
            # Find current video and return next
            if current_video_id:
                for i, item in enumerate(items):
                    if item.video_id == current_video_id:
                        next_index = (i + 1) % len(items)
                        return items[next_index].video
            return items[0].video
        
        elif playlist.playback_mode == 'shuffle':
            # Random selection without immediate repeat
            available = [item for item in items if item.video_id != current_video_id]
            if not available:
                available = items
            return random.choice(available).video
        
        elif playlist.playback_mode == 'random':
            # Weighted random selection
            weights = [item.weight for item in items]
            selected = random.choices(items, weights=weights, k=1)[0]
            return selected.video
        
        return items[0].video
    
    def reorder_playlist(self, playlist_id, video_order):
        """Reorder videos in playlist"""
        for index, video_id in enumerate(video_order):
            item = PlaylistItem.query.filter_by(
                playlist_id=playlist_id,
                video_id=video_id
            ).first()
            if item:
                item.order_index = index
        db.session.commit()


class MultiPlatformStreamer:
    """Handle streaming to multiple platforms simultaneously"""
    
    def __init__(self, stream_manager):
        self.stream_manager = stream_manager
        self.platform_processes = {}  # {channel_id: {platform_id: process}}
    
    def start_multi_platform_stream(self, channel_id):
        """Start streaming to all enabled platforms for a channel"""
        destinations = PlatformDestination.query.filter_by(
            channel_id=channel_id,
            enabled=True
        ).order_by(PlatformDestination.priority.desc()).all()
        
        if not destinations:
            return False, "No platforms configured"
        
        channel = StreamChannel.query.get(channel_id)
        if not channel or not channel.video_path or not os.path.exists(channel.video_path):
            return False, "Video not found"
        
        # Initialize platform processes dict
        if channel_id not in self.platform_processes:
            self.platform_processes[channel_id] = {}
        
        success_count = 0
        for dest in destinations:
            try:
                process = self._start_platform_stream(channel, dest)
                if process:
                    self.platform_processes[channel_id][dest.id] = process
                    success_count += 1
                    self.stream_manager.add_log(
                        f"Started streaming to {dest.platform_name} for channel {channel.name}",
                        "INFO"
                    )
            except Exception as e:
                self.stream_manager.add_log(
                    f"Failed to start {dest.platform_name}: {e}",
                    "ERROR"
                )
        
        if success_count > 0:
            return True, f"Streaming to {success_count} platform(s)"
        return False, "Failed to start any platform streams"
    
    def _start_platform_stream(self, channel, destination):
        """Start stream to a specific platform"""
        import subprocess
        
        rtmp_url = destination.rtmp_url + destination.stream_key
        
        # Build FFmpeg command
        if channel.encoding_mode == 'copy':
            cmd = [
                'ffmpeg',
                '-re',
                '-stream_loop', '-1',
                '-i', channel.video_path,
                '-c:v', 'copy',
                '-c:a', 'copy',
                '-f', 'flv',
                rtmp_url
            ]
        else:
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
                '-r', str(channel.fps),
                '-pix_fmt', 'yuv420p',
                '-g', str(channel.fps * 2),
                '-c:a', 'aac',
                '-b:a', '128k',
                '-ar', '44100',
                '-f', 'flv',
                rtmp_url
            ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        return process
    
    def stop_multi_platform_stream(self, channel_id):
        """Stop all platform streams for a channel"""
        if channel_id not in self.platform_processes:
            return
        
        for platform_id, process in self.platform_processes[channel_id].items():
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        
        del self.platform_processes[channel_id]


class AdvancedAnalytics:
    """Advanced analytics and reporting"""
    
    def __init__(self):
        pass
    
    def get_channel_analytics(self, channel_id, days=30):
        """Get analytics for a specific channel"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        sessions = StreamSession.query.filter(
            StreamSession.channel_id == channel_id,
            StreamSession.start_time >= start_date
        ).all()
        
        total_sessions = len(sessions)
        total_duration = sum([s.duration_seconds or 0 for s in sessions])
        successful = len([s for s in sessions if s.status == 'stopped'])
        failed = len([s for s in sessions if s.status == 'error'])
        
        # Average session duration
        avg_duration = total_duration / total_sessions if total_sessions > 0 else 0
        
        # Uptime percentage
        total_possible_seconds = days * 24 * 3600
        uptime_percentage = (total_duration / total_possible_seconds * 100) if total_possible_seconds > 0 else 0
        
        return {
            'channel_id': channel_id,
            'period_days': days,
            'total_sessions': total_sessions,
            'total_duration_seconds': total_duration,
            'total_duration_formatted': self._format_duration(total_duration),
            'successful_sessions': successful,
            'failed_sessions': failed,
            'success_rate': (successful / total_sessions * 100) if total_sessions > 0 else 0,
            'average_session_duration': avg_duration,
            'uptime_percentage': round(uptime_percentage, 2)
        }
    
    def get_platform_comparison(self, days=30):
        """Compare performance across platforms"""
        # This would require tracking which platform each session used
        # For now, return placeholder
        return {
            'youtube': {'sessions': 0, 'duration': 0},
            'facebook': {'sessions': 0, 'duration': 0},
            'twitch': {'sessions': 0, 'duration': 0}
        }
    
    def get_peak_hours(self, channel_id=None, days=30):
        """Get peak streaming hours"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = StreamSession.query.filter(StreamSession.start_time >= start_date)
        if channel_id:
            query = query.filter_by(channel_id=channel_id)
        
        sessions = query.all()
        
        # Count sessions by hour
        hour_counts = {}
        for session in sessions:
            hour = session.start_time.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Sort by count
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'peak_hours': [{'hour': h, 'sessions': c} for h, c in sorted_hours[:5]],
            'hour_distribution': hour_counts
        }
    
    def get_video_performance(self, days=30):
        """Get performance metrics for videos"""
        videos = VideoLibrary.query.all()
        
        results = []
        for video in videos:
            sessions = StreamSession.query.filter(
                StreamSession.video_file == video.file_path,
                StreamSession.start_time >= datetime.utcnow() - timedelta(days=days)
            ).all()
            
            results.append({
                'video_id': video.id,
                'video_title': video.title,
                'usage_count': len(sessions),
                'total_duration': sum([s.duration_seconds or 0 for s in sessions]),
                'last_used': video.last_used.isoformat() if video.last_used else None
            })
        
        # Sort by usage
        results.sort(key=lambda x: x['usage_count'], reverse=True)
        return results
    
    def _format_duration(self, seconds):
        """Format duration in human readable format"""
        if not seconds:
            return "0s"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        return f"{secs}s"
    
    def export_report(self, report_type, format='json', **kwargs):
        """Export analytics report"""
        if report_type == 'channel':
            data = self.get_channel_analytics(**kwargs)
        elif report_type == 'peak_hours':
            data = self.get_peak_hours(**kwargs)
        elif report_type == 'video_performance':
            data = self.get_video_performance(**kwargs)
        else:
            data = {}
        
        if format == 'json':
            import json
            return json.dumps(data, indent=2)
        elif format == 'csv':
            # TODO: Implement CSV export
            return "CSV export not yet implemented"
        
        return data
