from celery import current_task
from app.celery_app import celery_app
from app.database import get_database, connect_to_mongo
from app.services.report_generator import report_generator
from app.services.email_service import email_service
from datetime import datetime, timedelta
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def generate_weekly_reports(self):
    """Generate weekly reports for all active profiles"""
    try:
        connect_to_mongo()
        db = get_database()
        
        # Calculate date range (last week)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        # Get all active profiles
        profiles = list(db.profiles.find({
            "instagram_tokens": {"$exists": True}
        }))
        
        logger.info(f"Generating weekly reports for {len(profiles)} profiles")
        
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
                        'status': f'Generating report for profile {profile_id}'
                    }
                )
                
                # Generate report
                success = generate_profile_report.delay(
                    profile_id=profile_id,
                    report_type='weekly',
                    period_start=start_date,
                    period_end=end_date
                )
                
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error generating weekly report for profile {profile.get('_id')}: {e}")
        
        result = {
            'total_profiles': len(profiles),
            'success_count': success_count,
            'error_count': error_count,
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Weekly reports generation completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_weekly_reports task: {e}")
        raise

@celery_app.task(bind=True)
def generate_monthly_reports(self):
    """Generate monthly reports for all active profiles"""
    try:
        connect_to_mongo()
        db = get_database()
        
        # Calculate date range (last month)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Get all active profiles
        profiles = list(db.profiles.find({
            "instagram_tokens": {"$exists": True}
        }))
        
        logger.info(f"Generating monthly reports for {len(profiles)} profiles")
        
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
                        'status': f'Generating report for profile {profile_id}'
                    }
                )
                
                # Generate report
                success = generate_profile_report.delay(
                    profile_id=profile_id,
                    report_type='monthly',
                    period_start=start_date,
                    period_end=end_date
                )
                
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error generating monthly report for profile {profile.get('_id')}: {e}")
        
        result = {
            'total_profiles': len(profiles),
            'success_count': success_count,
            'error_count': error_count,
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Monthly reports generation completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_monthly_reports task: {e}")
        raise

@celery_app.task(bind=True)
def generate_profile_report(
    self, 
    profile_id: str, 
    report_type: str = 'weekly',
    period_start: datetime = None,
    period_end: datetime = None,
    send_email: bool = True
):
    """Generate a report for a specific profile"""
    try:
        connect_to_mongo()
        db = get_database()
        
        # Set default date range if not provided
        if not period_end:
            period_end = datetime.utcnow()
        if not period_start:
            days = 7 if report_type == 'weekly' else 30
            period_start = period_end - timedelta(days=days)
        
        current_task.update_state(
            state='PROGRESS',
            meta={'status': f'Generating {report_type} report for profile {profile_id}'}
        )
        
        # Get profile data
        profile = db.profiles.find_one({"_id": ObjectId(profile_id)})
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")
        
        # Get user data for email
        user = db.users.find_one({"_id": profile['user_id']})
        if not user:
            raise ValueError(f"User for profile {profile_id} not found")
        
        # Get metrics data for the period
        metrics_data = list(db.metrics.find({
            "profile_id": ObjectId(profile_id),
            "date": {
                "$gte": period_start,
                "$lte": period_end
            }
        }).sort("date", -1))
        
        # Get feedback data for the period
        feedback_data = list(db.posts_feedback.find({
            "profile_id": ObjectId(profile_id),
            "created_at": {
                "$gte": period_start,
                "$lte": period_end
            }
        }).sort("created_at", -1))
        
        # Generate report title
        report_title = f"Relatório {report_type.title()} - {period_start.strftime('%d/%m/%Y')} a {period_end.strftime('%d/%m/%Y')}"
        
        # Generate PDF report
        current_task.update_state(
            state='PROGRESS',
            meta={'status': 'Generating PDF report'}
        )
        
        report_path = report_generator.generate_performance_report(
            profile_data=profile,
            metrics_data=metrics_data,
            feedback_data=feedback_data,
            report_title=report_title,
            period_start=period_start,
            period_end=period_end
        )
        
        # Save report record to database
        current_task.update_state(
            state='PROGRESS',
            meta={'status': 'Saving report to database'}
        )
        
        report_record = {
            "profile_id": ObjectId(profile_id),
            "title": report_title,
            "summary": f"Relatório {report_type} gerado automaticamente",
            "report_type": report_type,
            "period_start": period_start,
            "period_end": period_end,
            "file_path": report_path,
            "is_ready": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.reports.insert_one(report_record)
        report_id = str(result.inserted_id)
        
        # Send email notification
        if send_email:
            current_task.update_state(
                state='PROGRESS',
                meta={'status': 'Sending email notification'}
            )
            
            email_sent = email_service.send_report_notification(
                to_email=user['email'],
                user_name=user['full_name'],
                report_title=report_title,
                report_path=report_path
            )
            
            if not email_sent:
                logger.warning(f"Failed to send email notification for report {report_id}")
        
        logger.info(f"Successfully generated report {report_id} for profile {profile_id}")
        
        return {
            'profile_id': profile_id,
            'report_id': report_id,
            'report_type': report_type,
            'report_path': report_path,
            'email_sent': send_email and email_sent,
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating report for profile {profile_id}: {e}")
        raise

@celery_app.task(bind=True)
def cleanup_old_reports(self, days_to_keep: int = 180):
    """Clean up old report files and records"""
    try:
        connect_to_mongo()
        db = get_database()
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Get old reports
        old_reports = list(db.reports.find({
            "created_at": {"$lt": cutoff_date}
        }))
        
        deleted_files = 0
        
        # Delete files
        for report in old_reports:
            try:
                file_path = report.get('file_path')
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_files += 1
            except Exception as e:
                logger.warning(f"Could not delete report file {file_path}: {e}")
        
        # Delete database records
        result = db.reports.delete_many({
            "created_at": {"$lt": cutoff_date}
        })
        
        logger.info(f"Cleaned up {result.deleted_count} old report records and {deleted_files} files")
        
        return {
            'deleted_records': result.deleted_count,
            'deleted_files': deleted_files,
            'cutoff_date': cutoff_date.isoformat(),
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old reports: {e}")
        raise

