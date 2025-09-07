import re
import json
from datetime import datetime, timedelta

class UserTracker:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    # ---------------- Track a User ----------------
    def track_user(self, username: str, pgp_key: str = None, email: str = None) -> dict | None:
        """
        Track a specific user across platforms and store information.
        Returns user information if successful, else None.
        """
        print(f"[+] Tracking user: {username}")

        user_info = self._simulate_user_search(username, pgp_key, email)

        # Store user info in DB
        if self.db_manager.store_user(
            username=user_info['username'],
            pgp_key=user_info['pgp_key'],
            email=user_info['email'],
            marketplaces=json.dumps(user_info['marketplaces']),
            products=json.dumps(user_info['products']),
            geo_location=user_info['geo_location'],
            risk_level=user_info['risk_level']
        ):
            print(f"[+] User {username} tracked and information stored successfully.")
            return user_info
        else:
            print(f"[-] Failed to track user {username}")
            return None

    # ---------------- Simulated User Search ----------------
    def _simulate_user_search(self, username: str, pgp_key: str, email: str) -> dict:
        """
        Simulate finding user information across dark web platforms.
        Replace with actual search logic for real implementation.
        """
        return {
            "username": username,
            "pgp_key": pgp_key or f"Simulated PGP Key for {username}",
            "email": email or f"{username}@example.mail",
            "marketplaces": ["Example Market", "Dark Marketplace"],
            "products": ["Product A", "Product B"],
            "last_active": datetime.now().strftime("%Y-%m-%d"),
            "geo_location": "Unknown",
            "risk_level": 7
        }

    # ---------------- Find Similar Users ----------------
    def find_similar_users(self, username: str, threshold: float = 0.7) -> list:
        """
        Find usernames similar to the given username based on character overlap.
        """
        cursor = self.db_manager.conn.cursor()
        try:
            cursor.execute('SELECT username FROM users')
            all_users = [row[0] for row in cursor.fetchall()]

            similar_users = [
                user for user in all_users
                if user != username and self._similarity_score(username, user) >= threshold
            ]
            return similar_users
        except Exception as e:
            print(f"[-] Error finding similar users: {str(e)}")
            return []

    # ---------------- Similarity Score ----------------
    def _similarity_score(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using Jaccard index.
        """
        set1, set2 = set(str1.lower()), set(str2.lower())
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return len(intersection) / len(union) if union else 0.0

    # ---------------- User Activity Timeline ----------------
    def get_user_activity(self, username: str, days: int = 30) -> list:
        """
        Simulate user activity timeline over the past 'days' days.
        Returns a list of activity dictionaries.
        """
        activity = []
        for i in range(days):
            if hash(username + str(i)) % 5 == 0:  # Random activity simulation
                activity.append({
                    'date': (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                    'action': 'Posted listing' if i % 2 == 0 else 'Commented on forum',
                    'location': 'Example Market' if i % 2 == 0 else 'Dark Forum'
                })
        return activity
