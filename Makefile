# Malta Property Analyzer - Makefile
# Common commands for development, testing, and deployment

.PHONY: help install lint test test-coverage test-e2e build sam-local deploy-staging deploy-prod clean

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m # No Color

# =============================================================================
# Help
# =============================================================================

help: ## Show this help message
	@echo "$(BLUE)Malta Property Analyzer - Available Commands$(NC)"
	@echo "================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# Installation
# =============================================================================

install: install-backend install-frontend install-hooks ## Install all dependencies
	@echo "$(GREEN)✅ All dependencies installed successfully!$(NC)"

install-backend: ## Install backend dependencies
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && \
		python -m pip install --upgrade pip && \
		pip install -r requirements.txt && \
		pip install -r requirements-dev.txt
	@echo "$(GREEN)✅ Backend dependencies installed$(NC)"

install-frontend: ## Install frontend dependencies
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && npm ci
	@echo "$(GREEN)✅ Frontend dependencies installed$(NC)"

install-hooks: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	pip install pre-commit
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "$(GREEN)✅ Pre-commit hooks installed$(NC)"

# =============================================================================
# Linting & Formatting
# =============================================================================

lint: lint-backend lint-frontend ## Run all linters
	@echo "$(GREEN)✅ All linting passed!$(NC)"

lint-backend: ## Run backend linters (black, ruff, mypy)
	@echo "$(BLUE)Running backend linters...$(NC)"
	cd backend && \
		echo "Running Black..." && \
		black --check . && \
		echo "Running Ruff..." && \
		ruff check . && \
		echo "Running MyPy..." && \
		mypy src/ tests/
	@echo "$(GREEN)✅ Backend linting passed$(NC)"

lint-frontend: ## Run frontend linters (eslint, prettier)
	@echo "$(BLUE)Running frontend linters...$(NC)"
	cd frontend && \
		echo "Running ESLint..." && \
		npm run lint && \
		echo "Running Prettier..." && \
		npm run format:check
	@echo "$(GREEN)✅ Frontend linting passed$(NC)"

format: format-backend format-frontend ## Format all code
	@echo "$(GREEN)✅ All code formatted!$(NC)"

format-backend: ## Format backend code
	@echo "$(BLUE)Formatting backend code...$(NC)"
	cd backend && \
		black . && \
		ruff check --fix .
	@echo "$(GREEN)✅ Backend formatted$(NC)"

format-frontend: ## Format frontend code
	@echo "$(BLUE)Formatting frontend code...$(NC)"
	cd frontend && npm run format
	@echo "$(GREEN)✅ Frontend formatted$(NC)"

# =============================================================================
# Testing
# =============================================================================

test: test-backend test-frontend ## Run all tests
	@echo "$(GREEN)✅ All tests passed!$(NC)"

test-backend: ## Run backend tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd backend && pytest tests/ -v
	@echo "$(GREEN)✅ Backend tests passed$(NC)"

test-frontend: ## Run frontend unit tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && npm run test:run
	@echo "$(GREEN)✅ Frontend tests passed$(NC)"

test-coverage: test-coverage-backend test-coverage-frontend ## Run all tests with coverage
	@echo "$(GREEN)✅ All coverage reports generated!$(NC)"

test-coverage-backend: ## Run backend tests with coverage
	@echo "$(BLUE)Running backend tests with coverage...$(NC)"
	cd backend && pytest tests/ \
		--cov=src \
		--cov-report=html \
		--cov-report=xml \
		--cov-report=term-missing \
		--cov-fail-under=90 \
		-v
	@echo "$(GREEN)✅ Backend coverage report generated$(NC)"
	@echo "$(YELLOW)📊 Open backend/htmlcov/index.html to view coverage report$(NC)"

test-coverage-frontend: ## Run frontend tests with coverage
	@echo "$(BLUE)Running frontend tests with coverage...$(NC)"
	cd frontend && npm run test:coverage
	@echo "$(GREEN)✅ Frontend coverage report generated$(NC)"

test-e2e: ## Run Playwright E2E tests
	@echo "$(BLUE)Running E2E tests...$(NC)"
	cd frontend && npm run test:e2e
	@echo "$(GREEN)✅ E2E tests completed$(NC)"

test-e2e-ui: ## Run Playwright E2E tests with UI
	@echo "$(BLUE)Running E2E tests with UI...$(NC)"
	cd frontend && npm run test:e2e:ui

test-smoke: ## Run smoke tests
	@echo "$(BLUE)Running smoke tests...$(NC)"
	cd frontend && npm run test:smoke
	@echo "$(GREEN)✅ Smoke tests completed$(NC)"

# =============================================================================
# Building
# =============================================================================

build: build-backend build-frontend ## Build all projects
	@echo "$(GREEN)✅ All projects built successfully!$(NC)"

build-backend: ## Build backend (SAM)
	@echo "$(BLUE)Building backend with SAM...$(NC)"
	cd backend && sam build --use-container
	@echo "$(GREEN)✅ Backend built$(NC)"

