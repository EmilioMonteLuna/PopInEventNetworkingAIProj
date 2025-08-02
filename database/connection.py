# Database Connection Management for Event Networking AI System
"""
Database connection setup, session management, and initialization utilities.
Handles SQLAlchemy engine configuration and database operations.
"""

import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from config.settings import settings
from models.database import Base, create_performance_indexes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════════════
# DATABASE ENGINE CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════════

def create_database_engine():
    """Create and configure the SQLAlchemy database engine"""
    
    # SQLite configuration for development
    if settings.database_url.startswith("sqlite"):
        engine = create_engine(
            settings.database_url,
            # SQLite-specific settings
            connect_args={
                "check_same_thread": False,  # Allow multiple threads
                "timeout": 30,  # Connection timeout in seconds
            },
            # Connection pooling for SQLite
            poolclass=StaticPool,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,   # Recycle connections every hour
            echo=settings.debug,  # Log SQL queries in debug mode
        )
        
        # Enable WAL mode for better concurrency with SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            # Enable WAL mode for better concurrent access
            cursor.execute("PRAGMA journal_mode=WAL")
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=ON")
            # Optimize SQLite performance
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.close()
    
    # PostgreSQL configuration for production
    else:
        engine = create_engine(
            settings.database_url,
            # Connection pool settings
            pool_size=10,           # Number of connections in pool
            max_overflow=20,        # Additional connections beyond pool_size
            pool_pre_ping=True,     # Verify connections before use
            pool_recycle=3600,      # Recycle connections every hour
            # Performance settings
            echo=settings.debug,    # Log SQL queries in debug mode
            future=True,           # Use SQLAlchemy 2.0 style
        )
    
    return engine

# Create the engine instance
engine = create_database_engine()

# Create a session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Keep objects accessible after commit
)

# ════════════════════════════════════════════════════════════════════════════════
# DATABASE INITIALIZATION
# ════════════════════════════════════════════════════════════════════════════════

