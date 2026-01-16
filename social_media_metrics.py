#!/usr/bin/env python3
"""
Social Media Metrics Collection and Analysis System
Handles real-time metrics, analytics, and performance statistics
from multiple social media platforms
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

class MetricType(Enum):
    """Types of metrics to track"""
    FOLLOWERS = "followers"
    ENGAGEMENT = "engagement"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    SHARES = "shares"
    COMMENTS = "comments"
    LIKES = "likes"
    CLICKS = "clicks"
    SAVES = "saves"
    VIDEO_VIEWS = "video_views"
    PROFILE_VISITS = "profile_visits"
    MENTIONS = "mentions"

class SocialMediaMetrics:
    """Manages social media metrics collection and analysis"""
    
    def __init__(self, database='shotlist_analytics.db'):
        self.database = database
        self._init_tables()
    
    def _get_connection(self):
        """Create database connection"""
        conn = sqlite3.connect(self.database)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_tables(self):
        """Initialize metrics tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Daily Metrics Table
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
        
        # Monthly Aggregated Metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_media_monthly_metrics (
                monthly_metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                total_followers INTEGER DEFAULT 0,
                avg_engagement_rate REAL DEFAULT 0,
                total_reach INTEGER DEFAULT 0,
                total_impressions INTEGER DEFAULT 0,
                total_shares INTEGER DEFAULT 0,
                total_comments INTEGER DEFAULT 0,
                total_likes INTEGER DEFAULT 0,
                total_clicks INTEGER DEFAULT 0,
                total_saves INTEGER DEFAULT 0,
                total_video_views INTEGER DEFAULT 0,
                total_profile_visits INTEGER DEFAULT 0,
                total_mentions INTEGER DEFAULT 0,
                growth_rate REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES social_media_accounts(account_id),
                UNIQUE(account_id, platform, year, month)
            )
        ''')
        
        # Campaign Performance Metrics
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
        
        # Platform-Specific Metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS platform_specific_metrics (
                platform_metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                date DATE NOT NULL,
                metric_key TEXT NOT NULL,
                metric_value TEXT,
                metric_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES social_media_accounts(account_id)
            )
        ''')
        
        # Audience Demographics
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
        
        # Content Performance
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
        
        conn.commit()
        conn.close()
    
    def add_daily_metrics(self, account_id: int, platform: str, metrics: Dict) -> Dict:
        """Add daily metrics for an account"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT OR REPLACE INTO social_media_daily_metrics
                (account_id, platform, date, followers, engagement_rate, reach, 
                 impressions, shares, comments, likes, clicks, saves, video_views, 
                 profile_visits, mentions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                account_id,
                platform,
                today,
                metrics.get('followers', 0),
                metrics.get('engagement_rate', 0),
                metrics.get('reach', 0),
                metrics.get('impressions', 0),
                metrics.get('shares', 0),
                metrics.get('comments', 0),
                metrics.get('likes', 0),
                metrics.get('clicks', 0),
                metrics.get('saves', 0),
                metrics.get('video_views', 0),
                metrics.get('profile_visits', 0),
                metrics.get('mentions', 0)
            ))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': f'Daily metrics recorded for {platform}',
                'date': today
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'DATABASE_ERROR'
            }
    
    def get_daily_metrics(self, account_id: int, platform: str, days: int = 30) -> Dict:
        """Get daily metrics for specified period"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT * FROM social_media_daily_metrics
                WHERE account_id = ? AND platform = ? AND date >= ?
                ORDER BY date DESC
            ''', (account_id, platform, start_date))
            
            metrics = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return {
                'success': True,
                'metrics': metrics,
                'count': len(metrics),
                'period_days': days
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'DATABASE_ERROR'
            }
    
    def get_performance_summary(self, account_id: int, platform: str) -> Dict:
        """Get performance summary with key metrics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get latest metrics
            cursor.execute('''
                SELECT * FROM social_media_daily_metrics
                WHERE account_id = ? AND platform = ?
                ORDER BY date DESC LIMIT 1
            ''', (account_id, platform))
            
            latest = cursor.fetchone()
            
            # Get metrics from 30 days ago
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT * FROM social_media_daily_metrics
                WHERE account_id = ? AND platform = ? AND date >= ?
                ORDER BY date
            ''', (account_id, platform, start_date))
            
            all_metrics = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            if not latest or not all_metrics:
                return {
                    'success': False,
                    'message': 'No metrics data available'
                }
            
            # Calculate growth
            first_followers = all_metrics[0]['followers']
            current_followers = latest['followers']
            follower_growth = current_followers - first_followers
            growth_rate = (follower_growth / first_followers * 100) if first_followers > 0 else 0
            
            # Calculate averages
            avg_engagement = sum(m['engagement_rate'] for m in all_metrics) / len(all_metrics)
            total_reach = sum(m['reach'] for m in all_metrics)
            total_impressions = sum(m['impressions'] for m in all_metrics)
            
            return {
                'success': True,
                'summary': {
                    'platform': platform,
                    'current_followers': current_followers,
                    'follower_growth': follower_growth,
                    'growth_rate': round(growth_rate, 2),
                    'avg_engagement_rate': round(avg_engagement, 2),
                    'total_reach_30d': total_reach,
                    'total_impressions_30d': total_impressions,
                    'latest_date': latest['date'],
                    'data_points': len(all_metrics)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'DATABASE_ERROR'
            }
    
    def add_content_performance(self, account_id: int, platform: str, 
                               post_data: Dict) -> Dict:
        """Track individual post performance"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO content_performance
                (account_id, platform, post_id, post_type, caption, hashtags, 
                 posted_at, likes, comments, shares, saves, views, reach, engagement_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                account_id,
                platform,
                post_data.get('post_id'),
                post_data.get('post_type', 'post'),
                post_data.get('caption', ''),
                post_data.get('hashtags', ''),
                post_data.get('posted_at'),
                post_data.get('likes', 0),
                post_data.get('comments', 0),
                post_data.get('shares', 0),
                post_data.get('saves', 0),
                post_data.get('views', 0),
                post_data.get('reach', 0),
                post_data.get('engagement_rate', 0)
            ))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Post performance recorded',
                'post_id': post_data.get('post_id')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'DATABASE_ERROR'
            }
    
    def get_top_content(self, account_id: int, platform: str, limit: int = 10) -> Dict:
        """Get top performing content"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM content_performance
                WHERE account_id = ? AND platform = ?
                ORDER BY engagement_rate DESC LIMIT ?
            ''', (account_id, platform, limit))
            
            content = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return {
                'success': True,
                'top_content': content,
                'count': len(content)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'DATABASE_ERROR'
            }
    
    def add_audience_demographics(self, account_id: int, platform: str, 
                                 demographics: Dict) -> Dict:
        """Record audience demographic data"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT OR REPLACE INTO audience_demographics
                (account_id, platform, date, age_13_17, age_18_24, age_25_34, 
                 age_35_44, age_45_54, age_55_64, age_65_plus, male_percentage, 
                 female_percentage, top_countries, top_cities)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                account_id,
                platform,
                today,
                demographics.get('age_13_17', 0),
                demographics.get('age_18_24', 0),
                demographics.get('age_25_34', 0),
                demographics.get('age_35_44', 0),
                demographics.get('age_45_54', 0),
                demographics.get('age_55_64', 0),
                demographics.get('age_65_plus', 0),
                demographics.get('male_percentage', 0),
                demographics.get('female_percentage', 0),
                demographics.get('top_countries', ''),
                demographics.get('top_cities', '')
            ))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Audience demographics recorded'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'DATABASE_ERROR'
            }
    
    def get_audience_insights(self, account_id: int, platform: str) -> Dict:
        """Get audience insights"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM audience_demographics
                WHERE account_id = ? AND platform = ?
                ORDER BY date DESC LIMIT 1
            ''', (account_id, platform))
            
            demographics = cursor.fetchone()
            conn.close()
            
            if not demographics:
                return {
                    'success': False,
                    'message': 'No demographic data available'
                }
            
            return {
                'success': True,
                'demographics': dict(demographics)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'DATABASE_ERROR'
            }
    
    def calculate_roi(self, account_id: int, platform: str, 
                     campaign_data: Dict) -> Dict:
        """Calculate ROI for social media campaign"""
        try:
            impressions = campaign_data.get('impressions', 1)
            cost = campaign_data.get('cost', 0)
            revenue = campaign_data.get('revenue', 0)
            conversions = campaign_data.get('conversions', 0)
            
            # Calculate metrics
            roi = ((revenue - cost) / cost * 100) if cost > 0 else 0
            cpc = (cost / conversions) if conversions > 0 else 0
            conversion_rate = (conversions / impressions * 100) if impressions > 0 else 0
            roas = (revenue / cost) if cost > 0 else 0
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO campaign_social_metrics
                (account_id, platform, campaign_id, start_date, end_date,
                 total_reach, total_impressions, total_engagement, engagement_rate,
                 conversion_rate, cost_per_engagement, cost_per_reach, 
                 revenue_generated, roi)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                account_id,
                platform,
                campaign_data.get('campaign_id'),
                campaign_data.get('start_date'),
                campaign_data.get('end_date'),
                campaign_data.get('reach', 0),
                impressions,
                campaign_data.get('engagement', 0),
                campaign_data.get('engagement_rate', 0),
                conversion_rate,
                cpc,
                (cost / campaign_data.get('reach', 1)) if campaign_data.get('reach') else 0,
                revenue,
                roi
            ))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'roi': round(roi, 2),
                'roas': round(roas, 2),
                'conversion_rate': round(conversion_rate, 2),
                'cost_per_conversion': round(cpc, 2)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'DATABASE_ERROR'
            }


