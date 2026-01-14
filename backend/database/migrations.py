from backend.database.models import db
import logging

logger = logging.getLogger(__name__)

def run_migrations(app):
    """Execute database migrations"""
    with app.app_context():
        try:
            logger.info("Running database migrations...")
            db.create_all()
            logger.info("Migrations completed successfully")
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            raise

def rollback_migrations(app):
    """Rollback database migrations"""
    with app.app_context():
        try:
            logger.info("Rolling back database migrations...")
            db.drop_all()
            logger.info("Rollback completed successfully")
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            raise

def get_migration_status(app):
    """Check migration status"""
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            return {
                'tables': tables,
                'count': len(tables),
                'status': 'current' if tables else 'pending'
            }
        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
