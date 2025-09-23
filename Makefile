# UGC SaaS Makefile
.PHONY: help build up down restart logs clean test backup restore

# Default target
help:
	@echo "UGC SaaS - Available commands:"
	@echo ""
	@echo "  build     - Build all Docker images"
	@echo "  up        - Start all services"
	@echo "  down      - Stop all services"
	@echo "  restart   - Restart all services"
	@echo "  logs      - Show logs from all services"
	@echo "  clean     - Clean up containers, images, and volumes"
	@echo "  test      - Run tests"
	@echo "  backup    - Backup database"
	@echo "  restore   - Restore database from backup"
	@echo "  shell     - Open shell in backend container"
	@echo "  worker    - Show worker status"
	@echo "  flower    - Open Flower monitoring"
	@echo ""

# Build all images
build:
	@echo "Building Docker images..."
	docker-compose build --no-cache

# Start all services
up:
	@echo "Starting UGC SaaS services..."
	docker-compose up -d
	@echo "Services started! Access:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend API: http://localhost:8000"
	@echo "  Flower (Worker Monitor): http://localhost:5555"
	@echo "  MongoDB: localhost:27017"

# Stop all services
down:
	@echo "Stopping UGC SaaS services..."
	docker-compose down

# Restart all services
restart: down up

# Show logs
logs:
	docker-compose logs -f

# Show logs for specific service
logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-worker:
	docker-compose logs -f worker

logs-mongo:
	docker-compose logs -f mongo

# Clean up everything
clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	docker volume prune -f

# Run tests (placeholder)
test:
	@echo "Running tests..."
	docker-compose exec backend python -m pytest tests/ -v

# Database backup
backup:
	@echo "Creating database backup..."
	mkdir -p backups
	docker-compose exec mongo mongodump --host localhost --port 27017 --db ugc_saas --out /tmp/backup
	docker cp ugc_saas_mongo:/tmp/backup ./backups/backup_$(shell date +%Y%m%d_%H%M%S)
	@echo "Backup created in ./backups/"

# Database restore
restore:
	@echo "Restoring database..."
	@read -p "Enter backup directory name: " backup_dir; \
	docker cp ./backups/$$backup_dir ugc_saas_mongo:/tmp/restore; \
	docker-compose exec mongo mongorestore --host localhost --port 27017 --db ugc_saas /tmp/restore/ugc_saas --drop

# Open shell in backend container
shell:
	docker-compose exec backend /bin/bash

# Show worker status
worker:
	docker-compose exec worker celery -A app.celery_app inspect active

# Open Flower monitoring
flower:
	@echo "Opening Flower monitoring..."
	@echo "Visit: http://localhost:5555"
	@python -c "import webbrowser; webbrowser.open('http://localhost:5555')" 2>/dev/null || true

# Development commands
dev-setup:
	@echo "Setting up development environment..."
	cp .env.example .env
	@echo "Please edit .env file with your API keys"

dev-install:
	@echo "Installing development dependencies..."
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	cd worker && pip install -r requirements.txt

# Production commands
prod-build:
	@echo "Building for production..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up:
	@echo "Starting production services..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:3000 > /dev/null 2>&1 && echo "✓ Frontend: OK" || echo "✗ Frontend: FAIL"
	@curl -f http://localhost:8000/health > /dev/null 2>&1 && echo "✓ Backend: OK" || echo "✗ Backend: FAIL"
	@curl -f http://localhost:5555 > /dev/null 2>&1 && echo "✓ Flower: OK" || echo "✗ Flower: FAIL"

# Monitor resources
monitor:
	@echo "Resource usage:"
	docker stats --no-stream

# Update services
update:
	@echo "Updating services..."
	git pull
	docker-compose build
	docker-compose up -d

