import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # Redis settings
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

    # Cookie settings
    COOKIE_NAME = 'dinner_roulette_user'
    COOKIE_MAX_AGE = 31536000  # 1 year in seconds
    COOKIE_HTTPONLY = True
    COOKIE_SECURE = os.getenv('COOKIE_SECURE', 'False').lower() == 'true'
    COOKIE_SAMESITE = 'Lax'

    # Restaurant categories
    VALID_CATEGORIES = ['quick', 'sit-down', 'nice']
