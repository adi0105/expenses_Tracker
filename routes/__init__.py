"""
Routes module initialization
"""
from .auth import auth_bp
from .expenses import expense_bp
from .income import income_bp
from .summary import summary_bp

__all__ = ['auth_bp', 'expense_bp', 'income_bp', 'summary_bp']
