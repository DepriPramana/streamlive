"""
Authentication Module
Handles user authentication and authorization
"""
from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

# Default credentials
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD_HASH = generate_password_hash('admin123')

def check_auth(username, password):
    """Check if username/password is valid"""
    # For now, use simple check
    # In production, check against database
    return username == DEFAULT_USERNAME and check_password_hash(DEFAULT_PASSWORD_HASH, password)

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
