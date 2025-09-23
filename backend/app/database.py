from pymongo import MongoClient
from pymongo.database import Database
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: MongoClient = None
    database: Database = None

mongodb = MongoDB()

def connect_to_mongo():
    """Create database connection"""
    try:
        mongodb.client = MongoClient(settings.mongodb_url)
        mongodb.database = mongodb.client[settings.database_name]
        
        # Test connection
        mongodb.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes
        create_indexes()
        
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise

def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("MongoDB connection closed")

def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Users collection indexes
        mongodb.database.users.create_index("email", unique=True)
        
        # Profiles collection indexes
        mongodb.database.profiles.create_index("user_id", unique=True)
        mongodb.database.profiles.create_index("instagram_user_id")
        
        # Metrics collection indexes
        mongodb.database.metrics.create_index([("profile_id", 1), ("date", -1)])
        mongodb.database.metrics.create_index("post_id")
        
        # Reports collection indexes
        mongodb.database.reports.create_index([("profile_id", 1), ("created_at", -1)])
        
        # Posts feedback collection indexes
        mongodb.database.posts_feedback.create_index("post_id", unique=True)
        mongodb.database.posts_feedback.create_index("profile_id")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

def get_database() -> Database:
    """Get database instance"""
    return mongodb.database