if __name__ == '__main__':
    print("🎬 Social Media Metrics System")
    print("=" * 60)
    
    # Initialize metrics system
    metrics = SocialMediaMetrics()
    
    # Test data - add sample metrics
    test_metrics = {
        'followers': 15250,
        'engagement_rate': 4.8,
        'reach': 50000,
        'impressions': 125000,
        'shares': 450,
        'comments': 2100,
        'likes': 8950,
        'clicks': 1200,
        'saves': 350,
        'video_views': 75000,
        'profile_visits': 2500,
        'mentions': 120
    }
    
    print("\n✅ Adding daily metrics for account 1...")
    result = metrics.add_daily_metrics(1, 'instagram', test_metrics)
    print(f"Result: {result}")
    
    print("\n✅ Getting performance summary...")
    summary = metrics.get_performance_summary(1, 'instagram')
    print(f"Summary: {json.dumps(summary, indent=2)}")
    
    print("\n✅ Adding content performance...")
    post_data = {
        'post_id': 'post_123456',
        'post_type': 'carousel',
        'caption': 'Amazing product launch! 🚀',
        'hashtags': '#launch #product #innovation',
        'posted_at': datetime.now().isoformat(),
        'likes': 2450,
        'comments': 320,
        'shares': 180,
        'saves': 150,
        'views': 45000,
        'reach': 38000,
        'engagement_rate': 7.2
    }
    
    result = metrics.add_content_performance(1, 'instagram', post_data)
    print(f"Result: {result}")
    
    print("\n✅ Getting top content...")
    top = metrics.get_top_content(1, 'instagram')
    print(f"Top content: {json.dumps(top, indent=2)}")

