#!/usr/bin/env python3
"""
Social Media Configuration Management for SHOTLIST Campaign Analytics
Handles configuration of social media accounts, credentials, and user settings
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class SocialMediaConfig:
    """Manages social media user configurations and account settings"""
    
    def __init__(self, database='shotlist_analytics.db'):
        self.database = database
        self._init_tables()
    
    def _get_connection(self):
        """Create database connection"""
        conn = sqlite3.connect(self.database)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_tables(self):
        """Initialize social media configuration tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
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
        
        # Social Media Credentials Audit table
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
        
        conn.commit()
        conn.close()
    
    def add_social_account(self, user_id: int, platform: str, username: str, 
                          account_email: str, access_token: str, 
                          refresh_token: Optional[str] = None) -> Dict:
        """Add a new social media account for a user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO social_media_accounts 
                (user_id, platform, username, account_email, access_token, refresh_token, last_sync)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, platform.lower(), username, account_email, access_token, refresh_token))
            
            account_id = cursor.lastrowid
            conn.commit()
            
            # Log the action
            self._audit_log(account_id, 'ACCOUNT_ADDED', 'success', 
                          f'Added {platform} account: {username}')
            
            conn.close()
            
            return {
                'success': True,
                'account_id': account_id,
                'message': f'Successfully added {platform} account'
            }
        except sqlite3.IntegrityError:
            return {
                'success': False,
                'error': 'Account already exists for this user on this platform',
                'error_code': 'DUPLICATE_ACCOUNT'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'DATABASE_ERROR'
            }
    
    def get_user_accounts(self, user_id: int) -> Dict:
        """Get all social media accounts for a user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT account_id, platform, username, account_email, 
                       is_connected, connection_date, last_sync, sync_frequency
                FROM social_media_accounts
                WHERE user_id = ?
                ORDER BY platform
            ''', (user_id,))
            
            accounts = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return {
                'success': True,
                'accounts': accounts,
                'count': len(accounts)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'DATABASE_ERROR'
            }
    
    def update_account_settings(self, user_id: int, settings: Dict) -> Dict:
        """Update social media settings for a user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if settings exist
            cursor.execute('SELECT setting_id FROM social_media_settings WHERE user_id = ?', (user_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing settings
                update_fields = []
                update_values = []
                
                for key, value in settings.items():
                    if key in ['auto_post', 'auto_schedule', 'analytics_enabled', 
                              'notifications_enabled', 'sync_followers', 'sync_engagement', 'sync_analytics']:
                        update_fields.append(f'{key} = ?')
                        update_values.append(value)
                
                if update_fields:
                    update_values.append(user_id)
                    query = f"UPDATE social_media_settings SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?"
                    cursor.execute(query, update_values)
            else:
                # Insert new settings
                cursor.execute('''
                    INSERT INTO social_media_settings 
                    (user_id, auto_post, auto_schedule, analytics_enabled, 
                     notifications_enabled, sync_followers, sync_engagement, sync_analytics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    settings.get('auto_post', 0),
                    settings.get('auto_schedule', 0),
                    settings.get('analytics_enabled', 1),
                    settings.get('notifications_enabled', 1),
                    settings.get('sync_followers', 1),
                    settings.get('sync_engagement', 1),
                    settings.get('sync_analytics', 1)
                ))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Settings updated successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'DATABASE_ERROR'
            }
    
    def disconnect_account(self, account_id: int) -> Dict:
        """Disconnect a social media account"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE social_media_accounts
                SET is_connected = 0, access_token = NULL, refresh_token = NULL
                WHERE account_id = ?
            ''', (account_id,))
            
            conn.commit()
            
            # Log the action
            self._audit_log(account_id, 'ACCOUNT_DISCONNECTED', 'success', 'Account disconnected')
            
            conn.close()
            
            return {
                'success': True,
                'message': 'Account disconnected successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'DATABASE_ERROR'
            }
    
    def _audit_log(self, account_id: int, action: str, status: str, details: str, ip_address: str = None):
        """Log account actions for audit trail"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO social_media_audit 
                (account_id, action, status, details, ip_address)
                VALUES (?, ?, ?, ?, ?)
            ''', (account_id, action, status, details, ip_address))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging audit: {e}")
    
    def get_account_audit_log(self, account_id: int, limit: int = 50) -> Dict:
        """Get audit log for a specific account"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT audit_id, action, timestamp, status, details
                FROM social_media_audit
                WHERE account_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (account_id, limit))
            
            logs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return {
                'success': True,
                'logs': logs,
                'count': len(logs)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'DATABASE_ERROR'
            }


if __name__ == '__main__':
    print("🔧 Social Media Configuration Manager")
    print("=" * 50)
    
    # Initialize configuration manager
    config = SocialMediaConfig()
    
    # Test adding an account
    result = config.add_social_account(
        user_id=2,
        platform='instagram',
        username='techstartup_official',
        account_email='instagram@techstartup.com',
        access_token='test_token_123',
        refresh_token='test_refresh_token'
    )
    print(f"Add Account: {result}")
    
    # Get user accounts
    result = config.get_user_accounts(2)
    print(f"\nUser Accounts: {result}")
    
    # Update settings
    result = config.update_account_settings(2, {
        'auto_post': 1,
        'analytics_enabled': 1,
        'sync_followers': 1
    })
    print(f"\nUpdate Settings: {result}")

