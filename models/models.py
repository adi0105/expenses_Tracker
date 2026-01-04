"""
Database Models for Expense Tracker Application

This module defines the core data models:
- User: User account information
- Income: User income records
- Expense: User expense records with AI-based classification
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import json

db = SQLAlchemy()


class User(db.Model):
    """
    User model for authentication and data isolation
    
    Attributes:
        id: Unique user identifier
        username: Unique username for login
        email: User's email address
        password_hash: Hashed password for security
        preferred_currency: ISO 4217 currency code (INR, USD, EUR, etc.)
        created_at: Account creation timestamp
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    preferred_currency = db.Column(db.String(3), default='INR', nullable=False)
    # Optional per-user custom currency symbol (e.g. '$', '₹')
    preferred_currency_symbol = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    incomes = db.relationship('Income', backref='user', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    balance = db.relationship('UserBalance', backref='user', lazy=True, cascade='all, delete-orphan', uselist=False)
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify a password against the stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary representation"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'preferred_currency': self.preferred_currency,
            'preferred_currency_symbol': self.preferred_currency_symbol,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Income(db.Model):
    """
    Income model for tracking user income
    
    Attributes:
        id: Unique income record identifier
        user_id: Foreign key to User
        amount: Income amount
        source: Source of income (e.g., Salary, Freelance, Investment)
        date: Date of income
        created_at: Record creation timestamp
    """
    __tablename__ = 'incomes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert income to dictionary representation"""
        return {
            'id': self.id,
            'amount': self.amount,
            'source': self.source,
            'date': self.date.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Income {self.source} - ${self.amount}>'


class Expense(db.Model):
    """
    Expense model for tracking user expenses with AI classification
    
    Attributes:
        id: Unique expense record identifier
        user_id: Foreign key to User
        amount: Expense amount
        description: Detailed expense description
        category: AI-classified or manually selected category
        date: Date of expense
        ai_classified: Boolean indicating if category was AI-generated
        created_at: Record creation timestamp
    """
    __tablename__ = 'expenses'
    
    # Category options
    CATEGORIES = [
        'Food',
        'Travel',
        'Shopping',
        'Bills',
        'Entertainment',
        'Health',
        'Other'
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    ai_classified = db.Column(db.Boolean, default=False)
    # New fields for auto-detected transactions
    transaction_type = db.Column(db.String(10), nullable=True)  # 'Debit' or 'Credit'
    merchant_or_source = db.Column(db.String(255), nullable=True)  # Extracted merchant name
    is_auto_detected = db.Column(db.Boolean, default=False)  # True if from message parsing
    message_hash = db.Column(db.String(64), nullable=True, index=True)  # Hash to avoid duplicates
    original_message = db.Column(db.Text, nullable=True)  # Encrypted/masked message
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert expense to dictionary representation"""
        return {
            'id': self.id,
            'amount': self.amount,
            'description': self.description,
            'category': self.category,
            'date': self.date.isoformat(),
            'ai_classified': self.ai_classified,
            'transaction_type': self.transaction_type,
            'merchant_or_source': self.merchant_or_source,
            'is_auto_detected': self.is_auto_detected,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Expense {self.category} - ${self.amount}>'


class UserBalance(db.Model):
    """
    UserBalance model for tracking current account balance
    
    Attributes:
        id: Unique record identifier
        user_id: Foreign key to User (one-to-one)
        current_balance: Current account balance
        total_credits: Total amount credited
        total_debits: Total amount debited
        last_updated: Last balance update timestamp
        created_at: Record creation timestamp
    """
    __tablename__ = 'user_balance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True, unique=True)
    current_balance = db.Column(db.Float, default=0.0)
    total_credits = db.Column(db.Float, default=0.0)
    total_debits = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert balance to dictionary representation"""
        return {
            'id': self.id,
            'current_balance': self.current_balance,
            'total_credits': self.total_credits,
            'total_debits': self.total_debits,
            'last_updated': self.last_updated.isoformat()
        }
    
    def __repr__(self):
        return f'<UserBalance ${self.current_balance}>'


class Transaction(db.Model):
    """
    Transaction model for storing parsed/processed transactions
    
    Attributes:
        id: Unique transaction identifier
        user_id: Foreign key to User
        message_text: Original transaction message text
        message_hash: Hash of message to detect duplicates
        transaction_type: 'Credit' or 'Debit'
        amount: Extracted amount
        merchant_or_source: Extracted merchant/source name
        category: Extracted category
        processing_status: 'pending', 'processed', 'error'
        llm_confidence: Confidence score (0-1) of LLM extraction
        raw_llm_response: Raw JSON response from LLM
        created_at: Record creation timestamp
        processed_at: When transaction was processed
    """
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    message_text = db.Column(db.Text, nullable=False)
    message_hash = db.Column(db.String(64), nullable=False, index=True)
    transaction_type = db.Column(db.String(10), nullable=True)
    amount = db.Column(db.Float, nullable=True)
    merchant_or_source = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    processing_status = db.Column(db.String(20), default='pending')  # pending, processed, error
    llm_confidence = db.Column(db.Float, default=0.0)
    raw_llm_response = db.Column(db.Text, nullable=True)  # JSON
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """Convert transaction to dictionary representation"""
        return {
            'id': self.id,
            'message_hash': self.message_hash,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'merchant_or_source': self.merchant_or_source,
            'category': self.category,
            'processing_status': self.processing_status,
            'llm_confidence': self.llm_confidence,
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def generate_message_hash(message_text):
        """Generate SHA256 hash of message to detect duplicates"""
        return hashlib.sha256(message_text.encode()).hexdigest()
    
    def __repr__(self):
        return f'<Transaction {self.transaction_type} {self.amount}>'
