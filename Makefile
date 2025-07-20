INIT_SCRIPT=scripts/init.sh
PLAIN_INIT_SCRIPT=scripts/init-plain.sh
RENDER_SCRIPT=scripts/render_template.sh
DEPLOYMENT_SCRIPT=scripts/deployment.sh
MIGRATE_SCRIPT=scripts/migrate.sh
SUPERUSER_SCRIPT=scripts/create_superuser.sh

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo ""
	@echo "Available targets:"
	@echo "  init         Run the interactive init script using gum"
	@echo "  init-plain   Run the plain init script (no gum)"
	@echo "  render       Run template rendering directly"
	@echo "  deploy       Deploy the application using Docker Compose"
	@echo "  migrate      Run database migrations"
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

.PHONY: create-superuser
create-superuser:
	@bash $(SUPERUSER_SCRIPT)
