#!/usr/bin/env python3
"""
Migration script for advanced features
Adds new tables: playlists, playlist_items, stream_health, scheduled_tasks, platform_destinations
"""

from app import app
from database import db

def migrate():
    """Run migration"""
    with app.app_context():
        print("🔄 Starting migration for advanced features...")
        
        try:
            # Create all new tables
            db.create_all()
            print("✅ All tables created successfully!")
            
            print("\n📋 New tables added:")
            print("  - playlists")
            print("  - playlist_items")
            print("  - stream_health")
            print("  - scheduled_tasks")
            print("  - platform_destinations")
            
            print("\n✨ Migration completed successfully!")
            print("\n🚀 New features available:")
            print("  1. Automated Scheduler")
            print("  2. Stream Health Monitoring")
            print("  3. Multi-Platform Streaming")
            print("  4. Video Playlist Management")
            print("  5. Advanced Analytics Dashboard")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == '__main__':
    migrate()
