"""
Income Routes Module
Handles income CRUD operations
"""

from flask import Blueprint, request, jsonify, session
from models.models import db, Income
from utils.helpers import validate_amount, validate_date
from datetime import date
from sqlalchemy import func

income_bp = Blueprint('incomes', __name__, url_prefix='/api/incomes')


@income_bp.before_request
def require_login():
    """Verify user is authenticated before processing requests"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401


@income_bp.route('/add', methods=['POST'])
def add_income():
    """
    Add a new income record
    
    Expected JSON:
    {
        "amount": float,
        "source": string,
        "date": string (YYYY-MM-DD, optional - defaults to today)
    }
    
    Returns:
        JSON response with created income data
    """
    user_id = session['user_id']
    data = request.get_json() or {}
    
    # Validation
    amount = data.get('amount')
    source = data.get('source', '').strip()
    date_str = data.get('date')
    
    # Validate amount
    is_valid, error = validate_amount(amount)
    if not is_valid:
        return jsonify({'success': False, 'message': error}), 400
    
    if not source:
        return jsonify({'success': False, 'message': 'Source is required'}), 400
    
    if len(source) > 120:
        return jsonify({'success': False, 'message': 'Source must be less than 120 characters'}), 400
    
    # Validate and parse date
    if date_str:
        is_valid, parsed_date, error = validate_date(date_str)
        if not is_valid:
            return jsonify({'success': False, 'message': error}), 400
    else:
        parsed_date = date.today()
    
    try:
        # Create income record
        income = Income(
            user_id=user_id,
            amount=float(amount),
            source=source,
            date=parsed_date
        )
        
        db.session.add(income)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Income added successfully',
            'income': income.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error adding income: {str(e)}'}), 500


@income_bp.route('/list', methods=['GET'])
def get_incomes():
    """
    Get all income records for the current user with optional filtering
    
    Query Parameters:
    - month: int (1-12, optional)
    - year: int (optional)
    - limit: int (optional, default 100)
    - offset: int (optional, default 0)
    
    Returns:
        JSON response with list of income records
    """
    user_id = session['user_id']
    
    # Get query parameters
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Build query
    query = Income.query.filter_by(user_id=user_id)
    
    # Filter by month/year
    if month and year:
        query = query.filter(
            func.extract('month', Income.date) == month,
            func.extract('year', Income.date) == year
        )
    elif year:
        query = query.filter(func.extract('year', Income.date) == year)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination and sorting
    incomes = query.order_by(Income.date.desc()).offset(offset).limit(limit).all()
    
    return jsonify({
        'success': True,
        'total': total_count,
        'count': len(incomes),
        'incomes': [income.to_dict() for income in incomes]
    }), 200


@income_bp.route('/<int:income_id>', methods=['GET'])
def get_income(income_id):
    """
    Get a specific income record by ID
    
    Returns:
        JSON response with income data
    """
    user_id = session['user_id']
    income = Income.query.filter_by(id=income_id, user_id=user_id).first()
    
    if not income:
        return jsonify({'success': False, 'message': 'Income record not found'}), 404
    
    return jsonify({
        'success': True,
        'income': income.to_dict()
    }), 200


@income_bp.route('/<int:income_id>', methods=['PUT'])
def update_income(income_id):
    """
    Update an existing income record
    
    Expected JSON:
    {
        "amount": float (optional),
        "source": string (optional),
        "date": string (optional)
    }
    
    Returns:
        JSON response with updated income data
    """
    user_id = session['user_id']
    income = Income.query.filter_by(id=income_id, user_id=user_id).first()
    
    if not income:
        return jsonify({'success': False, 'message': 'Income record not found'}), 404
    
    data = request.get_json() or {}
    
    try:
        # Update fields if provided
        if 'amount' in data:
            is_valid, error = validate_amount(data['amount'])
            if not is_valid:
                return jsonify({'success': False, 'message': error}), 400
            income.amount = float(data['amount'])
        
        if 'source' in data:
            source = data['source'].strip()
            if source:
                income.source = source
        
        if 'date' in data:
            is_valid, parsed_date, error = validate_date(data['date'])
            if not is_valid:
                return jsonify({'success': False, 'message': error}), 400
            income.date = parsed_date
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Income updated successfully',
            'income': income.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error updating income: {str(e)}'}), 500


@income_bp.route('/<int:income_id>', methods=['DELETE'])
def delete_income(income_id):
    """
    Delete an income record
    
    Returns:
        JSON response with success message
    """
    user_id = session['user_id']
    income = Income.query.filter_by(id=income_id, user_id=user_id).first()
    
    if not income:
        return jsonify({'success': False, 'message': 'Income record not found'}), 404
    
    try:
        db.session.delete(income)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Income deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error deleting income: {str(e)}'}), 500
