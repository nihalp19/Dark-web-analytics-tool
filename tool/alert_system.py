import re
from datetime import datetime
from config import ALERT_CONFIG

class AlertSystem:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    # ---------------- Keyword Alert Checks ----------------
    def check_keyword_alerts(self, keyword, results):
        """
        Check if a keyword search triggers alerts based on high-risk keywords
        or suspicious patterns in results.
        """
        keyword_lower = keyword.lower()

        # High-risk keyword check
        if any(risk_word.lower() in keyword_lower for risk_word in ALERT_CONFIG['high_risk_keywords']):
            self.create_alert(
                alert_type="High-risk keyword detected",
                content=f"Keyword '{keyword}' found in {len(results)} results",
                severity=ALERT_CONFIG['severity_levels'].get('high', 8)
            )

        # Check results for suspicious patterns
        for result in results:
            snippet = result.get('snippet', '')
            if self._contains_suspicious_pattern(snippet):
                self.create_alert(
                    alert_type="Suspicious content detected",
                    content=f"Suspicious pattern found in result: {result.get('url', 'Unknown')}",
                    severity=ALERT_CONFIG['severity_levels'].get('medium', 5)
                )

    # ---------------- Suspicious Pattern Detection ----------------
    def _contains_suspicious_pattern(self, text):
        """Return True if text contains suspicious patterns like credit cards, SSNs, or emails."""
        suspicious_patterns = [
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card numbers
            r'\b\d{3}[- ]?\d{2}[- ]?\d{4}\b',            # SSN pattern
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',  # Emails
        ]
        return any(re.search(pattern, text) for pattern in suspicious_patterns)

    # ---------------- Create Alert ----------------
    def create_alert(self, alert_type, content, severity=5):
        """Insert a new alert into the database."""
        try:
            cursor = self.db_manager.conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (type, content, severity, date_created, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (alert_type, content, severity, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "new"))
            self.db_manager.conn.commit()
            print(f"[!] ALERT: {alert_type} | Severity: {severity}/10 | {content}")
            return True
        except Exception as e:
            print(f"[-] Error creating alert: {str(e)}")
            return False

    # ---------------- Retrieve Alerts ----------------
    def get_alerts(self, status=None, min_severity=0, limit=50):
        """
        Retrieve alerts from the database.
        Can filter by status and minimum severity.
        """
        try:
            cursor = self.db_manager.conn.cursor()
            query = '''
                SELECT * FROM alerts 
                WHERE severity >= ?
            '''
            params = [min_severity]

            if status:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY severity DESC, date_created DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except Exception as e:
            print(f"[-] Error retrieving alerts: {str(e)}")
            return []

    # ---------------- Update Alert Status ----------------
    def update_alert_status(self, alert_id, status):
        """Update the status of a specific alert."""
        try:
            cursor = self.db_manager.conn.cursor()
            cursor.execute('UPDATE alerts SET status = ? WHERE id = ?', (status, alert_id))
            self.db_manager.conn.commit()
            print(f"[+] Alert ID {alert_id} status updated to '{status}'")
            return True
        except Exception as e:
            print(f"[-] Error updating alert status: {str(e)}")
            return False

    # ---------------- Optional: Bulk Update ----------------
    def bulk_update_alerts(self, alert_ids, status):
        """Update multiple alerts at once."""
        try:
            cursor = self.db_manager.conn.cursor()
            cursor.executemany('UPDATE alerts SET status = ? WHERE id = ?', [(status, aid) for aid in alert_ids])
            self.db_manager.conn.commit()
            print(f"[+] Bulk updated {len(alert_ids)} alerts to '{status}'")
            return True
        except Exception as e:
            print(f"[-] Error bulk updating alerts: {str(e)}")
            return False
