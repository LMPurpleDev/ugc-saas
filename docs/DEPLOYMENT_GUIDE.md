# Guia Completo de Deploy - UGC SaaS

Este guia fornece instruções detalhadas para fazer o deploy da plataforma UGC SaaS em diferentes ambientes, desde desenvolvimento local até produção em servidores cloud.

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Deploy Local (Desenvolvimento)](#deploy-local-desenvolvimento)
3. [Deploy em Servidor VPS](#deploy-em-servidor-vps)
4. [Deploy em Cloud (AWS/GCP/Azure)](#deploy-em-cloud)
5. [Configuração de SSL](#configuração-de-ssl)
6. [Monitoramento e Logs](#monitoramento-e-logs)
7. [Backup e Restore](#backup-e-restore)
8. [Troubleshooting](#troubleshooting)

## 🔧 Pré-requisitos

### Sistema Operacional
- Ubuntu 20.04+ (recomendado)
- CentOS 8+ ou RHEL 8+
- Debian 11+
- macOS 12+ (apenas desenvolvimento)

### Software Necessário
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.30+
- Make (opcional, mas recomendado)

### Recursos Mínimos
- **Desenvolvimento**: 4GB RAM, 2 CPU cores, 20GB storage
- **Produção**: 8GB RAM, 4 CPU cores, 100GB storage
- **Alta disponibilidade**: 16GB RAM, 8 CPU cores, 500GB storage

### Chaves de API Necessárias
- Instagram App ID e Secret
- OpenAI API Key
- SendGrid API Key (para emails)

## 🏠 Deploy Local (Desenvolvimento)

### 1. Clone do Repositório
```bash
git clone https://github.com/seu-usuario/ugc-saas.git
cd ugc-saas
```

### 2. Configuração das Variáveis de Ambiente
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas chaves
nano .env
```

Configurar as seguintes variáveis:
```env
INSTAGRAM_APP_ID=seu_app_id_instagram
INSTAGRAM_APP_SECRET=seu_app_secret_instagram
INSTAGRAM_REDIRECT_URI=http://localhost:3000/auth/instagram/callback
OPENAI_API_KEY=sua_chave_openai
SENDGRID_API_KEY=sua_chave_sendgrid
FROM_EMAIL=noreply@seudominio.com
```

### 3. Inicialização dos Serviços
```bash
# Usando Make (recomendado)
make up

# Ou usando Docker Compose diretamente
docker-compose up --build -d
```

### 4. Verificação dos Serviços
```bash
# Verificar status
make health

# Ver logs
make logs

# Acessar serviços
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Flower: http://localhost:5555
```

## 🌐 Deploy em Servidor VPS

### 1. Preparação do Servidor

#### Atualização do Sistema
```bash
sudo apt update && sudo apt upgrade -y
```

#### Instalação do Docker
```bash
# Instalar dependências
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Adicionar chave GPG do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
```

#### Configuração do Firewall
```bash
# Instalar UFW
sudo apt install -y ufw

# Configurar regras básicas
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir SSH
sudo ufw allow ssh

# Permitir HTTP e HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Ativar firewall
sudo ufw enable
```

### 2. Deploy da Aplicação

#### Clone e Configuração
```bash
# Clone do repositório
git clone https://github.com/seu-usuario/ugc-saas.git
cd ugc-saas

# Configurar variáveis de ambiente
cp .env.example .env
nano .env
```

Configurar para produção:
```env
INSTAGRAM_APP_ID=seu_app_id_instagram
INSTAGRAM_APP_SECRET=seu_app_secret_instagram
INSTAGRAM_REDIRECT_URI=https://seudominio.com/auth/instagram/callback
OPENAI_API_KEY=sua_chave_openai
SENDGRID_API_KEY=sua_chave_sendgrid
FROM_EMAIL=noreply@seudominio.com
DOMAIN=seudominio.com
SSL_EMAIL=admin@seudominio.com
MONGO_ROOT_PASSWORD=senha_super_segura
SECRET_KEY=chave_jwt_super_segura
```

#### Inicialização em Produção
```bash
# Build para produção
make prod-build

# Iniciar serviços
make prod-up

# Verificar status
docker-compose ps
```

### 3. Configuração de Domínio

#### DNS Records
Configure os seguintes registros DNS:
```
A     seudominio.com        IP_DO_SERVIDOR
A     www.seudominio.com    IP_DO_SERVIDOR
CNAME api.seudominio.com    seudominio.com
```

#### Nginx Configuration
O sistema já inclui configuração Nginx otimizada com:
- Proxy reverso para backend e frontend
- Rate limiting
- Headers de segurança
- Compressão gzip
- Cache de arquivos estáticos

## ☁️ Deploy em Cloud

### AWS (Amazon Web Services)

#### 1. Preparação da Instância EC2
```bash
# Criar instância EC2
# - AMI: Ubuntu Server 22.04 LTS
# - Tipo: t3.medium (mínimo) ou t3.large (recomendado)
# - Storage: 100GB GP3
# - Security Group: HTTP (80), HTTPS (443), SSH (22)
```

#### 2. Configuração do RDS (MongoDB Atlas)
```bash
# Usar MongoDB Atlas para produção
# 1. Criar cluster no MongoDB Atlas
# 2. Configurar IP whitelist
# 3. Criar usuário de banco
# 4. Atualizar MONGODB_URL no .env
```

#### 3. Configuração do ElastiCache (Redis)
```bash
# Criar cluster Redis no ElastiCache
# 1. Engine: Redis
# 2. Node type: cache.t3.micro
# 3. Atualizar REDIS_URL no .env
```

#### 4. Load Balancer e Auto Scaling
```bash
# Configurar Application Load Balancer
# 1. Target Group para porta 80
# 2. Health check em /health
# 3. SSL certificate via ACM
```

### Google Cloud Platform (GCP)

#### 1. Compute Engine
```bash
# Criar VM instance
gcloud compute instances create ugc-saas-vm \
    --zone=us-central1-a \
    --machine-type=e2-standard-2 \
    --boot-disk-size=100GB \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --tags=http-server,https-server
```

#### 2. Cloud SQL (PostgreSQL) ou MongoDB Atlas
```bash
# Usar MongoDB Atlas ou configurar MongoDB em VM separada
```

#### 3. Cloud Load Balancing
```bash
# Configurar load balancer
gcloud compute backend-services create ugc-saas-backend \
    --global \
    --health-checks=ugc-saas-health-check
```

### Azure

#### 1. Virtual Machine
```bash
# Criar VM via Azure CLI
az vm create \
    --resource-group ugc-saas-rg \
    --name ugc-saas-vm \
    --image UbuntuLTS \
    --size Standard_B2s \
    --admin-username azureuser \
    --generate-ssh-keys
```

#### 2. Azure Database for MongoDB
```bash
# Usar Azure Cosmos DB com MongoDB API
az cosmosdb create \
    --resource-group ugc-saas-rg \
    --name ugc-saas-cosmos \
    --kind MongoDB
```

## 🔒 Configuração de SSL

### Certbot (Let's Encrypt)
O sistema inclui configuração automática de SSL:

```bash
# SSL é configurado automaticamente via docker-compose.prod.yml
# O container certbot obtém certificados automaticamente
```

### SSL Manual
Para configuração manual:

```bash
# Gerar certificados
sudo certbot certonly --standalone -d seudominio.com -d www.seudominio.com

# Copiar certificados
sudo cp /etc/letsencrypt/live/seudominio.com/fullchain.pem ./nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/seudominio.com/privkey.pem ./nginx/ssl/key.pem

# Reiniciar nginx
docker-compose restart nginx
```

### Renovação Automática
```bash
# Adicionar ao crontab
0 12 * * * /usr/bin/certbot renew --quiet && docker-compose restart nginx
```

## 📊 Monitoramento e Logs

### Flower (Celery Monitor)
- URL: http://seudominio.com:5555
- Monitora workers e tarefas
- Estatísticas em tempo real

### Logs Centralizados
```bash
# Ver todos os logs
docker-compose logs -f

# Logs específicos
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f nginx

# Logs com timestamp
docker-compose logs -f -t
```

### Monitoramento de Recursos
```bash
# Status dos containers
docker stats

# Uso de disco
df -h

# Uso de memória
free -h

# Processos
htop
```

### Alertas (Opcional)
Configurar alertas com:
- Prometheus + Grafana
- New Relic
- DataDog
- AWS CloudWatch

## 💾 Backup e Restore

### Backup Automático
```bash
# Backup diário via cron
0 2 * * * cd /path/to/ugc-saas && make backup
```

### Backup Manual
```bash
# Backup completo
make backup

# Backup específico
docker-compose exec mongo mongodump --host localhost --port 27017 --db ugc_saas --out /tmp/backup
```

### Restore
```bash
#


### Restore
```bash
# Restore do backup
make restore

# Restore manual
docker cp ./backups/backup_20240101_120000 ugc_saas_mongo:/tmp/restore
docker-compose exec mongo mongorestore --host localhost --port 27017 --db ugc_saas /tmp/restore/ugc_saas --drop
```

### Backup de Arquivos
```bash
# Backup de relatórios e uploads
tar -czf reports_backup_$(date +%Y%m%d).tar.gz ./reports/
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Containers não iniciam
```bash
# Verificar logs
docker-compose logs

# Verificar recursos
docker system df
docker system prune -f

# Rebuild completo
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

#### 2. MongoDB não conecta
```bash
# Verificar status
docker-compose exec mongo mongo --eval "db.adminCommand('ping')"

# Verificar logs
docker-compose logs mongo

# Recriar volume se necessário
docker-compose down -v
docker volume rm ugc-saas_mongo_data
docker-compose up -d
```

#### 3. Redis não conecta
```bash
# Testar conexão
docker-compose exec redis redis-cli ping

# Verificar configuração
docker-compose exec backend python -c "import redis; r=redis.Redis(host='redis'); print(r.ping())"
```

#### 4. Workers não processam tarefas
```bash
# Verificar workers
docker-compose exec worker celery -A app.celery_app inspect active

# Reiniciar workers
docker-compose restart worker beat

# Verificar filas
docker-compose exec worker celery -A app.celery_app inspect reserved
```

#### 5. Frontend não carrega
```bash
# Verificar build
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend --no-cache
docker-compose up -d frontend

# Verificar nginx
docker-compose logs nginx
```

#### 6. SSL não funciona
```bash
# Verificar certificados
docker-compose exec nginx ls -la /etc/nginx/ssl/

# Renovar certificados
docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email admin@seudominio.com --agree-tos --no-eff-email -d seudominio.com

# Reiniciar nginx
docker-compose restart nginx
```

### Comandos de Diagnóstico

#### Verificar Conectividade
```bash
# Testar portas
telnet localhost 3000
telnet localhost 8000
telnet localhost 27017

# Testar URLs
curl -I http://localhost:3000
curl -I http://localhost:8000/health
```

#### Verificar Recursos
```bash
# Uso de CPU e memória
docker stats --no-stream

# Espaço em disco
docker system df
df -h

# Logs de sistema
journalctl -u docker.service
```

#### Verificar Configuração
```bash
# Variáveis de ambiente
docker-compose config

# Verificar serviços
docker-compose ps
docker-compose top
```

### Performance Tuning

#### Otimização do MongoDB
```javascript
// Conectar ao MongoDB
docker-compose exec mongo mongo ugc_saas

// Verificar índices
db.users.getIndexes()
db.profiles.getIndexes()
db.metrics.getIndexes()

// Estatísticas de performance
db.runCommand({collStats: "metrics"})
```

#### Otimização do Redis
```bash
# Configurar Redis para produção
docker-compose exec redis redis-cli CONFIG SET maxmemory 256mb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

#### Otimização do Nginx
```nginx
# Adicionar ao nginx.conf
worker_processes auto;
worker_connections 2048;
keepalive_timeout 30;
client_max_body_size 50M;
```

## 🚀 Otimizações para Produção

### Configurações de Segurança

#### 1. Firewall Avançado
```bash
# Configurar iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -j DROP

# Salvar regras
sudo iptables-save > /etc/iptables/rules.v4
```

#### 2. Fail2Ban
```bash
# Instalar fail2ban
sudo apt install -y fail2ban

# Configurar para SSH
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

#### 3. Monitoramento de Segurança
```bash
# Instalar OSSEC ou similar
# Configurar alertas de segurança
# Monitorar logs de acesso
```

### Escalabilidade

#### 1. Load Balancer
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3
  worker:
    deploy:
      replicas: 5
```

#### 2. Cache Redis Cluster
```yaml
redis-cluster:
  image: redis:7.2-alpine
  command: redis-server --cluster-enabled yes
  deploy:
    replicas: 3
```

#### 3. MongoDB Replica Set
```yaml
mongo-primary:
  image: mongo:7.0
  command: mongod --replSet rs0
mongo-secondary:
  image: mongo:7.0
  command: mongod --replSet rs0
```

### Monitoramento Avançado

#### 1. Prometheus + Grafana
```yaml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

#### 2. ELK Stack (Logs)
```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
  environment:
    - discovery.type=single-node

logstash:
  image: docker.elastic.co/logstash/logstash:8.8.0

kibana:
  image: docker.elastic.co/kibana/kibana:8.8.0
  ports:
    - "5601:5601"
```

## 📈 Métricas e KPIs

### Métricas de Sistema
- CPU Usage < 70%
- Memory Usage < 80%
- Disk Usage < 85%
- Network Latency < 100ms

### Métricas de Aplicação
- Response Time < 500ms
- Error Rate < 1%
- Throughput > 100 req/s
- Uptime > 99.9%

### Métricas de Negócio
- Usuários ativos diários
- Relatórios gerados
- Posts analisados
- Taxa de conversão

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to server
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /path/to/ugc-saas
            git pull origin main
            docker-compose build
            docker-compose up -d
```

### GitLab CI
```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

deploy:
  stage: deploy
  script:
    - docker-compose build
    - docker-compose up -d
  only:
    - main
```

## 📋 Checklist de Deploy

### Pré-Deploy
- [ ] Variáveis de ambiente configuradas
- [ ] Chaves de API válidas
- [ ] Domínio configurado
- [ ] SSL configurado
- [ ] Backup do banco atual
- [ ] Testes passando

### Deploy
- [ ] Build das imagens
- [ ] Inicialização dos serviços
- [ ] Verificação de saúde
- [ ] Teste de funcionalidades
- [ ] Verificação de logs
- [ ] Teste de performance

### Pós-Deploy
- [ ] Monitoramento ativo
- [ ] Alertas configurados
- [ ] Backup automático
- [ ] Documentação atualizada
- [ ] Equipe notificada
- [ ] Rollback plan pronto

## 🆘 Suporte e Manutenção

### Contatos de Emergência
- DevOps: devops@ugcsaas.com
- Backend: backend@ugcsaas.com
- Frontend: frontend@ugcsaas.com

### Horários de Manutenção
- Manutenção programada: Domingos 02:00-04:00 UTC
- Atualizações de segurança: Conforme necessário
- Backup diário: 02:00 UTC

### Procedimentos de Emergência
1. Identificar o problema
2. Verificar logs e métricas
3. Aplicar correção temporária
4. Notificar stakeholders
5. Implementar correção definitiva
6. Documentar incidente

---

**Este guia deve ser mantido atualizado conforme a evolução da plataforma e novas práticas de deploy.**

