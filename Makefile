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

analyze: ## Run analysis (REQUIRED: SERVICE_PATH=/path/to/service)
	@if [ -z "$(SERVICE_PATH)" ]; then \
		echo "$(YELLOW)Error: SERVICE_PATH is required$(NC)"; \
		echo "$(YELLOW)Example: SERVICE_PATH=customer-service make analyze$(NC)"; \
		exit 1; \
	fi
	@if [ ! -d "$(SERVICE_PATH)" ]; then \
		echo "$(YELLOW)Error: SERVICE_PATH directory does not exist: $(SERVICE_PATH)$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Running code-critique analysis...$(NC)"
	@echo "   Service Path: $(SERVICE_PATH)"
	@echo "   Service Name: $$(basename "$(SERVICE_PATH)")"
	@CURRENT_DIR=$$(pwd); \
	AGENT_VOLUME=""; \
	if echo "$$CURRENT_DIR" | grep -q "^/godata/"; then \
		HOSTNAME=$$(hostname); \
		if echo "$$HOSTNAME" | grep -q "gocd-agent"; then \
			AGENT_NUM=$$(echo "$$HOSTNAME" | grep -o '[0-9]' | head -1); \
			if [ -z "$$AGENT_NUM" ]; then AGENT_NUM="1"; fi; \
			AGENT_VOLUME="gocd-agent-$$AGENT_NUM-data"; \
			echo "   Detected GoCD Agent Volume: $$AGENT_VOLUME"; \
		fi; \
	fi; \
	if [ -n "$$AGENT_VOLUME" ]; then \
		VOLUME_MOUNT_PATH=$$(echo "$$CURRENT_DIR" | sed 's|^/godata||'); \
		FULL_SERVICE_PATH="$$VOLUME_MOUNT_PATH/$(SERVICE_PATH)"; \
		echo "   Using volume mount: $$AGENT_VOLUME:$$FULL_SERVICE_PATH"; \
		if [ -n "$(TEST_SCENARIOS_PATH)" ]; then \
			TEST_SCENARIOS_FILE="/service/$$(basename $(TEST_SCENARIOS_PATH))" \
			SERVICE_NAME=$$(basename "$(SERVICE_PATH)") \
			SERVICE_HOST_PATH="$$AGENT_VOLUME:$$FULL_SERVICE_PATH" \
			GOCD_VOLUME="$$AGENT_VOLUME" \
			docker-compose -f docker-compose.yml run --rm code-critique; \
		else \
			SERVICE_NAME=$$(basename "$(SERVICE_PATH)") \
			SERVICE_HOST_PATH="$$AGENT_VOLUME:$$FULL_SERVICE_PATH" \
			GOCD_VOLUME="$$AGENT_VOLUME" \
			docker-compose -f docker-compose.yml run --rm code-critique; \
		fi; \
	else \
		if [ -n "$(TEST_SCENARIOS_PATH)" ]; then \
			TEST_SCENARIOS_FILE="/service/$$(basename $(TEST_SCENARIOS_PATH))" \
			SERVICE_NAME=$$(basename "$(SERVICE_PATH)") \
			SERVICE_HOST_PATH="$$CURRENT_DIR/$(SERVICE_PATH)" \
			docker-compose -f docker-compose.yml run --rm code-critique; \
		else \
			SERVICE_NAME=$$(basename "$(SERVICE_PATH)") \
			SERVICE_HOST_PATH="$$CURRENT_DIR/$(SERVICE_PATH)" \
			docker-compose -f docker-compose.yml run --rm code-critique; \
		fi; \
	fi
	@echo "$(GREEN)✓ Analysis complete!$(NC)"
