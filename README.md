# UGC SaaS - Plataforma para Criadores de Conteúdo

Uma plataforma completa para criadores de conteúdo UGC (User Generated Content) que oferece análise de performance, relatórios automáticos e direcionamento de carreira usando inteligência artificial.

## 🚀 Funcionalidades

### 📊 Dashboard Completo
- Visualização de métricas em tempo real
- Gráficos interativos de evolução
- Análise de performance detalhada
- Comparação de períodos

### 🤖 Análise com IA
- Feedback automático para cada post
- Notas de 0-10 para qualidade, engajamento e apelo visual
- Sugestões personalizadas de melhoria
- Insights estratégicos baseados no nicho

### 📈 Relatórios Automáticos
- Relatórios semanais e mensais em PDF
- Gráficos e tabelas profissionais
- Recomendações estratégicas
- Envio automático por email

### 🔗 Integração com Redes Sociais
- Conexão com Instagram Business API
- Coleta automática de métricas
- Análise de posts e stories
- Monitoramento de engajamento

### 🎯 Direcionamento de Carreira
- Análise de audiência
- Sugestões de conteúdo por nicho
- Identificação de oportunidades de crescimento
- Benchmarking de performance

## 🛠️ Tecnologias

### Backend
- **FastAPI** - API REST moderna e rápida
- **MongoDB** - Banco de dados NoSQL
- **Celery** - Processamento assíncrono
- **Redis** - Cache e message broker
- **OpenAI GPT** - Inteligência artificial

### Frontend
- **React** - Interface de usuário
- **Tailwind CSS** - Estilização
- **shadcn/ui** - Componentes
- **Recharts** - Gráficos interativos
- **Axios** - Cliente HTTP

### Infraestrutura
- **Docker** - Containerização
- **Docker Compose** - Orquestração
- **Nginx** - Proxy reverso
- **Celery Beat** - Agendamento de tarefas

## 🚀 Instalação Rápida

### Pré-requisitos
- Docker e Docker Compose
- Git

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/ugc-saas.git
cd ugc-saas
```

### 2. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas chaves de API
```

### 3. Inicie todos os serviços
```bash
docker-compose up --build
```

### 4. Acesse a aplicação
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação API**: http://localhost:8000/docs
- **Flower (Monitor)**: http://localhost:5555

## ⚙️ Configuração

### Variáveis de Ambiente Obrigatórias

```env
# Instagram API
INSTAGRAM_APP_ID=seu_app_id_instagram
INSTAGRAM_APP_SECRET=seu_app_secret_instagram
INSTAGRAM_REDIRECT_URI=http://localhost:3000/auth/instagram/callback

# OpenAI
OPENAI_API_KEY=sua_chave_openai

# Email (SendGrid)
SENDGRID_API_KEY=sua_chave_sendgrid
FROM_EMAIL=noreply@seudominio.com
```

### Como obter as chaves de API

