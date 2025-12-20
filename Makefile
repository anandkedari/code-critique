.PHONY: help build run down test

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

#TEST_SCENARIOS_PATH := $(or no-scenarios-path.yaml, $$(basename "$(TEST_SCENARIOS_PATH)"))
#SERVICE_NAME=$$(basename "$(SERVICE_PATH)")

build: ## Build Docker image (REQUIRED: AI_PROVIDER=anthropic or AI_PROVIDER=openai)
	@if [ -z "$(AI_PROVIDER)" ]; then \
		echo "$(YELLOW)Error: AI_PROVIDER is required. Set to 'anthropic' or 'openai'$(NC)"; \
		echo "$(YELLOW)Example: AI_PROVIDER=anthropic make build$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Building Docker image with AI_PROVIDER=$(AI_PROVIDER)...$(NC)"
	@docker build --build-arg AI_PROVIDER=$(AI_PROVIDER) -t code-critique:latest -f Dockerfile .
	@echo "$(GREEN)✓ Image built for $(AI_PROVIDER) provider$(NC)"

publish: ## Publish Docker image to registry (OPTIONAL: REGISTRY=localhost:5000)
	@REGISTRY=$${REGISTRY:-localhost:5000}; \
	GIT_SHA=$$(git rev-parse HEAD); \
	SHORT_SHA=$$(git rev-parse --short=7 HEAD); \
	echo "$(BLUE)Publishing code-critique:latest to $$REGISTRY...$(NC)"; \
	docker tag code-critique:latest $$REGISTRY/code-critique:$$GIT_SHA && \
	docker tag code-critique:latest $$REGISTRY/code-critique:$$SHORT_SHA && \
	docker tag code-critique:latest $$REGISTRY/code-critique:latest && \
	echo "$(BLUE)Pushing images...$(NC)" && \
	docker push $$REGISTRY/code-critique:$$GIT_SHA && \
	docker push $$REGISTRY/code-critique:$$SHORT_SHA && \
	docker push $$REGISTRY/code-critique:latest && \
	echo "$(GREEN)✓ Published to $$REGISTRY/code-critique$(NC)" && \
	echo "  - $$REGISTRY/code-critique:$$GIT_SHA" && \
	echo "  - $$REGISTRY/code-critique:$$SHORT_SHA" && \
	echo "  - $$REGISTRY/code-critique:latest"

analyze: ## Run analysis (Docker-in-Docker compatible)
	@echo "Starting analysis with Docker-in-Docker support..."
	@# Clean up any existing containers and networks from previous runs
	@echo "Cleaning up previous run..."
	@docker-compose -f docker-compose.yml down --remove-orphans 2>/dev/null || true
	@docker rm -f code-critique 2>/dev/null || true
	@# Create container without starting (modern approach, replaces deprecated 'create')
	@docker-compose -f docker-compose.yml up --no-start
	@echo "Copying service code into container..."
	@docker cp $(SERVICE_PATH)/. code-critique:/service/
	@echo "Copying test scenarios into container..."
	@if [ -d "test-scenarios" ]; then \
		docker cp test-scenarios code-critique:/app/code-critique/test-scenarios; \
	fi
	@echo "Running analysis..."
	@TEST_SCENARIOS_FILE="$(TEST_SCENARIOS_PATH)" \
	SERVICE_NAME=$$(basename "$(SERVICE_PATH)") \
	docker-compose -f docker-compose.yml start code-critique
	@docker wait code-critique || true
	@docker logs code-critique
	@echo "Copying reports from container..."
	@mkdir -p ./reports
	@docker cp code-critique:/app/code-critique/reports/. ./reports/ || echo "Warning: Could not copy reports"
	@echo "Cleaning up..."
	@docker-compose -f docker-compose.yml down --remove-orphans


docker cp ./customer-service/. code-critique:/service/
