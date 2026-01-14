import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.database.models import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Initialize database tables"""
    logger.info("Setting up database...")
    
    app = create_app('production')
    
    with app.app_context():
        try:
            # Drop all tables
            logger.info("Dropping existing tables...")
            db.drop_all()
            
            # Create all tables
            logger.info("Creating tables...")
            db.create_all()
            
            logger.info("Database setup completed successfully")
            logger.info("Tables created:")
            for table in db.metadata.tables.keys():
                logger.info(f"  - {table}")
            
        except Exception as e:
            logger.error(f"Error setting up database: {str(e)}")
            raise

if __name__ == '__main__':
    setup_database()