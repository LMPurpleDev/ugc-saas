import openai
import logging
from typing import Dict, List, Optional, Any
from app.config import settings
from app.models import PostFeedbackCreate, FeedbackScore
from bson import ObjectId

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered content analysis and feedback"""
    
    def __init__(self):
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
        else:
            logger.warning("OpenAI API key not configured")
    
    def analyze_post_content(
        self, 
        caption: str, 
        media_type: str, 
        niche: str,
        engagement_data: Optional[Dict[str, int]] = None
    ) -> Optional[Dict[str, Any]]:
        """Analyze post content and generate feedback using AI"""
        
        if not settings.openai_api_key:
            logger.error("OpenAI API key not configured")
            return None
        
        try:
            # Prepare context for AI analysis
            context = f"""
            Você é um especialista em marketing digital e criação de conteúdo UGC (User Generated Content).
            Analise o seguinte post de um criador de conteúdo no nicho de {niche}.
            
            Tipo de mídia: {media_type}
            Legenda do post: "{caption}"
            """
            
            if engagement_data:
                context += f"""
                Dados de engajamento:
                - Curtidas: {engagement_data.get('likes', 0)}
                - Comentários: {engagement_data.get('comments', 0)}
                - Compartilhamentos: {engagement_data.get('shares', 0)}
                - Salvamentos: {engagement_data.get('saved', 0)}
                - Alcance: {engagement_data.get('reach', 0)}
                """
            
            prompt = context + """
            
            Por favor, forneça uma análise detalhada do post seguindo este formato JSON:
            {
                "scores": {
                    "overall": [nota de 0 a 1],
                    "content_quality": [nota de 0 a 1],
                    "engagement_potential": [nota de 0 a 1],
                    "visual_appeal": [nota de 0 a 1]
                },
                "feedback_text": "[feedback detalhado em português sobre o post]",
                "suggestions": [
                    "[sugestão 1 para melhorar o post]",
                    "[sugestão 2 para melhorar o post]",
                    "[sugestão 3 para melhorar o post]"
                ]
            }
            
            Critérios de avaliação:
            - overall: Nota geral do post considerando todos os aspectos
            - content_quality: Qualidade do conteúdo, relevância, originalidade
            - engagement_potential: Potencial de gerar engajamento (curtidas, comentários, compartilhamentos)
            - visual_appeal: Atratividade visual e estética (mesmo para posts de texto)
            
            O feedback deve ser construtivo, específico e focado em melhorias práticas.
            As sugestões devem ser acionáveis e relevantes para o nicho do criador.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em marketing digital e análise de conteúdo UGC."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Parse the response
            ai_response = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            import json
            try:
                analysis = json.loads(ai_response)
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response
                logger.warning("AI response was not valid JSON, creating fallback response")
                return {
                    "scores": {
                        "overall": 0.7,
                        "content_quality": 0.7,
                        "engagement_potential": 0.7,
                        "visual_appeal": 0.7
                    },
                    "feedback_text": ai_response,
                    "suggestions": [
                        "Considere adicionar mais elementos visuais ao seu conteúdo",
                        "Use hashtags relevantes para aumentar o alcance",
                        "Inclua uma call-to-action clara no final do post"
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error analyzing post content: {e}")
            return None
    
    def generate_content_suggestions(
        self, 
        niche: str, 
        recent_performance: List[Dict[str, Any]],
        target_audience: Optional[str] = None
    ) -> Optional[List[str]]:
        """Generate content suggestions based on niche and performance data"""
        
        if not settings.openai_api_key:
            logger.error("OpenAI API key not configured")
            return None
        
        try:
            # Analyze recent performance
            performance_summary = ""
            if recent_performance:
                avg_engagement = sum(p.get('engagement_rate', 0) for p in recent_performance) / len(recent_performance)
                best_performing = max(recent_performance, key=lambda x: x.get('engagement_rate', 0))
                performance_summary = f"""
                Performance recente:
                - Taxa de engajamento média: {avg_engagement:.2f}%
                - Melhor post teve {best_performing.get('engagement_rate', 0):.2f}% de engajamento
                - Tipo de conteúdo que mais engaja: {best_performing.get('media_type', 'N/A')}
                """
            
            audience_context = f"Público-alvo: {target_audience}" if target_audience else ""
            
            prompt = f"""
            Você é um especialista em estratégia de conteúdo para criadores UGC.
            
            Nicho do criador: {niche}
            {audience_context}
            {performance_summary}
            
            Gere 5 sugestões específicas e acionáveis de conteúdo para este criador.
            As sugestões devem:
            1. Ser relevantes para o nicho
            2. Ter potencial de alto engajamento
            3. Ser práticas e executáveis
            4. Considerar tendências atuais
            5. Levar em conta a performance recente
            
            Formato: Lista simples, uma sugestão por linha, sem numeração.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em estratégia de conteúdo e marketing digital."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.8
            )
            
            suggestions_text = response.choices[0].message.content.strip()
            
            # Split into individual suggestions
            suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip()]
            
            return suggestions[:5]  # Return max 5 suggestions
            
        except Exception as e:
            logger.error(f"Error generating content suggestions: {e}")
            return None
    
    def analyze_audience_insights(
        self, 
        follower_data: Dict[str, Any],
        engagement_patterns: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Analyze audience data and provide insights"""
        
        if not settings.openai_api_key:
            logger.error("OpenAI API key not configured")
            return None
        
        try:
            # Prepare data summary
            data_summary = f"""
            Dados do público:
            - Total de seguidores: {follower_data.get('count', 0)}
            - Crescimento recente: {follower_data.get('growth_rate', 0):.2f}%
            
            Padrões de engajamento:
            """
            
            for pattern in engagement_patterns[:5]:  # Limit to 5 recent patterns
                data_summary += f"- {pattern.get('date', 'N/A')}: {pattern.get('engagement_rate', 0):.2f}% de engajamento\n"
            
            prompt = f"""
            Você é um analista de dados especializado em redes sociais e comportamento de audiência.
            
            {data_summary}
            
            Com base nesses dados, forneça insights sobre:
            1. Perfil da audiência
            2. Melhores horários para postar
            3. Tipos de conteúdo que mais engajam
            4. Oportunidades de crescimento
            5. Recomendações estratégicas
            
            Responda em formato JSON:
            {
                "audience_profile": "[descrição do perfil da audiência]",
                "best_posting_times": ["horário1", "horário2", "horário3"],
                "top_content_types": ["tipo1", "tipo2", "tipo3"],
                "growth_opportunities": ["oportunidade1", "oportunidade2"],
                "strategic_recommendations": ["recomendação1", "recomendação2", "recomendação3"]
            }
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um analista de dados especializado em redes sociais."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.6
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            import json
            try:
                insights = json.loads(ai_response)
                return insights
            except json.JSONDecodeError:
                logger.warning("AI response was not valid JSON for audience insights")
                return {
                    "audience_profile": "Análise detalhada não disponível no momento",
                    "best_posting_times": ["09:00", "12:00", "18:00"],
                    "top_content_types": ["Imagens", "Vídeos", "Carrosséis"],
                    "growth_opportunities": ["Aumentar frequência de posts", "Usar mais hashtags"],
                    "strategic_recommendations": ["Foque em conteúdo visual", "Interaja mais com seguidores", "Poste consistentemente"]
                }
                
        except Exception as e:
            logger.error(f"Error analyzing audience insights: {e}")
            return None
    
    def create_post_feedback(
        self,
        profile_id: str,
        post_id: str,
        post_url: str,
        post_caption: str,
        post_type: str,
        niche: str,
        engagement_data: Optional[Dict[str, int]] = None
    ) -> Optional[PostFeedbackCreate]:
        """Create comprehensive post feedback using AI analysis"""
        
        try:
            # Get AI analysis
            analysis = self.analyze_post_content(
                caption=post_caption,
                media_type=post_type,
                niche=niche,
                engagement_data=engagement_data
            )
            
            if not analysis:
                logger.error("Failed to get AI analysis for post")
                return None
            
            # Create feedback scores
            scores = FeedbackScore(
                overall=analysis['scores'].get('overall', 0.5),
                content_quality=analysis['scores'].get('content_quality', 0.5),
                engagement_potential=analysis['scores'].get('engagement_potential', 0.5),
                visual_appeal=analysis['scores'].get('visual_appeal', 0.5)
            )
            
            # Create post feedback
            feedback = PostFeedbackCreate(
                profile_id=ObjectId(profile_id),
                post_id=post_id,
                post_url=post_url,
                post_caption=post_caption,
                post_type=post_type,
                scores=scores,
                feedback_text=analysis.get('feedback_text', ''),
                suggestions=analysis.get('suggestions', [])
            )
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error creating post feedback: {e}")
            return None

# Global instance
ai_service = AIService()