#### Instagram API
1. Acesse [Facebook Developers](https://developers.facebook.com/)
2. Crie um novo app
3. Adicione o produto "Instagram Basic Display"
4. Configure as URLs de redirecionamento
5. Copie o App ID e App Secret

#### OpenAI API
1. Acesse [OpenAI Platform](https://platform.openai.com/)
2. Crie uma conta e adicione créditos
3. Gere uma nova API key
4. Copie a chave

#### SendGrid API
1. Acesse [SendGrid](https://sendgrid.com/)
2. Crie uma conta gratuita
3. Gere uma API key
4. Configure um domínio verificado

## 📋 Comandos Úteis

### Usando Makefile
```bash
# Iniciar todos os serviços
make up

# Parar todos os serviços
make down

# Ver logs
make logs

# Backup do banco
make backup

# Limpar tudo
make clean

# Ver status dos workers
make worker

# Abrir Flower
make flower
```

### Comandos Docker Compose
```bash
# Iniciar em background
docker-compose up -d

# Ver logs de um serviço específico
docker-compose logs -f backend

# Executar comando no container
docker-compose exec backend python manage.py shell

# Rebuild de um serviço
docker-compose build backend
```

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Frontend    │    │     Backend     │    │     Worker      │
│   (React/Vite)  │◄──►│   (FastAPI)     │◄──►│    (Celery)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │     MongoDB     │              │
         │              │   (Database)    │              │
         │              └─────────────────┘              │
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│      Redis      │◄─────────────┘
                        │ (Cache/Broker)  │
                        └─────────────────┘
```

## 📊 Estrutura do Projeto

```
ugc-saas/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── routers/        # Endpoints da API
│   │   ├── models/         # Modelos Pydantic
│   │   ├── services/       # Lógica de negócio
│   │   └── auth/           # Autenticação JWT
│   └── Dockerfile
├── frontend/               # Interface React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── pages/          # Páginas da aplicação
│   │   ├── contexts/       # Context API
│   │   └── lib/            # Utilitários
│   └── Dockerfile
├── worker/                 # Workers Celery
│   ├── app/
│   │   ├── tasks/          # Tarefas assíncronas
│   │   └── services/       # Serviços do worker
│   └── Dockerfile
├── nginx/                  # Configuração Nginx
├── scripts/                # Scripts de inicialização
└── docker-compose.yml      # Orquestração
```

## 🔄 Fluxo de Dados

1. **Usuário se cadastra** → Email de boas-vindas automático
2. **Conecta Instagram** → Coleta inicial de dados
3. **Worker coleta métricas** → A cada hora automaticamente
4. **IA analisa posts** → Feedback automático a cada 2 horas
5. **Relatórios gerados** → Semanais/mensais automáticos
6. **Notificações enviadas** → Email quando relatório fica pronto

## 🧪 Testes

```bash
# Testes do backend
docker-compose exec backend python -m pytest

# Testes do frontend
docker-compose exec frontend npm test

# Testes de integração
make test
```

## 📈 Monitoramento

### Flower (Celery Monitor)
- URL: http://localhost:5555
- Monitora workers e tarefas
- Visualiza filas e estatísticas

### Logs
```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f backend
```

### Health Checks
```bash
# Status dos serviços
make health

# Recursos do sistema
make monitor
```

## 🚀 Deploy em Produção

### 1. Configurar domínio e SSL
```bash
# Editar .env com seu domínio
DOMAIN=seudominio.com
SSL_EMAIL=admin@seudominio.com
```

### 2. Deploy com SSL
```bash
# Build para produção
make prod-build

# Iniciar em produção
make prod-up
```

### 3. Configurar SSL automático
O sistema usa Certbot para SSL automático com Let's Encrypt.

## 🔒 Segurança

- Autenticação JWT com refresh tokens
- Rate limiting no Nginx
- Headers de segurança configurados
- Validação de dados com Pydantic
- Sanitização de inputs
- CORS configurado adequadamente

## 📝 API Documentation

A documentação completa da API está disponível em:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Principais Endpoints

```
POST /auth/register          # Registro de usuário
POST /auth/login            # Login
GET  /profiles/me           # Perfil do usuário
GET  /profiles/me/dashboard # Dados do dashboard
POST /instagram/callback    # Callback Instagram
GET  /reports/              # Lista de relatórios
POST /ai/analyze-post       # Análise de post com IA
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- **Documentação**: Consulte este README
- **Issues**: Abra uma issue no GitHub
- **Email**: contato@ugcsaas.com

## 🎯 Roadmap

- [ ] Integração com TikTok API
- [ ] Integração com YouTube API
- [ ] Dashboard para agências
- [ ] Sistema de white-label
- [ ] App mobile
- [ ] Análise de concorrentes
- [ ] Previsão de tendências com IA
- [ ] Sistema de afiliados

---

**Desenvolvido com ❤️ para criadores de conteúdo**

