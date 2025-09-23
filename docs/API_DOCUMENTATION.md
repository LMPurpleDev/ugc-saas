# Documentação da API - UGC SaaS

Esta documentação fornece informações detalhadas sobre todos os endpoints da API do UGC SaaS, incluindo autenticação, parâmetros, exemplos de requisições e respostas.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Autenticação](#autenticação)
3. [Endpoints de Autenticação](#endpoints-de-autenticação)
4. [Endpoints de Perfil](#endpoints-de-perfil)
5. [Endpoints de Relatórios](#endpoints-de-relatórios)
6. [Endpoints de Feedback](#endpoints-de-feedback)
7. [Endpoints do Instagram](#endpoints-do-instagram)
8. [Endpoints de IA](#endpoints-de-ia)
9. [Códigos de Status](#códigos-de-status)
10. [Exemplos de Uso](#exemplos-de-uso)

## 🌐 Visão Geral

### Base URL
- **Desenvolvimento**: `http://localhost:8000`
- **Produção**: `https://api.ugcsaas.com`

### Formato de Dados
- **Content-Type**: `application/json`
- **Charset**: `UTF-8`
- **Date Format**: ISO 8601 (`YYYY-MM-DDTHH:mm:ss.sssZ`)

### Rate Limiting
- **Geral**: 100 requisições por minuto
- **Autenticação**: 10 requisições por minuto
- **Upload**: 10 requisições por minuto

## 🔐 Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação. Todos os endpoints protegidos requerem um token válido no header `Authorization`.

### Header de Autenticação
```http
Authorization: Bearer <access_token>
```

### Fluxo de Autenticação
1. **Login**: Obter access_token e refresh_token
2. **Requisições**: Usar access_token no header
3. **Renovação**: Usar refresh_token quando access_token expirar

### Expiração de Tokens
- **Access Token**: 30 minutos
- **Refresh Token**: 7 dias

## 🔑 Endpoints de Autenticação

### POST /auth/register
Registra um novo usuário na plataforma.

#### Parâmetros
```json
{
  "full_name": "string",
  "email": "string",
  "password": "string"
}
```

#### Validações
- `full_name`: Mínimo 2 caracteres
- `email`: Formato de email válido, único
- `password`: Mínimo 8 caracteres

#### Resposta de Sucesso (201)
```json
{
  "message": "User created successfully",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "full_name": "João Silva",
    "email": "joao@email.com",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00.000Z"
  }
}
```

#### Exemplo de Requisição
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "João Silva",
    "email": "joao@email.com",
    "password": "minhasenha123"
  }'
```

### POST /auth/login
Autentica um usuário e retorna tokens de acesso.

#### Parâmetros
```json
{
  "email": "string",
  "password": "string"
}
```

#### Resposta de Sucesso (200)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "full_name": "João Silva",
    "email": "joao@email.com"
  }
}
```

#### Exemplo de Requisição
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@email.com",
    "password": "minhasenha123"
  }'
```

### POST /auth/refresh
Renova o access token usando o refresh token.

#### Parâmetros
```json
{
  "refresh_token": "string"
}
```

#### Resposta de Sucesso (200)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### POST /auth/logout
Invalida os tokens do usuário.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Resposta de Sucesso (200)
```json
{
  "message": "Successfully logged out"
}
```

## 👤 Endpoints de Perfil

### GET /profiles/me
Retorna o perfil do usuário autenticado.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Resposta de Sucesso (200)
```json
{
  "id": "507f1f77bcf86cd799439011",
  "user_id": "507f1f77bcf86cd799439012",
  "display_name": "João Silva",
  "bio": "Criador de conteúdo focado em lifestyle",
  "niche": "lifestyle",
  "target_audience": "Jovens adultos interessados em estilo de vida",
  "social_links": {
    "instagram": "https://instagram.com/joaosilva",
    "tiktok": "https://tiktok.com/@joaosilva"
  },
  "instagram_tokens": {
    "user_id": "17841400455970028",
    "expires_at": "2024-03-15T10:30:00.000Z"
  },
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-20T15:45:00.000Z"
}
```

### PUT /profiles/me
Atualiza o perfil do usuário autenticado.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Parâmetros
```json
{
  "display_name": "string",
  "bio": "string",
  "niche": "string",
  "target_audience": "string",
  "social_links": {
    "instagram": "string",
    "tiktok": "string",
    "youtube": "string"
  }
}
```

#### Valores Válidos para `niche`
- `lifestyle`
- `fashion`
- `beauty`
- `fitness`
- `food`
- `travel`
- `tech`
- `gaming`
- `music`
- `art`

#### Resposta de Sucesso (200)
```json
{
  "message": "Profile updated successfully",
  "profile": {
    "id": "507f1f77bcf86cd799439011",
    "display_name": "João Silva - Lifestyle",
    "bio": "Criador de conteúdo focado em lifestyle e bem-estar",
    "niche": "lifestyle",
    "updated_at": "2024-01-20T16:00:00.000Z"
  }
}
```

### GET /profiles/me/dashboard
Retorna dados do dashboard do usuário.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Parâmetros de Query (Opcionais)
- `period`: `7d`, `30d`, `90d` (padrão: `30d`)

#### Resposta de Sucesso (200)
```json
{
  "profile": {
    "id": "507f1f77bcf86cd799439011",
    "display_name": "João Silva",
    "niche": "lifestyle"
  },
  "current_metrics": {
    "followers_count": 15420,
    "following_count": 892,
    "posts_count": 156,
    "avg_engagement_rate": 4.2,
    "total_likes": 45230,
    "total_comments": 3420,
    "total_reach": 125000
  },
  "growth_metrics": {
    "followers_growth": 8.5,
    "engagement_growth": -2.1,
    "posts_growth": 12.0
  },
  "recent_posts": [
    {
      "post_id": "18123456789012345",
      "media_type": "image",
      "timestamp": "2024-01-20T14:30:00.000Z",
      "likes": 342,
      "comments": 28,
      "engagement_rate": 4.8
    }
  ],
  "top_performing_posts": [
    {
      "post_id": "18123456789012346",
      "media_type": "video",
      "likes": 1250,
      "comments": 89,
      "engagement_rate": 8.7,
      "performance_score": 9.2
    }
  ]
}
```

## 📊 Endpoints de Relatórios

### GET /reports/
Lista todos os relatórios do usuário.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Parâmetros de Query (Opcionais)
- `limit`: Número máximo de relatórios (padrão: 20, máximo: 100)
- `offset`: Número de relatórios para pular (padrão: 0)
- `report_type`: `weekly`, `monthly`, `custom`
- `is_ready`: `true`, `false`

#### Resposta de Sucesso (200)
```json
{
  "reports": [
    {
      "id": "507f1f77bcf86cd799439013",
      "title": "Relatório Semanal - 15/01 a 22/01",
      "summary": "Análise de performance da semana",
      "report_type": "weekly",
      "period_start": "2024-01-15T00:00:00.000Z",
      "period_end": "2024-01-22T23:59:59.000Z",
      "is_ready": true,
      "created_at": "2024-01-22T10:30:00.000Z",
      "file_size": 2048576
    }
  ],
  "total": 15,
  "limit": 20,
  "offset": 0
}
```

### POST /reports/generate
Gera um novo relatório personalizado.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Parâmetros
```json
{
  "title": "string",
  "summary": "string",
  "report_type": "custom",
  "period_start": "2024-01-01T00:00:00.000Z",
  "period_end": "2024-01-31T23:59:59.000Z"
}
```

#### Resposta de Sucesso (202)
```json
{
  "message": "Report generation started",
  "report_id": "507f1f77bcf86cd799439014",
  "estimated_completion": "2024-01-22T11:00:00.000Z"
}
```

### GET /reports/{report_id}
Retorna detalhes de um relatório específico.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Resposta de Sucesso (200)
```json
{
  "id": "507f1f77bcf86cd799439013",
  "title": "Relatório Semanal - 15/01 a 22/01",
  "summary": "Análise de performance da semana",
  "report_type": "weekly",
  "period_start": "2024-01-15T00:00:00.000Z",
  "period_end": "2024-01-22T23:59:59.000Z",
  "is_ready": true,
  "file_path": "/reports/report_507f1f77bcf86cd799439013.pdf",
  "file_size": 2048576,
  "created_at": "2024-01-22T10:30:00.000Z",
  "updated_at": "2024-01-22T10:35:00.000Z"
}
```

### GET /reports/{report_id}/download
Faz download do arquivo PDF do relatório.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Resposta de Sucesso (200)
```http
Content-Type: application/pdf
Content-Disposition: attachment; filename="relatorio_semanal_20240122.pdf"
Content-Length: 2048576

[Binary PDF content]
```

### DELETE /reports/{report_id}
Remove um relatório específico.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Resposta de Sucesso (200)
```json
{
  "message": "Report deleted successfully"
}
```

## 💬 Endpoints de Feedback

### GET /feedback/
Lista feedback de posts do usuário.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Parâmetros de Query (Opcionais)
- `limit`: Número máximo de feedbacks (padrão: 20, máximo: 100)
- `offset`: Número de feedbacks para pular (padrão: 0)
- `post_type`: `image`, `video`, `carousel`
- `min_score`: Nota mínima (0.0 a 1.0)

#### Resposta de Sucesso (200)
```json
{
  "feedback": [
    {
      "id": "507f1f77bcf86cd799439015",
      "post_id": "18123456789012345",
      "post_url": "https://instagram.com/p/ABC123/",
      "post_caption": "Meu look do dia! ✨",
      "post_type": "image",
      "scores": {
        "overall": 0.85,
        "content_quality": 0.82,
        "engagement_potential": 0.88,
        "visual_appeal": 0.85
      },
      "feedback_text": "Excelente post! A composição visual está muito boa e o conteúdo é relevante para sua audiência. A legenda poderia incluir mais call-to-actions para aumentar o engajamento.",
      "suggestions": [
        "Adicione uma pergunta no final da legenda",
        "Use hashtags mais específicas do seu nicho",
        "Considere postar no horário de maior atividade"
      ],
      "created_at": "2024-01-20T15:30:00.000Z"
    }
  ],
  "total": 45,
  "limit": 20,
  "offset": 0
}
```

### GET /feedback/summary
Retorna resumo estatístico dos feedbacks.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Parâmetros de Query (Opcionais)
- `period`: `7d`, `30d`, `90d` (padrão: `30d`)

#### Resposta de Sucesso (200)
```json
{
  "total_posts_analyzed": 45,
  "average_scores": {
    "overall": 0.78,
    "content_quality": 0.75,
    "engagement_potential": 0.82,
    "visual_appeal": 0.77
  },
  "best_post_score": 0.95,
  "worst_post_score": 0.42,
  "score_distribution": {
    "excellent": 12,
    "good": 18,
    "average": 10,
    "needs_improvement": 5
  },
  "top_suggestions": [
    "Adicione mais call-to-actions",
    "Use hashtags mais relevantes",
    "Melhore a qualidade visual"
  ]
}
```

### POST /feedback/analyze
Solicita análise de um post específico.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Parâmetros
```json
{
  "post_id": "string",
  "post_url": "string",
  "post_caption": "string",
  "post_type": "image|video|carousel"
}
```

#### Resposta de Sucesso (202)
```json
{
  "message": "Post analysis started",
  "feedback_id": "507f1f77bcf86cd799439016",
  "estimated_completion": "2024-01-20T15:35:00.000Z"
}
```

## 📱 Endpoints do Instagram

### GET /instagram/auth-url
Retorna URL de autorização do Instagram.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Parâmetros de Query (Opcionais)
- `state`: String para validação de estado

#### Resposta de Sucesso (200)
```json
{
  "auth_url": "https://api.instagram.com/oauth/authorize?client_id=123&redirect_uri=...&scope=instagram_basic&response_type=code&state=abc123",
  "state": "abc123"
}
```

### POST /instagram/callback
Processa callback de autorização do Instagram.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Parâmetros
```json
{
  "code": "string",
  "state": "string"
}
```

#### Resposta de Sucesso (200)
```json
{
  "message": "Instagram account connected successfully",
  "instagram_user": {
    "id": "17841400455970028",
    "username": "joaosilva",
    "account_type": "BUSINESS",
    "media_count": 156
  }
}
```

### POST /instagram/disconnect
Desconecta conta do Instagram.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Resposta de Sucesso (200)
```json
{
  "message": "Instagram account disconnected successfully"
}
```

### GET /instagram/status
Verifica status da conexão com Instagram.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Resposta de Sucesso (200)
```json
{
  "connected": true,
  "expired": false,
  "expires_at": "2024-03-15T10:30:00.000Z",
  "instagram_user": {
    "id": "17841400455970028",
    "username": "joaosilva",
    "account_type": "BUSINESS",
    "media_count": 156
  }
}
```

### POST /instagram/collect-metrics
Inicia coleta manual de métricas do Instagram.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Resposta de Sucesso (202)
```json
{
  "message": "Metrics collection started",
  "task_id": "collect_metrics_507f1f77bcf86cd799439017",
  "estimated_completion": "2024-01-20T16:00:00.000Z"
}
```

### GET /instagram/recent-posts
Lista posts recentes do Instagram.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Parâmetros de Query (Opcionais)
- `limit`: Número máximo de posts (padrão: 10, máximo: 25)

#### Resposta de Sucesso (200)
```json
{
  "posts": [
    {
      "id": "18123456789012345",
      "caption": "Meu look do dia! ✨ #fashion #ootd",
      "media_type": "IMAGE",
      "media_url": "https://scontent.cdninstagram.com/...",
      "permalink": "https://instagram.com/p/ABC123/",
      "timestamp": "2024-01-20T14:30:00.000Z"
    }
  ]
}
```

## 🤖 Endpoints de IA

### POST /ai/analyze-post
Analisa um post usando IA.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Parâmetros
```json
{
  "post_caption": "string",
  "media_type": "image|video|carousel"
}
```

#### Resposta de Sucesso (200)
```json
{
  "scores": {
    "overall": 0.85,
    "content_quality": 0.82,
    "engagement_potential": 0.88,
    "visual_appeal": 0.85
  },
  "feedback_text": "Excelente post! A composição visual está muito boa...",
  "suggestions": [
    "Adicione uma pergunta no final da legenda",
    "Use hashtags mais específicas do seu nicho"
  ]
}
```

### GET /ai/content-suggestions
Obtém sugestões de conteúdo personalizadas.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Resposta de Sucesso (200)
```json
{
  "suggestions": [
    "Mostre sua rotina matinal de skincare",
    "Faça um antes e depois de um look",
    "Compartilhe 5 dicas de organização",
    "Crie um post sobre tendências da estação",
    "Mostre os bastidores de uma sessão de fotos"
  ]
}
```

### GET /ai/audience-insights
Obtém insights da audiência usando IA.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Resposta de Sucesso (200)
```json
{
  "insights": {
    "audience_profile": "Sua audiência é composta principalmente por mulheres jovens (18-34 anos) interessadas em lifestyle e moda...",
    "best_posting_times": ["09:00", "12:00", "18:00"],
    "top_content_types": ["Imagens", "Vídeos", "Stories"],
    "growth_opportunities": [
      "Aumentar frequência de posts",
      "Usar mais hashtags relevantes"
    ],
    "strategic_recommendations": [
      "Foque em conteúdo visual de alta qualidade",
      "Interaja mais com seus seguidores",
      "Poste consistentemente nos horários de pico"
    ]
  }
}
```

### POST /ai/generate-post-feedback
Gera feedback de IA para um post específico.

#### Headers
```http
Authorization: Bearer <access_token>
```

#### Parâmetros
```json
{
  "post_id": "string",
  "post_url": "string",
  "post_caption": "string",
  "post_type": "image|video|carousel"
}
```

#### Resposta de Sucesso (202)
```json
{
  "message": "Post feedback generated successfully",
  "feedback_id": "507f1f77bcf86cd799439018"
}
```

## 📋 Códigos de Status

### Códigos de Sucesso
- **200 OK**: Requisição processada com sucesso
- **201 Created**: Recurso criado com sucesso
- **202 Accepted**: Requisição aceita para processamento assíncrono
- **204 No Content**: Requisição processada, sem conteúdo de retorno

### Códigos de Erro do Cliente
- **400 Bad Request**: Dados inválidos na requisição
- **401 Unauthorized**: Token de autenticação inválido ou ausente
- **403 Forbidden**: Acesso negado ao recurso
- **404 Not Found**: Recurso não encontrado
- **409 Conflict**: Conflito com estado atual do recurso
- **422 Unprocessable Entity**: Dados válidos mas não processáveis
- **429 Too Many Requests**: Limite de rate limiting excedido

### Códigos de Erro do Servidor
- **500 Internal Server Error**: Erro interno do servidor
- **502 Bad Gateway**: Erro de gateway
- **503 Service Unavailable**: Serviço temporariamente indisponível
- **504 Gateway Timeout**: Timeout de gateway

### Formato de Erro
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Dados de entrada inválidos",
    "details": [
      {
        "field": "email",
        "message": "Formato de email inválido"
      }
    ]
  }
}
```

## 💡 Exemplos de Uso

### Fluxo Completo de Autenticação
```bash
# 1. Registrar usuário
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Maria Silva",
    "email": "maria@email.com",
    "password": "minhasenha123"
  }'

# 2. Fazer login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria@email.com",
    "password": "minhasenha123"
  }'

# 3. Usar token nas requisições
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/profiles/me \
  -H "Authorization: Bearer $TOKEN"
```

### Configuração de Perfil
```bash
# Atualizar perfil
curl -X PUT http://localhost:8000/profiles/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Maria Silva - Beauty Creator",
    "bio": "Apaixonada por beleza e skincare 💄",
    "niche": "beauty",
    "target_audience": "Mulheres interessadas em beleza e cuidados pessoais",
    "social_links": {
      "instagram": "https://instagram.com/mariabeauty",
      "tiktok": "https://tiktok.com/@mariabeauty"
    }
  }'
```

### Conexão com Instagram
```bash
# 1. Obter URL de autorização
curl -X GET http://localhost:8000/instagram/auth-url \
  -H "Authorization: Bearer $TOKEN"

# 2. Usuário autoriza no Instagram e retorna com código

# 3. Processar callback
curl -X POST http://localhost:8000/instagram/callback \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "AQBx7s...",
    "state": "abc123"
  }'

# 4. Verificar status da conexão
curl -X GET http://localhost:8000/instagram/status \
  -H "Authorization: Bearer $TOKEN"
```

### Geração de Relatórios
```bash
# 1. Gerar relatório personalizado
curl -X POST http://localhost:8000/reports/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Relatório Janeiro 2024",
    "summary": "Análise completa do mês de janeiro",
    "report_type": "custom",
    "period_start": "2024-01-01T00:00:00.000Z",
    "period_end": "2024-01-31T23:59:59.000Z"
  }'

# 2. Listar relatórios
curl -X GET "http://localhost:8000/reports/?limit=10&is_ready=true" \
  -H "Authorization: Bearer $TOKEN"

# 3. Download de relatório
curl -X GET http://localhost:8000/reports/507f1f77bcf86cd799439013/download \
  -H "Authorization: Bearer $TOKEN" \
  -o relatorio_janeiro.pdf
```

### Análise com IA
```bash
# 1. Obter sugestões de conteúdo
curl -X GET http://localhost:8000/ai/content-suggestions \
  -H "Authorization: Bearer $TOKEN"

# 2. Analisar post
curl -X POST http://localhost:8000/ai/analyze-post \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "post_caption": "Minha rotina de skincare matinal ✨ #skincare #beauty",
    "media_type": "video"
  }'

# 3. Obter insights da audiência
curl -X GET http://localhost:8000/ai/audience-insights \
  -H "Authorization: Bearer $TOKEN"
```

## 🔧 SDKs e Bibliotecas

### JavaScript/Node.js
```javascript
// Exemplo usando axios
const axios = require('axios');

class UGCSaaSAPI {
  constructor(baseURL, accessToken) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });
  }

  async getProfile() {
    const response = await this.client.get('/profiles/me');
    return response.data;
  }

  async generateReport(reportData) {
    const response = await this.client.post('/reports/generate', reportData);
    return response.data;
  }
}

// Uso
const api = new UGCSaaSAPI('http://localhost:8000', 'your_token_here');
const profile = await api.getProfile();
```

### Python
```python
import requests

class UGCSaaSAPI:
    def __init__(self, base_url, access_token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_profile(self):
        response = requests.get(f'{self.base_url}/profiles/me', headers=self.headers)
        return response.json()
    
    def generate_report(self, report_data):
        response = requests.post(f'{self.base_url}/reports/generate', 
                               json=report_data, headers=self.headers)
        return response.json()

# Uso
api = UGCSaaSAPI('http://localhost:8000', 'your_token_here')
profile = api.get_profile()
```

---

**Esta documentação é mantida atualizada conforme a evolução da API. Para dúvidas ou sugestões, entre em contato com a equipe de desenvolvimento.**

