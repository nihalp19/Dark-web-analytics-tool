import sqlite3
import json
from datetime import datetime
from config import DATABASE_CONFIG

# ---------------- Database Manager ----------------
class DataBaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or DATABASE_CONFIG['path']
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            print(f"[+] Connected to database: {self.db_path}")
        except Exception as e:
            print(f"[-] Database connection error: {str(e)}")

    def create_tables(self):
        cursor = self.conn.cursor()
        for table_name, table_sql in DATABASE_CONFIG['tables'].items():
            try:
                cursor.execute(table_sql)
                print(f"[+] Table '{table_name}' created or already exists")
            except Exception as e:
                print(f"[-] Error creating table '{table_name}': {str(e)}")
        self.conn.commit()

    # ---------------- Websites ----------------
    def store_website(self, url, title, content, website_type, geo_location, risk_level=0):
        cursor = self.conn.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO websites
                (url, title, content, type, first_seen, last_seen, geo_location, risk_level)
                VALUES (?, ?, ?, ?, COALESCE((SELECT first_seen FROM websites WHERE url = ?), ?), ?, ?, ?)
            ''', (url, title, content, website_type, url, current_date, current_date, geo_location, risk_level))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[-] Error storing website: {str(e)}")
            return False

    # ---------------- Users ----------------
    def store_user(self, username, pgp_key, email, marketplaces, products, geo_location, risk_level=0):
        cursor = self.conn.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users
                (username, pgp_key, email, marketplaces, products, last_active, geo_location, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, pgp_key, email,
                  json.dumps(marketplaces) if marketplaces else None,
                  json.dumps(products) if products else None,
                  current_date, geo_location, risk_level))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[-] Error storing user: {str(e)}")
            return False

    # ---------------- Search Results ----------------
    def store_search_result(self, keyword, url, title, snippet, relevance=0):
        cursor = self.conn.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")
        try:
            cursor.execute('''
                INSERT INTO search_results (keyword, url, title, snippet, relevance, date_found)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (keyword, url, title, snippet, relevance, current_date))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[-] Error storing search result: {str(e)}")
            return False

    def get_search_results(self, keyword=None, limit=50):
        cursor = self.conn.cursor()
        try:
            if keyword:
                cursor.execute('''
                    SELECT * FROM search_results
                    WHERE keyword = ?
                    ORDER BY date_found DESC, relevance DESC
                    LIMIT ?
                ''', (keyword, limit))
            else:
                cursor.execute('''
                    SELECT * FROM search_results
                    ORDER BY date_found DESC, relevance DESC
                    LIMIT ?
                ''', (limit,))
            return cursor.fetchall()
        except Exception as e:
            print(f"[-] Error retrieving search results: {str(e)}")
            return []

    def get_all_urls(self):
        """Retrieve all website URLs from the database"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('SELECT url FROM websites')
            urls = [row[0] for row in cursor.fetchall()]
            return urls
        except Exception as e:
            print(f"[-] Error retrieving URLs: {str(e)}")
            return []

    # ---------------- Close Connection ----------------
    def close(self):
        if self.conn:
            self.conn.close()
            print("[+] Database connection closed")
