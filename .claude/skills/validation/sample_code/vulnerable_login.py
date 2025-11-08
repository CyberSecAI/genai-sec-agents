"""
Vulnerable login implementation for testing authentication-security skill activation.

This code contains INTENTIONAL security vulnerabilities to test if the
authentication-security skill detects them during review.

DO NOT USE IN PRODUCTION - FOR TESTING ONLY
"""

import hashlib
import sqlite3
from flask import Flask, request, session

app = Flask(__name__)
app.secret_key = "hardcoded-secret-key-12345"  # VULN: Hardcoded secret


def authenticate_user(username, password):
    """
    Authenticate user against database.

    VULNERABILITIES (should be detected by authentication-security skill):
    1. MD5 password hashing (weak crypto)
    2. SQL injection via string concatenation
    3. No rate limiting on login attempts
    4. No account lockout mechanism
    5. Session fixation vulnerability
    6. No password complexity requirements
    7. Timing attack vulnerability
    8. No MFA support
    """

    # VULN: MD5 is cryptographically broken
    password_hash = hashlib.md5(password.encode()).hexdigest()

    # VULN: SQL injection - string concatenation
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password_hash}'"
    cursor.execute(query)
    user = cursor.fetchone()

    # VULN: Timing attack - early return reveals if username exists
    if not user:
        return False

    # VULN: No account lockout after failed attempts
    # VULN: No rate limiting
    # VULN: Session fixation - not regenerating session ID
    session['user_id'] = user[0]
    session['username'] = user[1]

    return True


@app.route('/login', methods=['POST'])
def login():
    """
    Login endpoint.

    ADDITIONAL VULNERABILITIES:
    1. No CSRF protection
    2. Credentials over HTTP (no HTTPS enforcement)
    3. No input validation on username/password
    4. Password transmitted in plain text
    """
    username = request.form.get('username')  # VULN: No input validation
    password = request.form.get('password')  # VULN: No length limits

    # VULN: No validation of input
    if authenticate_user(username, password):
        return {"status": "success", "user": username}
    else:
        # VULN: Information disclosure - reveals if username exists
        return {"status": "error", "message": "Invalid username or password"}


def reset_password(username, new_password):
    """
    Password reset function.

    VULNERABILITIES:
    1. No password strength validation
    2. No length requirements
    3. MD5 hashing (weak)
    4. SQL injection
    5. No email verification
    6. No secure token for reset
    """
    # VULN: No password complexity check
    # VULN: No minimum length validation
    if len(new_password) < 6:  # VULN: Too short minimum
        return False

    # VULN: MD5 hashing
    password_hash = hashlib.md5(new_password.encode()).hexdigest()

    # VULN: SQL injection
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"UPDATE users SET password='{password_hash}' WHERE username='{username}'"
    cursor.execute(query)
    conn.commit()

    return True


def create_session(user_id):
    """
    Create user session.

    VULNERABILITIES:
    1. Weak session ID generation
    2. No session timeout
    3. No secure/httponly flags
    4. Session fixation
    """
    # VULN: Predictable session ID
    import random
    session_id = str(random.randint(100000, 999999))

    # VULN: No session timeout set
    # VULN: No secure flags
    session['id'] = session_id
    session['user_id'] = user_id
    session.permanent = True  # VULN: No expiration

    return session_id


# VULN: No HTTPS enforcement
if __name__ == '__main__':
    app.run(debug=True)  # VULN: Debug mode in production
