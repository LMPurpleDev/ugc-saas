from celery import current_task
from app.celery_app import celery_app
from app.database import get_database, connect_to_mongo
from datetime import datetime, timedelta
import logging
import asyncio
import sys
import os

# Add the backend directory to the path to import services
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

try:
    from app.services.instagram_service import instagram_service
except ImportError:
    # Fallback if import fails
    instagram_service = None

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def collect_all_metrics(self):
    """Collect metrics for all active profiles"""
    try:
        connect_to_mongo()
        db = get_database()
        
        # Get all profiles with Instagram tokens
        profiles = list(db.profiles.find({
            "instagram_tokens": {"$exists": True},
            "instagram_tokens.access_token": {"$exists": True}
        }))
        
        logger.info(f"Found {len(profiles)} profiles to collect metrics for")
        
        success_count = 0
        error_count = 0
        
        for profile in profiles:
            try:
                profile_id = str(profile['_id'])
                
                # Update task progress
                current_task.update_state(
                    state='PROGRESS',
                    meta={
                        'current': success_count + error_count,
                        'total': len(profiles),
                        'status': f'Processing profile {profile_id}'
                    }
                )
                
                if instagram_service:
                    # Use asyncio to run the async function
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    success = loop.run_until_complete(
                        instagram_service.collect_user_metrics(profile_id)
                    )
                    
                    loop.close()
                    
                    if success:
                        success_count += 1
                        logger.info(f"Successfully collected metrics for profile {profile_id}")
                    else:
                        error_count += 1
                        logger.error(f"Failed to collect metrics for profile {profile_id}")
                else:
                    logger.warning("Instagram service not available")
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error collecting metrics for profile {profile.get('_id')}: {e}")
        
        result = {
            'total_profiles': len(profiles),
            'success_count': success_count,
            'error_count': error_count,
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Metrics collection completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in collect_all_metrics task: {e}")
        raise

@celery_app.task(bind=True)
def collect_profile_metrics(self, profile_id: str):
    """Collect metrics for a specific profile"""
    try:
        connect_to_mongo()
        
        current_task.update_state(
            state='PROGRESS',
            meta={'status': f'Collecting metrics for profile {profile_id}'}
        )
        
        if instagram_service:
            # Use asyncio to run the async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            success = loop.run_until_complete(
                instagram_service.collect_user_metrics(profile_id)
            )
            
            loop.close()
            
            if success:
                logger.info(f"Successfully collected metrics for profile {profile_id}")
                return {
                    'profile_id': profile_id,
                    'success': True,
                    'completed_at': datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Failed to collect metrics for profile {profile_id}")
                return {
                    'profile_id': profile_id,
                    'success': False,
                    'error': 'Failed to collect metrics',
                    'completed_at': datetime.utcnow().isoformat()
                }
        else:
            logger.error("Instagram service not available")
            return {
                'profile_id': profile_id,
                'success': False,
                'error': 'Instagram service not available',
                'completed_at': datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error collecting metrics for profile {profile_id}: {e}")
        return {
            'profile_id': profile_id,
            'success': False,
            'error': str(e),
            'completed_at': datetime.utcnow().isoformat()
        }

@celery_app.task(bind=True)
def cleanup_old_metrics(self, days_to_keep: int = 90):
    """Clean up old metrics data"""
    try:
        connect_to_mongo()
        db = get_database()
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Delete old metrics
        result = db.metrics.delete_many({
            "date": {"$lt": cutoff_date}
        })
        
        logger.info(f"Cleaned up {result.deleted_count} old metrics records")
        
        return {
            'deleted_count': result.deleted_count,
            'cutoff_date': cutoff_date.isoformat(),
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old metrics: {e}")
        raise

