"""
Tests for secure signup functionality with MFA enrollment.

Following TDD approach - tests written BEFORE implementation.
"""

import pytest
import sqlite3
import os
import tempfile
from datetime import datetime
from secure_login import app, validate_password_complexity, is_common_password


@pytest.fixture
def client():
    """Create test client with temporary database."""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()

    # Initialize test database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            totp_secret TEXT,
            mfa_enabled INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            password_changed_at TIMESTAMP
        )
    """)

    # Create failed_logins table
    cursor.execute("""
        CREATE TABLE failed_logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            attempt_time TIMESTAMP NOT NULL
        )
    """)

    conn.commit()
    conn.close()

    # Configure app for testing
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path

    with app.test_client() as client:
        yield client

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


def test_signup_creates_user_with_valid_data(client):
    """Test that signup creates a user with valid username, email, and password."""
    # This test MUST fail first because signup_user doesn't exist yet
    from secure_login import signup_user

    username = "testuser"
    email = "test@example.com"
    password = "SecurePass123!"

    success, message, user_data = signup_user(username, email, password)

    assert success is True
    assert "created successfully" in message.lower()
    assert user_data is not None
    assert user_data['username'] == username
    assert user_data['email'] == email


def test_signup_rejects_weak_password(client):
    """Test that signup rejects passwords that don't meet complexity requirements."""
    from secure_login import signup_user

    username = "testuser"
    email = "test@example.com"
    weak_password = "password"  # No uppercase, no numbers, no special chars

    success, message, user_data = signup_user(username, email, weak_password)

    assert success is False
    assert "complexity" in message.lower()
    assert user_data is None


def test_signup_rejects_common_password(client):
    """Test that signup rejects common passwords."""
    from secure_login import signup_user

    username = "testuser"
    email = "test@example.com"
    common_password = "Password123!"  # Meets complexity but is common

    success, message, user_data = signup_user(username, email, common_password)

    assert success is False
    assert "common" in message.lower()


def test_signup_validates_password_length(client):
    """Test that signup enforces minimum and maximum password length."""
    from secure_login import signup_user

    username = "testuser"
    email = "test@example.com"

    # Too short
    short_password = "Short1!"
    success, message, _ = signup_user(username, email, short_password)
    assert success is False
    assert "8 characters" in message

    # Too long
    long_password = "A" * 129 + "a1!"
    success, message, _ = signup_user(username, email, long_password)
    assert success is False
    assert "128 characters" in message


def test_signup_prevents_duplicate_username(client):
    """Test that signup prevents duplicate usernames."""
    from secure_login import signup_user

    username = "testuser"
    email1 = "test1@example.com"
    email2 = "test2@example.com"
    password = "SecurePass123!"

    # First signup should succeed
    success1, _, _ = signup_user(username, email1, password)
    assert success1 is True

    # Second signup with same username should fail
    success2, message, _ = signup_user(username, email2, password)
    assert success2 is False
    assert "username" in message.lower() or "exists" in message.lower()


def test_signup_prevents_duplicate_email(client):
    """Test that signup prevents duplicate email addresses."""
    from secure_login import signup_user

    username1 = "testuser1"
    username2 = "testuser2"
    email = "test@example.com"
    password = "SecurePass123!"

    # First signup should succeed
    success1, _, _ = signup_user(username1, email, password)
    assert success1 is True

    # Second signup with same email should fail
    success2, message, _ = signup_user(username2, email, password)
    assert success2 is False
    assert "email" in message.lower() or "exists" in message.lower()


def test_signup_with_mfa_enrollment(client):
    """Test that signup can enroll user in MFA and return TOTP secret."""
    from secure_login import signup_user

    username = "mfauser"
    email = "mfa@example.com"
    password = "SecurePass123!"
    enable_mfa = True

    success, message, user_data = signup_user(username, email, password, enable_mfa=enable_mfa)

    assert success is True
    assert user_data is not None
    assert 'totp_secret' in user_data
    assert user_data['totp_secret'] is not None
    assert len(user_data['totp_secret']) > 0
    assert user_data['mfa_enabled'] is True


def test_signup_without_mfa(client):
    """Test that signup works without MFA enrollment."""
    from secure_login import signup_user

    username = "nomfauser"
    email = "nomfa@example.com"
    password = "SecurePass123!"
    enable_mfa = False

    success, message, user_data = signup_user(username, email, password, enable_mfa=enable_mfa)

    assert success is True
    assert user_data is not None
    assert user_data['mfa_enabled'] is False


def test_signup_endpoint_accepts_valid_request(client):
    """Test /signup endpoint accepts valid JSON request."""
    response = client.post('/signup', json={
        'username': 'apiuser',
        'email': 'api@example.com',
        'password': 'SecurePass123!',
        'enable_mfa': True
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'user' in data
    # Secure: Raw secret should NOT be in response, only URI
    assert 'totp_secret' not in data['user']
    assert 'totp_uri' in data['user']


def test_signup_endpoint_rate_limiting(client):
    """Test that signup endpoint has rate limiting."""
    # Make multiple requests rapidly
    for i in range(6):  # Exceed rate limit of 5 per minute
        response = client.post('/signup', json={
            'username': f'user{i}',
            'email': f'user{i}@example.com',
            'password': 'SecurePass123!'
        })

    # Last request should be rate limited
    assert response.status_code == 429


def test_signup_endpoint_validates_content_type(client):
    """Test that signup endpoint requires JSON content type."""
    response = client.post('/signup', data='not json')

    assert response.status_code == 400


def test_signup_endpoint_validates_required_fields(client):
    """Test that signup endpoint validates required fields."""
    # Missing username
    response = client.post('/signup', json={
        'email': 'test@example.com',
        'password': 'SecurePass123!'
    })
    assert response.status_code == 400

    # Missing email
    response = client.post('/signup', json={
        'username': 'testuser',
        'password': 'SecurePass123!'
    })
    assert response.status_code == 400

    # Missing password
    response = client.post('/signup', json={
        'username': 'testuser',
        'email': 'test@example.com'
    })
    assert response.status_code == 400


def test_password_hashing_uses_bcrypt(client):
    """Test that passwords are hashed with bcrypt (not stored in plaintext)."""
    from secure_login import signup_user
    import sqlite3

    username = "hashtest"
    email = "hash@example.com"
    password = "SecurePass123!"

    success, _, _ = signup_user(username, email, password)
    assert success is True

    # Verify password is hashed in database
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    assert result is not None
    password_hash = result[0]

    # Bcrypt hashes start with $2b$ and are 60 characters
    assert password_hash.startswith('$2b$')
    assert len(password_hash) == 60
    assert password_hash != password  # Not plaintext