build-frontend: ## Build frontend (Next.js)
	@echo "$(BLUE)Building frontend...$(NC)"
	cd frontend && npm run build
	@echo "$(GREEN)✅ Frontend built$(NC)"

# =============================================================================
# Local Development
# =============================================================================

dev: ## Start local development environment
	@echo "$(BLUE)Starting local development environment...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Local services started$(NC)"
	@echo "$(YELLOW)Services:$(NC)"
	@echo "  - DynamoDB Local: http://localhost:8000"
	@echo "  - LocalStack: http://localhost:4566"
	@echo "  - Frontend: http://localhost:3000"

dev-stop: ## Stop local development environment
	@echo "$(BLUE)Stopping local development environment...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ Local services stopped$(NC)"

dev-logs: ## View logs from local development environment
	@echo "$(BLUE)Viewing logs...$(NC)"
	docker-compose logs -f

sam-local: ## Run SAM locally
	@echo "$(BLUE)Starting SAM local...$(NC)"
	cd backend && sam local start-api --env-vars env.json

sam-local-lambda: ## Invoke Lambda function locally
	@echo "$(BLUE)Invoking Lambda function locally...$(NC)"
	cd backend && sam local invoke

# =============================================================================
# Deployment
# =============================================================================

deploy-staging: ## Deploy to staging environment
	@echo "$(BLUE)Deploying to staging...$(NC)"
	cd backend && sam deploy \
		--stack-name malta-property-analyzer-staging \
		--s3-prefix staging \
		--capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
		--parameter-overrides Stage=staging
	@echo "$(GREEN)✅ Staging deployment complete$(NC)"

deploy-prod: ## Deploy to production environment
	@echo "$(YELLOW)⚠️  Deploying to PRODUCTION...$(NC)"
	@read -p "Are you sure? (yes/no): " confirm && [ $$confirm = yes ] || exit 1
	cd backend && sam deploy \
		--stack-name malta-property-analyzer-prod \
		--s3-prefix production \
		--capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
		--parameter-overrides Stage=production
	@echo "$(GREEN)✅ Production deployment complete$(NC)"

# =============================================================================
# Security
# =============================================================================

security-scan: ## Run security scans
	@echo "$(BLUE)Running security scans...$(NC)"
	@echo "Running Bandit..."
	cd backend && bandit -r src/ -f json -o bandit-report.json || true
	@echo "Running Safety..."
	cd backend && safety check || true
	@echo "$(GREEN)✅ Security scans complete$(NC)"

# =============================================================================
# Database
# =============================================================================

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	cd backend && python -m src.infrastructure.db.migrate

db-seed: ## Seed database with sample data
	@echo "$(BLUE)Seeding database...$(NC)"
	cd backend && python -m scripts.seed_data

db-reset: ## Reset local database
	@echo "$(YELLOW)Resetting local database...$(NC)"
	docker-compose exec dynamodb-local aws dynamodb delete-table \
		--table-name Properties \
		--endpoint-url http://localhost:8000 2>/dev/null || true
	@echo "$(GREEN)✅ Database reset$(NC)"

# =============================================================================
# Utilities
# =============================================================================

clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	cd backend && rm -rf .aws-sam/ htmlcov/ .pytest_cache/ __pycache__/ \
		*/__pycache__/ */*/__pycache__/ .coverage *.pyc
	cd frontend && rm -rf .next/ out/ coverage/ node_modules/.cache/
	@echo "$(GREEN)✅ Build artifacts cleaned$(NC)"

clean-all: clean ## Clean all including dependencies
	@echo "$(BLUE)Cleaning all artifacts and dependencies...$(NC)"
	cd backend && rm -rf venv/ .venv/
	cd frontend && rm -rf node_modules/
	@echo "$(GREEN)✅ All artifacts and dependencies cleaned$(NC)"

update-deps: ## Update all dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	cd backend && pip-compile requirements.in && pip-compile requirements-dev.in
	cd frontend && npm update
	@echo "$(GREEN)✅ Dependencies updated$(NC)"

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files
	@echo "$(GREEN)✅ Pre-commit hooks completed$(NC)"

validate-template: ## Validate SAM template
	@echo "$(BLUE)Validating SAM template...$(NC)"
	cd backend && sam validate --lint
	@echo "$(GREEN)✅ SAM template valid$(NC)"

# =============================================================================
# CI/CD Helpers
# =============================================================================

ci-backend: lint-backend test-coverage-backend security-scan validate-template ## Full CI pipeline for backend
	@echo "$(GREEN)✅ Backend CI pipeline complete$(NC)"

ci-frontend: lint-frontend test-coverage-frontend build-frontend ## Full CI pipeline for frontend
	@echo "$(GREEN)✅ Frontend CI pipeline complete$(NC)"

# =============================================================================
# Documentation
# =============================================================================

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	cd docs && mkdocs serve

docs-build: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	cd docs && mkdocs build
