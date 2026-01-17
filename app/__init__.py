import logging
import sys
from flask import Flask, render_template, request
from app.config import Config
from app.models import get_redis_client
from app.routes import api


def setup_logging(app):
    """
    Configure application logging

    Sets up structured logging with timestamps, log levels, and proper formatting
    for both console output and application loggers.
    """
    # Get log level from environment (defaults to INFO)
    log_level = app.config.get('LOG_LEVEL', 'INFO').upper()

    # Create formatter with timestamps
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S %z'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)

    # Set Flask's logger to use the same level
    app.logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Reduce noise from verbose libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

    app.logger.info(f"Logging initialized at {log_level} level")


def create_app():
    """
    Flask application factory

    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Setup logging first
    setup_logging(app)

    # Initialize Redis client
    app.redis = get_redis_client()

    # Test Redis connection
    try:
        app.redis.ping()
        app.logger.info(f"Connected to Redis at {Config.REDIS_HOST}:{Config.REDIS_PORT}")
    except Exception as e:
        app.logger.error(f"Failed to connect to Redis: {e}")
        app.logger.error(f"Host: {Config.REDIS_HOST}:{Config.REDIS_PORT}")

    # Add request/response logging middleware
    @app.before_request
    def log_request_info():
        """Log incoming request details"""
        app.logger.info(f"Request: {request.method} {request.path}")
        if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
            app.logger.debug(f"Request body: {request.get_json()}")

    @app.after_request
    def log_response_info(response):
        """Log response details"""
        app.logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
        return response

    # Register blueprints
    app.register_blueprint(api)

    # Main route
    @app.route('/')
    def index():
        """Serve the main application page"""
        return render_template('index.html')

    # Health check endpoint
    @app.route('/health')
    def health():
        """Health check endpoint for monitoring"""
        try:
            app.redis.ping()
            return {"status": "healthy", "redis": "connected"}, 200
        except:
            return {"status": "unhealthy", "redis": "disconnected"}, 503

    # Hidden admin page (no link from main UI)
    @app.route('/admin')
    def admin():
        """Hidden admin page for backup/restore management"""
        return render_template('admin.html')

    return app
