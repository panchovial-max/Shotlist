#!/usr/bin/env python3
"""
Initialize SQLite database for SHOTLIST Campaign Analytics
"""

import sqlite3
import os
import hashlib
import uuid
from datetime import datetime, timedelta

# Database file path
DATABASE = 'shotlist_analytics.db'

def create_database():
    """Create and initialize the database"""
    # Remove existing database if it exists
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    
    # Create a new database connection
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Users table with OAuth support
    cursor.execute('''
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            full_name TEXT,
            password TEXT,
            role TEXT DEFAULT 'client',
            provider TEXT DEFAULT 'email',
            oauth_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # Sessions table
    cursor.execute('''
        CREATE TABLE sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    # OAuth states table for CSRF protection
    cursor.execute('''
        CREATE TABLE oauth_states (
            state TEXT PRIMARY KEY,
            provider TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Login attempts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success INTEGER DEFAULT 0,
            ip_address TEXT,
            user_agent TEXT
        )
    ''')

    # Social Media Accounts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS social_media_accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            username TEXT NOT NULL,
            account_email TEXT,
            access_token TEXT,
            refresh_token TEXT,
            token_expires_at TIMESTAMP,
            is_connected INTEGER DEFAULT 1,
            connection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_sync TIMESTAMP,
            sync_frequency TEXT DEFAULT 'daily',
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(user_id, platform, username)
        )
    ''')

    # Social Media Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS social_media_settings (
            setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            auto_post INTEGER DEFAULT 0,
            auto_schedule INTEGER DEFAULT 0,
            analytics_enabled INTEGER DEFAULT 1,
            notifications_enabled INTEGER DEFAULT 1,
            sync_followers INTEGER DEFAULT 1,
            sync_engagement INTEGER DEFAULT 1,
            sync_analytics INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(user_id)
        )
    ''')

    # Social Media Audit table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS social_media_audit (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            status TEXT,
            details TEXT,
            FOREIGN KEY (account_id) REFERENCES social_media_accounts(account_id)
        )
    ''')

    # Social Media Daily Metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS social_media_daily_metrics (
            metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            date DATE NOT NULL,
            followers INTEGER DEFAULT 0,
            engagement_rate REAL DEFAULT 0,
            reach INTEGER DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            saves INTEGER DEFAULT 0,
            video_views INTEGER DEFAULT 0,
            profile_visits INTEGER DEFAULT 0,
            mentions INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES social_media_accounts(account_id),
            UNIQUE(account_id, platform, date)
        )
    ''')

    # Content Performance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS content_performance (
            content_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            post_id TEXT NOT NULL,
            post_type TEXT,
            caption TEXT,
            hashtags TEXT,
            posted_at TIMESTAMP,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            saves INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0,
            reach INTEGER DEFAULT 0,
            engagement_rate REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES social_media_accounts(account_id),
            UNIQUE(account_id, platform, post_id)
        )
    ''')

    # Audience Demographics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audience_demographics (
            demographic_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            date DATE NOT NULL,
            age_13_17 REAL DEFAULT 0,
            age_18_24 REAL DEFAULT 0,
            age_25_34 REAL DEFAULT 0,
            age_35_44 REAL DEFAULT 0,
            age_45_54 REAL DEFAULT 0,
            age_55_64 REAL DEFAULT 0,
            age_65_plus REAL DEFAULT 0,
            male_percentage REAL DEFAULT 0,
            female_percentage REAL DEFAULT 0,
            top_countries TEXT,
            top_cities TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES social_media_accounts(account_id)
        )
    ''')

    # Campaign Social Metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaign_social_metrics (
            campaign_metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            campaign_id TEXT,
            platform TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            total_reach INTEGER DEFAULT 0,
            total_impressions INTEGER DEFAULT 0,
            total_engagement INTEGER DEFAULT 0,
            engagement_rate REAL DEFAULT 0,
            conversion_rate REAL DEFAULT 0,
            cost_per_engagement REAL DEFAULT 0,
            cost_per_reach REAL DEFAULT 0,
            revenue_generated REAL DEFAULT 0,
            roi REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES social_media_accounts(account_id)
        )
    ''')

    # Figma Sync Configuration table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS figma_sync_config (
            config_id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            last_sync TIMESTAMP,
            sync_direction TEXT CHECK(sync_direction IN ('export', 'import', 'config')),
            node_count INTEGER DEFAULT 0,
            settings TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(file_path)
        )
    ''')

    # Create default admin user
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute('''
        INSERT INTO users 
        (email, full_name, password, role, provider) 
        VALUES (?, ?, ?, ?, ?)
    ''', (
        'admin@shotlist.com', 
        'Admin User', 
        admin_password, 
        'admin', 
        'email'
    ))

    # Create sample client users
    sample_users = [
        ('techstartup@example.com', 'Tech Startup Client', 'demo123', 'client'),
        ('ecommerce@example.com', 'E-commerce Client', 'demo123', 'client'),
        ('fashionbrand@example.com', 'Fashion Brand Client', 'demo123', 'client'),
        ('restaurant@example.com', 'Restaurant Client', 'demo123', 'client'),
        ('saascompany@example.com', 'SaaS Company Client', 'demo123', 'client')
    ]

    for email, full_name, password, role in sample_users:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users 
            (email, full_name, password, role, provider) 
            VALUES (?, ?, ?, ?, ?)
        ''', (email, full_name, hashed_password, role, 'email'))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"✅ Database {DATABASE} created successfully!")
    print(f"👤 Default users created:")
    print(f"   - admin@shotlist.com (admin)")
    for user in sample_users:
        print(f"   - {user[0]} (client)")

def main():
    create_database()

if __name__ == '__main__':
    main()
