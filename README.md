# Code Critique System with Multi-Provider AI Support

Automated code quality analysis using AI (Anthropic, OpenAI-compatible APIs) with standardized, reproducible HTML reports.

## 🎯 Features

- ✅ **Multi-Provider AI Support** - Anthropic (Claude), OpenAI-compatible APIs (Perplexity, Ollama, vLLM, LocalAI, etc.)
- ✅ **Dual Deployment** - TW (public) and IDFC (enterprise with artifactory) setups
- ✅ **Flexible Configuration** - Environment variables + config file
- ✅ **Cloud & Self-Hosted** - Use cloud providers or run your own models locally
- ✅ **6 Categories** - Architecture, Error Handling, Performance, AI Quality, Domain Logic, Functional Compliance
- ✅ **Consistent Reports** - Fixed HTML structure for reproducibility
- ✅ **Actionable Insights** - Specific issues with code snippets and fixes
- ✅ **JSON Schema Validation** - Ensures output consistency

---

## 📂 File Structure

```
sentinel/code-critique/
├── Dockerfile                 # Public/TW Docker setup
├── Dockerfile.idfc            # Enterprise/IDFC Docker setup with artifactory
├── docker-compose.yml         # Public/TW compose configuration
├── docker-compose.idfc.yml    # Enterprise/IDFC compose configuration
├── Makefile                   # Public/TW build/run workflow
├── Makefile.idfc              # Enterprise/IDFC build/publish workflow
├── scripts/
│   └── analyze-service.py     # Main analysis script
├── prompts/
│   └── code-critique-system-prompt.md  # AI analysis guidelines
├── templates/
│   └── code-critique-template.html     # HTML report template
├── schemas/
│   └── code-critique-schema.json       # JSON validation schema
└── infrastructure/
    └── IDFCBANKCA.pem        # Corporate CA certificate (IDFC only)
```

---

## 🚀 Quick Start

### Option 1: Direct Python Execution (No Docker)

#### 1. Prerequisites

```bash
# Python 3.8+ required
python3 --version

# Install dependencies
cd sentinel/code-critique/scripts
pip install anthropic jinja2 jsonschema requests openai
```

#### 2. Run Analysis

```bash
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-your-key-here
export SERVICE_PATH=/path/to/customer-service
python3 analyze-service.py
```

#### 3. View Report

```bash
open ../reports/customer-service/code-critique-report.html
```

---

### Option 2: Docker - TW/Public Setup

For external/open-source usage with public Docker registries.

#### Prerequisites
- Docker and Docker Compose installed
- AI API key (Anthropic or OpenAI)

#### Setup

```bash
cd sentinel/code-critique

# 1. Set environment variables
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-your-key-here
export SERVICE_PATH=/path/to/your/service

# 2. Build image
make build AI_PROVIDER=anthropic

# 3. Run analysis
make analyze

# 4. View report
open reports/$(basename $SERVICE_PATH)/code-critique-report.html
```

#### With Test Scenarios

```bash
export TEST_SCENARIOS_PATH=/path/to/test-scenarios.yml
make analyze
```

**Note**: The Makefile automatically converts the host path to container path (`/service/filename`).

---

### Option 3: Docker - IDFC/Enterprise Setup

For internal IDFC Bank usage with corporate artifactory and proxies.

#### Prerequisites
- Docker and Docker Compose installed
- IDFC Bank network access
- Artifactory credentials
- Corporate CA certificate
- AI API key

#### One-Time Setup

```bash
# 1. Configure CA Certificate
vim sentinel/code-critique/infrastructure/IDFCBANKCA.pem
# Replace placeholder with actual IDFC Bank CA certificate
```

#### Build & Publish

```bash
cd sentinel/code-critique

# Set credentials
export ARTIFACTORY_USER=your.username
export ARTIFACTORY_PASSWORD=your.token

# Optional: Set proxy if needed
export http_proxy=http://10.169.48.5:3128
export https_proxy=http://10.169.48.5:3128

# Build
make -f Makefile.idfc build

# Publish to artifactory
make -f Makefile.idfc publish
```

