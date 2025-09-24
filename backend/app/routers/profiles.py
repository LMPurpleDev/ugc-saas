from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from app.models import (
    Profile, ProfileCreate, ProfileUpdate, ProfileInDB, 
    User, DashboardStats, DashboardCharts, ChartDataPoint
)
from app.auth import get_current_active_user
from app.database import get_database
from bson import ObjectId
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.post("/", response_model=Profile)
async def create_profile(
    profile: ProfileCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new profile for the current user"""
    try:
        db = get_database()
        
        # Check if user already has a profile
        # Comentário: current_user.id já é um ObjectId após a refatoração de PyObjectId.
        existing_profile = db.profiles.find_one({"user_id": current_user.id})
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has a profile"
            )
        
        # Create new profile
        # Comentário: Atualizado profile.dict() para profile.model_dump() para Pydantic v2.
        # Comentário: current_user.id já é um ObjectId após a refatoração de PyObjectId.
        profile_data = ProfileInDB(
            **profile.model_dump(),
            user_id=current_user.id
        )
        
        # Comentário: Atualizado profile_data.dict(by_alias=True) para profile_data.model_dump(by_alias=True) para Pydantic v2.
        result = db.profiles.insert_one(profile_data.model_dump(by_alias=True))
        
        if result.inserted_id:
            created_profile = db.profiles.find_one({"_id": result.inserted_id})
            # Comentário: A instanciação de Profile a partir de created_profile funciona com Pydantic v2.
            return Profile(**created_profile)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create profile"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=Profile)
async def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user's profile"""
    try:
        db = get_database()
        # Comentário: current_user.id já é um ObjectId após a refatoração de PyObjectId.
        profile_data = db.profiles.find_one({"user_id": current_user.id})
        
        if not profile_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Comentário: A instanciação de Profile a partir de profile_data funciona com Pydantic v2.
        return Profile(**profile_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/me", response_model=Profile)
async def update_my_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update current user's profile"""
    try:
        db = get_database()
        
        # Get existing profile
        # Comentário: current_user.id já é um ObjectId após a refatoração de PyObjectId.
        existing_profile = db.profiles.find_one({"user_id": current_user.id})
        if not existing_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Update profile
        # Comentário: Atualizado profile_update.dict(exclude_unset=True) para profile_update.model_dump(exclude_unset=True) para Pydantic v2.
        update_data = profile_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        # Comentário: current_user.id já é um ObjectId após a refatoração de PyObjectId.
        result = db.profiles.update_one(
            {"user_id": current_user.id},
            {"$set": update_data}
        )
        
        if result.modified_count:
            # Comentário: current_user.id já é um ObjectId após a refatoração de PyObjectId.
            updated_profile = db.profiles.find_one({"user_id": current_user.id})
            # Comentário: A instanciação de Profile a partir de updated_profile funciona com Pydantic v2.
            return Profile(**updated_profile)
        else:
            # Return existing profile if no changes were made
            # Comentário: A instanciação de Profile a partir de existing_profile funciona com Pydantic v2.
            return Profile(**existing_profile)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me/dashboard", response_model=dict)
async def get_dashboard_data(current_user: User = Depends(get_current_active_user)):
    """Get dashboard data for current user"""
    try:
        db = get_database()
        
        # Get user's profile
        # Comentário: current_user.id já é um ObjectId após a refatoração de PyObjectId.
        profile = db.profiles.find_one({"user_id": current_user.id})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        profile_id = profile["_id"]
        
        # Get latest metrics
        latest_metrics = db.metrics.find_one(
            {"profile_id": profile_id},
            sort=[("date", -1)]
        )
        
        # Get metrics from 30 days ago for growth calculation
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        old_metrics = db.metrics.find_one(
            {"profile_id": profile_id, "date": {"$lte": thirty_days_ago}},
            sort=[("date", -1)]
        )
        
        # Calculate stats
        if latest_metrics:
            stats = DashboardStats(
                followers_count=latest_metrics.get("followers_count", 0),
                following_count=latest_metrics.get("following_count", 0),
                posts_count=latest_metrics.get("posts_count", 0),
                avg_engagement_rate=latest_metrics.get("avg_engagement_rate", 0.0),
                total_likes=latest_metrics.get("total_likes", 0),
                total_comments=latest_metrics.get("total_comments", 0),
                followers_growth=0.0,
                engagement_growth=0.0
            )
            
            # Calculate growth percentages
            if old_metrics:
                old_followers = old_metrics.get("followers_count", 0)
                if old_followers > 0:
                    stats.followers_growth = ((stats.followers_count - old_followers) / old_followers) * 100
                
                old_engagement = old_metrics.get("avg_engagement_rate", 0)
                if old_engagement > 0:
                    stats.engagement_growth = ((stats.avg_engagement_rate - old_engagement) / old_engagement) * 100
        else:
            stats = DashboardStats(
                followers_count=0,
                following_count=0,
                posts_count=0,
                avg_engagement_rate=0.0,
                total_likes=0,
                total_comments=0,
                followers_growth=0.0,
                engagement_growth=0.0
            )
        
        # Get chart data (last 30 days)
        chart_data = list(db.metrics.find(
            {"profile_id": profile_id, "date": {"$gte": thirty_days_ago}},
            sort=[("date", 1)]
        ))
        
        followers_evolution = []
        engagement_evolution = []
        reach_evolution = []
        
        for data in chart_data:
            date_str = data["date"].strftime("%Y-%m-%d")
            followers_evolution.append(ChartDataPoint(
                date=date_str,
                value=data.get("followers_count", 0)
            ))
            engagement_evolution.append(ChartDataPoint(
                date=date_str,
                value=data.get("avg_engagement_rate", 0.0)
            ))
            reach_evolution.append(ChartDataPoint(
                date=date_str,
                value=data.get("total_reach", 0)
            ))
        
        charts = DashboardCharts(
            followers_evolution=followers_evolution,
            engagement_evolution=engagement_evolution,
            reach_evolution=reach_evolution
        )
        
        # Comentário: Atualizado stats.dict() para stats.model_dump() para Pydantic v2.
        # Comentário: Atualizado charts.dict() para charts.model_dump() para Pydantic v2.
        return {
            "stats": stats.model_dump(),
            "charts": charts.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


