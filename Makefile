.PHONY: help up down restart logs build clean \
        backend-shell frontend-shell db-shell \
        migrate migrate-down lint-backend \
        setup

# ─── Colours ─────────────────────────────────────────────────────────────────
BOLD  := \033[1m
RESET := \033[0m
GREEN := \033[32m
CYAN  := \033[36m

# ─── Default: show help ───────────────────────────────────────────────────────
help:
	@echo ""
	@echo "$(BOLD)Threadline — available commands$(RESET)"
	@echo ""
	@echo "  $(CYAN)make setup$(RESET)           Copy .env.example → .env (first-time setup)"
	@echo "  $(CYAN)make up$(RESET)              Build images and start all services (detached)"
	@echo "  $(CYAN)make down$(RESET)            Stop and remove containers"
	@echo "  $(CYAN)make restart$(RESET)         Restart all services"
	@echo "  $(CYAN)make build$(RESET)           Rebuild images without cache"
	@echo "  $(CYAN)make logs$(RESET)            Tail logs for all services"
	@echo "  $(CYAN)make logs-backend$(RESET)    Tail backend logs only"
	@echo "  $(CYAN)make logs-frontend$(RESET)   Tail frontend logs only"
	@echo "  $(CYAN)make migrate$(RESET)         Run Alembic migrations (upgrade head)"
	@echo "  $(CYAN)make migrate-down$(RESET)    Rollback last Alembic migration"
	@echo "  $(CYAN)make db-shell$(RESET)        Open psql shell in the db container"
	@echo "  $(CYAN)make backend-shell$(RESET)   Open bash shell in the backend container"
	@echo "  $(CYAN)make frontend-shell$(RESET)  Open sh shell in the frontend container"
	@echo "  $(CYAN)make clean$(RESET)           Remove containers, images, and volumes (destructive)"
	@echo ""

# ─── First-time setup ─────────────────────────────────────────────────────────
setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✓ .env created from .env.example — fill in your secrets before running 'make up'$(RESET)"; \
	else \
		echo ".env already exists — skipping"; \
	fi

# ─── Docker lifecycle ─────────────────────────────────────────────────────────
up:
	docker compose up --build -d
	@echo "$(GREEN)✓ Services started. Frontend → http://localhost:3000  Backend → http://localhost:8000$(RESET)"

down:
	docker compose down

restart:
	docker compose restart

build:
	docker compose build --no-cache

# ─── Logs ─────────────────────────────────────────────────────────────────────
logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

# ─── Database ─────────────────────────────────────────────────────────────────
migrate:
	docker compose exec backend alembic upgrade head

migrate-down:
	docker compose exec backend alembic downgrade -1

db-shell:
	docker compose exec db psql -U postgres -d threadline

# ─── Shells ───────────────────────────────────────────────────────────────────
backend-shell:
	docker compose exec backend bash

frontend-shell:
	docker compose exec frontend sh

# ─── Cleanup ──────────────────────────────────────────────────────────────────
clean:
	@echo "$(BOLD)WARNING: This removes all containers, volumes, and images for this project.$(RESET)"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	docker compose down -v --rmi local
	@echo "$(GREEN)✓ Cleaned up$(RESET)"
