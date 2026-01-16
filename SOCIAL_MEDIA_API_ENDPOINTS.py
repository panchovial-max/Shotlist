"""
Social Media API Endpoints to add to api_server.py
Copy these methods into the CampaignAnalyticsAPI class
"""

# Add these imports at the top of api_server.py:
# from social_media_integration import SocialMediaAPI, SocialMediaDatabase

# Add this in __init__ method:
# self.social_db = SocialMediaDatabase()

# Add these routes in do_GET method:
"""
        elif path == '/api/social/accounts':
            self.get_social_accounts(query_params)
        elif path == '/api/social/metrics':
            self.get_social_metrics(query_params)
        elif path == '/api/social/dashboard':
            self.get_social_dashboard(query_params)
        elif path == '/api/social/top-content':
            self.get_top_social_content(query_params)
"""

# Add these routes in do_POST method:
"""
        elif path == '/api/social/connect':
            self.connect_social_account()
        elif path == '/api/social/sync':
            self.sync_social_metrics(query_params)
        elif path == '/api/social/disconnect':
            self.disconnect_social_account()
"""

# ============================================================================
# METHOD IMPLEMENTATIONS - Add these to CampaignAnalyticsAPI class
# ============================================================================

def connect_social_account(self):
    """Connect a social media account to user"""
    try:
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'No data'}).encode())
            return
        
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        user_id = data.get('user_id')
        platform = data.get('platform')
        access_token = data.get('access_token')
        
        if not all([user_id, platform, access_token]):
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Missing required fields'}).encode())
            return
        
        # Verify token and get user info
        try:
            api = SocialMediaAPI(platform, access_token)
            user_info = api.get_user_info()
            
            if not user_info:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid token or user not found'}).encode())
                return
            
            # Save account connection
            account_id = self.social_db.connect_account(
                user_id,
                platform,
                {**user_info, 'access_token': access_token}
            )
            
            # Fetch initial metrics
            metrics = api.get_metrics()
            self.social_db.save_metrics(account_id, platform, metrics)
            
            self._set_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'account_id': account_id,
                'platform': platform,
                'username': user_info.get('username') or user_info.get('name'),
                'metrics': metrics
            }).encode())
        
        except Exception as e:
            logger.error(f"Failed to authenticate: {e}")
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': f'Authentication failed: {str(e)}'}).encode())
    
    except Exception as e:
        logger.error(f"Connect account error: {e}")
        self._set_headers(500)
        self.wfile.write(json.dumps({'error': str(e)}).encode())


def get_social_accounts(self, query_params):
    """Get all social media accounts for a user"""
    try:
        user_id = query_params.get('user_id', [None])[0]
        
        if not user_id:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'user_id required'}).encode())
            return
        
        accounts = self.social_db.get_user_accounts(int(user_id))
        
        self._set_headers()
        self.wfile.write(json.dumps({
            'accounts': accounts,
            'total': len(accounts)
        }).encode())
    
    except Exception as e:
        logger.error(f"Get accounts error: {e}")
        self._set_headers(500)
        self.wfile.write(json.dumps({'error': str(e)}).encode())


def get_social_metrics(self, query_params):
    """Get metrics for a specific platform or all platforms"""
    try:
        user_id = query_params.get('user_id', [None])[0]
        platform = query_params.get('platform', [None])[0]
        
        if not user_id:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'user_id required'}).encode())
            return
        
        metrics = self.social_db.get_latest_metrics(int(user_id), platform)
        
        self._set_headers()
        if platform:
            # Single platform
            result = metrics[0] if metrics else {}
        else:
            # All platforms
            result = {m.get('platform'): m for m in metrics}
        
        self.wfile.write(json.dumps(result).encode())
    
    except Exception as e:
        logger.error(f"Get metrics error: {e}")
        self._set_headers(500)
        self.wfile.write(json.dumps({'error': str(e)}).encode())


def get_social_dashboard(self, query_params):
    """Get dashboard summary for all social media accounts"""
    try:
        user_id = query_params.get('user_id', [None])[0]
        
        if not user_id:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'user_id required'}).encode())
            return
        
        summary = self.social_db.get_dashboard_summary(int(user_id))
        
        self._set_headers()
        self.wfile.write(json.dumps(summary).encode())
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        self._set_headers(500)
        self.wfile.write(json.dumps({'error': str(e)}).encode())


