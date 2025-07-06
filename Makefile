.PHONY: help build-prod up-prod down-prod logs-prod migrate collectstatic createsuperuser celery-prod healthcheck

# Show help
help:
	@echo ""
	@echo "🛠️  Production Deployment Targets"
	@echo "--------------------------------"
	@echo "make build-prod         Build images for production"
	@echo "make up-prod            Run production docker-compose"
	@echo "make down-prod          Tear down production setup"
	@echo "make logs-prod          View logs from all services"
	@echo "make migrate            Run migrations"
	@echo "make collectstatic      Collect static files"
	@echo "make createsuperuser    Create Django superuser"
	@echo "make celery-prod        Run Celery worker manually"
	@echo "make healthcheck        Ping /health/ endpoint"
	@echo ""

# Build all images
build-prod:
	docker-compose -f prod.compose.yml build

# Start production stack
up-prod:
	docker-compose -f prod.compose.yml up -d

# Stop production stack
down-prod:
	docker-compose -f prod.compose.yml down

# Tail logs
logs-prod:
	docker-compose -f prod.compose.yml logs -f

# Django manage.py migrate
migrate:
	docker-compose -f prod.compose.yml exec django python manage.py migrate

# Django collectstatic
collectstatic:
	docker-compose -f prod.compose.yml exec django python manage.py collectstatic --noinput

# Django createsuperuser
createsuperuser:
	docker-compose -f prod.compose.yml exec django python manage.py createsuperuser

# Run Celery manually
celery-prod:
	docker-compose -f prod.compose.yml run --rm celery

# Health check (assumes you have a /health/ endpoint)
healthcheck:
	curl -f http://localhost/health/ || echo "Health check failed"
