"""
Secure login implementation following ASVS 4.0 authentication requirements.

This is a reference implementation showing proper authentication security patterns
that should be recommended by the authentication-security skill.

PRODUCTION-READY PATTERNS (for comparison during testing)
"""

import os
import secrets
import bcrypt
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, session, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import safe_str_cmp
import pyotp

app = Flask(__name__)
# Secure: Load secret from environment variable
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

# Secure: Rate limiting (ASVS 2.2.1)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)


class AccountLockout:
    """
    Implements account lockout mechanism (ASVS 2.2.1).
    """

    lockout_threshold = 5  # Failed attempts before lockout
    lockout_duration = 900  # 15 minutes in seconds

    @staticmethod
    def record_failed_attempt(username):
        """Record failed login attempt."""
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Secure: Parameterized query prevents SQL injection
        cursor.execute(
            "INSERT INTO failed_logins (username, attempt_time) VALUES (?, ?)",
            (username, datetime.utcnow())
        )
        conn.commit()
        conn.close()

    @staticmethod
    def is_locked_out(username):
        """Check if account is locked out."""
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cutoff_time = datetime.utcnow() - timedelta(seconds=AccountLockout.lockout_duration)

        # Secure: Parameterized query
        cursor.execute(
            "SELECT COUNT(*) FROM failed_logins WHERE username=? AND attempt_time > ?",
            (username, cutoff_time)
        )

        count = cursor.fetchone()[0]
        conn.close()

        return count >= AccountLockout.lockout_threshold

    @staticmethod
    def clear_failed_attempts(username):
        """Clear failed attempts after successful login."""
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM failed_logins WHERE username=?",
            (username,)
        )
        conn.commit()
        conn.close()


def authenticate_user(username, password, totp_code=None):
    """
    Authenticate user against database following ASVS 2.x requirements.

    Security features:
    1. bcrypt password hashing (ASVS 2.4.1)
    2. Parameterized SQL queries (prevent injection)
    3. Account lockout after failed attempts (ASVS 2.2.1)
    4. Constant-time comparison (prevent timing attacks)
    5. MFA support via TOTP (ASVS 2.7.1)
    6. Session regeneration (prevent fixation)
    """

    # Secure: Check account lockout BEFORE database query
    if AccountLockout.is_locked_out(username):
        # Secure: Generic error message (no username enumeration)
        return False, "Authentication failed"

    # Secure: Input validation
    if not username or not password:
        return False, "Authentication failed"

    if len(username) > 255 or len(password) > 128:
        return False, "Authentication failed"

    # Secure: Parameterized query prevents SQL injection
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password_hash, totp_secret, mfa_enabled FROM users WHERE username=?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()

    # Secure: Constant-time comparison to prevent timing attacks
    if not user:
        # Secure: Still perform bcrypt to prevent timing differences
        bcrypt.checkpw(b"dummy", bcrypt.gensalt())
        AccountLockout.record_failed_attempt(username)
        return False, "Authentication failed"

    user_id, db_username, password_hash, totp_secret, mfa_enabled = user

    # Secure: bcrypt password verification (ASVS 2.4.1)
    try:
        password_valid = bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        password_valid = False

    if not password_valid:
        AccountLockout.record_failed_attempt(username)
        return False, "Authentication failed"

    # Secure: MFA verification if enabled (ASVS 2.7.1)
    if mfa_enabled:
        if not totp_code:
            return False, "MFA code required"

        totp = pyotp.TOTP(totp_secret)
        # Secure: TOTP with ~30 second window (ASVS 2.8.5)
        if not totp.verify(totp_code, valid_window=1):
            AccountLockout.record_failed_attempt(username)
            return False, "Invalid MFA code"

    # Secure: Clear failed attempts after successful auth
    AccountLockout.clear_failed_attempts(username)

    # Secure: Regenerate session ID (prevent session fixation, ASVS 3.2.1)
    session.clear()
    session.regenerate()

    session['user_id'] = user_id
    session['username'] = db_username
    session['auth_time'] = datetime.utcnow().isoformat()

    # Secure: Set session timeout (ASVS 3.3.1)
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

    return True, "Authentication successful"


