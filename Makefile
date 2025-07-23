INIT_SCRIPT=scripts/init.sh
PLAIN_INIT_SCRIPT=scripts/init-plain.sh
RENDER_SCRIPT=scripts/render_template.sh
DEPLOYMENT_SCRIPT=scripts/deployment.sh
MIGRATE_SCRIPT=scripts/migrate.sh
SUPERUSER_SCRIPT=scripts/create_superuser.sh
INIT_SSL_SCRIPT=scripts/init-letsencrypt.sh

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo ""
	@echo "Available targets:"
	@echo "  init         Run the interactive init script using gum"
	@echo "  init-plain   Run the plain init script (no gum)"
	@echo "  render       Run template rendering directly"
	@echo "  init-ssl     Initialize SSL certificates with Let's Encrypt"
	@echo "  deploy       Deploy the application using Docker Compose"
	@echo "  migrate      Run database migrations"
	@echo "  create-superuser Create a Django superuser"
	@echo ""


.PHONY: init
init:
	@bash $(INIT_SCRIPT)


.PHONY: init-plain
init-plain:
	@bash $(PLAIN_INIT_SCRIPT)


.PHONY: render
render:
	@bash $(RENDER_SCRIPT) templates/.django.template .envs/.production/.django


.PHONY: deploy
deploy:
	@bash $(DEPLOYMENT_SCRIPT)


.PHONY: migrate
migrate:
	@bash $(MIGRATE_SCRIPT)

.PHONY: init-ssl
init-ssl:
	@bash $(INIT_SSL_SCRIPT)

.PHONY: create-superuser
create-superuser:
	@bash $(SUPERUSER_SCRIPT)
