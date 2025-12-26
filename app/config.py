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
    COOKIE_NAME = os.getenv('COOKIE_NAME', 'dinner_roulette_user')
    COOKIE_MAX_AGE = int(os.getenv('COOKIE_MAX_AGE', 31536000))  # 1 year in seconds
    COOKIE_HTTPONLY = os.getenv('COOKIE_HTTPONLY', 'True').lower() == 'true'
    COOKIE_SECURE = os.getenv('COOKIE_SECURE', 'False').lower() == 'true'
    COOKIE_SAMESITE = os.getenv('COOKIE_SAMESITE', 'Lax')

    # Restaurant categories (default set, can be customized via Redis)
    DEFAULT_CATEGORIES = os.getenv('DEFAULT_CATEGORIES', 'quick,sit-down,nice').split(',')

    # Distance levels
    VALID_DISTANCES = os.getenv('VALID_DISTANCES', 'nearby,short-drive,medium-drive,far').split(',')
    DEFAULT_DISTANCE = os.getenv('DEFAULT_DISTANCE', 'nearby')

    # "Eat at Home" weighted option
    EAT_AT_HOME_ENABLED = os.getenv('EAT_AT_HOME_ENABLED', 'True').lower() == 'true'
    EAT_AT_HOME_WEIGHT = int(os.getenv('EAT_AT_HOME_WEIGHT', 2))
    EAT_AT_HOME_NAME = os.getenv('EAT_AT_HOME_NAME', 'Eat at Home')

    # History retention
    HISTORY_RETENTION_DAYS = int(os.getenv('HISTORY_RETENTION_DAYS', 30))
