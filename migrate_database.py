#!/usr/bin/env python3
"""
Database Migration Script
Menambahkan kolom baru ke tabel yang sudah ada
"""
import sqlite3
import os

def migrate_database():
    db_path = 'streaming.db'
    
    if not os.path.exists(db_path):
        print("Database belum ada, tidak perlu migrasi")
        return
    
    print("Starting database migration...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check existing columns in stream_channels
        cursor.execute("PRAGMA table_info(stream_channels)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Add new columns if they don't exist
        migrations = []
        
        if 'start_date' not in existing_columns:
            migrations.append("ALTER TABLE stream_channels ADD COLUMN start_date DATE")
        
        if 'end_date' not in existing_columns:
            migrations.append("ALTER TABLE stream_channels ADD COLUMN end_date DATE")
        
        if 'encoding_mode' not in existing_columns:
            migrations.append("ALTER TABLE stream_channels ADD COLUMN encoding_mode VARCHAR(20) DEFAULT 'copy'")
        
        if 'fps' not in existing_columns:
            migrations.append("ALTER TABLE stream_channels ADD COLUMN fps INTEGER DEFAULT 30")
        
        if 'preset' not in existing_columns:
            migrations.append("ALTER TABLE stream_channels ADD COLUMN preset VARCHAR(20) DEFAULT 'veryfast'")
        
        # Execute migrations
        for migration in migrations:
            print(f"Executing: {migration}")
            cursor.execute(migration)
        
        conn.commit()
        print(f"✅ Migration completed! Added {len(migrations)} new columns")
        
        # Show updated schema
        cursor.execute("PRAGMA table_info(stream_channels)")
        columns = cursor.fetchall()
        print("\nUpdated schema:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
