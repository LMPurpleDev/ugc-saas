import requests
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from app.config import settings
from app.database import get_database
from app.models import ProfileInDB, MetricsInDB
from bson import ObjectId

logger = logging.getLogger(__name__)

class InstagramService:
    """Service for Instagram Graph API integration"""
    
    BASE_URL = "https://graph.instagram.com"
    
    def __init__(self):
        self.app_id = settings.instagram_app_id
        self.app_secret = settings.instagram_app_secret
        self.redirect_uri = settings.instagram_redirect_uri
    
    def get_authorization_url(self, state: str = None) -> str:
        """Generate Instagram authorization URL"""
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement',
            'response_type': 'code',
        }
        
        if state:
            params['state'] = state
            
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"https://api.instagram.com/oauth/authorize?{query_string}"
    
    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        try:
            # Step 1: Get short-lived token
            token_url = "https://api.instagram.com/oauth/access_token"
            data = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri,
                'code': code,
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            short_token_data = response.json()
            short_token = short_token_data['access_token']
            user_id = short_token_data['user_id']
            
            # Step 2: Exchange for long-lived token
            long_token_url = f"{self.BASE_URL}/access_token"
            params = {
                'grant_type': 'ig_exchange_token',
                'client_secret': self.app_secret,
                'access_token': short_token,
            }
            
            response = requests.get(long_token_url, params=params)
            response.raise_for_status()
            
            long_token_data = response.json()
            
            return {
                'access_token': long_token_data['access_token'],
                'user_id': user_id,
                'expires_in': long_token_data.get('expires_in', 5184000),  # ~60 days
            }
            
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return None
    
    def refresh_access_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Refresh long-lived access token"""
        try:
            refresh_url = f"{self.BASE_URL}/refresh_access_token"
            params = {
                'grant_type': 'ig_refresh_token',
                'access_token': access_token,
            }
            
            response = requests.get(refresh_url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            return None
    
    def get_user_info(self, access_token: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get basic user information"""
        try:
            url = f"{self.BASE_URL}/{user_id}"
            params = {
                'fields': 'id,username,account_type,media_count',
                'access_token': access_token,
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    def get_user_media(self, access_token: str, user_id: str, limit: int = 25) -> Optional[List[Dict[str, Any]]]:
        """Get user's media posts"""
        try:
            url = f"{self.BASE_URL}/{user_id}/media"
            params = {
                'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp',
                'limit': limit,
                'access_token': access_token,
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json().get('data', [])
            
        except Exception as e:
            logger.error(f"Error getting user media: {e}")
            return None
    
    def get_media_insights(self, access_token: str, media_id: str) -> Optional[Dict[str, Any]]:
        """Get insights for a specific media post"""
        try:
            url = f"{self.BASE_URL}/{media_id}/insights"
            
            # Different metrics for different media types
            metrics = [
                'engagement', 'impressions', 'reach', 
                'saved', 'video_views', 'likes', 'comments', 'shares'
            ]
            
            params = {
                'metric': ','.join(metrics),
                'access_token': access_token,
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            insights_data = response.json().get('data', [])
            
            # Convert to more usable format
            insights = {}
            for insight in insights_data:
                metric_name = insight['name']
                metric_value = insight['values'][0]['value'] if insight['values'] else 0
                insights[metric_name] = metric_value
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting media insights for {media_id}: {e}")
            return None
    
    def get_account_insights(self, access_token: str, user_id: str, period: str = 'day') -> Optional[Dict[str, Any]]:
        """Get account-level insights"""
        try:
            url = f"{self.BASE_URL}/{user_id}/insights"
            
            # Account metrics
            metrics = [
                'follower_count', 'impressions', 'reach', 'profile_views'
            ]
            
            params = {
                'metric': ','.join(metrics),
                'period': period,
                'access_token': access_token,
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            insights_data = response.json().get('data', [])
            
            # Convert to more usable format
            insights = {}
            for insight in insights_data:
                metric_name = insight['name']
                if insight['values']:
                    metric_value = insight['values'][0]['value']
                    insights[metric_name] = metric_value
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting account insights: {e}")
            return None
    
    async def collect_user_metrics(self, profile_id: str) -> bool:
        """Collect and store metrics for a user profile"""
        try:
            db = get_database()
            
            # Get profile with Instagram tokens
            profile = db.profiles.find_one({"_id": ObjectId(profile_id)})
            if not profile or not profile.get('instagram_tokens'):
                logger.error(f"Profile {profile_id} not found or no Instagram tokens")
                return False
            
            instagram_tokens = profile['instagram_tokens']
            access_token = instagram_tokens['access_token']
            user_id = instagram_tokens['user_id']
            
            # Check if token needs refresh
            expires_at = instagram_tokens.get('expires_at')
            if expires_at and datetime.utcnow() > expires_at:
                # Try to refresh token
                refreshed = self.refresh_access_token(access_token)
                if refreshed:
                    access_token = refreshed['access_token']
                    # Update token in database
                    new_expires_at = datetime.utcnow() + timedelta(seconds=refreshed.get('expires_in', 5184000))
                    db.profiles.update_one(
                        {"_id": ObjectId(profile_id)},
                        {"$set": {
                            "instagram_tokens.access_token": access_token,
                            "instagram_tokens.expires_at": new_expires_at
                        }}
                    )
                else:
                    logger.error(f"Failed to refresh token for profile {profile_id}")
                    return False
            
            # Get account insights
            account_insights = self.get_account_insights(access_token, user_id)
            if not account_insights:
                logger.error(f"Failed to get account insights for profile {profile_id}")
                return False
            
            # Get recent media
            media_list = self.get_user_media(access_token, user_id, limit=10)
            if not media_list:
                logger.warning(f"No media found for profile {profile_id}")
                media_list = []
            
            # Collect media insights
            post_metrics = []
            total_likes = 0
            total_comments = 0
            total_reach = 0
            
            for media in media_list:
                media_insights = self.get_media_insights(access_token, media['id'])
                if media_insights:
                    post_metric = {
                        'post_id': media['id'],
                        'media_type': media['media_type'],
                        'timestamp': media['timestamp'],
                        'likes': media_insights.get('likes', 0),
                        'comments': media_insights.get('comments', 0),
                        'shares': media_insights.get('shares', 0),
                        'saved': media_insights.get('saved', 0),
                        'reach': media_insights.get('reach', 0),
                        'impressions': media_insights.get('impressions', 0),
                    }
                    post_metrics.append(post_metric)
                    
                    total_likes += post_metric['likes']
                    total_comments += post_metric['comments']
                    total_reach += post_metric['reach']
            
            # Calculate engagement rate
            follower_count = account_insights.get('follower_count', 0)
            avg_engagement_rate = 0.0
            if follower_count > 0 and post_metrics:
                total_engagement = total_likes + total_comments
                avg_engagement_rate = (total_engagement / (follower_count * len(post_metrics))) * 100
            
            # Create metrics record
            metrics_data = MetricsInDB(
                profile_id=ObjectId(profile_id),
                date=datetime.utcnow(),
                followers_count=follower_count,
                following_count=0,  # Not available in Instagram Basic Display API
                posts_count=len(media_list),
                avg_engagement_rate=avg_engagement_rate,
                total_likes=total_likes,
                total_comments=total_comments,
                total_reach=total_reach,
                post_metrics=post_metrics
            )
            
            # Store in database
            result = db.metrics.insert_one(metrics_data.dict(by_alias=True))
            
            if result.inserted_id:
                logger.info(f"Successfully collected metrics for profile {profile_id}")
                return True
            else:
                logger.error(f"Failed to store metrics for profile {profile_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error collecting metrics for profile {profile_id}: {e}")
            return False

# Global instance
instagram_service = InstagramService()