#### Run Analysis

```bash
# Set all required variables
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-your-key-here
export SERVICE_PATH=/path/to/your/service
export SERVICE_NAME=customer-service

# Optional: GoCD pipeline variables (auto-set in CI/CD)
export GO_REVISION_CODE_CRITIQUE=1.2.3

# Run analysis
make -f Makefile.idfc analyze

# View report
open reports/customer-service/code-critique-report.html
```

---

## ⚙️ Configuration

### Environment Variables

**Required:**
```bash
export AI_PROVIDER=anthropic|openai   # Provider type
export AI_MODEL=model-name             # Model identifier
export AI_API_KEY=your-key            # API authentication key
export SERVICE_PATH=/path/to/service  # Service to analyze
```

**Optional:**
```bash
export AI_API_URL=https://api.example.com      # For non-standard endpoints
export AI_CONFIDENCE_THRESHOLD=70               # Confidence threshold 0-100
export TEST_SCENARIOS_PATH=/path/to/file.yml   # Test scenarios for functional compliance
export SERVICE_NAME=my-service                  # Override service name
```

### Configuration File (config.json)

```json
{
  "confidence_threshold": 70,
  "max_tokens": 20000,
  "temperature": 0,
  "timeout": 180.0
}
```

---

## 🤖 AI Provider Examples

### Anthropic (Claude)
```bash
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-...
```

### OpenAI
```bash
export AI_PROVIDER=openai
export AI_MODEL=gpt-4
export AI_API_KEY=sk-...
```

### Perplexity
```bash
export AI_PROVIDER=openai
export AI_API_URL=https://api.perplexity.ai
export AI_MODEL=llama-3.1-sonar-huge-128k-online
export AI_API_KEY=pplx-...
```

### Ollama (Self-hosted)
```bash
export AI_PROVIDER=openai
export AI_API_URL=http://localhost:11434/v1
export AI_MODEL=llama3.1
export AI_API_KEY=not-needed
```

---

## 📋 What Gets Analyzed

### 1. 🏗️ Code Architecture & Design
- SOLID principles, abstraction layers, dependency injection
- Code duplication, method length, naming conventions
- AI-generated code issues (hallucinations, fake imports)
- Semantic dead code (obsolete methods, stale config)

### 2. 🛡️ Error Handling & Observability
- Exception handling, empty catch blocks, retry logic
- Logging quality, correlation IDs, distributed tracing

### 3. ⚡ Performance & Resource Management
- Algorithmic complexity, N+1 queries, memory leaks
- Resource cleanup, unbounded operations

### 4. 🤖 AI Quality Assurance
- AI code issues (hallucinations, placeholders)
- Bug detection (race conditions, validation bypass)
- Missing edge cases, over-engineering

### 5. 🎯 Domain & Business Logic
- Domain patterns (DDD, CQRS), business rule validation
- Domain model quality

### 6. 🧪 Functional Compliance (Optional)
- Validates against test-scenarios.yml
- Evidence-based verification with code snippets
- Status: PASS ✅ / FAIL ❌ / PARTIAL ⚠️ / CANNOT_VERIFY ❓

---

## 🧪 Test Scenarios

Create `test-scenarios.yml`:

```yaml
service_name: "customer-service"
description: "Business logic validation"

global_validations:
  - "Data stored must match request payload"
  - "Timestamps set automatically"
  - "Proper HTTP status codes"

scenarios:
  - "If customer does not exist, create new customer"
  - "When creating duplicate customer, throw error"
  - "Customer age must be 18 or older"
```

Run with scenarios:

```bash
export TEST_SCENARIOS_PATH=/path/to/test-scenarios.yml
make analyze
```

---

## 📝 Makefile Commands

