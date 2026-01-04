"""
Transaction Routes Module
Handles transaction message processing, auto-detection, and balance management

APIs:
- POST /api/transactions/upload-message - Process transaction message
- GET /api/transactions/auto - Get auto-detected transactions
- PUT /api/transactions/:id - Edit transaction
- DELETE /api/transactions/:id - Delete transaction
- GET /api/balance - Get user balance
- POST /api/transactions/statistics - Get transaction statistics
"""

from flask import Blueprint, request, jsonify, session
from models.models import db, Expense, Transaction
from services.transaction_service import get_transaction_service
from utils.helpers import login_required, validate_amount
from datetime import datetime, date

transactions_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

# Initialize transaction service lazily to avoid blocking app startup
_transaction_service = None

def _get_service():
    global _transaction_service
    if _transaction_service is None:
        _transaction_service = get_transaction_service()
    return _transaction_service


@transactions_bp.route('/upload-message', methods=['POST'])
@login_required
def upload_transaction_message():
    """
    Process a transaction message (SMS/alert/notification)
    
    Expected JSON:
    {
        "message": "₹2,500 debited from your account via UPI at Amazon"
    }
    
    Returns:
        - success: Boolean indicating if message was processed
        - data: Parsed transaction data or error details
        - message: User-friendly message
        - balance: Updated balance if successful
    """
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'message': 'Message text is required'
            }), 400
        
        message_text = data['message'].strip()
        
        if len(message_text) < 10:
            return jsonify({
                'success': False,
                'message': 'Message is too short. Please provide a complete transaction message.'
            }), 400
        
        if len(message_text) > 2000:
            return jsonify({
                'success': False,
                'message': 'Message is too long. Maximum 2000 characters allowed.'
            }), 400
        
        # Process the message
        success, parsed_data, result_message = _get_service().process_transaction_message(
            user_id=user_id,
            message_text=message_text
        )
        
        response_data = {
            'success': success,
            'message': result_message,
            'data': parsed_data
        }
        
        # Include updated balance if successful
        if success:
            balance = _get_service().get_user_balance(user_id)
            response_data['balance'] = balance
        
        return jsonify(response_data), 200 if success else 400
    
    except Exception as e:
        print(f"Error uploading transaction message: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@transactions_bp.route('/auto', methods=['GET'])
@login_required
def get_auto_transactions():
    """
    Get auto-detected transactions for the user
    
    Query Parameters:
    - month: Month (1-12)
    - year: Year (e.g., 2024)
    - limit: Max results (default: 50)
    - offset: Pagination offset (default: 0)
    
    Returns:
        - transactions: List of auto-detected transaction objects
        - total: Total count of matching transactions
    """
    try:
        user_id = session.get('user_id')
        
        # Get query parameters
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate limits
        limit = min(limit, 100)  # Max 100 per request
        offset = max(offset, 0)
        
        # Get auto-detected transactions
        transactions, total = _get_service().get_auto_detected_transactions(
            user_id=user_id,
            month=month,
            year=year,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'success': True,
            'transactions': transactions,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
    
    except Exception as e:
        print(f"Error fetching auto transactions: {e}")
        return jsonify({
            'success': False,
            'message': f'Error fetching transactions: {str(e)}'
        }), 500


@transactions_bp.route('/<int:transaction_id>', methods=['PUT'])
@login_required
def edit_auto_transaction(transaction_id):
    """
    Edit an auto-detected transaction
    
    Expected JSON (any of these fields):
    {
        "amount": 2500,
        "category": "Shopping",
        "description": "Amazon purchase",
        "merchant_or_source": "Amazon"
    }
    
    Returns:
        - success: Boolean
        - message: Result message
        - transaction: Updated transaction data
    """
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate amount if provided
        if 'amount' in data:
            is_valid, error_msg = validate_amount(data['amount'])
            if not is_valid:
                return jsonify({
                    'success': False,
                    'message': error_msg
                }), 400
        
        # Edit the transaction
        success, message = _get_service().edit_auto_transaction(
            expense_id=transaction_id,
            user_id=user_id,
            updates=data
        )
        
        if success:
            # Fetch updated transaction
            expense = Expense.query.get(transaction_id)
            return jsonify({
                'success': True,
                'message': message,
                'transaction': expense.to_dict() if expense else None
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
    
    except Exception as e:
        print(f"Error editing transaction: {e}")
        return jsonify({
            'success': False,
            'message': f'Error editing transaction: {str(e)}'
        }), 500


@transactions_bp.route('/<int:transaction_id>', methods=['DELETE'])
@login_required
def delete_auto_transaction(transaction_id):
    """
    Delete an auto-detected transaction
    
    Reverses the balance update and removes the transaction
    
    Returns:
        - success: Boolean
        - message: Result message
        - balance: Updated balance
    """
    try:
        user_id = session.get('user_id')
        
        # Delete the transaction
        success, message = _get_service().delete_auto_transaction(
            expense_id=transaction_id,
            user_id=user_id
        )
        
        response_data = {
            'success': success,
            'message': message
        }
        
        # Include updated balance
        if success:
            balance = _get_service().get_user_balance(user_id)
            response_data['balance'] = balance
        
        return jsonify(response_data), 200 if success else 400
    
    except Exception as e:
        print(f"Error deleting transaction: {e}")
        return jsonify({
            'success': False,
            'message': f'Error deleting transaction: {str(e)}'
        }), 500


# Balance routes
balance_bp = Blueprint('balance', __name__, url_prefix='/api/balance')


@balance_bp.route('/current', methods=['GET'])
@login_required
def get_current_balance():
    """
    Get user's current balance
    
    Returns:
        - current_balance: Current balance
        - total_credits: Total credits so far
        - total_debits: Total debits so far
        - last_updated: Timestamp of last update
    """
    try:
        user_id = session.get('user_id')
        balance = _get_service().get_user_balance(user_id)
        
        return jsonify({
            'success': True,
            'balance': balance
        }), 200
    
    except Exception as e:
        print(f"Error fetching balance: {e}")
        return jsonify({
            'success': False,
            'message': f'Error fetching balance: {str(e)}'
        }), 500


# Statistics route
@balance_bp.route('/statistics', methods=['GET'])
@login_required
def get_transaction_statistics():
    """
    Get transaction statistics (auto vs manual breakdown)
    
    Returns:
        - auto_detected: Auto-detected transaction stats
        - manual: Manual transaction stats
        - total_expenses: Total expenses
        - total_income: Total income
        - savings: Savings amount
    """
    try:
        user_id = session.get('user_id')
        stats = _get_service().get_transaction_statistics(user_id)
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
    
    except Exception as e:
        print(f"Error fetching statistics: {e}")
        return jsonify({
            'success': False,
            'message': f'Error fetching statistics: {str(e)}'
        }), 500
