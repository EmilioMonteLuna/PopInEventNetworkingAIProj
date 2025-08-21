"""
Reset Database Script
Drops existing tables and recreates them with the latest schema
"""

import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def reset_database():
    """Reset the database by deleting the file and reinitializing"""
    try:
        # Database file path
        db_file = Path("event_networking.db")
        
        # Delete existing database file if it exists
        if db_file.exists():
            os.remove(db_file)
            logger.info(f"✅ Deleted existing database: {db_file}")
        else:
            logger.info("📄 No existing database file found")
        
        # Import and initialize database
        from database.connection import init_database
        logger.info("🔄 Initializing fresh database...")
        init_database()
        logger.info("✅ Database reset completed successfully!")
        
        # Create sample data
        logger.info("📊 Creating sample data...")
        from database.sample_data import create_sample_data
        stats = create_sample_data()
        logger.info(f"✅ Sample data created: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error resetting database: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Resetting Event Networking AI Database...")
    if reset_database():
        logger.info("🎉 Database reset complete! You can now run the application.")
    else:
        logger.error("💥 Database reset failed!")