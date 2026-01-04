"""
Settings Routes Module
Handles user settings including currency preferences
"""

from flask import Blueprint, request, jsonify, session
from models.models import db, User
from utils.currency import get_currency_list, validate_currency, get_currency_info
from datetime import datetime

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')


@settings_bp.before_request
def require_login():
    """Verify user is authenticated before processing requests"""
    # Allow the currencies listing to be publicly available (used on registration)
    if request.endpoint == 'settings.list_currencies':
        return None

    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401


@settings_bp.route('/currency', methods=['GET'])
def get_currency_settings():
    """
    Get current currency preference
    
    Returns:
        JSON response with current currency and available options
    """
    user_id = session['user_id']
    
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'current_currency': user.preferred_currency,
            'available_currencies': get_currency_list(),
            'currency_info': get_currency_info(user.preferred_currency),
            'custom_symbol': getattr(user, 'preferred_currency_symbol', None)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@settings_bp.route('/currency', methods=['POST'])
def set_currency():
    """
    Change user's preferred currency
    
    Request body:
        {
            "currency": "USD"  # ISO 4217 code
        }
    
    Returns:
        JSON response with updated currency
    """
    user_id = session['user_id']
    data = request.get_json() or {}
    
    new_currency = data.get('currency', '').upper()
    new_symbol = data.get('symbol')
    
    if not new_currency:
        return jsonify({'success': False, 'message': 'Currency code is required'}), 400
    
    if not validate_currency(new_currency):
        return jsonify({
            'success': False,
            'message': f'Unsupported currency: {new_currency}',
            'available_currencies': get_currency_list()
        }), 400
    
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        old_currency = user.preferred_currency
        user.preferred_currency = new_currency
        # Optionally allow user to set a custom symbol
        if new_symbol is not None:
            # Trim and store short symbol
            user.preferred_currency_symbol = str(new_symbol)[:10]
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Currency changed from {old_currency} to {new_currency}',
            'old_currency': old_currency,
            'new_currency': new_currency,
            'currency_info': get_currency_info(new_currency),
            'custom_symbol': user.preferred_currency_symbol
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@settings_bp.route('/currencies', methods=['GET'])
def list_currencies():
    """
    Get list of all supported currencies
    
    Returns:
        JSON response with currency list
    """
    try:
        return jsonify({
            'success': True,
            'currencies': get_currency_list()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@settings_bp.route('/profile', methods=['GET'])
def get_profile():
    """
    Get user profile with settings
    
    Returns:
        JSON response with user info and settings
    """
    user_id = session['user_id']
    
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'preferred_currency': user.preferred_currency,
                'preferred_currency_symbol': getattr(user, 'preferred_currency_symbol', None),
                'created_at': user.created_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
