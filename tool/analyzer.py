import json
from datetime import datetime, timedelta

class DataAnalyzer:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    # ---------------- Website Analysis ----------------
    def analyze_websites(self):
        """Analyze website data for type, risk level, and temporal patterns"""
        cursor = self.db_manager.conn.cursor()
        
        # Analyze by website type
        cursor.execute('SELECT type, COUNT(*) FROM websites GROUP BY type')
        website_types = dict(cursor.fetchall())
        
        # Analyze by risk levels
        cursor.execute('SELECT risk_level, COUNT(*) FROM websites GROUP BY risk_level ORDER BY risk_level DESC')
        risk_levels = dict(cursor.fetchall())
        
        # Temporal analysis for last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        cursor.execute('''
            SELECT substr(first_seen, 1, 10) as date, COUNT(*) 
            FROM websites 
            WHERE first_seen >= ? 
            GROUP BY date 
            ORDER BY date DESC
        ''', (thirty_days_ago,))
        temporal_patterns = dict(cursor.fetchall())
        
        return {
            'website_types': website_types,
            'risk_levels': risk_levels,
            'temporal_patterns': temporal_patterns
        }

    # ---------------- User Analysis ----------------
    def analyze_users(self):
        """Analyze user data for activity, risk, and marketplace distribution"""
        cursor = self.db_manager.conn.cursor()
        
        # Activity per month (last 6 months)
        cursor.execute('''
            SELECT substr(last_active, 1, 7) as month, COUNT(*) 
            FROM users 
            GROUP BY month 
            ORDER BY month DESC 
            LIMIT 6
        ''')
        user_activity = dict(cursor.fetchall())
        
        # Users by risk level
        cursor.execute('SELECT risk_level, COUNT(*) FROM users GROUP BY risk_level ORDER BY risk_level DESC')
        user_risks = dict(cursor.fetchall())
        
        # Marketplace distribution
        cursor.execute('SELECT marketplaces FROM users WHERE marketplaces IS NOT NULL')
        marketplace_dist = {}
        for row in cursor.fetchall():
            try:
                marketplaces = json.loads(row[0])
                for m in marketplaces:
                    marketplace_dist[m] = marketplace_dist.get(m, 0) + 1
            except json.JSONDecodeError:
                continue
        
        return {
            'user_activity': user_activity,
            'user_risks': user_risks,
            'marketplace_distribution': marketplace_dist
        }

    # ---------------- Alert Analysis ----------------
    def analyze_alerts(self):
        """Analyze alerts by severity, type, and recent trends"""
        cursor = self.db_manager.conn.cursor()
        
        # Alerts by severity
        cursor.execute('SELECT severity, COUNT(*) FROM alerts GROUP BY severity ORDER BY severity DESC')
        alert_severity = dict(cursor.fetchall())
        
        # Alerts by type
        cursor.execute('SELECT type, COUNT(*) FROM alerts GROUP BY type ORDER BY COUNT(*) DESC')
        alert_types = dict(cursor.fetchall())
        
        # Recent alerts (last 7 days)
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        cursor.execute('''
            SELECT substr(date_created, 1, 10) as date, COUNT(*) 
            FROM alerts 
            WHERE date_created >= ? 
            GROUP BY date 
            ORDER BY date DESC
        ''', (seven_days_ago,))
        recent_alerts = dict(cursor.fetchall())
        
        return {
            'alert_severity': alert_severity,
            'alert_types': alert_types,
            'recent_alerts': recent_alerts
        }

    # ---------------- Generate Report ----------------
    def generate_report(self):
        """Generate a comprehensive analysis report"""
        website_analysis = self.analyze_websites()
        user_analysis = self.analyze_users()
        alert_analysis = self.analyze_alerts()
        
        report = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'website_analysis': website_analysis,
            'user_analysis': user_analysis,
            'alert_analysis': alert_analysis,
            'summary': self._generate_summary(website_analysis, user_analysis, alert_analysis)
        }
        
        return report

    def _generate_summary(self, website_analysis, user_analysis, alert_analysis):
        """Generate summary metrics"""
        total_websites = sum(website_analysis.get('website_types', {}).values())
        total_users = sum(user_analysis.get('user_activity', {}).values())
        total_alerts = sum(alert_analysis.get('alert_severity', {}).values())
        
        high_risk_websites = sum(
            website_analysis.get('risk_levels', {}).get(r, 0) for r in range(8, 10)
        )
        high_risk_users = sum(
            user_analysis.get('user_risks', {}).get(r, 0) for r in range(8, 10)
        )
        high_severity_alerts = sum(
            alert_analysis.get('alert_severity', {}).get(r, 0) for r in range(8, 10)
        )
        
        most_common_website_type = max(
            website_analysis.get('website_types', {}).items(), key=lambda x: x[1], default=('None', 0)
        )[0]
        most_active_marketplace = max(
            user_analysis.get('marketplace_distribution', {}).items(), key=lambda x: x[1], default=('None', 0)
        )[0]
        
        return {
            'total_websites': total_websites,
            'total_users': total_users,
            'total_alerts': total_alerts,
            'high_risk_websites': high_risk_websites,
            'high_risk_users': high_risk_users,
            'high_severity_alerts': high_severity_alerts,
            'most_common_website_type': most_common_website_type,
            'most_active_marketplace': most_active_marketplace
        }
