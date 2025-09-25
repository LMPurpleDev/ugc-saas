from celery import current_task
from app.celery_app import celery_app
from app.database import get_database, connect_to_mongo
from datetime import datetime, timedelta
from bson import ObjectId
import logging
import sys
import os

# Add the backend directory to the path to import services
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

try:
    from app.services.ai_service import ai_service
    from app.services.instagram_service import instagram_service
    from app.models import PostFeedbackInDB
except ImportError:
    # Fallback if import fails
    ai_service = None
    instagram_service = None
    PostFeedbackInDB = None

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def analyze_recent_posts(self):
    """Analyze recent posts for all active profiles"""
    try:
        connect_to_mongo()
        db = get_database()
        
        # Get all profiles with Instagram tokens
        profiles = list(db.profiles.find({
            "instagram_tokens": {"$exists": True},
            "instagram_tokens.access_token": {"$exists": True}
        }))
        
        logger.info(f"Analyzing recent posts for {len(profiles)} profiles")
        
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
                        'status': f'Analyzing posts for profile {profile_id}'
                    }
                )
                
                # Analyze posts for this profile
                result = analyze_profile_posts.delay(profile_id)
                
                if result:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error analyzing posts for profile {profile.get('_id')}: {e}")
        
        result = {
            'total_profiles': len(profiles),
            'success_count': success_count,
            'error_count': error_count,
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Post analysis completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in analyze_recent_posts task: {e}")
        raise

@celery_app.task(bind=True)
def analyze_profile_posts(self, profile_id: str, limit: int = 5):
    """Analyze recent posts for a specific profile"""
    try:
        connect_to_mongo()
        db = get_database()
        
        current_task.update_state(
            state='PROGRESS',
            meta={'status': f'Analyzing posts for profile {profile_id}'}
        )
        
        # Get profile data
        profile = db.profiles.find_one({"_id": ObjectId(profile_id)})
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")
        
        instagram_tokens = profile.get('instagram_tokens')
        if not instagram_tokens:
            raise ValueError(f"No Instagram tokens for profile {profile_id}")
        
        niche = profile.get('niche', 'lifestyle')
        
        if not instagram_service or not ai_service:
            logger.error("Required services not available")
            return {
                'profile_id': profile_id,
                'success': False,
                'error': 'Required services not available',
                'completed_at': datetime.utcnow().isoformat()
            }
        
        # Get recent posts from Instagram
        posts = instagram_service.get_user_media(
            instagram_tokens['access_token'],
            instagram_tokens['user_id'],
            limit=limit
        )
        
        if not posts:
            logger.warning(f"No posts found for profile {profile_id}")
            return {
                'profile_id': profile_id,
                'success': True,
                'analyzed_posts': 0,
                'completed_at': datetime.utcnow().isoformat()
            }
        
        analyzed_count = 0
        
        for post in posts:
            try:
                post_id = post['id']
                
                # Check if feedback already exists
                existing_feedback = db.posts_feedback.find_one({"post_id": post_id})
                if existing_feedback:
                    continue
                
                # Get post insights
                insights = instagram_service.get_media_insights(
                    instagram_tokens['access_token'],
                    post_id
                )
                
                # Create post feedback using AI
                feedback = ai_service.create_post_feedback(
                    profile_id=profile_id,
                    post_id=post_id,
                    post_url=post.get('permalink', ''),
                    post_caption=post.get('caption', ''),
                    post_type=post.get('media_type', 'IMAGE').lower(),
                    niche=niche,
                    engagement_data=insights
                )
                
                if feedback and PostFeedbackInDB:
                    # Save feedback to database
                    feedback_data = PostFeedbackInDB(**feedback.dict())
                    result = db.posts_feedback.insert_one(feedback_data.dict(by_alias=True))
                    
                    if result.inserted_id:
                        analyzed_count += 1
                        logger.info(f"Created feedback for post {post_id}")
                    else:
                        logger.error(f"Failed to save feedback for post {post_id}")
                else:
                    logger.error(f"Failed to create feedback for post {post_id}")
                    
            except Exception as e:
                logger.error(f"Error analyzing post {post.get('id')}: {e}")
        
        logger.info(f"Analyzed {analyzed_count} posts for profile {profile_id}")
        
        return {
            'profile_id': profile_id,
            'success': True,
            'analyzed_posts': analyzed_count,
            'total_posts': len(posts),
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing posts for profile {profile_id}: {e}")
        return {
            'profile_id': profile_id,
            'success': False,
            'error': str(e),
            'completed_at': datetime.utcnow().isoformat()
        }

@celery_app.task(bind=True)
def generate_content_suggestions_for_all(self):
    """Generate content suggestions for all active profiles"""
    try:
        connect_to_mongo()
        db = get_database()
        
        # Get all active profiles
        profiles = list(db.profiles.find({
            "instagram_tokens": {"$exists": True}
        }))
        
        logger.info(f"Generating content suggestions for {len(profiles)} profiles")
        
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
                        'status': f'Generating suggestions for profile {profile_id}'
                    }
                )
                
                # Generate suggestions for this profile
                result = generate_profile_content_suggestions.delay(profile_id)
                
                if result:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error generating suggestions for profile {profile.get('_id')}: {e}")
        
        result = {
            'total_profiles': len(profiles),
            'success_count': success_count,
            'error_count': error_count,
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Content suggestions generation completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_content_suggestions_for_all task: {e}")
        raise

@celery_app.task(bind=True)
def generate_profile_content_suggestions(self, profile_id: str):
    """Generate content suggestions for a specific profile"""
    try:
        connect_to_mongo()
        db = get_database()
        
        current_task.update_state(
            state='PROGRESS',
            meta={'status': f'Generating content suggestions for profile {profile_id}'}
        )
        
        # Get profile data
        profile = db.profiles.find_one({"_id": ObjectId(profile_id)})
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")
        
        niche = profile.get('niche', 'lifestyle')
        
        if not ai_service:
            logger.error("AI service not available")
            return {
                'profile_id': profile_id,
                'success': False,
                'error': 'AI service not available',
                'completed_at': datetime.utcnow().isoformat()
            }
        
        # Get recent performance data
        recent_metrics = list(db.metrics.find(
            {"profile_id": ObjectId(profile_id)}
        ).sort("date", -1).limit(5))
        
        # Convert metrics to performance data
        recent_performance = []
        for metric in recent_metrics:
            if metric.get('followers_count', 0) > 0:
                engagement_rate = metric.get('avg_engagement_rate', 0)
                recent_performance.append({
                    'engagement_rate': engagement_rate,
                    'media_type': 'mixed',
                    'date': metric.get('date')
                })
        
        # Generate content suggestions using AI
        suggestions = ai_service.generate_content_suggestions(
            profile_id=profile_id,
            niche=niche,
            performance_data=recent_performance
        )
        
        # Save suggestions to database
        if suggestions:
            result = db.content_suggestions.insert_one({
                'profile_id': ObjectId(profile_id),
                'suggestions': suggestions,
                'created_at': datetime.utcnow(),
                'niche': niche
            })
            
            if result.inserted_id:
                logger.info(f"Generated {len(suggestions)} content suggestions for profile {profile_id}")
                return {
                    'profile_id': profile_id,
                    'success': True,
                    'suggestion_count': len(suggestions),
                    'completed_at': datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Failed to save suggestions for profile {profile_id}")
                return {
                    'profile_id': profile_id,
                    'success': False,
                    'error': 'Failed to save suggestions',
                    'completed_at': datetime.utcnow().isoformat()
                }
                
        else:
            logger.warning(f"No suggestions generated for profile {profile_id}")
            return {
                'profile_id': profile_id,
                'success': True,
                'suggestion_count': 0,
                'completed_at': datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error generating content suggestions for profile {profile_id}: {e}")
        return {
            'profile_id': profile_id,
            'success': False,
            'error': str(e),
            'completed_at': datetime.utcnow().isoformat()
        }