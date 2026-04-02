.PHONY: help up down restart logs build clean \
        backend-shell frontend-shell db-shell \
        migrate migrate-down \
        setup \
        local-setup local-backend local-frontend local-migrate

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
	@echo "  $(BOLD)── Docker ──────────────────────────────────────────$(RESET)"
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
	@echo "  $(BOLD)── Local (without Docker) ──────────────────────────$(RESET)"
	@echo "  $(CYAN)make local-setup$(RESET)     Install Python venv + npm deps + copy env files"
	@echo "  $(CYAN)make local-migrate$(RESET)   Run Alembic migrations against local PostgreSQL"
	@echo "  $(CYAN)make local-backend$(RESET)   Start FastAPI dev server on :8000"
	@echo "  $(CYAN)make local-frontend$(RESET)  Start Next.js dev server on :3000"
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

# ─── Local development (without Docker) ──────────────────────────────────────
local-setup:
	@echo "$(BOLD)Setting up local development environment...$(RESET)"
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env; \
		echo "$(GREEN)✓ backend/.env created — fill in DATABASE_URL and secrets$(RESET)"; \
	else \
		echo "backend/.env already exists — skipping"; \
	fi
	@if [ ! -f frontend/.env.local ]; then \
		cp frontend/env.local.example frontend/.env.local; \
		echo "$(GREEN)✓ frontend/.env.local created$(RESET)"; \
	else \
		echo "frontend/.env.local already exists — skipping"; \
	fi
	@echo "Installing Python dependencies..."
	cd backend && python3 -m venv venv && ./venv/bin/pip install --quiet -r requirements.txt
	@echo "$(GREEN)✓ Python venv ready$(RESET)"
	@echo "Installing Node dependencies..."
	cd frontend && npm install --silent
	@echo "$(GREEN)✓ Node modules ready$(RESET)"
	@echo ""
	@echo "$(BOLD)Next steps:$(RESET)"
	@echo "  1. Edit $(CYAN)backend/.env$(RESET) — set DATABASE_URL, ACCESS_SECRET, REFRESH_SECRET"
	@echo "  2. Run $(CYAN)make local-migrate$(RESET)"
	@echo "  3. Run $(CYAN)make local-backend$(RESET) and $(CYAN)make local-frontend$(RESET) in separate terminals"

local-migrate:
	cd backend && ./venv/bin/alembic upgrade head

local-backend:
	cd backend && ./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

local-frontend:
	cd frontend && npm run dev

# ─── Cleanup ──────────────────────────────────────────────────────────────────
clean:
	@echo "$(BOLD)WARNING: This removes all containers, volumes, and images for this project.$(RESET)"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	docker compose down -v --rmi local
	@echo "$(GREEN)✓ Cleaned up$(RESET)"
