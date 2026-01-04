"""
Summary & Insights Routes Module
Handles financial summaries and AI-generated insights
"""

from flask import Blueprint, request, jsonify, session
from models.models import db, Income, Expense
from services.llm_service import get_llm_service
from sqlalchemy import func
from datetime import date, datetime
import json

summary_bp = Blueprint('summary', __name__, url_prefix='/api/summary')


@summary_bp.before_request
def require_login():
    """Verify user is authenticated before processing requests"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401


@summary_bp.route('/monthly', methods=['GET'])
def get_monthly_summary():
    """
    Get monthly financial summary
    
    Query Parameters:
    - month: int (1-12, required)
    - year: int (required)
    
    Returns:
        JSON response with monthly summary including:
        - total_income
        - total_expenses
        - savings
        - category breakdown
    """
    user_id = session['user_id']
    
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    if not month or not year:
        return jsonify({'success': False, 'message': 'Month and year are required'}), 400
    
    if month < 1 or month > 12:
        return jsonify({'success': False, 'message': 'Month must be between 1 and 12'}), 400
    
    try:
        # Get total income for the month
        total_income = db.session.query(func.sum(Income.amount)).filter(
            Income.user_id == user_id,
            func.extract('month', Income.date) == month,
            func.extract('year', Income.date) == year
        ).scalar() or 0
        
        # Get total expenses for the month
        total_expenses = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            func.extract('month', Expense.date) == month,
            func.extract('year', Expense.date) == year
        ).scalar() or 0
        
        # Get expenses by category
        category_data = db.session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.user_id == user_id,
            func.extract('month', Expense.date) == month,
            func.extract('year', Expense.date) == year
        ).group_by(Expense.category).all()
        
        expenses_by_category = {cat: float(total) for cat, total in category_data}
        
        # Sort by amount descending
        sorted_categories = sorted(expenses_by_category.items(), key=lambda x: x[1], reverse=True)
        
        savings = total_income - total_expenses
        
        return jsonify({
            'success': True,
            'month': month,
            'year': year,
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'savings': float(savings),
            'expenses_by_category': dict(sorted_categories)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating summary: {str(e)}'}), 500


@summary_bp.route('/ai-insights', methods=['GET'])
def get_ai_insights():
    """
    Generate AI-based monthly financial insights
    
    Query Parameters:
    - month: int (1-12, required)
    - year: int (required)
    
    Returns:
        JSON response with AI-generated insights
    """
    user_id = session['user_id']
    
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    if not month or not year:
        return jsonify({'success': False, 'message': 'Month and year are required'}), 400
    
    if month < 1 or month > 12:
        return jsonify({'success': False, 'message': 'Month must be between 1 and 12'}), 400
    
    try:
        # Get monthly summary
        total_income = db.session.query(func.sum(Income.amount)).filter(
            Income.user_id == user_id,
            func.extract('month', Income.date) == month,
            func.extract('year', Income.date) == year
        ).scalar() or 0
        
        total_expenses = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            func.extract('month', Expense.date) == month,
            func.extract('year', Expense.date) == year
        ).scalar() or 0
        
        # Get expenses by category
        category_data = db.session.query(
            Expense.category,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count')
        ).filter(
            Expense.user_id == user_id,
            func.extract('month', Expense.date) == month,
            func.extract('year', Expense.date) == year
        ).group_by(Expense.category).all()
        
        expenses_by_category = {cat: float(total) for cat, total, _ in category_data}
        expense_count = {cat: int(count) for cat, _, count in category_data}
        
        # Count income sources
        income_count = db.session.query(func.count(Income.id)).filter(
            Income.user_id == user_id,
            func.extract('month', Income.date) == month,
            func.extract('year', Income.date) == year
        ).scalar() or 0
        
        # Prepare data for LLM
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month - 1]
        
        expense_data = {
            'month': month_name,
            'year': year,
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'savings': float(total_income - total_expenses),
            'expense_count': int(income_count),
            'expenses_by_category': expenses_by_category
        }
        
        # Get AI insights
        llm_service = get_llm_service()
        
        if not llm_service:
            return jsonify({
                'success': False,
                'message': 'LLM service not available'
            }), 503
        
        insights = llm_service.generate_monthly_insights(expense_data)
        
        if insights:
            return jsonify({
                'success': True,
                'month': month,
                'year': year,
                'summary': expense_data,
                'insights': insights
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to generate insights'
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating insights: {str(e)}'}), 500


@summary_bp.route('/yearly', methods=['GET'])
def get_yearly_summary():
    """
    Get yearly financial summary
    
    Query Parameters:
    - year: int (required)
    
    Returns:
        JSON response with yearly summary
    """
    user_id = session['user_id']
    
    year = request.args.get('year', type=int)
    
    if not year:
        return jsonify({'success': False, 'message': 'Year is required'}), 400
    
    try:
        # Get total income for the year
        total_income = db.session.query(func.sum(Income.amount)).filter(
            Income.user_id == user_id,
            func.extract('year', Income.date) == year
        ).scalar() or 0
        
        # Get total expenses for the year
        total_expenses = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            func.extract('year', Expense.date) == year
        ).scalar() or 0
        
        # Get monthly breakdown
        monthly_data = []
        for month in range(1, 13):
            month_income = db.session.query(func.sum(Income.amount)).filter(
                Income.user_id == user_id,
                func.extract('month', Income.date) == month,
                func.extract('year', Income.date) == year
            ).scalar() or 0
            
            month_expenses = db.session.query(func.sum(Expense.amount)).filter(
                Expense.user_id == user_id,
                func.extract('month', Expense.date) == month,
                func.extract('year', Expense.date) == year
            ).scalar() or 0
            
            monthly_data.append({
                'month': month,
                'income': float(month_income),
                'expenses': float(month_expenses),
                'savings': float(month_income - month_expenses)
            })
        
        savings = total_income - total_expenses
        
        return jsonify({
            'success': True,
            'year': year,
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'savings': float(savings),
            'monthly_breakdown': monthly_data
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating yearly summary: {str(e)}'}), 500
