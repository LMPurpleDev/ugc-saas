from celery import current_task
from app.celery_app import celery_app
from app.database import get_database, connect_to_mongo
from app.services.email_service import email_service
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def send_welcome_email(self, user_id: str):
    """Send welcome email to a new user"""
    try:
        connect_to_mongo()
        db = get_database()
        
        current_task.update_state(
            state='PROGRESS',
            meta={'status': f'Sending welcome email to user {user_id}'}
        )
        
        # Get user data
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Send welcome email
        success = email_service.send_welcome_email(
            to_email=user['email'],
            user_name=user['full_name']
        )
        
        if success:
            logger.info(f"Welcome email sent successfully to {user['email']}")
            return {
                'user_id': user_id,
                'email': user['email'],
                'success': True,
                'completed_at': datetime.utcnow().isoformat()
            }
        else:
            logger.error(f"Failed to send welcome email to {user['email']}")
            return {
                'user_id': user_id,
                'email': user['email'],
                'success': False,
                'error': 'Failed to send email',
                'completed_at': datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error sending welcome email to user {user_id}: {e}")
        return {
            'user_id': user_id,
            'success': False,
            'error': str(e),
            'completed_at': datetime.utcnow().isoformat()
        }

@celery_app.task(bind=True)
def send_report_notification(self, user_id: str, report_id: str):
    """Send report notification email"""
    try:
        connect_to_mongo()
        db = get_database()
        
        current_task.update_state(
            state='PROGRESS',
            meta={'status': f'Sending report notification to user {user_id}'}
        )
        
        # Get user data
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Get report data
        report = db.reports.find_one({"_id": ObjectId(report_id)})
        if not report:
            raise ValueError(f"Report {report_id} not found")
        
        # Send notification email
        success = email_service.send_report_notification(
            to_email=user['email'],
            user_name=user['full_name'],
            report_title=report['title'],
            report_path=report.get('file_path')
        )
        
        if success:
            logger.info(f"Report notification sent successfully to {user['email']}")
            return {
                'user_id': user_id,
                'report_id': report_id,
                'email': user['email'],
                'success': True,
                'completed_at': datetime.utcnow().isoformat()
            }
        else:
            logger.error(f"Failed to send report notification to {user['email']}")
            return {
                'user_id': user_id,
                'report_id': report_id,
                'email': user['email'],
                'success': False,
                'error': 'Failed to send email',
                'completed_at': datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error sending report notification to user {user_id}: {e}")
        return {
            'user_id': user_id,
            'report_id': report_id,
            'success': False,
            'error': str(e),
            'completed_at': datetime.utcnow().isoformat()
        }

@celery_app.task(bind=True)
def send_weekly_digest(self):
    """Send weekly digest emails to all active users"""
    try:
        connect_to_mongo()
        db = get_database()
        
        # Get all active users (with profiles and Instagram connections)
        pipeline = [
            {
                "$lookup": {
                    "from": "profiles",
                    "localField": "_id",
                    "foreignField": "user_id",
                    "as": "profile"
                }
            },
            {
                "$match": {
                    "profile.instagram_tokens": {"$exists": True}
                }
            }
        ]
        
        users = list(db.users.aggregate(pipeline))
        
        logger.info(f"Sending weekly digest to {len(users)} users")
        
        success_count = 0
        error_count = 0
        
        for user in users:
            try:
                user_id = str(user['_id'])
                
                # Update task progress
                current_task.update_state(
                    state='PROGRESS',
                    meta={
                        'current': success_count + error_count,
                        'total': len(users),
                        'status': f'Sending digest to user {user_id}'
                    }
                )
                
                # Send digest email (placeholder - implement actual digest content)
                success = email_service.send_report_notification(
                    to_email=user['email'],
                    user_name=user['full_name'],
                    report_title="Resumo Semanal da Sua Performance"
                )
                
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error sending weekly digest to user {user.get('_id')}: {e}")
        
        result = {
            'total_users': len(users),
            'success_count': success_count,
            'error_count': error_count,
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Weekly digest sending completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in send_weekly_digest task: {e}")
        raise

@celery_app.task(bind=True)
def send_bulk_notification(self, subject: str, message: str, user_ids: list = None):
    """Send bulk notification to users"""
    try:
        connect_to_mongo()
        db = get_database()
        
        # Get users to send to
        if user_ids:
            users = list(db.users.find({"_id": {"$in": [ObjectId(uid) for uid in user_ids]}}))
        else:
            # Send to all active users
            users = list(db.users.find({"is_active": True}))
        
        logger.info(f"Sending bulk notification to {len(users)} users")
        
        success_count = 0
        error_count = 0
        
        for user in users:
            try:
                user_id = str(user['_id'])
                
                # Update task progress
                current_task.update_state(
                    state='PROGRESS',
                    meta={
                        'current': success_count + error_count,
                        'total': len(users),
                        'status': f'Sending notification to user {user_id}'
                    }
                )
                
                # Send notification (using report notification template as base)
                success = email_service.send_report_notification(
                    to_email=user['email'],
                    user_name=user['full_name'],
                    report_title=subject
                )
                
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error sending notification to user {user.get('_id')}: {e}")
        
        result = {
            'total_users': len(users),
            'success_count': success_count,
            'error_count': error_count,
            'subject': subject,
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Bulk notification sending completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in send_bulk_notification task: {e}")
        raise

