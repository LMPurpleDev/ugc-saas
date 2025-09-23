import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
from typing import List, Optional
import base64
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        if settings.sendgrid_api_key:
            self.sg = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)
        else:
            self.sg = None
            logger.warning("SendGrid API key not configured")
    
    def send_report_notification(
        self,
        to_email: str,
        user_name: str,
        report_title: str,
        report_path: Optional[str] = None
    ) -> bool:
        """Send report notification email"""
        
        if not self.sg:
            logger.error("SendGrid not configured")
            return False
        
        try:
            from_email = Email(settings.from_email)
            to_email_obj = To(to_email)
            subject = f"Seu relatório '{report_title}' está pronto!"
            
            # HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Relatório Pronto - UGC SaaS</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #2563eb, #3b82f6);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 8px 8px 0 0;
                    }}
                    .content {{
                        background: #f9fafb;
                        padding: 30px;
                        border-radius: 0 0 8px 8px;
                    }}
                    .button {{
                        display: inline-block;
                        background: #2563eb;
                        color: white;
                        padding: 12px 24px;
                        text-decoration: none;
                        border-radius: 6px;
                        font-weight: 600;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #e5e7eb;
                        color: #6b7280;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 Relatório Pronto!</h1>
                </div>
                <div class="content">
                    <p>Olá, <strong>{user_name}</strong>!</p>
                    
                    <p>Seu relatório "<strong>{report_title}</strong>" foi gerado com sucesso e está pronto para download.</p>
                    
                    <p>Este relatório contém:</p>
                    <ul>
                        <li>📈 Análise detalhada da sua performance</li>
                        <li>📊 Gráficos de evolução das métricas</li>
                        <li>🤖 Feedback de IA dos seus posts</li>
                        <li>💡 Recomendações estratégicas personalizadas</li>
                    </ul>
                    
                    <p>Acesse sua conta para visualizar e baixar o relatório:</p>
                    
                    <a href="https://ugcsaas.com/reports" class="button">Ver Relatórios</a>
                    
                    <p>Continue criando conteúdo incrível! 🚀</p>
                </div>
                <div class="footer">
                    <p>UGC SaaS - Plataforma para Criadores de Conteúdo</p>
                    <p>Este é um email automático, não responda.</p>
                </div>
            </body>
            </html>
            """
            
            # Plain text content
            plain_content = f"""
            Olá, {user_name}!
            
            Seu relatório "{report_title}" foi gerado com sucesso e está pronto para download.
            
            Este relatório contém:
            - Análise detalhada da sua performance
            - Gráficos de evolução das métricas
            - Feedback de IA dos seus posts
            - Recomendações estratégicas personalizadas
            
            Acesse sua conta em https://ugcsaas.com/reports para visualizar e baixar o relatório.
            
            Continue criando conteúdo incrível!
            
            UGC SaaS - Plataforma para Criadores de Conteúdo
            """
            
            mail = Mail(
                from_email=from_email,
                to_emails=to_email_obj,
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_content
            )
            
            # Attach PDF if provided
            if report_path:
                try:
                    with open(report_path, 'rb') as f:
                        data = f.read()
                        encoded_file = base64.b64encode(data).decode()
                    
                    attachment = Attachment(
                        FileContent(encoded_file),
                        FileName(f"{report_title}.pdf"),
                        FileType("application/pdf"),
                        Disposition("attachment")
                    )
                    mail.attachment = attachment
                except Exception as e:
                    logger.warning(f"Could not attach report file: {e}")
            
            # Send email
            response = self.sg.send(mail)
            
            if response.status_code in [200, 202]:
                logger.info(f"Report notification sent to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending report notification: {e}")
            return False
    
    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Send welcome email to new users"""
        
        if not self.sg:
            logger.error("SendGrid not configured")
            return False
        
        try:
            from_email = Email(settings.from_email)
            to_email_obj = To(to_email)
            subject = "Bem-vindo ao UGC SaaS! 🎉"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Bem-vindo - UGC SaaS</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #2563eb, #3b82f6);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 8px 8px 0 0;
                    }}
                    .content {{
                        background: #f9fafb;
                        padding: 30px;
                        border-radius: 0 0 8px 8px;
                    }}
                    .button {{
                        display: inline-block;
                        background: #2563eb;
                        color: white;
                        padding: 12px 24px;
                        text-decoration: none;
                        border-radius: 6px;
                        font-weight: 600;
                        margin: 20px 0;
                    }}
                    .feature {{
                        background: white;
                        padding: 20px;
                        margin: 15px 0;
                        border-radius: 6px;
                        border-left: 4px solid #2563eb;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #e5e7eb;
                        color: #6b7280;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🎉 Bem-vindo ao UGC SaaS!</h1>
                </div>
                <div class="content">
                    <p>Olá, <strong>{user_name}</strong>!</p>
                    
                    <p>Seja bem-vindo à plataforma que vai revolucionar a forma como você analisa e otimiza seu conteúdo UGC!</p>
                    
                    <div class="feature">
                        <h3>📊 Dashboard Completo</h3>
                        <p>Visualize todas as suas métricas em tempo real com gráficos interativos.</p>
                    </div>
                    
                    <div class="feature">
                        <h3>🤖 Análise com IA</h3>
                        <p>Receba feedback automático e sugestões personalizadas para cada post.</p>
                    </div>
                    
                    <div class="feature">
                        <h3>📈 Relatórios Automáticos</h3>
                        <p>Relatórios semanais e mensais gerados automaticamente.</p>
                    </div>
                    
                    <div class="feature">
                        <h3>🎯 Direcionamento de Carreira</h3>
                        <p>Insights estratégicos para acelerar seu crescimento como criador.</p>
                    </div>
                    
                    <p><strong>Próximos passos:</strong></p>
                    <ol>
                        <li>Complete seu perfil</li>
                        <li>Conecte sua conta do Instagram</li>
                        <li>Aguarde a primeira análise automática</li>
                    </ol>
                    
                    <a href="https://ugcsaas.com/profile" class="button">Completar Perfil</a>
                    
                    <p>Estamos aqui para ajudar você a crescer! 🚀</p>
                </div>
                <div class="footer">
                    <p>UGC SaaS - Plataforma para Criadores de Conteúdo</p>
                    <p>Precisa de ajuda? Entre em contato conosco.</p>
                </div>
            </body>
            </html>
            """
            
            plain_content = f"""
            Olá, {user_name}!
            
            Seja bem-vindo à plataforma UGC SaaS!
            
            Nossa plataforma oferece:
            - Dashboard completo com métricas em tempo real
            - Análise com IA e feedback automático
            - Relatórios semanais e mensais automáticos
            - Direcionamento estratégico de carreira
            
            Próximos passos:
            1. Complete seu perfil
            2. Conecte sua conta do Instagram
            3. Aguarde a primeira análise automática
            
            Acesse: https://ugcsaas.com/profile
            
            Estamos aqui para ajudar você a crescer!
            
            UGC SaaS - Plataforma para Criadores de Conteúdo
            """
            
            mail = Mail(
                from_email=from_email,
                to_emails=to_email_obj,
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_content
            )
            
            response = self.sg.send(mail)
            
            if response.status_code in [200, 202]:
                logger.info(f"Welcome email sent to {to_email}")
                return True
            else:
                logger.error(f"Failed to send welcome email. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
            return False

# Global instance
email_service = EmailService()

