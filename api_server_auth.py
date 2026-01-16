#!/usr/bin/env python3
"""
SHOTLIST Campaign Analytics API Server with Authentication
Provides RESTful API with user authentication and session management
"""

import sqlite3
import json
import hashlib
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import os

DATABASE = 'shotlist_analytics.db'

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_session_id():
    """Generate a secure session ID"""
    return secrets.token_urlsafe(32)

class AuthenticatedAPI(BaseHTTPRequestHandler):
    """API Handler with Authentication"""

    def _set_headers(self, status=200, content_type='application/json'):
        """Set HTTP headers"""
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID')
        self.end_headers()

    def do_OPTIONS(self):
        """Handle OPTIONS request for CORS"""
        self._set_headers()

    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/api/login':
            self.handle_login()
        elif path == '/api/logout':
            self.handle_logout()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        params = parse_qs(parsed_path.query)

        # Public endpoints (no auth required)
        if path == '/api/verify-session':
            self.verify_session()
            return

        # Protected endpoints - require authentication
        user_id = self.authenticate_request()
        if not user_id:
            self._set_headers(401)
            self.wfile.write(json.dumps({'error': 'Unauthorized', 'message': 'Please login first'}).encode())
            return

        # Route handling
        if path == '/api/campaigns':
            self.get_campaigns(params, user_id)
        elif path == '/api/kpis':
            self.get_kpis(params, user_id)
        elif path == '/api/roi-trend':
            self.get_roi_trend(params, user_id)
        elif path == '/api/revenue-cost':
            self.get_revenue_cost(params, user_id)
        elif path == '/api/social-media':
            self.get_social_media(params, user_id)
        elif path == '/api/seo-metrics':
            self.get_seo_metrics(params, user_id)
        elif path == '/api/calendar':
            self.get_calendar_events(params, user_id)
        elif path == '/api/user-info':
            self.get_user_info(user_id)
        elif path == '/api/export':
            self.export_data(params, user_id)
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())

    def authenticate_request(self):
        """Authenticate request using session ID"""
        session_id = self.headers.get('X-Session-ID')
        if not session_id:
            return None

        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Check if session is valid
        cursor.execute('''
            SELECT user_id FROM sessions
            WHERE session_id = ? AND expires_at > datetime('now')
        ''', (session_id,))

        result = cursor.fetchone()
        conn.close()

        return result['user_id'] if result else None

    def handle_login(self):
        """Handle user login"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            username = data.get('username')
            password = data.get('password')
            remember_me = data.get('rememberMe', False)

            if not username or not password:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Username and password required'
                }).encode())
                return

            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Get user
            password_hash = hash_password(password)
            cursor.execute('''
                SELECT user_id, username, email, full_name, company_name, role, is_active
                FROM users
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))

            user = cursor.fetchone()

            if not user:
                self._set_headers(401)
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Invalid username or password'
                }).encode())
                conn.close()
                return

            if not user['is_active']:
                self._set_headers(403)
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Account is inactive. Please contact support.'
                }).encode())
                conn.close()
                return

            # Create session
            session_id = generate_session_id()
            expires_in_days = 30 if remember_me else 1
            expires_at = datetime.now() + timedelta(days=expires_in_days)

            cursor.execute('''
                INSERT INTO sessions (session_id, user_id, expires_at)
                VALUES (?, ?, ?)
            ''', (session_id, user['user_id'], expires_at.strftime('%Y-%m-%d %H:%M:%S')))

            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = datetime('now')
                WHERE user_id = ?
            ''', (user['user_id'],))

            # Log activity
            cursor.execute('''
                INSERT INTO activity_log (user_id, action)
                VALUES (?, ?)
            ''', (user['user_id'], 'Login'))

            conn.commit()
            conn.close()

            self._set_headers(200)
            self.wfile.write(json.dumps({
                'success': True,
                'message': 'Login successful',
                'session_id': session_id,
                'user': {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'company_name': user['company_name'],
                    'role': user['role']
                }
            }).encode())

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'success': False, 'message': str(e)}).encode())

    def handle_logout(self):
        """Handle user logout"""
        session_id = self.headers.get('X-Session-ID')

        if session_id:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
            conn.commit()
            conn.close()

        self._set_headers(200)
        self.wfile.write(json.dumps({'success': True, 'message': 'Logged out successfully'}).encode())

    def verify_session(self):
        """Verify if session is valid"""
        session_id = self.headers.get('X-Session-ID')

        if not session_id:
            self._set_headers(200)
            self.wfile.write(json.dumps({'valid': False}).encode())
            return

        user_id = self.authenticate_request()

        self._set_headers(200)
        self.wfile.write(json.dumps({'valid': bool(user_id)}).encode())

    def get_user_info(self, user_id):
        """Get current user information"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT user_id, username, email, full_name, company_name, role, created_at, last_login
                FROM users WHERE user_id = ?
            ''', (user_id,))

            user = cursor.fetchone()

            # Get campaign count
            cursor.execute('SELECT COUNT(*) as count FROM campaigns WHERE user_id = ?', (user_id,))
            campaign_count = cursor.fetchone()['count']

            conn.close()

            self._set_headers()
            self.wfile.write(json.dumps({
                'user': dict(user),
                'campaign_count': campaign_count
            }).encode())

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def get_db_connection(self):
        """Create database connection"""
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

    def get_campaigns(self, params, user_id):
        """Get campaigns for authenticated user"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Check if user is admin
            cursor.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
            user_role = cursor.fetchone()['role']

            campaign_type = params.get('type', ['all'])[0]
            status = params.get('status', ['all'])[0]

            # Build query
            if user_role == 'admin':
                query = 'SELECT * FROM campaigns WHERE 1=1'
                query_params = []
            else:
                query = 'SELECT * FROM campaigns WHERE user_id = ?'
                query_params = [user_id]

            if campaign_type != 'all':
                query += ' AND campaign_type = ?'
                query_params.append(campaign_type)

            if status != 'all':
                query += ' AND status = ?'
                query_params.append(status)

            query += ' ORDER BY created_at DESC'

            cursor.execute(query, query_params)
            rows = cursor.fetchall()

            campaigns = []
            for row in rows:
                # Get ROI metrics
                cursor.execute('''
                    SELECT SUM(cost) as total_spent, SUM(revenue) as total_revenue
                    FROM roi_metrics WHERE campaign_id = ?
                ''', (row['campaign_id'],))
                metrics = cursor.fetchone()

                total_spent = metrics['total_spent'] or 0
                total_revenue = metrics['total_revenue'] or 0
                roi = ((total_revenue - total_spent) / total_spent * 100) if total_spent > 0 else 0

                campaigns.append({
                    'campaign_id': row['campaign_id'],
                    'campaign_name': row['campaign_name'],
                    'client_name': row['client_name'],
                    'campaign_type': row['campaign_type'],
                    'start_date': row['start_date'],
                    'end_date': row['end_date'],
                    'budget': row['budget'],
                    'spent': round(total_spent, 2),
                    'revenue': round(total_revenue, 2),
                    'roi': round(roi, 2),
                    'status': row['status']
                })

            conn.close()

            self._set_headers()
            self.wfile.write(json.dumps({'campaigns': campaigns}).encode())

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def get_kpis(self, params, user_id):
        """Get KPI metrics for user"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Check if admin
            cursor.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
            is_admin = cursor.fetchone()['role'] == 'admin'

            days = int(params.get('days', ['30'])[0])
            campaign_id = params.get('campaign_id', ['all'])[0]

            date_filter = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            # Build user filter
            user_filter = '' if is_admin else ' AND c.user_id = ?'
            base_params = [date_filter]
            if not is_admin:
                base_params.append(user_id)

            if campaign_id != 'all':
                user_filter += ' AND r.campaign_id = ?'
                base_params.append(campaign_id)

            # Get current metrics
            cursor.execute(f'''
                SELECT
                    SUM(r.revenue) as total_revenue,
                    SUM(r.cost) as total_cost,
                    SUM(r.conversions) as total_conversions,
                    AVG(r.roi_percentage) as avg_roi,
                    AVG(r.roas) as avg_roas
                FROM roi_metrics r
                JOIN campaigns c ON r.campaign_id = c.campaign_id
                WHERE r.date >= ?{user_filter}
            ''', base_params)

            current_metrics = cursor.fetchone()

            # Get previous period
            prev_date_start = (datetime.now() - timedelta(days=days*2)).strftime('%Y-%m-%d')
            prev_params = [prev_date_start, date_filter]
            if not is_admin:
                prev_params.append(user_id)
            if campaign_id != 'all':
                prev_params.append(campaign_id)

            cursor.execute(f'''
                SELECT
                    SUM(r.revenue) as total_revenue,
                    SUM(r.conversions) as total_conversions,
                    AVG(r.roi_percentage) as avg_roi,
                    AVG(r.roas) as avg_roas
                FROM roi_metrics r
                JOIN campaigns c ON r.campaign_id = c.campaign_id
                WHERE r.date >= ? AND r.date < ?{user_filter}
            ''', prev_params)

            prev_metrics = cursor.fetchone()

            def calc_change(current, previous):
                if previous and previous > 0:
                    return round(((current - previous) / previous) * 100, 2)
                return 0

            total_revenue = current_metrics['total_revenue'] or 0
            total_conversions = current_metrics['total_conversions'] or 0
            avg_roi = current_metrics['avg_roi'] or 0
            avg_roas = current_metrics['avg_roas'] or 0

            prev_revenue = prev_metrics['total_revenue'] or 0
            prev_conversions = prev_metrics['total_conversions'] or 0
            prev_roi = prev_metrics['avg_roi'] or 0
            prev_roas = prev_metrics['avg_roas'] or 0

            kpis = {
                'roi': {'value': round(avg_roi, 2), 'change': calc_change(avg_roi, prev_roi)},
                'revenue': {'value': round(total_revenue, 2), 'change': calc_change(total_revenue, prev_revenue)},
                'conversions': {'value': int(total_conversions), 'change': calc_change(total_conversions, prev_conversions)},
                'roas': {'value': round(avg_roas, 2), 'change': calc_change(avg_roas, prev_roas)}
            }

            conn.close()

            self._set_headers()
            self.wfile.write(json.dumps({'kpis': kpis}).encode())

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def get_calendar_events(self, params, user_id):
        """Get calendar events for user"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Check if admin
            cursor.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
            is_admin = cursor.fetchone()['role'] == 'admin'

            month = params.get('month', [(datetime.now()).strftime('%Y-%m')])[0]
            start_date = f"{month}-01"
            end_date = f"{month}-31"

            # Build query based on role
            if is_admin:
                query = '''
                    SELECT e.*, c.campaign_name, u.full_name as user_name
                    FROM campaign_events e
                    LEFT JOIN campaigns c ON e.campaign_id = c.campaign_id
                    LEFT JOIN users u ON e.user_id = u.user_id
                    WHERE e.event_date >= ? AND e.event_date <= ?
                    ORDER BY e.event_date, e.event_time
                '''
                cursor.execute(query, (start_date, end_date))
            else:
                query = '''
                    SELECT e.*, c.campaign_name
                    FROM campaign_events e
                    LEFT JOIN campaigns c ON e.campaign_id = c.campaign_id
                    WHERE e.user_id = ? AND e.event_date >= ? AND e.event_date <= ?
                    ORDER BY e.event_date, e.event_time
                '''
                cursor.execute(query, (user_id, start_date, end_date))

            rows = cursor.fetchall()

            events = []
            for row in rows:
                event = {
                    'event_id': row['event_id'],
                    'event_title': row['event_title'],
                    'event_description': row['event_description'],
                    'event_type': row['event_type'],
                    'event_date': row['event_date'],
                    'event_time': row['event_time'],
                    'duration_minutes': row['duration_minutes'],
                    'status': row['status'],
                    'priority': row['priority'],
                    'campaign_name': row['campaign_name']
                }
                if is_admin and 'user_name' in row.keys():
                    event['user_name'] = row['user_name']
                events.append(event)

            conn.close()

            self._set_headers()
            self.wfile.write(json.dumps({'events': events}).encode())

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    # Keeping existing methods from original API for consistency
    def get_roi_trend(self, params, user_id):
        """Get ROI trend data for user"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
            is_admin = cursor.fetchone()['role'] == 'admin'

            days = int(params.get('days', ['30'])[0])
            campaign_id = params.get('campaign_id', ['all'])[0]
            date_filter = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            user_filter = '' if is_admin else ' AND c.user_id = ?'
            query_params = [date_filter]
            if not is_admin:
                query_params.append(user_id)
            if campaign_id != 'all':
                user_filter += ' AND r.campaign_id = ?'
                query_params.append(campaign_id)

            cursor.execute(f'''
                SELECT r.date, AVG(r.roi_percentage) as roi
                FROM roi_metrics r
                JOIN campaigns c ON r.campaign_id = c.campaign_id
                WHERE r.date >= ?{user_filter}
                GROUP BY r.date
                ORDER BY r.date
            ''', query_params)

            rows = cursor.fetchall()
            trend = {
                'labels': [row['date'] for row in rows],
                'data': [round(row['roi'], 2) for row in rows]
            }

            conn.close()
            self._set_headers()
            self.wfile.write(json.dumps({'trend': trend}).encode())

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def get_revenue_cost(self, params, user_id):
        """Get revenue vs cost data for user"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
            is_admin = cursor.fetchone()['role'] == 'admin'

            days = int(params.get('days', ['30'])[0])
            campaign_id = params.get('campaign_id', ['all'])[0]
            date_filter = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            user_filter = '' if is_admin else ' AND c.user_id = ?'
            query_params = [date_filter]
            if not is_admin:
                query_params.append(user_id)
            if campaign_id != 'all':
                user_filter += ' AND r.campaign_id = ?'
                query_params.append(campaign_id)

            cursor.execute(f'''
                SELECT r.date, SUM(r.revenue) as revenue, SUM(r.cost) as cost
                FROM roi_metrics r
                JOIN campaigns c ON r.campaign_id = c.campaign_id
                WHERE r.date >= ?{user_filter}
                GROUP BY r.date
                ORDER BY r.date
            ''', query_params)

            rows = cursor.fetchall()
            data = {
                'labels': [row['date'] for row in rows],
                'revenue': [round(row['revenue'], 2) for row in rows],
                'cost': [round(row['cost'], 2) for row in rows]
            }

            conn.close()
            self._set_headers()
            self.wfile.write(json.dumps({'data': data}).encode())

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def get_social_media(self, params, user_id):
        """Get social media metrics for user"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
            is_admin = cursor.fetchone()['role'] == 'admin'

            days = int(params.get('days', ['30'])[0])
            campaign_id = params.get('campaign_id', ['all'])[0]
            date_filter = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            user_filter = '' if is_admin else ' AND c.user_id = ?'
            query_params = [date_filter]
            if not is_admin:
                query_params.append(user_id)
            if campaign_id != 'all':
                user_filter += ' AND s.campaign_id = ?'
                query_params.append(campaign_id)

            cursor.execute(f'''
                SELECT
                    s.platform,
                    SUM(s.impressions) as impressions,
                    SUM(s.engagement) as engagement,
                    SUM(s.reach) as reach,
                    SUM(s.followers_gained) as followers,
                    SUM(s.clicks) as clicks
                FROM social_media_metrics s
                JOIN campaigns c ON s.campaign_id = c.campaign_id
                WHERE s.date >= ?{user_filter}
                GROUP BY s.platform
            ''', query_params)

            rows = cursor.fetchall()
            platforms = {}
            for row in rows:
                platforms[row['platform']] = {
                    'impressions': row['impressions'],
                    'engagement': row['engagement'],
                    'reach': row['reach'],
                    'followers': row['followers'],
                    'clicks': row['clicks']
                }

            conn.close()
            self._set_headers()
            self.wfile.write(json.dumps({'platforms': platforms}).encode())

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def get_seo_metrics(self, params, user_id):
        """Get SEO metrics for user"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
            is_admin = cursor.fetchone()['role'] == 'admin'

            days = int(params.get('days', ['30'])[0])
            date_filter = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            user_filter = '' if is_admin else ' AND c.user_id = ?'
            query_params = [date_filter]
            if not is_admin:
                query_params.append(user_id)

            cursor.execute(f'''
                SELECT
                    SUM(s.organic_traffic) as traffic,
                    AVG(s.keyword_rankings) as keywords,
                    SUM(s.backlinks) as backlinks,
                    AVG(s.domain_authority) as domain_authority
                FROM seo_metrics s
                JOIN campaigns c ON s.campaign_id = c.campaign_id
                WHERE s.date >= ?{user_filter}
            ''', query_params)

            current = cursor.fetchone()

            # Get previous period
            prev_date_start = (datetime.now() - timedelta(days=days*2)).strftime('%Y-%m-%d')
            prev_params = [prev_date_start, date_filter]
            if not is_admin:
                prev_params.append(user_id)

            cursor.execute(f'''
                SELECT
                    SUM(s.organic_traffic) as traffic,
                    AVG(s.keyword_rankings) as keywords,
                    SUM(s.backlinks) as backlinks
                FROM seo_metrics s
                JOIN campaigns c ON s.campaign_id = c.campaign_id
                WHERE s.date >= ? AND s.date < ?{user_filter}
            ''', prev_params)

            prev = cursor.fetchone()

            def calc_change(current, previous):
                if previous and previous > 0:
                    return round(((current - previous) / previous) * 100, 2)
                return 0

            metrics = {
                'organic_traffic': {
                    'value': int(current['traffic'] or 0),
                    'change': calc_change(current['traffic'] or 0, prev['traffic'] or 0)
                },
                'keyword_rankings': {
                    'value': int(current['keywords'] or 0),
                    'change': int((current['keywords'] or 0) - (prev['keywords'] or 0))
                },
                'backlinks': {
                    'value': int(current['backlinks'] or 0),
                    'change': int((current['backlinks'] or 0) - (prev['backlinks'] or 0))
                },
                'domain_authority': {
                    'value': int(current['domain_authority'] or 0),
                    'change': 0
                }
            }

            conn.close()
            self._set_headers()
            self.wfile.write(json.dumps({'metrics': metrics}).encode())

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def export_data(self, params, user_id):
        """Export campaign data as CSV for user"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
            is_admin = cursor.fetchone()['role'] == 'admin'

            user_filter = '' if is_admin else ' AND c.user_id = ?'
            query_params = [user_id] if not is_admin else []

            cursor.execute(f'''
                SELECT
                    c.campaign_name,
                    c.client_name,
                    c.campaign_type,
                    c.budget,
                    c.status,
                    r.date,
                    r.revenue,
                    r.cost,
                    r.conversions,
                    r.roi_percentage
                FROM campaigns c
                LEFT JOIN roi_metrics r ON c.campaign_id = r.campaign_id
                WHERE 1=1{user_filter}
                ORDER BY c.campaign_name, r.date
            ''', query_params)

            rows = cursor.fetchall()

            csv_data = 'Campaign,Client,Type,Budget,Status,Date,Revenue,Cost,Conversions,ROI\n'
            for row in rows:
                csv_data += f"{row['campaign_name']},{row['client_name']},{row['campaign_type']},"
                csv_data += f"{row['budget']},{row['status']},{row['date'] or ''},"
                csv_data += f"{row['revenue'] or 0},{row['cost'] or 0},"
                csv_data += f"{row['conversions'] or 0},{row['roi_percentage'] or 0}\n"

            conn.close()

            self._set_headers(content_type='text/csv')
            self.send_header('Content-Disposition', 'attachment; filename=campaign_data.csv')
            self.wfile.write(csv_data.encode())

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())

def run_server(port=8001):
    """Start the API server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, AuthenticatedAPI)

    print(f"🎨 SHOTLIST Campaign Analytics API (Authenticated)")
    print(f"{'=' * 60}")
    print(f"✅ Server running on http://localhost:{port}")
    print(f"📊 Database: {DATABASE}")
    print(f"🔐 Authentication: ENABLED")
    print(f"{'=' * 60}")
    print(f"\n📡 API Endpoints:")
    print(f"  POST /api/login           - User login")
    print(f"  POST /api/logout          - User logout")
    print(f"  GET  /api/verify-session  - Verify session")
    print(f"  GET  /api/user-info       - Get user info")
    print(f"  GET  /api/campaigns       - List campaigns (user-specific)")
    print(f"  GET  /api/kpis            - Get KPI metrics")
    print(f"  GET  /api/roi-trend       - ROI trend data")
    print(f"  GET  /api/revenue-cost    - Revenue vs Cost")
    print(f"  GET  /api/social-media    - Social media metrics")
    print(f"  GET  /api/seo-metrics     - SEO metrics")
    print(f"  GET  /api/calendar        - Calendar events")
    print(f"  GET  /api/export          - Export data as CSV")
    print(f"\n⌨️  Press Ctrl+C to stop the server\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n⛔ Server stopped")
        httpd.server_close()

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        print(f"❌ Database not found: {DATABASE}")
        print(f"💡 Run 'python3 init_database.py' and 'python3 setup_auth.py' first")
        exit(1)

    run_server()
