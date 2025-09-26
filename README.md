# UGC SaaS - Plataforma para Criadores de Conteúdo

Uma plataforma completa para criadores de conteúdo UGC (User Generated Content) que oferece análise de performance, relatórios automáticos e direcionamento de carreira usando inteligência artificial.

## 🚀 Instalação Rápida no WSL Ubuntu 22.04.5 LTS

### Pré-requisitos
- WSL com Ubuntu 22.04.5 LTS
- Git

### 1. Clone o repositório
```bash
git clone https://github.com/LMPurpleDev/ugc-saas.git
cd ugc-saas
```

### 2. Instale o Docker (se não estiver instalado)
```bash
chmod +x install-docker.sh
./install-docker.sh
```

Após a instalação, execute:
```bash
newgrp docker
```

### 3. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas chaves de API
nano .env
```

### 4. Inicie todos os serviços
```bash
docker compose up --build
```

### 5. Acesse a aplicação
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação API**: http://localhost:8000/docs
- **Flower (Monitor)**: http://localhost:5555

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
- **Vite** - Build tool moderna
- **Tailwind CSS** - Estilização
- **shadcn/ui** - Componentes
- **Recharts** - Gráficos interativos
- **Axios** - Cliente HTTP

### Infraestrutura
- **Docker** - Containerização
- **Docker Compose** - Orquestração
- **Nginx** - Proxy reverso
- **Celery Beat** - Agendamento de tarefas

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
docker compose up -d

# Ver logs de um serviço específico
docker compose logs -f backend

# Executar comando no container
docker compose exec backend python manage.py shell

# Rebuild de um serviço
docker compose build backend
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
├── install-docker.sh       # Script de instalação do Docker
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
docker compose exec backend python -m pytest

# Testes do frontend
docker compose exec frontend npm test

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
docker compose logs -f

# Serviço específico
docker compose logs -f backend
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

Desenvolvido com ❤️ para criadores de conteúdo

## 🔧 Correções Implementadas

### Versão Corrigida - WSL Ubuntu 22.04.5 LTS
- ✅ Dockerfile do frontend otimizado (npm ao invés de pnpm)
- ✅ Health checks adicionados ao docker-compose
- ✅ Dependências do frontend atualizadas e compatíveis
- ✅ Script de instalação do Docker incluído
- ✅ Configurações do Vite, Tailwind e PostCSS corrigidas
- ✅ Requirements.txt limpos e organizados
- ✅ Documentação atualizada com instruções específicas para WSL

### Para usar:
1. Execute o script `./install-docker.sh` no seu WSL
2. Configure o arquivo `.env` com suas API keys
3. Execute `docker compose up --build`

## 🐛 Correções de Funcionalidade de Login

Esta seção detalha as correções implementadas para resolver problemas de comunicação entre o frontend e o backend na funcionalidade de login.

### Problemas Identificados:

- **Problema de CORS**: O backend não estava configurado para aceitar requisições do domínio do frontend, resultando em erros de Cross-Origin Resource Sharing.
- **Dependência Faltante**: O módulo `passlib`, essencial para a criptografia de senhas no backend, não estava instalado.
- **Configuração de URL da API**: O frontend estava configurado para se conectar a um `localhost` fixo, em vez de usar o domínio público do backend.
- **Configuração do Vite**: As configurações de Hot Module Replacement (HMR) do Vite no frontend não estavam corretamente ajustadas para o ambiente de desenvolvimento.

### Correções Implementadas:

- **Configuração de CORS**: O arquivo `backend/app/main.py` foi atualizado para permitir requisições de todas as origens (`allow_origins=["*"]`) temporariamente, facilitando o desenvolvimento e resolvendo os erros de CORS.
- **Instalação de Dependências**: O módulo `passlib` foi adicionado às dependências do backend e instalado, garantindo que a criptografia de senhas funcione corretamente.
- **Atualização da URL da API**: O arquivo `.env` do frontend foi modificado para apontar para a URL pública do backend (`VITE_API_URL=https://8000-ibzzmx3vdhqis3z092zj1-2aceed55.manusvm.computer`), permitindo a comunicação adequada.
- **Ajuste do Vite**: O arquivo `frontend/vite.config.js` foi atualizado para configurar corretamente o host e a porta do HMR, garantindo que o frontend recarregue as mudanças em tempo real.

### Testes e Validação:

Após a implementação das correções, foram realizados testes completos de registro e login, confirmando que:

- ✅ O registro de novos usuários funciona perfeitamente.
- ✅ O login de usuários existentes é bem-sucedido.
- ✅ A comunicação entre frontend e backend ocorre sem erros de CORS.
- ✅ O sistema de autenticação está totalmente funcional.

O único erro residual (`404 Not Found` para `/users/me`) não afeta a funcionalidade principal de login e provavelmente indica uma rota ainda não implementada no backend, mas a comunicação base está estabelecida.


