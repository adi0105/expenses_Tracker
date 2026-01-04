"""
Utility functions and helpers for the Expense Tracker application
"""
from functools import wraps
from flask import session, redirect, url_for, flash
from datetime import datetime, date


def login_required(f):
    """
    Decorator to protect routes that require authentication
    Redirects to login page if user is not authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def validate_email(email):
    """
    Validate email format
    
    Args:
        email: Email string to validate
    
    Returns:
        bool: True if email is valid
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_amount(amount):
    """
    Validate that amount is a positive number
    
    Args:
        amount: Amount to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            return False, "Amount must be greater than 0"
        return True, None
    except (ValueError, TypeError):
        return False, "Invalid amount format"


def validate_date(date_str):
    """
    Validate date format (YYYY-MM-DD)
    
    Args:
        date_str: Date string to validate
    
    Returns:
        tuple: (is_valid, parsed_date, error_message)
    """
    try:
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        if parsed_date > date.today():
            return False, None, "Date cannot be in the future"
        return True, parsed_date, None
    except ValueError:
        return False, None, "Invalid date format. Use YYYY-MM-DD"


def format_currency(amount):
    """
    Format amount as currency string
    
    Args:
        amount: Numeric amount
    
    Returns:
        str: Formatted currency string
    """
    return f"${amount:,.2f}"


def get_month_name(month_num):
    """
    Get month name from month number
    
    Args:
        month_num: Month number (1-12)
    
    Returns:
        str: Month name
    """
    months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    return months[month_num - 1] if 1 <= month_num <= 12 else 'Unknown'


def get_current_month_year():
    """
    Get current month and year
    
    Returns:
        tuple: (month_num, year, month_name)
    """
    today = date.today()
    month_name = get_month_name(today.month)
    return today.month, today.year, month_name
