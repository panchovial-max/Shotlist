"""
Unified Social Media Integration for SHOTLIST
Supports: Instagram, Facebook, Twitter, LinkedIn, TikTok, YouTube, Snapchat
"""

import requests
import json
import os
import sqlite3
from datetime import datetime, timedelta
import logging
import hashlib
import hmac

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialMediaAPI:
    """Unified API for multiple social media platforms"""
    
    # Platform configurations
    PLATFORMS = {
        'instagram': {
            'base_url': 'https://graph.instagram.com/v18.0',
            'auth_url': 'https://api.instagram.com/oauth/authorize',
            'token_url': 'https://graph.instagram.com/v18.0/oauth/access_token',
            'scopes': ['user_profile', 'user_media'],
            'rate_limit': 200,  # per hour
        },
        'facebook': {
            'base_url': 'https://graph.facebook.com/v18.0',
            'auth_url': 'https://www.facebook.com/v18.0/dialog/oauth',
            'token_url': 'https://graph.facebook.com/v18.0/oauth/access_token',
            'scopes': ['pages_read_engagement', 'pages_read_user_content'],
            'rate_limit': 200,
        },
        'twitter': {
            'base_url': 'https://api.twitter.com/2',
            'auth_url': 'https://twitter.com/i/oauth2/authorize',
            'token_url': 'https://twitter.com/2/oauth2/token',
            'scopes': ['tweet.read', 'users.read'],
            'rate_limit': 450,  # per 15 minutes
        },
        'linkedin': {
            'base_url': 'https://api.linkedin.com/v2',
            'auth_url': 'https://www.linkedin.com/oauth/v2/authorization',
            'token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
            'scopes': ['r_liteprofile', 'r_basicprofile'],
            'rate_limit': 10000,  # per day
        },
        'tiktok': {
            'base_url': 'https://open-api.tiktok.com/v1',
            'auth_url': 'https://www.tiktok.com/oauth/authorize',
            'token_url': 'https://open-api.tiktok.com/oauth/token',
            'scopes': ['user.info.basic', 'video.list'],
            'rate_limit': 200,
        },
        'youtube': {
            'base_url': 'https://www.googleapis.com/youtube/v3',
            'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
            'token_url': 'https://oauth2.googleapis.com/token',
            'scopes': ['https://www.googleapis.com/auth/youtube.readonly'],
            'rate_limit': 10000,  # per day
        },
    }
    
    def __init__(self, platform, access_token):
        """Initialize with platform and access token"""
        self.platform = platform.lower()
        self.access_token = access_token
        
        if self.platform not in self.PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")
        
        self.config = self.PLATFORMS[self.platform]
        self.base_url = self.config['base_url']
    
    def get_user_info(self):
        """Get user profile information"""
        try:
            if self.platform == 'instagram':
                return self._get_instagram_user()
            elif self.platform == 'facebook':
                return self._get_facebook_user()
            elif self.platform == 'twitter':
                return self._get_twitter_user()
            elif self.platform == 'linkedin':
                return self._get_linkedin_user()
            elif self.platform == 'tiktok':
                return self._get_tiktok_user()
            elif self.platform == 'youtube':
                return self._get_youtube_user()
        except Exception as e:
            logger.error(f"Failed to get {self.platform} user info: {e}")
            return None
    
    def _get_instagram_user(self):
        """Get Instagram user info"""
        url = f"{self.base_url}/me"
        params = {
            'fields': 'id,username,name,biography,website,profile_picture_url,followers_count,media_count',
            'access_token': self.access_token
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def _get_facebook_user(self):
        """Get Facebook user info"""
        url = f"{self.base_url}/me"
        params = {
            'fields': 'id,name,email,picture,pages',
            'access_token': self.access_token
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def _get_twitter_user(self):
        """Get Twitter user info"""
        url = f"{self.base_url}/users/me"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        params = {
            'user.fields': 'created_at,description,followers_count,public_metrics,verified'
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get('data', {})
    
    def _get_linkedin_user(self):
        """Get LinkedIn user info"""
        url = f"{self.base_url}/me"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def _get_tiktok_user(self):
        """Get TikTok user info"""
        url = f"{self.base_url}/user/info"
        params = {
            'access_token': self.access_token,
            'fields': 'open_id,union_id,display_name,avatar,bio_description,follower_count,following_count,video_count,heart_count'
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('data', {})
    
    def _get_youtube_user(self):
        """Get YouTube channel info"""
        url = f"{self.base_url}/channels"
        params = {
            'part': 'snippet,statistics',
            'mine': True,
            'access_token': self.access_token
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json().get('items', [])
        return data[0] if data else {}
    
    def get_metrics(self):
        """Get platform-specific metrics"""
        try:
            if self.platform == 'instagram':
                return self._get_instagram_metrics()
            elif self.platform == 'facebook':
                return self._get_facebook_metrics()
            elif self.platform == 'twitter':
                return self._get_twitter_metrics()
            elif self.platform == 'linkedin':
                return self._get_linkedin_metrics()
            elif self.platform == 'tiktok':
                return self._get_tiktok_metrics()
            elif self.platform == 'youtube':
                return self._get_youtube_metrics()
        except Exception as e:
            logger.error(f"Failed to get {self.platform} metrics: {e}")
            return {}
    
    def _get_instagram_metrics(self):
        """Get Instagram metrics"""
        user_info = self.get_user_info()
        if not user_info:
            return {}
        
        return {
            'followers': user_info.get('followers_count', 0),
            'following': user_info.get('following_count', 0),
            'posts': user_info.get('media_count', 0),
            'engagement_rate': self._calculate_engagement(),
            'reach': 0,
            'impressions': 0,
            'platform': 'instagram'
        }
    
    def _get_facebook_metrics(self):
        """Get Facebook metrics"""
        user_info = self.get_user_info()
        if not user_info:
            return {}
        
        return {
            'followers': 0,
            'pages': len(user_info.get('pages', [])),
            'engagement_rate': 0,
            'reach': 0,
            'impressions': 0,
            'platform': 'facebook'
        }
    
    def _get_twitter_metrics(self):
        """Get Twitter metrics"""
        user_info = self.get_user_info()
        if not user_info:
            return {}
        
        metrics = user_info.get('public_metrics', {})
        return {
            'followers': metrics.get('followers_count', 0),
            'following': metrics.get('following_count', 0),
            'tweets': metrics.get('tweet_count', 0),
            'engagement_rate': 0,
            'reach': metrics.get('impression_count', 0),
            'platform': 'twitter'
        }
    
    def _get_linkedin_metrics(self):
        """Get LinkedIn metrics"""
        user_info = self.get_user_info()
        if not user_info:
            return {}
        
        return {
            'followers': user_info.get('followerCount', 0),
            'connections': user_info.get('connectionCount', 0),
            'engagement_rate': 0,
            'reach': 0,
            'platform': 'linkedin'
        }
    
    def _get_tiktok_metrics(self):
        """Get TikTok metrics"""
        user_info = self.get_user_info()
        if not user_info:
            return {}
        
        return {
            'followers': user_info.get('follower_count', 0),
            'following': user_info.get('following_count', 0),
            'videos': user_info.get('video_count', 0),
            'likes': user_info.get('heart_count', 0),
            'engagement_rate': 0,
            'platform': 'tiktok'
        }
    
    def _get_youtube_metrics(self):
        """Get YouTube metrics"""
        user_info = self.get_user_info()
        if not user_info:
            return {}
        
        stats = user_info.get('statistics', {})
        return {
            'subscribers': stats.get('subscriberCount', 0),
            'videos': stats.get('videoCount', 0),
            'views': stats.get('viewCount', 0),
            'engagement_rate': 0,
            'platform': 'youtube'
        }
    
    def _calculate_engagement(self):
        """Calculate engagement rate"""
        # Placeholder - implement based on actual metrics
        return 0.0


class SocialMediaDatabase:
    """Database operations for social media integration"""
    
    def __init__(self, db_path="shotlist_analytics.db"):
        """Initialize database"""
        self.db_path = db_path
        self.create_tables()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def create_tables(self):
        """Create social media tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Social media accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_media_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                platform_id TEXT,
                username TEXT,
                access_token TEXT,
                refresh_token TEXT,
                token_expires_at TIMESTAMP,
                connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_sync TIMESTAMP,
                sync_status TEXT DEFAULT 'pending',
                UNIQUE(user_id, platform),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Social media metrics cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_media_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                followers INTEGER,
                following INTEGER,
                posts INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0,
                reach INTEGER DEFAULT 0,
                impressions INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES social_media_accounts(id)
            )
        ''')
        
        # Social media content performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_media_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                content_id TEXT UNIQUE,
                content_type TEXT,
                caption TEXT,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                reach INTEGER DEFAULT 0,
                impressions INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0,
                posted_at TIMESTAMP,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES social_media_accounts(id)
            )
        ''')
        
        # Daily analytics summary
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_media_daily_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                date DATE,
                followers_added INTEGER DEFAULT 0,
                posts_count INTEGER DEFAULT 0,
                total_engagement INTEGER DEFAULT 0,
                total_reach INTEGER DEFAULT 0,
                top_content TEXT,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(account_id, date),
                FOREIGN KEY (account_id) REFERENCES social_media_accounts(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def connect_account(self, user_id, platform, platform_data):
        """Connect social media account"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO social_media_accounts
                (user_id, platform, platform_id, username, access_token, last_sync, sync_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                platform,
                platform_data.get('id') or platform_data.get('platform_id'),
                platform_data.get('username') or platform_data.get('name'),
                platform_data.get('access_token'),
                datetime.now().isoformat(),
                'completed'
            ))
            
            conn.commit()
            account_id = cursor.lastrowid
            conn.close()
            return account_id
        except Exception as e:
            logger.error(f"Failed to connect account: {e}")
            return None
    
    def save_metrics(self, account_id, platform, metrics):
        """Save metrics for account"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO social_media_metrics
                (account_id, platform, followers, following, posts, engagement_rate, reach, impressions, likes, comments, shares)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                account_id,
                platform,
                metrics.get('followers', 0),
                metrics.get('following', 0),
                metrics.get('posts', 0),
                metrics.get('engagement_rate', 0),
                metrics.get('reach', 0),
                metrics.get('impressions', 0),
                metrics.get('likes', 0),
                metrics.get('comments', 0),
                metrics.get('shares', 0)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
            return False
    
    def get_user_accounts(self, user_id):
        """Get all social media accounts for user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, platform, username, last_sync, sync_status
                FROM social_media_accounts
                WHERE user_id = ?
                ORDER BY connected_at DESC
            ''', (user_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            accounts = []
            for row in results:
                accounts.append({
                    'id': row[0],
                    'platform': row[1],
                    'username': row[2],
                    'last_sync': row[3],
                    'sync_status': row[4]
                })
            
            return accounts
        except Exception as e:
            logger.error(f"Failed to get user accounts: {e}")
            return []
    
    def get_latest_metrics(self, user_id, platform=None):
        """Get latest metrics for user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if platform:
                cursor.execute('''
                    SELECT m.* FROM social_media_metrics m
                    JOIN social_media_accounts a ON m.account_id = a.id
                    WHERE a.user_id = ? AND m.platform = ?
                    ORDER BY m.saved_at DESC
                    LIMIT 1
                ''', (user_id, platform))
            else:
                cursor.execute('''
                    SELECT m.* FROM social_media_metrics m
                    JOIN social_media_accounts a ON m.account_id = a.id
                    WHERE a.user_id = ?
                    ORDER BY m.saved_at DESC
                ''', (user_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            metrics_list = []
            for row in results:
                metrics_list.append({
                    'platform': row[3],
                    'followers': row[4],
                    'following': row[5],
                    'posts': row[6],
                    'engagement_rate': row[7],
                    'reach': row[8],
                    'impressions': row[9],
                    'likes': row[10],
                    'comments': row[11],
                    'shares': row[12],
                    'synced_at': row[13]
                })
            
            return metrics_list
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return []
    
    def get_dashboard_summary(self, user_id):
        """Get all platforms summary for dashboard"""
        try:
            accounts = self.get_user_accounts(user_id)
            all_metrics = self.get_latest_metrics(user_id)
            
            summary = {
                'total_accounts': len(accounts),
                'platforms': {},
                'total_followers': 0,
                'total_reach': 0,
                'total_engagement': 0
            }
            
            for metric in all_metrics:
                platform = metric.get('platform')
                summary['platforms'][platform] = metric
                summary['total_followers'] += metric.get('followers', 0)
                summary['total_reach'] += metric.get('reach', 0)
                summary['total_engagement'] += metric.get('engagement_rate', 0)
            
            return summary
        except Exception as e:
            logger.error(f"Failed to get dashboard summary: {e}")
            return {}


if __name__ == "__main__":
    db = SocialMediaDatabase()
    print("✅ Social media integration module loaded")
    print(f"📱 Supported platforms: {', '.join(SocialMediaAPI.PLATFORMS.keys())}")
