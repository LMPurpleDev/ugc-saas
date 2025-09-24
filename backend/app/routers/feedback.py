from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from app.models import PostFeedback, PostFeedbackCreate, User
from app.auth import get_current_active_user
from app.database import get_database
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.get("/", response_model=List[PostFeedback])
async def get_my_feedback(
    current_user: User = Depends(get_current_active_user),
    limit: int = 20,
    skip: int = 0
):
    """Get current user's post feedback"""
    try:
        db = get_database()
        
        # Get user's profile
        profile = db.profiles.find_one({"user_id": ObjectId(current_user.id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        profile_id = profile["_id"]
        
        # Get feedback
        feedback_cursor = db.posts_feedback.find(
            {"profile_id": profile_id}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        feedback_list = []
        for feedback_data in feedback_cursor:
            # Comentário: A instanciação de PostFeedback a partir de feedback_data funciona com Pydantic v2.
            feedback_list.append(PostFeedback(**feedback_data))
        
        return feedback_list
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{post_id}", response_model=PostFeedback)
async def get_post_feedback(
    post_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get feedback for a specific post"""
    try:
        db = get_database()
        
        # Get user's profile
        profile = db.profiles.find_one({"user_id": ObjectId(current_user.id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        profile_id = profile["_id"]
        
        # Get feedback
        feedback_data = db.posts_feedback.find_one({
            "post_id": post_id,
            "profile_id": profile_id
        })
        
        if not feedback_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found for this post"
            )
        
        # Comentário: A instanciação de PostFeedback a partir de feedback_data funciona com Pydantic v2.
        return PostFeedback(**feedback_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting post feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/stats/summary", response_model=dict)
async def get_feedback_summary(
    current_user: User = Depends(get_current_active_user)
):
    """Get summary statistics of user's post feedback"""
    try:
        db = get_database()
        
        # Get user's profile
        profile = db.profiles.find_one({"user_id": ObjectId(current_user.id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        profile_id = profile["_id"]
        
        # Aggregate feedback statistics
        pipeline = [
            {"$match": {"profile_id": profile_id}},
            {"$group": {
                "_id": None,
                "total_posts": {"$sum": 1},
                "avg_overall_score": {"$avg": "$scores.overall"},
                "avg_content_quality": {"$avg": "$scores.content_quality"},
                "avg_engagement_potential": {"$avg": "$scores.engagement_potential"},
                "avg_visual_appeal": {"$avg": "$scores.visual_appeal"},
                "best_post": {"$max": "$scores.overall"},
                "worst_post": {"$min": "$scores.overall"}
            }}
        ]
        
        result = list(db.posts_feedback.aggregate(pipeline))
        
        if result:
            stats = result[0]
            return {
                "total_posts_analyzed": stats.get("total_posts", 0),
                "average_scores": {
                    "overall": round(stats.get("avg_overall_score", 0.0), 2),
                    "content_quality": round(stats.get("avg_content_quality", 0.0), 2),
                    "engagement_potential": round(stats.get("avg_engagement_potential", 0.0), 2),
                    "visual_appeal": round(stats.get("avg_visual_appeal", 0.0), 2)
                },
                "best_post_score": round(stats.get("best_post", 0.0), 2),
                "worst_post_score": round(stats.get("worst_post", 0.0), 2)
            }
        else:
            return {
                "total_posts_analyzed": 0,
                "average_scores": {
                    "overall": 0.0,
                    "content_quality": 0.0,
                    "engagement_potential": 0.0,
                    "visual_appeal": 0.0
                },
                "best_post_score": 0.0,
                "worst_post_score": 0.0
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feedback summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Comentário: Nenhuma alteração direta foi necessária neste arquivo para compatibilidade com Pydantic v2,
# pois ele utiliza modelos que já foram atualizados em `app/models.py` e a instanciação de modelos
# a partir de dados do banco de dados funciona de forma compatível com Pydantic v2.