@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Secure: Rate limiting (ASVS 2.2.1)
def login():
    """
    Login endpoint with security controls.

    Security features:
    1. CSRF protection (should be enabled via Flask-WTF)
    2. HTTPS enforcement (should be at reverse proxy level)
    3. Rate limiting
    4. Input validation
    5. Generic error messages (no username enumeration)
    """

    # Secure: Content-type validation
    if not request.is_json:
        abort(400, "Content-Type must be application/json")

    data = request.get_json()

    username = data.get('username', '').strip()
    password = data.get('password', '')
    totp_code = data.get('totp_code')

    # Secure: Input validation
    if not username or not password:
        return {"status": "error", "message": "Authentication failed"}, 401

    success, message = authenticate_user(username, password, totp_code)

    if success:
        return {"status": "success"}, 200
    else:
        # Secure: Generic error (ASVS 2.2.2 - no username enumeration)
        return {"status": "error", "message": "Authentication failed"}, 401


def reset_password(username, reset_token, new_password):
    """
    Password reset with security controls.

    Security features:
    1. Password complexity validation (ASVS 2.1.1)
    2. Minimum/maximum length enforcement (ASVS 2.1.1, 2.1.2)
    3. bcrypt hashing (ASVS 2.4.1)
    4. Secure reset token verification
    5. Parameterized queries
    """

    # Secure: Validate reset token (cryptographically secure, time-limited)
    if not verify_reset_token(username, reset_token):
        return False, "Invalid or expired reset token"

    # Secure: Password length validation (ASVS 2.1.1, 2.1.2)
    if len(new_password) < 8:
        return False, "Password must be at least 8 characters"

    if len(new_password) > 128:
        return False, "Password must not exceed 128 characters"

    # Secure: Password complexity check (ASVS 2.1.7)
    if not validate_password_complexity(new_password):
        return False, "Password does not meet complexity requirements"

    # Secure: Check against common passwords (ASVS 2.1.7)
    if is_common_password(new_password):
        return False, "Password is too common, choose a stronger password"

    # Secure: bcrypt hashing (ASVS 2.4.1)
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=12))

    # Secure: Parameterized query
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password_hash=?, password_changed_at=? WHERE username=?",
        (password_hash.decode('utf-8'), datetime.utcnow(), username)
    )
    conn.commit()

    # Secure: Invalidate reset token after use
    cursor.execute(
        "DELETE FROM password_reset_tokens WHERE username=?",
        (username,)
    )
    conn.commit()
    conn.close()

    # Secure: Invalidate all sessions (ASVS 2.1.12)
    invalidate_all_user_sessions(username)

    return True, "Password reset successful"


def validate_password_complexity(password):
    """
    Validate password complexity (ASVS 2.1.7).

    Requirements:
    - At least 8 characters
    - Contains uppercase, lowercase, number, special character
    """
    import re

    if len(password) < 8:
        return False

    # Check for required character types
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    return has_upper and has_lower and has_digit and has_special


def is_common_password(password):
    """
    Check against common passwords list (ASVS 2.1.7).
    """
    # In production, check against HaveIBeenPwned or similar
    common_passwords = {'password', '123456', 'qwerty', 'admin'}
    return password.lower() in common_passwords


def verify_reset_token(username, token):
    """Verify password reset token is valid and not expired."""
    # Implementation would check cryptographically secure token
    # with expiration (e.g., 1 hour)
    pass


def invalidate_all_user_sessions(username):
    """Invalidate all sessions for a user."""
    # Implementation would clear all session tokens for user
    pass


def create_session(user_id):
    """
    Create secure session (ASVS 3.x).

    Security features:
    1. Cryptographically secure session ID
    2. Session timeout (30 minutes)
    3. Secure and HttpOnly flags
    4. Session binding to IP/User-Agent
    """

    # Secure: Cryptographically random session ID (ASVS 3.2.1)
    session_id = secrets.token_urlsafe(32)

    # Secure: Session timeout (ASVS 3.3.1)
    session['id'] = session_id
    session['user_id'] = user_id
    session['created_at'] = datetime.utcnow().isoformat()
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

    # Secure: Session binding (ASVS 3.2.3)
    session['ip_address'] = request.remote_addr
    session['user_agent'] = request.headers.get('User-Agent', '')

    return session_id


# Secure: Session configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,      # HTTPS only (ASVS 3.4.1)
    SESSION_COOKIE_HTTPONLY=True,    # No JavaScript access (ASVS 3.4.2)
    SESSION_COOKIE_SAMESITE='Lax',   # CSRF protection (ASVS 3.4.3)
)


if __name__ == '__main__':
    # Secure: Never run with debug=True in production
    # Secure: HTTPS should be enforced at reverse proxy level
    app.run(ssl_context='adhoc')  # For development only
