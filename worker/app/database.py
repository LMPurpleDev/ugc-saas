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
        
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise

def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("MongoDB connection closed")

def get_database() -> Database:
    """Get database instance"""
    return mongodb.database

