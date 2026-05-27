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

    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Validates username and password. Returns True if valid, False otherwise.
        """
        if username not in self.users:
            return False
        
        hashed = hash_password(password)
        return self.users[username]["password_hash"] == hashed

    def get_user_role(self, username: str):
        """
        Returns the Role enum of the user if found, default to Role.EMPLOYEE.
        """
        from app.ingestion.rbac_metadata import Role
        if username in self.users:
            role_str = self.users[username].get("role", "EMPLOYEE")
            return Role.from_str(role_str)
        return Role.EMPLOYEE

    def save_users(self) -> bool:
        """
        Saves users dictionary back to the JSON database file.
        """
        try:
            # Ensure directories exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, "w") as f:
                json.dump(self.users, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving user database: {e}")
            return False

    def register_user(self, username: str, password: str, role_str: str) -> bool:
        """
        Registers a new user in the database. Returns True if success, False if user already exists.
        """
        if username in self.users:
            return False
            
        self.users[username] = {
            "role": role_str.upper(),
            "password_hash": hash_password(password)
        }
        return self.save_users()