def init_database():
    """Initialize the database by creating all tables and indexes"""
    try:
        logger.info("Initializing database...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Create performance indexes
        try:
            create_performance_indexes(engine)
            logger.info("✅ Performance indexes created successfully")
        except Exception as e:
            logger.warning(f"⚠️  Could not create performance indexes: {e}")
        
        # Initialize system configuration
        _initialize_system_config()
        
        logger.info("✅ Database initialization completed")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

def _initialize_system_config():
    """Initialize default system configuration values"""
    from models.database import SystemConfig
    
    default_configs = [
        {
            "key": "recommendation.min_similarity_threshold",
            "value": "0.1",
            "value_type": "float",
            "description": "Minimum similarity score for recommendations"
        },
        {
            "key": "recommendation.max_recommendations",
            "value": "10",
            "value_type": "int",
            "description": "Maximum number of recommendations per user"
        },
        {
            "key": "clustering.default_algorithm",
            "value": "louvain",
            "value_type": "string",
            "description": "Default clustering algorithm"
        },
        {
            "key": "clustering.min_cluster_size",
            "value": "2",
            "value_type": "int",
            "description": "Minimum size for valid clusters"
        },
        {
            "key": "api.rate_limit_per_minute",
            "value": "100",
            "value_type": "int",
            "description": "API rate limit per minute per user"
        }
    ]
    
    with get_db_session() as db:
        for config in default_configs:
            existing = db.query(SystemConfig).filter(
                SystemConfig.key == config["key"]
            ).first()
            
            if not existing:
                db_config = SystemConfig(**config)
                db.add(db_config)
        
        db.commit()

# ════════════════════════════════════════════════════════════════════════════════
# SESSION MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════════

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database sessions.
    Automatically handles session lifecycle and cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def get_db_session() -> Session:
    """
    Context manager for database sessions outside of FastAPI.
    Use this for standalone scripts or background tasks.
    
    Example:
        with get_db_session() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# ════════════════════════════════════════════════════════════════════════════════
# DATABASE UTILITIES
# ════════════════════════════════════════════════════════════════════════════════

def reset_database():
    """Drop all tables and recreate them (USE WITH CAUTION!)"""
    logger.warning("🚨 Resetting database - all data will be lost!")
    
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ All tables dropped")
        
        # Recreate everything
        init_database()
        logger.info("✅ Database reset completed")
        
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        raise

def check_database_health() -> dict:
    """Check database connectivity and basic health metrics"""
    try:
        with get_db_session() as db:
            # Test basic connectivity
            db.execute("SELECT 1")
            
            # Get table counts for health metrics
            from models.database import User, Event, EventAttendee, Recommendation
            
            user_count = db.query(User).count()
            event_count = db.query(Event).count()
            attendee_count = db.query(EventAttendee).count()
            recommendation_count = db.query(Recommendation).count()
            
            return {
                "status": "healthy",
                "database_url": settings.database_url.split("@")[-1] if "@" in settings.database_url else "local",
                "tables": {
                    "users": user_count,
                    "events": event_count,
                    "attendees": attendee_count,
                    "recommendations": recommendation_count
                },
                "engine_info": {
                    "pool_size": engine.pool.size(),
                    "pool_checked_in": engine.pool.checkedin(),
                    "pool_checked_out": engine.pool.checkedout()
                }
            }
            
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def backup_database(backup_path: str = None) -> str:
    """Create a backup of the database (SQLite only)"""
    if not settings.database_url.startswith("sqlite"):
        raise ValueError("Database backup is only supported for SQLite")
    
    import shutil
    from datetime import datetime
    
    # Extract database file path
    db_file = settings.database_url.replace("sqlite:///", "")
    
    # Generate backup filename
    if not backup_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backup_{timestamp}.db"
    
    try:
        shutil.copy2(db_file, backup_path)
        logger.info(f"✅ Database backed up to: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"❌ Database backup failed: {e}")
        raise

def get_system_config(key: str, default=None):
    """Get a system configuration value"""
    try:
        with get_db_session() as db:
            from models.database import SystemConfig
            
            config = db.query(SystemConfig).filter(
                SystemConfig.key == key,
                SystemConfig.is_active == True
            ).first()
            
            if config:
                # Parse value based on type
                if config.value_type == "int":
                    return int(config.value)
                elif config.value_type == "float":
                    return float(config.value)
                elif config.value_type == "boolean":
                    return config.value.lower() in ("true", "1", "yes")
                elif config.value_type == "json":
                    import json
                    return json.loads(config.value)
                else:
                    return config.value
            
            return default
            
    except Exception as e:
        logger.error(f"Error getting system config '{key}': {e}")
        return default

def set_system_config(key: str, value, value_type: str = "string", description: str = None):
    """Set a system configuration value"""
    try:
        with get_db_session() as db:
            from models.database import SystemConfig
            
            config = db.query(SystemConfig).filter(
                SystemConfig.key == key
            ).first()
            
            if config:
                config.value = str(value)
                config.value_type = value_type
                if description:
                    config.description = description
                config.updated_at = datetime.utcnow()
            else:
                config = SystemConfig(
                    key=key,
                    value=str(value),
                    value_type=value_type,
                    description=description or f"Configuration for {key}"
                )
                db.add(config)
            
            db.commit()
            logger.info(f"✅ System config '{key}' set to '{value}'")
            
    except Exception as e:
        logger.error(f"Error setting system config '{key}': {e}")
        raise

# ════════════════════════════════════════════════════════════════════════════════
# PERFORMANCE MONITORING
# ════════════════════════════════════════════════════════════════════════════════

@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Monitor SQL query execution time"""
    import time
    context._query_start_time = time.time()

@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries for performance monitoring"""
    import time
    total = time.time() - context._query_start_time
    
    # Log slow queries (>1 second)
    if total > 1.0:
        logger.warning(f"Slow query detected ({total:.2f}s): {statement[:100]}...")

# ════════════════════════════════════════════════════════════════════════════════
# CONNECTION POOL EVENT HANDLERS
# ════════════════════════════════════════════════════════════════════════════════

# Note: Pool events are not supported by SQLite, only MySQL/PostgreSQL
# SQLite uses a simpler connection model and doesn't support pool events

# @event.listens_for(engine, "pool_pre_ping")
# def receive_pool_pre_ping(dbapi_connection, connection_record, info):
#     """Handle connection pool pre-ping events"""
#     logger.debug("Pre-ping connection validation")

# @event.listens_for(engine, "pool_checkout")
# def receive_pool_checkout(dbapi_connection, connection_record, info):
#     """Handle connection pool checkout events"""
#     logger.debug("Connection checked out from pool")

# @event.listens_for(engine, "pool_checkin")
# def receive_pool_checkin(dbapi_connection, connection_record):
#     """Handle connection pool checkin events"""
#     logger.debug("Connection checked in to pool")

# For production PostgreSQL/MySQL, you can uncomment these:
# if not settings.database_url.startswith("sqlite"):
#     @event.listens_for(engine, "pool_checkout")
#     def receive_pool_checkout(dbapi_connection, connection_record, info):
#         logger.debug("Connection checked out from pool")
#
#     @event.listens_for(engine, "pool_checkin")
#     def receive_pool_checkin(dbapi_connection, connection_record):
#         logger.debug("Connection checked in to pool")

# ════════════════════════════════════════════════════════════════════════════════
# MIGRATION UTILITIES
# ════════════════════════════════════════════════════════════════════════════════

def upgrade_database_schema():
    """Apply any pending database schema upgrades"""
    try:
        logger.info("Checking for database schema upgrades...")
        
        # Add any schema migration logic here
        # For now, just ensure all tables exist
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database schema is up to date")
        
    except Exception as e:
        logger.error(f"❌ Database schema upgrade failed: {e}")
        raise

# ════════════════════════════════════════════════════════════════════════════════
# CLEANUP UTILITIES
# ════════════════════════════════════════════════════════════════════════════════

def cleanup_old_data(days_old: int = 90):
    """Clean up old data to maintain database performance"""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    
    try:
        with get_db_session() as db:
            from models.database import ApiLog, RecommendationFeedback
            
            # Clean up old API logs
            old_logs = db.query(ApiLog).filter(
                ApiLog.timestamp < cutoff_date
            ).count()
            
            if old_logs > 0:
                db.query(ApiLog).filter(
                    ApiLog.timestamp < cutoff_date
                ).delete()
                logger.info(f"✅ Cleaned up {old_logs} old API log entries")
            
            # Clean up old inactive recommendations
            from models.database import Recommendation
            old_recommendations = db.query(Recommendation).filter(
                Recommendation.created_at < cutoff_date,
                Recommendation.is_active == False
            ).count()
            
            if old_recommendations > 0:
                db.query(Recommendation).filter(
                    Recommendation.created_at < cutoff_date,
                    Recommendation.is_active == False
                ).delete()
                logger.info(f"✅ Cleaned up {old_recommendations} old inactive recommendations")
            
            db.commit()
            
    except Exception as e:
        logger.error(f"❌ Data cleanup failed: {e}")
        raise

# Initialize database on module import if not in test mode
if not settings.database_url.endswith("test.db"):
    try:
        # Only initialize if tables don't exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        if not inspector.get_table_names():
            init_database()
    except Exception as e:
        logger.warning(f"Could not auto-initialize database: {e}")