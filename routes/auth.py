"""
Authentication Routes Module
Handles user registration, login, logout, and session management
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash
from models.models import db, User
from utils.helpers import validate_email
from utils.currency import validate_currency
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration endpoint
    
    GET: Render registration page
    POST: Register new user
    
    Expected JSON:
    {
        "username": "string",
        "email": "string",
        "password": "string",
        "confirm_password": "string"
    }
    
    Returns:
        JSON response with success/error message
    """
    if request.method == 'POST':
        # Get data from form or JSON
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        preferred_currency = data.get('preferred_currency', '').upper() or 'INR'
        preferred_currency_symbol = data.get('preferred_currency_symbol')
        
        # Validation
        if not username or not email or not password:
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        if len(username) < 3:
            return jsonify({
                'success': False,
                'message': 'Username must be at least 3 characters'
            }), 400
        
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters'
            }), 400
        
        if password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'Passwords do not match'
            }), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({
                'success': False,
                'message': 'Username already exists'
            }), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            }), 409
        
        # Create new user
        try:
            # Validate preferred currency
            if preferred_currency and not validate_currency(preferred_currency):
                return jsonify({'success': False, 'message': 'Unsupported preferred currency'}), 400

            user = User(username=username, email=email, preferred_currency=preferred_currency)
            if preferred_currency_symbol:
                user.preferred_currency_symbol = str(preferred_currency_symbol)[:10]
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Registration successful! Please log in.',
                'user_id': user.id
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }), 500
    
    # GET request - render registration page
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login endpoint
    
    GET: Render login page
    POST: Authenticate user
    
    Expected JSON:
    {
        "username": "string",
        "password": "string"
    }
    
    Returns:
        JSON response with success/error message and session token
    """
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # Find user and verify password
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Create session
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user_id': user.id,
                'username': user.username
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
    
    # GET request - render login page
    return render_template('auth/login.html')


@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """
    User logout endpoint
    Clears user session
    
    Returns:
        JSON response with success message
    """
    session.clear()
    
    if request.is_json:
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
    else:
        flash('Logged out successfully', 'success')
        return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """
    Get current user profile
    
    Returns:
        JSON response with user data
    """
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({
            'success': False,
            'message': 'Not authenticated'
        }), 401
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            'success': False,
            'message': 'User not found'
        }), 404
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    """
    Check if user is authenticated
    
    Returns:
        JSON response with authentication status
    """
    user_id = session.get('user_id')
    
    return jsonify({
        'authenticated': user_id is not None,
        'user_id': user_id,
        'username': session.get('username')
    }), 200
