import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from io import BytesIO
import base64
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Service for generating PDF reports"""
    
    def __init__(self, reports_dir: str = "/app/reports"):
        self.reports_dir = reports_dir
        os.makedirs(reports_dir, exist_ok=True)
        
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def generate_performance_report(
        self,
        profile_data: Dict[str, Any],
        metrics_data: List[Dict[str, Any]],
        feedback_data: List[Dict[str, Any]],
        report_title: str,
        period_start: datetime,
        period_end: datetime
    ) -> str:
        """Generate a comprehensive performance report"""
        
        try:
            # Create filename
            filename = f"report_{profile_data['_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.reports_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#2563eb')
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.HexColor('#1f2937')
            )
            
            # Title
            story.append(Paragraph(report_title, title_style))
            story.append(Spacer(1, 20))
            
            # Profile info
            story.append(Paragraph("Informações do Perfil", heading_style))
            profile_info = [
                ['Nome:', profile_data.get('display_name', 'N/A')],
                ['Nicho:', profile_data.get('niche', 'N/A').title()],
                ['Período:', f"{period_start.strftime('%d/%m/%Y')} - {period_end.strftime('%d/%m/%Y')}"],
                ['Gerado em:', datetime.now().strftime('%d/%m/%Y às %H:%M')]
            ]
            
            profile_table = Table(profile_info, colWidths=[2*inch, 4*inch])
            profile_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
            ]))
            
            story.append(profile_table)
            story.append(Spacer(1, 30))
            
            # Metrics summary
            if metrics_data:
                story.append(Paragraph("Resumo de Métricas", heading_style))
                
                latest_metrics = metrics_data[0] if metrics_data else {}
                oldest_metrics = metrics_data[-1] if len(metrics_data) > 1 else latest_metrics
                
                # Calculate growth
                followers_growth = self._calculate_growth(
                    latest_metrics.get('followers_count', 0),
                    oldest_metrics.get('followers_count', 0)
                )
                
                engagement_growth = self._calculate_growth(
                    latest_metrics.get('avg_engagement_rate', 0),
                    oldest_metrics.get('avg_engagement_rate', 0)
                )
                
                metrics_summary = [
                    ['Métrica', 'Valor Atual', 'Crescimento'],
                    ['Seguidores', f"{latest_metrics.get('followers_count', 0):,}", f"{followers_growth:+.1f}%"],
                    ['Taxa de Engajamento', f"{latest_metrics.get('avg_engagement_rate', 0):.2f}%", f"{engagement_growth:+.1f}%"],
                    ['Total de Curtidas', f"{latest_metrics.get('total_likes', 0):,}", "-"],
                    ['Total de Comentários', f"{latest_metrics.get('total_comments', 0):,}", "-"],
                    ['Posts Analisados', f"{latest_metrics.get('posts_count', 0)}", "-"]
                ]
                
                metrics_table = Table(metrics_summary, colWidths=[2*inch, 1.5*inch, 1.5*inch])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
                ]))
                
                story.append(metrics_table)
                story.append(Spacer(1, 30))
                
                # Generate charts
                charts_path = self._generate_charts(metrics_data)
                if charts_path:
                    story.append(Paragraph("Evolução das Métricas", heading_style))
                    story.append(Image(charts_path, width=6*inch, height=4*inch))
                    story.append(Spacer(1, 20))
            
            # Feedback analysis
            if feedback_data:
                story.append(Paragraph("Análise de Feedback", heading_style))
                
                # Calculate average scores
                avg_scores = self._calculate_average_scores(feedback_data)
                
                feedback_summary = [
                    ['Métrica', 'Nota Média', 'Classificação'],
                    ['Nota Geral', f"{avg_scores['overall']:.1f}/10", self._get_score_classification(avg_scores['overall'])],
                    ['Qualidade do Conteúdo', f"{avg_scores['content_quality']:.1f}/10", self._get_score_classification(avg_scores['content_quality'])],
                    ['Potencial de Engajamento', f"{avg_scores['engagement_potential']:.1f}/10", self._get_score_classification(avg_scores['engagement_potential'])],
                    ['Apelo Visual', f"{avg_scores['visual_appeal']:.1f}/10", self._get_score_classification(avg_scores['visual_appeal'])]
                ]
                
                feedback_table = Table(feedback_summary, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
                feedback_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')])
                ]))
                
                story.append(feedback_table)
                story.append(Spacer(1, 20))
                
                # Top suggestions
                all_suggestions = []
                for feedback in feedback_data:
                    all_suggestions.extend(feedback.get('suggestions', []))
                
                if all_suggestions:
                    story.append(Paragraph("Principais Sugestões de Melhoria", heading_style))
                    
                    # Get unique suggestions (limit to top 5)
                    unique_suggestions = list(set(all_suggestions))[:5]
                    
                    for i, suggestion in enumerate(unique_suggestions, 1):
                        story.append(Paragraph(f"{i}. {suggestion}", styles['Normal']))
                        story.append(Spacer(1, 6))
                    
                    story.append(Spacer(1, 20))
            
            # Recommendations
            story.append(Paragraph("Recomendações Estratégicas", heading_style))
            
            recommendations = self._generate_recommendations(metrics_data, feedback_data, profile_data)
            
            for i, rec in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
                story.append(Spacer(1, 8))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"Report generated successfully: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    def _calculate_growth(self, current: float, previous: float) -> float:
        """Calculate growth percentage"""
        if previous == 0:
            return 0.0
        return ((current - previous) / previous) * 100
    
    def _calculate_average_scores(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average scores from feedback data"""
        if not feedback_data:
            return {'overall': 0, 'content_quality': 0, 'engagement_potential': 0, 'visual_appeal': 0}
        
        totals = {'overall': 0, 'content_quality': 0, 'engagement_potential': 0, 'visual_appeal': 0}
        count = len(feedback_data)
        
        for feedback in feedback_data:
            scores = feedback.get('scores', {})
            for key in totals.keys():
                totals[key] += scores.get(key, 0) * 10  # Convert to 0-10 scale
        
        return {key: total / count for key, total in totals.items()}
    
    def _get_score_classification(self, score: float) -> str:
        """Get classification for a score"""
        if score >= 8:
            return "Excelente"
        elif score >= 6:
            return "Bom"
        elif score >= 4:
            return "Regular"
        else:
            return "Precisa Melhorar"
    
    def _generate_charts(self, metrics_data: List[Dict[str, Any]]) -> Optional[str]:
        """Generate charts for metrics data"""
        try:
            if not metrics_data:
                return None
            
            # Prepare data
            dates = [m.get('date', datetime.now()) for m in reversed(metrics_data)]
            followers = [m.get('followers_count', 0) for m in reversed(metrics_data)]
            engagement = [m.get('avg_engagement_rate', 0) for m in reversed(metrics_data)]
            
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Followers chart
            ax1.plot(dates, followers, marker='o', linewidth=2, markersize=6)
            ax1.set_title('Evolução de Seguidores', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Seguidores')
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='x', rotation=45)
            
            # Engagement chart
            ax2.plot(dates, engagement, marker='s', color='orange', linewidth=2, markersize=6)
            ax2.set_title('Taxa de Engajamento (%)', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Engajamento (%)')
            ax2.set_xlabel('Data')
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Save chart
            chart_path = os.path.join(self.reports_dir, f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
            return None
    
    def _generate_recommendations(
        self, 
        metrics_data: List[Dict[str, Any]], 
        feedback_data: List[Dict[str, Any]],
        profile_data: Dict[str, Any]
    ) -> List[str]:
        """Generate strategic recommendations based on data"""
        
        recommendations = []
        
        # Analyze metrics trends
        if len(metrics_data) >= 2:
            latest = metrics_data[0]
            previous = metrics_data[-1]
            
            followers_growth = self._calculate_growth(
                latest.get('followers_count', 0),
                previous.get('followers_count', 0)
            )
            
            engagement_growth = self._calculate_growth(
                latest.get('avg_engagement_rate', 0),
                previous.get('avg_engagement_rate', 0)
            )
            
            if followers_growth < 5:
                recommendations.append("Foque em estratégias de crescimento de seguidores, como colaborações e uso de hashtags relevantes.")
            
            if engagement_growth < 0:
                recommendations.append("Sua taxa de engajamento está diminuindo. Considere criar conteúdo mais interativo e responder aos comentários mais rapidamente.")
            
            if latest.get('avg_engagement_rate', 0) < 3:
                recommendations.append("Sua taxa de engajamento está abaixo da média. Experimente diferentes tipos de conteúdo e horários de postagem.")
        
        # Analyze feedback data
        if feedback_data:
            avg_scores = self._calculate_average_scores(feedback_data)
            
            if avg_scores['content_quality'] < 7:
                recommendations.append("Invista mais tempo na qualidade do seu conteúdo. Planeje suas postagens com antecedência.")
            
            if avg_scores['visual_appeal'] < 7:
                recommendations.append("Melhore o apelo visual dos seus posts com melhor iluminação, composição e edição.")
            
            if avg_scores['engagement_potential'] < 7:
                recommendations.append("Inclua mais call-to-actions em seus posts para incentivar interações.")
        
        # Niche-specific recommendations
        niche = profile_data.get('niche', '').lower()
        niche_recommendations = {
            'fashion': "Mostre mais looks completos e detalhes dos acessórios para aumentar o engajamento.",
            'beauty': "Crie mais tutoriais passo a passo e antes/depois para gerar mais interações.",
            'fitness': "Compartilhe sua jornada pessoal e resultados para inspirar seus seguidores.",
            'food': "Inclua receitas e dicas culinárias para agregar mais valor ao seu conteúdo.",
            'travel': "Conte histórias sobre os lugares visitados e dê dicas práticas de viagem."
        }
        
        if niche in niche_recommendations:
            recommendations.append(niche_recommendations[niche])
        
        # General recommendations
        recommendations.extend([
            "Mantenha uma frequência consistente de postagens para manter o engajamento.",
            "Analise os horários de maior atividade da sua audiência para otimizar o timing dos posts.",
            "Interaja genuinamente com seus seguidores respondendo comentários e mensagens."
        ])
        
        return recommendations[:6]  # Return top 6 recommendations

# Global instance
report_generator = ReportGenerator()

