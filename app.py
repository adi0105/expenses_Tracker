"""
Expense Tracker Application - Main Application File

A production-ready expense tracking web application with AI-powered
classification and financial insights using Flask and OpenAI API.

Author: Aditya
Created: January 2024
Version: 1.0.0
"""

from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config import get_config
from models.models import db
from routes.auth import auth_bp
from routes.expenses import expense_bp
from routes.income import income_bp
from routes.summary import summary_bp
from routes.transactions import transactions_bp, balance_bp
from routes.settings import settings_bp


def create_app(config_name=None):
    """
    Application factory function
    
    Args:
        config_name: Configuration environment (development, production, testing)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize database
    db.init_app(app)
    
    # Enable CORS for API endpoints
    # Restrict CORS origins via environment variable in production.
    # Provide a comma-separated list in `CORS_ALLOWED_ORIGINS` or leave empty to restrict to same-origin.
    cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '')
    if cors_origins:
        origins = [o.strip() for o in cors_origins.split(',') if o.strip()]
        CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=True)
    else:
        # default: do not allow cross-origin requests (same-origin only)
        CORS(app, resources={r"/api/*": {"origins": None}}, supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(summary_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(balance_bp)
    app.register_blueprint(settings_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()

    # Ensure session cookie settings are explicit
    app.config.setdefault('SESSION_COOKIE_NAME', 'expense_tracker_session')
    # SESSION_COOKIE_SECURE/HTTPONLY/SAMESITE are configured via Config

    # Security headers
    @app.after_request
    def set_security_headers(response):
        # Content Security Policy: allow self, allow CDN for Chart.js; adjust as needed
        csp = "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data:; font-src 'self' data:;"
        response.headers.setdefault('Content-Security-Policy', csp)
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('Referrer-Policy', 'no-referrer-when-downgrade')
        response.headers.setdefault('Permissions-Policy', 'geolocation=(), microphone=()')
        # Strict-Transport-Security only in production (when running over HTTPS)
        if not app.config.get('DEBUG'):
            response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
        return response
    
    # Home page route
    @app.route('/')
    def index():
        """Home page"""
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard page"""
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return render_template('dashboard.html', username=session.get('username'))
    
    @app.route('/settings')
    def settings():
        """Settings page"""
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return render_template('settings.html', username=session.get('username'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return render_template('errors/500.html'), 500
    
    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    # Run development server
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )
    # Note: single run call above uses configured PORT and DEBUG.
    # Removed duplicate `app.run(debug=True)` to avoid socket/port conflicts.
