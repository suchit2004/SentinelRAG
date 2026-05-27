import pytest
import os
import json
from app.auth.auth_manager import AuthManager, hash_password
from app.ingestion.rbac_metadata import Role

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_users.json"
    # Write empty database
    with open(db_file, "w") as f:
        json.dump({}, f)
    return str(db_file)

def test_hash_password():
    password = "password123"
    h1 = hash_password(password)
    h2 = hash_password(password)
    assert h1 == h2
    assert len(h1) == 64

def test_auth_manager_register(temp_db):
    auth = AuthManager(db_path=temp_db)
    
    # Registration should succeed
    assert auth.register_user("test_user", "pass123", "EXECUTIVE") is True
    assert "test_user" in auth.users
    assert auth.users["test_user"]["role"] == "EXECUTIVE"
    
    # Duplicate registration should fail
    assert auth.register_user("test_user", "otherpass", "EMPLOYEE") is False

def test_auth_manager_authenticate(temp_db):
    auth = AuthManager(db_path=temp_db)
    auth.register_user("bob", "secret", "EMPLOYEE")
    
    assert auth.authenticate_user("bob", "secret") is True
    assert auth.authenticate_user("bob", "wrong_secret") is False
    assert auth.authenticate_user("unknown", "secret") is False

def test_auth_manager_get_role(temp_db):
    auth = AuthManager(db_path=temp_db)
    auth.register_user("alice", "secure", "ADMIN")
    
    assert auth.get_user_role("alice") == Role.ADMIN
    # Default fallback role
    assert auth.get_user_role("unknown") == Role.EMPLOYEE
