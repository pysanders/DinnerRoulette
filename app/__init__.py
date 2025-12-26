from flask import Flask, render_template
from app.config import Config
from app.models import get_redis_client
from app.routes import api


def create_app():
    """
    Flask application factory

    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Redis client
    app.redis = get_redis_client()

    # Test Redis connection
    try:
        app.redis.ping()
        print(f"✓ Connected to Redis at {Config.REDIS_HOST}:{Config.REDIS_PORT}")
    except Exception as e:
        print(f"✗ Failed to connect to Redis: {e}")
        print(f"  Host: {Config.REDIS_HOST}:{Config.REDIS_PORT}")

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

    return app
