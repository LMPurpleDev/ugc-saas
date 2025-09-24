from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from app.models import User
from app.auth import get_current_active_user
from app.database import get_database
from app.services.ai_service import ai_service
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai-insights"])

@router.post("/analyze-post")
async def analyze_post(
    post_caption: str,
    media_type: str,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze a post using AI"""
    try:
        db = get_database()
        
        # Get user\'s profile to determine niche
        profile = db.profiles.find_one({"user_id": ObjectId(current_user.id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        niche = profile.get("niche", "lifestyle")
        
        # Analyze post with AI
        analysis = ai_service.analyze_post_content(
            caption=post_caption,
            media_type=media_type,
            niche=niche
        )
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to analyze post content"
            )
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/content-suggestions")
async def get_content_suggestions(current_user: User = Depends(get_current_active_user)):
    """Get AI-generated content suggestions"""
    try:
        db = get_database()
        
        # Get user\'s profile
        profile = db.profiles.find_one({"user_id": ObjectId(current_user.id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        niche = profile.get("niche", "lifestyle")
        profile_id = profile["_id"]
        
        # Get recent performance data
        recent_metrics = list(db.metrics.find(
            {"profile_id": profile_id}
        ).sort("date", -1).limit(5))
        
        # Convert metrics to performance data
        recent_performance = []
        for metric in recent_metrics:
            if metric.get("followers_count", 0) > 0:
                engagement_rate = metric.get("avg_engagement_rate", 0)
                recent_performance.append({
                    "engagement_rate": engagement_rate,
                    "media_type": "mixed",  # We don\'t have specific type in metrics
                    "date": metric.get("date")
                })
        
        # Generate suggestions
        suggestions = ai_service.generate_content_suggestions(
            niche=niche,
            recent_performance=recent_performance
        )
        
        if not suggestions:
            # Fallback suggestions based on niche
            fallback_suggestions = {
                "fashion": [
                    "Mostre seu look do dia com detalhes dos acessórios",
                    "Faça um antes e depois de um styling",
                    "Compartilhe dicas de como combinar peças básicas",
                    "Mostre sua rotina matinal de escolha de roupas",
                    "Crie um post sobre tendências da estação"
                ],
                "beauty": [
                    "Tutorial de maquiagem passo a passo",
                    "Rotina de skincare matinal e noturna",
                    "Resenha de produtos que você usa",
                    "Transformação com maquiagem",
                    "Dicas de cuidados com a pele"
                ],
                "fitness": [
                    "Treino rápido de 10 minutos",
                    "Receita de pré-treino saudável",
                    "Progresso da sua jornada fitness",
                    "Dicas de motivação para exercícios",
                    "Comparação de antes e depois"
                ]
            }
            
            suggestions = fallback_suggestions.get(niche, [
                "Compartilhe uma dica valiosa do seu nicho",
                "Mostre os bastidores do seu trabalho",
                "Faça uma pergunta para engajar sua audiência",
                "Conte uma história pessoal relacionada ao seu conteúdo",
                "Crie um post educativo sobre seu tema"
            ])
        
        return {"suggestions": suggestions}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/audience-insights")
async def get_audience_insights(current_user: User = Depends(get_current_active_user)):
    """Get AI-powered audience insights"""
    try:
        db = get_database()
        
        # Get user\'s profile
        profile = db.profiles.find_one({"user_id": ObjectId(current_user.id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        profile_id = profile["_id"]
        
        # Get recent metrics for analysis
        recent_metrics = list(db.metrics.find(
            {"profile_id": profile_id}
        ).sort("date", -1).limit(10))
        
        if not recent_metrics:
            return {
                "message": "Não há dados suficientes para análise. Conecte sua conta do Instagram e aguarde a coleta de dados.",
                "insights": None
            }
        
        # Prepare follower data
        latest_metric = recent_metrics[0]
        oldest_metric = recent_metrics[-1] if len(recent_metrics) > 1 else recent_metrics[0]
        
        follower_growth = 0
        if oldest_metric.get("followers_count", 0) > 0:
            follower_growth = ((latest_metric.get("followers_count", 0) - oldest_metric.get("followers_count", 0)) / oldest_metric.get("followers_count", 1)) * 100
        
        follower_data = {
            "count": latest_metric.get("followers_count", 0),
            "growth_rate": follower_growth
        }
        
        # Prepare engagement patterns
        engagement_patterns = []
        for metric in recent_metrics:
            engagement_patterns.append({
                "date": metric.get("date", "").strftime("%Y-%m-%d") if metric.get("date") else "N/A",
                "engagement_rate": metric.get("avg_engagement_rate", 0)
            })
        
        # Get AI insights
        insights = ai_service.analyze_audience_insights(
            follower_data=follower_data,
            engagement_patterns=engagement_patterns
        )
        
        if not insights:
            # Provide basic insights based on data
            avg_engagement = sum(p["engagement_rate"] for p in engagement_patterns) / len(engagement_patterns) if engagement_patterns else 0
            
            insights = {
                "audience_profile": f"Sua audiência de {follower_data['count']} seguidores tem uma taxa de engajamento média de {avg_engagement:.2f}%",
                "best_posting_times": ["09:00", "12:00", "18:00"],
                "top_content_types": ["Imagens", "Vídeos", "Stories"],
                "growth_opportunities": [
                    "Postar com mais consistência",
                    "Usar hashtags relevantes",
                    "Interagir mais com seguidores"
                ],
                "strategic_recommendations": [
                    "Mantenha uma frequência regular de posts",
                    "Responda aos comentários rapidamente",
                    "Crie conteúdo que gere conversas"
                ]
            }
        
        return {"insights": insights}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audience insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/generate-post-feedback")
async def generate_post_feedback(
    post_id: str,
    post_url: str,
    post_caption: str,
    post_type: str,
    current_user: User = Depends(get_current_active_user)
):
    """Generate AI feedback for a specific post"""
    try:
        db = get_database()
        
        # Get user\'s profile
        profile = db.profiles.find_one({"user_id": ObjectId(current_user.id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        profile_id = str(profile["_id"])
        niche = profile.get("niche", "lifestyle")
        
        # Check if feedback already exists
        existing_feedback = db.posts_feedback.find_one({"post_id": post_id})
        if existing_feedback:
            return {"message": "Feedback already exists for this post"}
        
        # Create post feedback using AI
        feedback = ai_service.create_post_feedback(
            profile_id=profile_id,
            post_id=post_id,
            post_url=post_url,
            post_caption=post_caption,
            post_type=post_type,
            niche=niche
        )
        
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate post feedback"
            )
        
        # Save feedback to database
        from app.models import PostFeedbackInDB
        # Comentário: Atualizado feedback.dict() para feedback.model_dump() para Pydantic v2.
        feedback_data = PostFeedbackInDB(**feedback.model_dump())
        # Comentário: Atualizado feedback_data.dict(by_alias=True) para feedback_data.model_dump(by_alias=True) para Pydantic v2.
        result = db.posts_feedback.insert_one(feedback_data.model_dump(by_alias=True))
        
        if result.inserted_id:
            return {"message": "Post feedback generated successfully", "feedback_id": str(result.inserted_id)}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save post feedback"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating post feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


