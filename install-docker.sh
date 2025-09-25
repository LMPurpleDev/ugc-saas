#!/bin/bash

# Script para instalar Docker no WSL Ubuntu 22.04.5 LTS
echo "🐳 Instalando Docker no WSL Ubuntu 22.04.5 LTS..."

# Atualizar repositórios
sudo apt update

# Instalar dependências
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Adicionar chave GPG do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório do Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Atualizar repositórios novamente
sudo apt update

# Instalar Docker
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Iniciar e habilitar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

echo "✅ Docker instalado com sucesso!"
echo "⚠️  Execute 'newgrp docker' ou faça logout/login para aplicar as permissões"
echo "🚀 Depois execute: docker compose up --build"