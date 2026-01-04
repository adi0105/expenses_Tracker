"""
Expense Routes Module
Handles expense CRUD operations and AI-based classification
"""

from flask import Blueprint, request, jsonify, session
from models.models import db, Expense
from services.llm_service import get_llm_service
from utils.helpers import validate_amount, validate_date
from datetime import date, datetime
from sqlalchemy import func

expense_bp = Blueprint('expenses', __name__, url_prefix='/api/expenses')


@expense_bp.before_request
def require_login():
    """Verify user is authenticated before processing requests"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401


@expense_bp.route('/add', methods=['POST'])
def add_expense():
    """
    Add a new expense with optional AI classification
    
    Expected JSON:
    {
        "amount": float,
        "description": string,
        "category": string (optional),
        "date": string (YYYY-MM-DD, optional - defaults to today),
        "ai_classify": boolean (optional - defaults to false)
    }
    
    Returns:
        JSON response with created expense data
    """
    user_id = session['user_id']
    data = request.get_json() or {}
    
    # Validation
    amount = data.get('amount')
    description = data.get('description', '').strip()
    category = data.get('category', '').strip()
    date_str = data.get('date')
    ai_classify = data.get('ai_classify', False)
    
    # Validate amount
    is_valid, error = validate_amount(amount)
    if not is_valid:
        return jsonify({'success': False, 'message': error}), 400
    
    if not description:
        return jsonify({'success': False, 'message': 'Description is required'}), 400
    
    # Validate and parse date
    if date_str:
        is_valid, parsed_date, error = validate_date(date_str)
        if not is_valid:
            return jsonify({'success': False, 'message': error}), 400
    else:
        parsed_date = date.today()
    
    try:
        # Classify expense using AI if requested
        if ai_classify:
            llm_service = get_llm_service()
            if llm_service:
                classified_category = llm_service.classify_expense(description)
                if classified_category:
                    category = classified_category
                    ai_classified = True
                else:
                    ai_classified = False
                    if not category:
                        category = 'Other'
            else:
                ai_classified = False
                if not category:
                    category = 'Other'
        else:
            ai_classified = False
            if not category:
                category = 'Other'
        
        # Create expense record
        expense = Expense(
            user_id=user_id,
            amount=float(amount),
            description=description,
            category=category,
            date=parsed_date,
            ai_classified=ai_classified
        )
        
        db.session.add(expense)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Expense added successfully',
            'expense': expense.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error adding expense: {str(e)}'}), 500


@expense_bp.route('/list', methods=['GET'])
def get_expenses():
    """
    Get all expenses for the current user with optional filtering
    
    Query Parameters:
    - month: int (1-12, optional)
    - year: int (optional)
    - category: string (optional)
    - limit: int (optional, default 100)
    - offset: int (optional, default 0)
    
    Returns:
        JSON response with list of expenses
    """
    user_id = session['user_id']
    
    # Get query parameters
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    category = request.args.get('category', '').strip()
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Build query
    query = Expense.query.filter_by(user_id=user_id)
    
    # Filter by month/year
    if month and year:
        query = query.filter(
            func.extract('month', Expense.date) == month,
            func.extract('year', Expense.date) == year
        )
    elif year:
        query = query.filter(func.extract('year', Expense.date) == year)
    
    # Filter by category
    if category:
        query = query.filter_by(category=category)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination and sorting
    expenses = query.order_by(Expense.date.desc()).offset(offset).limit(limit).all()
    
    return jsonify({
        'success': True,
        'total': total_count,
        'count': len(expenses),
        'expenses': [expense.to_dict() for expense in expenses]
    }), 200


@expense_bp.route('/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """
    Get a specific expense by ID
    
    Returns:
        JSON response with expense data
    """
    user_id = session['user_id']
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    
    if not expense:
        return jsonify({'success': False, 'message': 'Expense not found'}), 404
    
    return jsonify({
        'success': True,
        'expense': expense.to_dict()
    }), 200


@expense_bp.route('/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """
    Update an existing expense
    
    Expected JSON:
    {
        "amount": float (optional),
        "description": string (optional),
        "category": string (optional),
        "date": string (optional)
    }
    
    Returns:
        JSON response with updated expense data
    """
    user_id = session['user_id']
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    
    if not expense:
        return jsonify({'success': False, 'message': 'Expense not found'}), 404
    
    data = request.get_json() or {}
    
    try:
        # Update fields if provided
        if 'amount' in data:
            is_valid, error = validate_amount(data['amount'])
            if not is_valid:
                return jsonify({'success': False, 'message': error}), 400
            expense.amount = float(data['amount'])
        
        if 'description' in data:
            description = data['description'].strip()
            if description:
                expense.description = description
        
        if 'category' in data:
            category = data['category'].strip()
            if category:
                expense.category = category
        
        if 'date' in data:
            is_valid, parsed_date, error = validate_date(data['date'])
            if not is_valid:
                return jsonify({'success': False, 'message': error}), 400
            expense.date = parsed_date
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Expense updated successfully',
            'expense': expense.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error updating expense: {str(e)}'}), 500


@expense_bp.route('/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """
    Delete an expense
    
    Returns:
        JSON response with success message
    """
    user_id = session['user_id']
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    
    if not expense:
        return jsonify({'success': False, 'message': 'Expense not found'}), 404
    
    try:
        db.session.delete(expense)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Expense deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error deleting expense: {str(e)}'}), 500


@expense_bp.route('/classify', methods=['POST'])
def classify_expense():
    """
    Classify an expense description using AI
    
    Expected JSON:
    {
        "description": string
    }
    
    Returns:
        JSON response with classified category
    """
    data = request.get_json() or {}
    description = data.get('description', '').strip()
    
    if not description:
        return jsonify({'success': False, 'message': 'Description is required'}), 400
    
    try:
        llm_service = get_llm_service()
        
        if not llm_service:
            return jsonify({
                'success': False,
                'message': 'LLM service not available'
            }), 503
        
        category = llm_service.classify_expense(description)
        
        if category:
            return jsonify({
                'success': True,
                'category': category
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to classify expense'
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Classification error: {str(e)}'}), 500
