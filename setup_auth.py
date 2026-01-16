#!/usr/bin/env python3
"""
SHOTLIST Campaign Analytics - Authentication Setup
Adds user authentication and calendar functionality to existing database
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
import random

DATABASE = 'shotlist_analytics.db'

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_auth_tables():
    """Create authentication and calendar tables"""
    print("🔐 Setting up authentication system...")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            company_name TEXT,
            role TEXT DEFAULT 'client',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')

    # Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    # Add user_id to campaigns if it doesn't exist
    try:
        cursor.execute('ALTER TABLE campaigns ADD COLUMN user_id INTEGER REFERENCES users(user_id)')
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Create campaign events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaign_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            campaign_id INTEGER,
            event_title TEXT NOT NULL,
            event_description TEXT,
            event_type TEXT NOT NULL,
            event_date DATE NOT NULL,
            event_time TIME,
            duration_minutes INTEGER,
            status TEXT DEFAULT 'scheduled',
            priority TEXT DEFAULT 'medium',
            reminder_enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
        )
    ''')

    # Create activity log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_campaigns_user ON campaigns(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_user ON campaign_events(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_date ON campaign_events(event_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_log(user_id)')

    conn.commit()
    print("✅ Authentication tables created")
    return conn

def create_sample_users(conn):
    """Create sample client users"""
    print("\n👥 Creating sample users...")

    cursor = conn.cursor()

    # Sample users (clients)
    users = [
        ('techstartup', 'demo123', 'contact@techstartup.com', 'Tech Startup A', 'Tech Startup Inc', 'client'),
        ('ecommerce', 'demo123', 'contact@ecommerce.com', 'E-commerce Store B', 'E-commerce Solutions LLC', 'client'),
        ('fashionbrand', 'demo123', 'contact@fashion.com', 'Fashion Brand C', 'Fashion Enterprises', 'client'),
        ('restaurant', 'demo123', 'contact@restaurant.com', 'Restaurant Chain D', 'Restaurant Group', 'client'),
        ('saascompany', 'demo123', 'contact@saas.com', 'SaaS Company E', 'SaaS Innovations', 'client'),
        ('admin', 'admin123', 'admin@shotlist.com', 'SHOTLIST Admin', 'SHOTLIST Agency', 'admin'),
    ]

    user_ids = {}
    for username, password, email, full_name, company, role in users:
        password_hash = hash_password(password)
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, full_name, company_name, role)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, email, full_name, company, role))
            user_ids[username] = cursor.lastrowid
            print(f"  ✓ Created user: {username} ({role})")
        except sqlite3.IntegrityError:
            cursor.execute('SELECT user_id FROM users WHERE username = ?', (username,))
            user_ids[username] = cursor.fetchone()[0]
            print(f"  ⚠ User already exists: {username}")

    conn.commit()
    print(f"✅ Created {len(user_ids)} users")
    return user_ids

def assign_campaigns_to_users(conn, user_ids):
    """Assign existing campaigns to users"""
    print("\n📊 Assigning campaigns to users...")

    cursor = conn.cursor()

    # Get all campaigns
    cursor.execute('SELECT campaign_id, client_name FROM campaigns')
    campaigns = cursor.fetchall()

    # Mapping of client names to usernames
    client_mapping = {
        'Tech Startup A': 'techstartup',
        'E-commerce Store B': 'ecommerce',
        'Fashion Brand C': 'fashionbrand',
        'Restaurant Chain D': 'restaurant',
        'SaaS Company E': 'saascompany',
    }

    for campaign_id, client_name in campaigns:
        username = client_mapping.get(client_name, 'admin')
        user_id = user_ids.get(username, user_ids['admin'])

        cursor.execute('UPDATE campaigns SET user_id = ? WHERE campaign_id = ?', (user_id, campaign_id))
        print(f"  ✓ Assigned campaign {campaign_id} to {username}")

    conn.commit()
    print("✅ Campaigns assigned to users")

def create_calendar_events(conn, user_ids):
    """Create sample calendar events"""
    print("\n📅 Creating calendar events...")

    cursor = conn.cursor()

    # Get campaigns for each user
    cursor.execute('''
        SELECT c.campaign_id, c.user_id, c.campaign_name, c.start_date, c.end_date, c.status
        FROM campaigns c
        WHERE c.user_id IS NOT NULL
    ''')
    campaigns = cursor.fetchall()

    event_types = [
        ('campaign_start', 'Campaign Launch', 0),
        ('campaign_end', 'Campaign End', 0),
        ('milestone', 'Mid-Campaign Review', 15),
        ('meeting', 'Strategy Meeting', 7),
        ('deadline', 'Content Deadline', 5),
    ]

    events_created = 0

    for campaign_id, user_id, campaign_name, start_date, end_date, status in campaigns:
        # Add campaign start event
        cursor.execute('''
            INSERT INTO campaign_events
            (user_id, campaign_id, event_title, event_description, event_type, event_date, event_time, duration_minutes, status, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, campaign_id,
            f"{campaign_name} - Launch",
            f"Campaign kickoff and initial deployment",
            'campaign_start', start_date, '09:00:00', 60,
            'completed' if status == 'completed' else 'scheduled',
            'high'
        ))
        events_created += 1

        # Add campaign end event
        if end_date:
            cursor.execute('''
                INSERT INTO campaign_events
                (user_id, campaign_id, event_title, event_description, event_type, event_date, event_time, duration_minutes, status, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, campaign_id,
                f"{campaign_name} - Completion",
                f"Campaign wrap-up and final review",
                'campaign_end', end_date, '17:00:00', 90,
                'completed' if status == 'completed' else 'scheduled',
                'high'
            ))
            events_created += 1

        # Add milestone events for active campaigns
        if status == 'active':
            # Add upcoming meetings
            for i in range(3):
                days_ahead = 7 * (i + 1)
                event_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')

                cursor.execute('''
                    INSERT INTO campaign_events
                    (user_id, campaign_id, event_title, event_description, event_type, event_date, event_time, duration_minutes, status, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, campaign_id,
                    f"{campaign_name} - Weekly Review",
                    f"Performance review and optimization discussion",
                    'meeting', event_date, '14:00:00', 60,
                    'scheduled', 'medium'
                ))
                events_created += 1

            # Add content deadlines
            for i in range(2):
                days_ahead = 5 + (i * 14)
                event_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')

                cursor.execute('''
                    INSERT INTO campaign_events
                    (user_id, campaign_id, event_title, event_description, event_type, event_date, event_time, duration_minutes, status, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, campaign_id,
                    f"{campaign_name} - Content Delivery",
                    f"Submit content for approval and deployment",
                    'deadline', event_date, '12:00:00', 30,
                    'scheduled', 'high'
                ))
                events_created += 1

    # Add some general events for admin
    admin_id = user_ids.get('admin', 1)
    general_events = [
        ('Monthly Review', 'Team performance review and planning', 'meeting', 7, 'high'),
        ('Client Reports Due', 'Prepare and send monthly client reports', 'deadline', 14, 'high'),
        ('Strategy Planning', 'Q4 strategy planning session', 'meeting', 21, 'medium'),
    ]

    for title, desc, event_type, days_ahead, priority in general_events:
        event_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        cursor.execute('''
            INSERT INTO campaign_events
            (user_id, event_title, event_description, event_type, event_date, event_time, duration_minutes, status, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (admin_id, title, desc, event_type, event_date, '10:00:00', 120, 'scheduled', priority))
        events_created += 1

    conn.commit()
    print(f"✅ Created {events_created} calendar events")

def create_activity_log(conn, user_ids):
    """Create sample activity log entries"""
    print("\n📝 Creating activity log...")

    cursor = conn.cursor()

    actions = [
        'Login',
        'View Dashboard',
        'Export Data',
        'Update Campaign',
        'View Reports',
    ]

    entries_created = 0
    for username, user_id in list(user_ids.items())[:5]:  # For non-admin users
        for _ in range(random.randint(3, 8)):
            action = random.choice(actions)
            days_ago = random.randint(0, 30)
            timestamp = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute('''
                INSERT INTO activity_log (user_id, action, timestamp)
                VALUES (?, ?, ?)
            ''', (user_id, action, timestamp))
            entries_created += 1

    conn.commit()
    print(f"✅ Created {entries_created} activity log entries")

def main():
    """Main setup function"""
    print("🎨 SHOTLIST CAMPAIGN ANALYTICS - AUTHENTICATION SETUP")
    print("=" * 60)

    # Create auth tables
    conn = create_auth_tables()

    # Create sample users
    user_ids = create_sample_users(conn)

    # Assign campaigns to users
    assign_campaigns_to_users(conn, user_ids)

    # Create calendar events
    create_calendar_events(conn, user_ids)

    # Create activity log
    create_activity_log(conn, user_ids)

    # Display login credentials
    print("\n" + "=" * 60)
    print("✅ AUTHENTICATION SETUP COMPLETE!")
    print("=" * 60)
    print("\n🔑 LOGIN CREDENTIALS:")
    print("\nClients:")
    print("  Username: techstartup    | Password: demo123")
    print("  Username: ecommerce      | Password: demo123")
    print("  Username: fashionbrand   | Password: demo123")
    print("  Username: restaurant     | Password: demo123")
    print("  Username: saascompany    | Password: demo123")
    print("\nAdmin:")
    print("  Username: admin          | Password: admin123")
    print("\n" + "=" * 60)

    conn.close()

if __name__ == '__main__':
    main()
