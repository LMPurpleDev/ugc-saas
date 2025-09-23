from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from app.models import User
from app.auth import get_current_active_user
from app.database import get_database
from app.services.instagram_service import instagram_service
from bson import ObjectId
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/instagram", tags=["instagram"])

@router.get("/auth-url")
async def get_instagram_auth_url(
    current_user: User = Depends(get_current_active_user),
    state: Optional[str] = None
):
    """Get Instagram authorization URL"""
    try:
        # Use user ID as state if not provided
        if not state:
            state = str(current_user.id)
        
        auth_url = instagram_service.get_authorization_url(state)
        
        return {
            "auth_url": auth_url,
            "state": state
        }
        
    except Exception as e:
        logger.error(f"Error generating Instagram auth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authorization URL"
        )

@router.post("/callback")
async def instagram_callback(
    code: str,
    state: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Handle Instagram OAuth callback"""
    try:
        db = get_database()
        
        # Exchange code for token
        token_data = instagram_service.exchange_code_for_token(code)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for access token"
            )
        
        # Calculate expiration date
        expires_at = datetime.utcnow() + timedelta(seconds=token_data.get('expires_in', 5184000))
        
        # Get user's profile
        profile = db.profiles.find_one({"user_id": ObjectId(current_user.id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found. Please create a profile first."
            )
        
        # Update profile with Instagram tokens
        instagram_tokens = {
            "access_token": token_data['access_token'],
            "user_id": token_data['user_id'],
            "expires_at": expires_at
        }
        
        result = db.profiles.update_one(
            {"user_id": ObjectId(current_user.id)},
            {"$set": {"instagram_tokens": instagram_tokens}}
        )
        
        if result.modified_count:
            # Get Instagram user info
            user_info = instagram_service.get_user_info(
                token_data['access_token'], 
                token_data['user_id']
            )
            
            return {
                "message": "Instagram account connected successfully",
                "instagram_user": user_info
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save Instagram tokens"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Instagram callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/disconnect")
async def disconnect_instagram(current_user: User = Depends(get_current_active_user)):
    """Disconnect Instagram account"""
    try:
        db = get_database()
        
        result = db.profiles.update_one(
            {"user_id": ObjectId(current_user.id)},
            {"$unset": {"instagram_tokens": ""}}
        )
        
        if result.modified_count:
            return {"message": "Instagram account disconnected successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Instagram connection found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting Instagram: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/status")
async def get_instagram_status(current_user: User = Depends(get_current_active_user)):
    """Get Instagram connection status"""
    try:
        db = get_database()
        
        profile = db.profiles.find_one({"user_id": ObjectId(current_user.id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        instagram_tokens = profile.get('instagram_tokens')
        if not instagram_tokens:
            return {
                "connected": False,
                "message": "Instagram account not connected"
            }
        
        # Check if token is expired
        expires_at = instagram_tokens.get('expires_at')
        is_expired = expires_at and datetime.utcnow() > expires_at
        
        # Get basic user info if connected and not expired
        user_info = None
        if not is_expired:
            user_info = instagram_service.get_user_info(
                instagram_tokens['access_token'],
                instagram_tokens['user_id']
            )
        
        return {
            "connected": True,
            "expired": is_expired,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "instagram_user": user_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Instagram status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/collect-metrics")
async def collect_instagram_metrics(current_user: User = Depends(get_current_active_user)):
    """Manually trigger Instagram metrics collection"""
    try:
        db = get_database()
        
        # Get user's profile
        profile = db.profiles.find_one({"user_id": ObjectId(current_user.id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        profile_id = str(profile['_id'])
        
        # Collect metrics
        success = await instagram_service.collect_user_metrics(profile_id)
        
        if success:
            return {"message": "Metrics collected successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to collect metrics"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error collecting Instagram metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/recent-posts")
async def get_recent_instagram_posts(
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(default=10, ge=1, le=25)
):
    """Get recent Instagram posts"""
    try:
        db = get_database()
        
        # Get user's profile
        profile = db.profiles.find_one({"user_id": ObjectId(current_user.id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        instagram_tokens = profile.get('instagram_tokens')
        if not instagram_tokens:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Instagram account not connected"
            )
        
        # Get recent posts
        posts = instagram_service.get_user_media(
            instagram_tokens['access_token'],
            instagram_tokens['user_id'],
            limit=limit
        )
        
        if posts is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch Instagram posts"
            )
        
        return {"posts": posts}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recent Instagram posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