def get_top_social_content(self, query_params):
    """Get top performing content across all platforms"""
    try:
        user_id = query_params.get('user_id', [None])[0]
        limit = int(query_params.get('limit', [5])[0])
        
        if not user_id:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'user_id required'}).encode())
            return
        
        conn = self.social_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, platform, content_id, caption, likes, comments, shares, engagement_rate
            FROM social_media_content
            WHERE account_id IN (
                SELECT id FROM social_media_accounts WHERE user_id = ?
            )
            ORDER BY engagement_rate DESC, likes DESC
            LIMIT ?
        ''', (int(user_id), limit))
        
        results = cursor.fetchall()
        conn.close()
        
        content = []
        for row in results:
            content.append({
                'id': row[0],
                'platform': row[1],
                'content_id': row[2],
                'caption': row[3],
                'likes': row[4],
                'comments': row[5],
                'shares': row[6],
                'engagement_rate': row[7]
            })
        
        self._set_headers()
        self.wfile.write(json.dumps({'content': content}).encode())
    
    except Exception as e:
        logger.error(f"Top content error: {e}")
        self._set_headers(500)
        self.wfile.write(json.dumps({'error': str(e)}).encode())


def sync_social_metrics(self, query_params):
    """Manually sync metrics for all user accounts"""
    try:
        user_id = query_params.get('user_id', [None])[0]
        
        if not user_id:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'user_id required'}).encode())
            return
        
        conn = self.social_db.get_connection()
        cursor = conn.cursor()
        
        # Get all accounts for user
        cursor.execute('''
            SELECT id, platform, access_token
            FROM social_media_accounts
            WHERE user_id = ?
        ''', (int(user_id),))
        
        accounts = cursor.fetchall()
        synced = 0
        failed = 0
        errors = []
        
        for account_id, platform, token in accounts:
            try:
                api = SocialMediaAPI(platform, token)
                metrics = api.get_metrics()
                self.social_db.save_metrics(account_id, platform, metrics)
                synced += 1
            except Exception as e:
                failed += 1
                errors.append(f"{platform}: {str(e)}")
                logger.error(f"Sync failed for {platform}: {e}")
        
        conn.close()
        
        self._set_headers()
        self.wfile.write(json.dumps({
            'synced': synced,
            'failed': failed,
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        }).encode())
    
    except Exception as e:
        logger.error(f"Sync error: {e}")
        self._set_headers(500)
        self.wfile.write(json.dumps({'error': str(e)}).encode())


def disconnect_social_account(self):
    """Disconnect a social media account"""
    try:
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'No data'}).encode())
            return
        
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        user_id = data.get('user_id')
        platform = data.get('platform')
        
        if not all([user_id, platform]):
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Missing required fields'}).encode())
            return
        
        conn = self.social_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM social_media_accounts
            WHERE user_id = ? AND platform = ?
        ''', (int(user_id), platform))
        
        conn.commit()
        conn.close()
        
        self._set_headers()
        self.wfile.write(json.dumps({
            'success': True,
            'message': f'{platform} account disconnected'
        }).encode())
    
    except Exception as e:
        logger.error(f"Disconnect error: {e}")
        self._set_headers(500)
        self.wfile.write(json.dumps({'error': str(e)}).encode())


# ============================================================================
# INTEGRATION INSTRUCTIONS
# ============================================================================

"""
1. Add import at top of api_server.py:
   from social_media_integration import SocialMediaAPI, SocialMediaDatabase

2. In CampaignAnalyticsAPI.__init__(), add:
   self.social_db = SocialMediaDatabase()

3. In do_GET method, add these routes before the final 'else':
   elif path == '/api/social/accounts':
       self.get_social_accounts(query_params)
   elif path == '/api/social/metrics':
       self.get_social_metrics(query_params)
   elif path == '/api/social/dashboard':
       self.get_social_dashboard(query_params)
   elif path == '/api/social/top-content':
       self.get_top_social_content(query_params)

4. In do_POST method, add these routes before the final 'else':
   elif path == '/api/social/connect':
       self.connect_social_account()
   elif path == '/api/social/sync':
       self.sync_social_metrics(query_params)
   elif path == '/api/social/disconnect':
       self.disconnect_social_account()

5. Add this method to start auto-sync in run_server():
   from threading import Thread
   
   def auto_sync():
       while True:
           # Sync all accounts every hour
           time.sleep(3600)
   
   sync_thread = Thread(target=auto_sync, daemon=True)
   sync_thread.start()
"""
