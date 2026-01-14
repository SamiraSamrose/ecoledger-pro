import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/ecoledger')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # API Configuration
    API_PORT = int(os.getenv('API_PORT', 5000))
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    
    # OCR Configuration
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract')
    OCR_CONFIDENCE_THRESHOLD = 0.60
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'ecoledger.log')
    
    # Model Configuration
    MODEL_PATH = os.path.join(BASE_DIR, 'data', 'models')
    
    # Business Logic Configuration
    COVENANT_THRESHOLDS = {
        'min_energy_savings_pct': 10,
        'min_carbon_reduction_pct': 5,
        'max_emissions_increase_pct': 2,
        'min_renewable_energy_pct': 15,
        'min_esg_score': 50
    }
    
    MILESTONE_TIERS = {
        'tier_1': {'carbon_reduction_min': 10, 'rate_discount': 0.25},
        'tier_2': {'carbon_reduction_min': 20, 'rate_discount': 0.50},
        'tier_3': {'carbon_reduction_min': 30, 'rate_discount': 0.75},
        'tier_4': {'carbon_reduction_min': 40, 'rate_discount': 1.00},
        'tier_5': {'carbon_reduction_min': 50, 'rate_discount': 1.50}
    }
    
    # External API Configuration
    WORLD_BANK_API_URL = 'http://api.worldbank.org/v2'
    SEC_EDGAR_API_URL = 'https://www.sec.gov/cgi-bin/browse-edgar'
    OPENCORPORATES_API_URL = 'https://api.opencorporates.com/v0.4'
    
    # Security Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True)
        os.makedirs(Config.MODEL_PATH, exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
