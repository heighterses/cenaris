from functools import wraps
from flask import redirect, url_for, flash, request
from flask_login import current_user

def login_required(f):
    """
    Custom login required decorator with better error handling.
    This supplements Flask-Login's login_required decorator.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please sign in to access this page.', 'info')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def anonymous_required(f):
    """
    Decorator to ensure user is not logged in.
    Redirects authenticated users to dashboard.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to require admin privileges.
    For future use when admin functionality is added.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please sign in to access this page.', 'info')
            return redirect(url_for('auth.login', next=request.url))
        
        # For now, check if user email contains 'admin'
        # This can be enhanced with proper role management later
        if 'admin' not in current_user.email.lower():
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function