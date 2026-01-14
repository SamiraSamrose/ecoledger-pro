import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.database.models import db
from backend.api.routes import api_bp
from config.settings import config
from config.logging_config import setup_logging
import logging

def create_app(config_name='production'):
    """Application factory pattern"""
    app = Flask(__name__, 
                static_folder='../frontend',
                static_url_path='')
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"Starting EcoLedger Pro in {config_name} mode")
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Serve frontend
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def static_files(path):
        return send_from_directory(app.static_folder, path)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return {'error': 'Internal server error'}, 500
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'service': 'EcoLedger Pro',
            'version': '1.0.0'
        }
    
    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        db.create_all()
        logging.info("Database tables created")
    
    port = int(os.getenv('API_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)