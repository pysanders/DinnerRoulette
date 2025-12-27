import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')

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
    DEFAULT_CATEGORIES = os.getenv('DEFAULT_CATEGORIES', 'takeout,sit-down,nice,fast-food').split(',')

    # Distance levels
    VALID_DISTANCES = os.getenv('VALID_DISTANCES', 'nearby,short-drive,medium-drive,far').split(',')
    DEFAULT_DISTANCE = os.getenv('DEFAULT_DISTANCE', 'nearby')

    # "Eat at Home" weighted option
    EAT_AT_HOME_ENABLED = os.getenv('EAT_AT_HOME_ENABLED', 'True').lower() == 'true'
    EAT_AT_HOME_WEIGHT = int(os.getenv('EAT_AT_HOME_WEIGHT', 2))
    EAT_AT_HOME_NAME = os.getenv('EAT_AT_HOME_NAME', 'Eat at Home')
    # Days to exclude "Eat at Home" (0=Sunday, 1=Monday, ..., 6=Saturday)
    # Default: 5,6 (Friday, Saturday)
    eat_at_home_excluded = os.getenv('EAT_AT_HOME_EXCLUDED_DAYS', '5,6')
    EAT_AT_HOME_EXCLUDED_DAYS = [int(d.strip()) for d in eat_at_home_excluded.split(',') if d.strip().isdigit()]
    # Whether "Eat at Home" ignores the 15-minute recent spin exclusion
    # True = can appear immediately after being selected (default)
    # False = follows same 15-minute exclusion as restaurants
    EAT_AT_HOME_IGNORE_RECENT_SPIN = os.getenv('EAT_AT_HOME_IGNORE_RECENT_SPIN', 'True').lower() == 'true'

    # History retention
    HISTORY_RETENTION_DAYS = int(os.getenv('HISTORY_RETENTION_DAYS', 30))

    # Backup configuration
    BACKUP_DIR = os.getenv('BACKUP_DIR', '/app/backups')

    # Spin rate limiting (seconds between spins per user)
    SPIN_TIMEOUT_SECONDS = int(os.getenv('SPIN_TIMEOUT_SECONDS', 300))  # 5 minutes default

    # Location settings for Google search
    ZIP_CODE = os.getenv('ZIP_CODE', '00000')

    # Google Places API settings
    GOOGLE_PLACES_ENABLED = os.getenv('GOOGLE_PLACES_ENABLED', 'False').lower() == 'true'
    GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY', '')
    GOOGLE_PLACES_LOCATION = os.getenv('GOOGLE_PLACES_LOCATION', '')  # Lat,Lng for search center
    GOOGLE_PLACES_RADIUS = int(os.getenv('GOOGLE_PLACES_RADIUS', '50000'))  # meters (default: 50km)