### TW/Public (Makefile)
```bash
make build AI_PROVIDER=anthropic    # Build Docker image
make analyze                         # Run analysis
```

### IDFC/Enterprise (Makefile.idfc)
```bash
make -f Makefile.idfc docker_login   # Login to artifactory
make -f Makefile.idfc build          # Build image
make -f Makefile.idfc publish        # Publish to artifactory
make -f Makefile.idfc analyze        # Run analysis
```

---

## 🐛 Troubleshooting

### "File not found" for test scenarios

The TEST_SCENARIOS_PATH is automatically converted to container path:
- Host path: `/path/to/service/test-scenarios.yml`
- Container path: `/service/test-scenarios.yml` (automatic)

Ensure the test scenarios file is inside your SERVICE_PATH directory.

### Docker Issues

**Build fails:**
```bash
# Check Docker is running
docker ps

# Rebuild without cache
docker build -f Dockerfile --no-cache -t code-critique:latest .
```

**Artifactory login fails (IDFC):**
```bash
# Test credentials
docker login -u $ARTIFACTORY_USER -p $ARTIFACTORY_PASSWORD artifactory.idfcbank.com/docker

# Check proxy
echo $http_proxy
echo $https_proxy
```

---

## 📈 CI/CD Integration (GoCD)

### Pipeline Example

```yaml
stages:
  - code-quality:
      jobs:
        code-critique:
          environment_variables:
            AI_API_KEY: "{{SECRET:[secret_config][ai_api_key]}}"
          artifacts:
            - build:
                source: sentinel/code-critique/reports/**/*
                destination: code-critique-reports
          tabs:
            report: code-critique-reports/customer-service/code-critique-report.html
          tasks:
            - exec:
                command: bash
                working_directory: sentinel/code-critique/scripts
                arguments:
                  - -c
                  - |
                    export AI_PROVIDER=anthropic
                    export AI_MODEL=claude-sonnet-4-5-20250929
                    export SERVICE_PATH=../../../customer-service
                    python3 analyze-service.py
```

---

## 💰 Cost Comparison

### Cloud APIs (per analysis)
- **Claude Opus**: ~$0.04-0.08
- **Claude Sonnet**: ~$0.02-0.04
- **Perplexity**: ~$0.02-0.05

### Self-Hosted
- **Ollama/vLLM**: FREE (requires GPU/CPU resources)

---

## 🔐 Security Best Practices

### TW/Public
- Never commit API keys to git
- Use environment variables
- Rotate keys regularly

### IDFC/Enterprise
- Never commit artifactory credentials or CA certificate to public repos
- Use GoCD secret management
- Rotate tokens quarterly

---

## 📚 Documentation

- **`prompts/code-critique-system-prompt.md`** - Analysis guidelines
- **`config.json`** - Configuration reference
- **`schemas/code-critique-schema.json`** - JSON structure

---

## 🔄 Version History

- **v6.0** - Category consolidation, linter overlap removal
- **v5.1** - No-defaults configuration
- **v5.0** - Unified provider system with self-hosted support
- **v4.0** - ENV-only configuration
- **v3.0** - Multi-provider AI support
- **v2.0** - Enhanced interactive reports
- **v1.0** - Initial release

---

## 🆘 Support

### TW/Public Issues
- Open GitHub issue

### IDFC/Enterprise Issues
- Contact DevOps team or #code-quality Slack channel

---

## 📄 License

Part of the Sentinel Code Quality Framework

---

**Ready to analyze your code? Choose your setup:**

```bash
# TW/Public - Simple Docker
cd sentinel/code-critique
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-...
export SERVICE_PATH=/path/to/service
make build AI_PROVIDER=anthropic
make analyze

# IDFC/Enterprise - With Artifactory
cd sentinel/code-critique
export ARTIFACTORY_USER=your.user
export ARTIFACTORY_PASSWORD=your.token
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-...
export SERVICE_PATH=/path/to/service
make -f Makefile.idfc build
make -f Makefile.idfc analyze
