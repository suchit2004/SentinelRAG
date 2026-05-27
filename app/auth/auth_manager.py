import hashlib
import json
import os

def hash_password(password: str) -> str:
    """
    Hashes a password using SHA-256.
    """
    return hashlib.sha256(password.encode()).hexdigest()

class AuthManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Resolve relative path from project root
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            self.db_path = os.path.join(base_dir, "data", "users.json")
        else:
            self.db_path = db_path
            
        self.users = {}
        self.load_users()

    def load_users(self):
        """
        Loads users from the JSON database file.
        """
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    self.users = json.load(f)
            except Exception as e:
                print(f"Error loading user database: {e}")
                self.users = {}
        else:
            self.users = {}

