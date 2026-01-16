"""
Instagram API Integration for SHOTLIST
Handles Instagram account linking and metrics fetching
"""

import requests
import json
import os
import sqlite3
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramAPI:
    """Instagram Graph API wrapper"""
    
    # Instagram Graph API Base URL
    BASE_URL = "https://graph.instagram.com/v18.0"
    
    # Instagram API Configuration (set via environment variables)
    APP_ID = os.getenv("INSTAGRAM_APP_ID", "YOUR_APP_ID")
    APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET", "YOUR_APP_SECRET")
    REDIRECT_URI = os.getenv("INSTAGRAM_REDIRECT_URI", "http://localhost:8000/oauth/callback/instagram")
    
    # Rate limiting
    RATE_LIMIT = 200  # requests per hour
    CACHE_TTL = 1800  # 30 minutes in seconds
    
    def __init__(self, access_token):
        """Initialize with access token"""
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}"
        }
    
    @staticmethod
    def get_auth_url():
        """Generate Instagram OAuth authorization URL"""
        return (
            f"{InstagramAPI.BASE_URL}/oauth/authorize?"
            f"client_id={InstagramAPI.APP_ID}&"
            f"redirect_uri={InstagramAPI.REDIRECT_URI}&"
            f"scopes=user_profile,user_media&"
            f"response_type=code"
        )
    
    @staticmethod
    def exchange_code_for_token(code):
        """Exchange authorization code for access token"""
        try:
            url = f"{InstagramAPI.BASE_URL}/oauth/access_token"
            data = {
                "client_id": InstagramAPI.APP_ID,
                "client_secret": InstagramAPI.APP_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": InstagramAPI.REDIRECT_URI,
                "code": code
            }
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            return None
    
    @staticmethod
    def refresh_long_lived_token(access_token):
        """Refresh access token to get long-lived token (valid for 60 days)"""
        try:
            url = f"{InstagramAPI.BASE_URL}/access_token"
            params = {
                "grant_type": "ig_refresh_token",
                "access_token": access_token
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None
    
    def get_user_info(self):
        """Get Instagram user profile information"""
        try:
            url = f"{self.BASE_URL}/me"
            params = {
                "fields": "id,username,name,biography,website,profile_picture_url,followers_count,media_count",
                "access_token": self.access_token
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None
    
    def get_media(self, limit=10):
        """Get user's recent media"""
        try:
            url = f"{self.BASE_URL}/me/media"
            params = {
                "fields": "id,caption,media_type,media_url,timestamp,like_count,comments_count",
                "limit": limit,
                "access_token": self.access_token
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get("data", [])
        except Exception as e:
            logger.error(f"Failed to get media: {e}")
            return []
    
    def get_media_insights(self, media_id):
        """Get insights for a specific media post"""
        try:
            url = f"{self.BASE_URL}/{media_id}/insights"
            params = {
                "metric": "engagement,impressions,reach",
                "access_token": self.access_token
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get("data", [])
        except Exception as e:
            logger.error(f"Failed to get media insights: {e}")
            return []
    
    def get_user_insights(self):
        """Get user-level insights"""
        try:
            url = f"{self.BASE_URL}/me/insights"
            params = {
                "metric": "impressions,reach,profile_views,follower_count",
                "period": "day",
                "access_token": self.access_token
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get("data", [])
        except Exception as e:
            logger.error(f"Failed to get user insights: {e}")
            return []
    
    def get_all_metrics(self):
        """Fetch all available metrics for user"""
        try:
            metrics = {
                "user_info": self.get_user_info(),
                "recent_media": self.get_media(limit=10),
                "insights": self.get_user_insights(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Get insights for each recent post
            if metrics["recent_media"]:
                metrics["media_insights"] = []
                for media in metrics["recent_media"][:5]:  # Top 5 posts
                    insights = self.get_media_insights(media["id"])
                    metrics["media_insights"].append({
                        "media_id": media["id"],
                        "insights": insights
                    })
            
            return metrics
        except Exception as e:
            logger.error(f"Failed to fetch all metrics: {e}")
            return None


class InstagramDatabase:
    """Database operations for Instagram integration"""
    
    def __init__(self, db_path="shotlist_analytics.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.create_tables()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def create_tables(self):
        """Create Instagram-related tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Instagram accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS instagram_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                instagram_id TEXT UNIQUE,
                username TEXT,
                access_token TEXT,
                refresh_token TEXT,
                token_expires_at TIMESTAMP,
                connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_sync TIMESTAMP,
                sync_status TEXT DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Instagram metrics cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS instagram_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instagram_account_id INTEGER NOT NULL,
                followers INTEGER,
                following INTEGER,
                media_count INTEGER,
                engagement_rate REAL,
                reach INTEGER,
                impressions INTEGER,
                profile_views INTEGER,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instagram_account_id) REFERENCES instagram_accounts(id)
            )
        ''')
        
        # Instagram media performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS instagram_media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instagram_account_id INTEGER NOT NULL,
                media_id TEXT UNIQUE,
                caption TEXT,
                media_type TEXT,
                likes INTEGER,
                comments INTEGER,
                reach INTEGER,
                impressions INTEGER,
                engagement_rate REAL,
                posted_at TIMESTAMP,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instagram_account_id) REFERENCES instagram_accounts(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_account(self, user_id, instagram_data):
        """Save Instagram account connection"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO instagram_accounts 
                (user_id, instagram_id, username, access_token, last_sync, sync_status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                instagram_data.get("id"),
                instagram_data.get("username"),
                instagram_data.get("access_token"),
                datetime.now().isoformat(),
                "completed"
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save Instagram account: {e}")
            return False
    
    def save_metrics(self, user_id, metrics):
        """Save Instagram metrics to database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get account ID
            cursor.execute(
                'SELECT id FROM instagram_accounts WHERE user_id = ?', 
                (user_id,)
            )
            account = cursor.fetchone()
            
            if not account:
                conn.close()
                return False
            
            account_id = account[0]
            user_info = metrics.get("user_info", {})
            
            # Save metrics
            cursor.execute('''
                INSERT INTO instagram_metrics 
                (instagram_account_id, followers, following, media_count, saved_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                account_id,
                user_info.get("followers_count", 0),
                user_info.get("following_count", 0),
                user_info.get("media_count", 0),
                datetime.now().isoformat()
            ))
            
            # Save media
            for media in metrics.get("recent_media", []):
                cursor.execute('''
                    INSERT OR REPLACE INTO instagram_media
                    (instagram_account_id, media_id, caption, media_type, likes, comments, posted_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    account_id,
                    media.get("id"),
                    media.get("caption", ""),
                    media.get("media_type", ""),
                    media.get("like_count", 0),
                    media.get("comments_count", 0),
                    media.get("timestamp")
                ))
            
            # Update last sync
            cursor.execute(
                'UPDATE instagram_accounts SET last_sync = ? WHERE id = ?',
                (datetime.now().isoformat(), account_id)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
            return False
    
    def get_user_instagram_metrics(self, user_id):
        """Get latest Instagram metrics for user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT m.* FROM instagram_metrics m
                JOIN instagram_accounts a ON m.instagram_account_id = a.id
                WHERE a.user_id = ?
                ORDER BY m.saved_at DESC
                LIMIT 1
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "followers": result[2],
                    "following": result[3],
                    "media_count": result[4],
                    "engagement_rate": result[5],
                    "reach": result[6],
                    "impressions": result[7],
                    "profile_views": result[8],
                    "synced_at": result[9]
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get user metrics: {e}")
            return None
    
    def get_user_top_posts(self, user_id, limit=5):
        """Get top performing posts for user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM instagram_media m
                JOIN instagram_accounts a ON m.instagram_account_id = a.id
                WHERE a.user_id = ?
                ORDER BY m.likes DESC, m.comments DESC
                LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            posts = []
            for row in results:
                posts.append({
                    "media_id": row[2],
                    "caption": row[3],
                    "media_type": row[4],
                    "likes": row[5],
                    "comments": row[6],
                    "reach": row[7],
                    "impressions": row[8]
                })
            
            return posts
        except Exception as e:
            logger.error(f"Failed to get top posts: {e}")
            return []


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = InstagramDatabase()
    
    # Example: Link Instagram account for user
    # instagram_data = {
    #     "id": "12345",
    #     "username": "myaccount",
    #     "access_token": "token_here"
    # }
    # db.save_account(user_id=1, instagram_data=instagram_data)
    
    # Get metrics for user
    # metrics = db.get_user_instagram_metrics(user_id=1)
    # print(metrics)
    
    print("✅ Instagram integration module loaded")
