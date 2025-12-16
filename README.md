# Code Critique System with Multi-Provider AI Support

Automated code quality analysis using AI (Anthropic, OpenAI-compatible APIs) with standardized, reproducible HTML reports.

## 🎯 Features

- ✅ **Multi-Provider AI Support** - Anthropic (Claude), OpenAI-compatible APIs (Perplexity, Ollama, vLLM, LocalAI, etc.)
- ✅ **Flexible Configuration** - Environment variables + config file
- ✅ **Cloud & Self-Hosted** - Use cloud providers or run your own models locally
- ✅ **6 Categories** - Code Architecture & Design, Error Handling & Observability, Performance & Resource Management, AI Quality Assurance, Domain & Business Logic, Functional Compliance (optional)
- ✅ **Consistent Reports** - Fixed HTML structure for reproducibility
- ✅ **Actionable Insights** - Specific issues with code snippets and fixes
- ✅ **JSON Schema Validation** - Ensures output consistency

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.8+ required
python3 --version

# Install dependencies
cd sentinel
pip install anthropic jinja2 jsonschema requests openai
```

### 2. Choose Your AI Provider

#### Option A: Anthropic Claude (Recommended)
```bash
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-your-key-here
export SERVICE_PATH=/path/to/customer-service
python3 analyze-service.py
```

#### Option B: OpenAI-compatible (Perplexity)
```bash
export AI_PROVIDER=openai
export AI_API_URL=https://api.perplexity.ai
export AI_MODEL=llama-3.1-sonar-huge-128k-online
export AI_API_KEY=pplx-your-key-here
export SERVICE_PATH=/path/to/customer-service
python3 analyze-service.py
```

#### Option C: Self-Hosted (Ollama)
```bash
export AI_PROVIDER=openai
export AI_API_URL=http://localhost:11434/v1
export AI_MODEL=llama3.1
export AI_API_KEY=not-needed
export SERVICE_PATH=/path/to/customer-service
python3 analyze-service.py
```

### 3. View Report

```bash
open ../reports/customer-service/code-critique-report.html
```

---

## 🐳 Docker Deployment

Run code-critique in a Docker container for consistent, portable analysis.

### Quick Start with Docker

```bash
# 1. Build the image (REQUIRED: specify AI_PROVIDER)
cd sentinel/code-critique
AI_PROVIDER=anthropic make build

# Or for OpenAI-compatible providers
AI_PROVIDER=openai make build

# 2. Run analysis (all variables required)
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY="your-key"
export SERVICE_PATH=../../customer-service
docker compose up

# 3. View report (opens automatically)
make view-report SERVICE=customer-service
```

### Docker Commands

```bash
# Build Docker image
docker build -t code-critique:latest -f Dockerfile .

# Run with Anthropic
docker run --rm \
  -e AI_PROVIDER=anthropic \
  -e AI_MODEL=claude-sonnet-4-5-20250929 \
  -e AI_API_KEY="your-key" \
  -v /path/to/service:/service:ro \
  -v $(pwd)/code-critique/reports:/app/code-critique/reports \
  code-critique:latest /service

# Run with OpenAI-compatible (Perplexity)
docker run --rm \
  -e AI_PROVIDER=openai \
  -e AI_API_URL=https://api.perplexity.ai \
  -e AI_MODEL=llama-3.1-sonar-huge-128k-online \
  -e AI_API_KEY="your-key" \
  -v /path/to/service:/service:ro \
  -v $(pwd)/code-critique/reports:/app/code-critique/reports \
  code-critique:latest /service

# Interactive shell
docker run --rm -it \
  -v /path/to/service:/service:ro \
  --entrypoint /bin/bash \
  code-critique:latest
```

### Docker Compose

Use docker-compose with all required environment variables:

```bash
# With Anthropic (all variables required)
AI_PROVIDER=anthropic \
MODEL=claude-sonnet-4-5-20250929 \
API_KEY="sk-ant-..." \
SERVICE_PATH=../../customer-service \
docker-compose up

# With OpenAI-compatible (Perplexity)
AI_PROVIDER=openai \
API_URL="https://api.perplexity.ai" \
MODEL="llama-3.1-sonar-huge-128k-online" \
API_KEY="pplx-..." \
SERVICE_PATH=../../customer-service \
docker-compose up

# With OpenAI-compatible (Ollama self-hosted)
AI_PROVIDER=openai \
API_URL="http://localhost:11434/v1" \
MODEL="llama3.1" \
API_KEY="not-needed" \
SERVICE_PATH=../../customer-service \
docker-compose up
```

### Volume Mounts

Two required volumes:

1. **Service Code** (read-only):
   ```bash
   -v /path/to/your/service:/service:ro
   ```

2. **Reports** (read-write):
   ```bash
   -v $(pwd)/code-critique/reports:/app/code-critique/reports
   ```

Optional config mount:
```bash
-v $(pwd)/code-critique/config.json:/app/code-critique/config.json:ro
```

---

## 🛠️ Makefile Commands

Professional Makefile with generic LLM configuration.

### Available Commands

```bash
make help              # Show all commands
make build             # Build Docker image
make run              # Run analysis (uses config.json or env vars)
make shell            # Interactive shell
make docker-up        # Start with docker-compose
make docker-down      # Stop docker-compose
make clean            # Clean reports and images
make clean-reports    # Clean only reports
make view-report      # Open HTML report
make test             # Test Docker setup
make info             # Show configuration
```

### Usage Examples

```bash
# Run with Anthropic (all variables required)
AI_PROVIDER=anthropic \
MODEL=claude-sonnet-4-5-20250929 \
API_KEY="sk-ant-..." \
SERVICE_PATH=../../customer-service \
make run

# Run with Perplexity
AI_PROVIDER=openai \
API_KEY="pplx-..." \
API_URL="https://api.perplexity.ai" \
MODEL="llama-3.1-sonar-huge-128k-online" \
SERVICE_PATH=../../customer-service \
make run

# Run with Ollama self-hosted
AI_PROVIDER=openai \
API_URL="http://localhost:11434/v1" \
MODEL="llama3.1" \
API_KEY="not-needed" \
SERVICE_PATH=../../customer-service \
make run

# Custom confidence and service
AI_PROVIDER=anthropic \
MODEL=claude-sonnet-4-5-20250929 \
API_KEY="..." \
SERVICE_PATH=../../my-service \
SERVICE_NAME=my-service \
CONFIDENCE=80 \
make run

# View specific report
make view-report SERVICE_NAME=customer-service

# Check current config
make info

# Clean everything
make clean
```

### Makefile Variables

All variables must be set via environment:

```bash
# Service configuration (required)
SERVICE_PATH                          # Path to service to analyze
SERVICE_NAME                          # Service name for reports

# AI Provider configuration (required)
AI_PROVIDER                           # Provider: anthropic or openai
MODEL                                 # Model identifier
API_KEY                               # API authentication key

# API Configuration (optional)
API_URL                               # API endpoint URL (only if non-standard)

# Analysis configuration (optional)
CONFIDENCE                            # Confidence threshold (0-100)
```

### Configuration Priority

Environment variables are the **only** configuration method:

1. **Environment variables** - All configuration must be provided via env vars
2. **config.json** - Contains only non-provider settings (temperature, max_tokens, timeout)

### Example: Switch Between Providers

```bash
# Use Anthropic
AI_PROVIDER=anthropic \
MODEL=claude-sonnet-4-5-20250929 \
API_KEY="sk-ant-..." \
SERVICE_PATH=../../customer-service \
make run

# Switch to Perplexity
AI_PROVIDER=openai \
API_URL="https://api.perplexity.ai" \
MODEL="llama-3.1-sonar-huge-128k-online" \
API_KEY="pplx-..." \
SERVICE_PATH=../../customer-service \
make run
```

All variables required - no defaults! 🎯

---

## 🤖 AI Provider Comparison

| Provider | Cost | Privacy | Speed | Quality | Best For |
|----------|------|---------|-------|---------|----------|
| **Claude Opus** | $$$$ | Cloud | Slow | ⭐⭐⭐⭐⭐ | Production, critical analysis |
| **Claude Sonnet** | $$ | Cloud | Fast | ⭐⭐⭐⭐ | Balanced performance & cost |
| **Perplexity** | $$ | Cloud | Fast | ⭐⭐⭐ | Web-enhanced analysis |
| **Ollama (Local)** | FREE | 100% Private | Medium | ⭐⭐⭐ | Privacy-sensitive, offline |
| **vLLM (Local)** | FREE | 100% Private | Fast | ⭐⭐⭐ | High-throughput, self-hosted |
| **LocalAI (Local)** | FREE | 100% Private | Medium | ⭐⭐⭐ | Drop-in OpenAI replacement |

---

## ⚙️ Configuration

Configuration is done **entirely through environment variables**. No CLI arguments for AI configuration.

### Configuration File (config.json)

The config.json file only contains the confidence threshold setting:

```json
{
  "confidence_threshold": 70,
  "description": "Minimum confidence percentage (0-100) required for AI to report issues.",
  "recommendations": {
    "strict": 80,
    "balanced": 70,
    "comprehensive": 60
  },
  "_note": "AI configuration (provider, model, API keys, etc.) must be provided via environment variables."
}
```

### Required Environment Variables

```bash
# Core Configuration (Required)
export AI_PROVIDER=anthropic|openai   # Provider: anthropic, openai
export AI_MODEL=model-name            # Model identifier
export AI_API_KEY=your-key            # API authentication key
```

### Optional Environment Variables

```bash
# API Configuration (Optional - only for non-standard endpoints)
export AI_API_URL=https://api.example.com  # API endpoint URL (required for self-hosted or non-standard endpoints)

# Analysis Configuration (Optional)
export AI_CONFIDENCE_THRESHOLD=70          # Confidence threshold 0-100 (from config.json if not set)
export TEST_SCENARIOS_PATH=/path/to/file   # Path to test-scenarios.yml
export SERVICE_NAME=my-service             # Override service name for reports
```

**Note:** `max_tokens`, `temperature`, and `timeout` are configured in `config.json` rather than environment variables.

### Provider-Specific Examples

#### Anthropic (Claude)
```bash
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-...
# AI_API_URL not required (uses https://api.anthropic.com)
```

#### OpenAI-compatible (Perplexity)
```bash
export AI_PROVIDER=openai
export AI_API_URL=https://api.perplexity.ai
export AI_MODEL=llama-3.1-sonar-huge-128k-online
export AI_API_KEY=pplx-...
```

#### OpenAI-compatible (Standard OpenAI)
```bash
export AI_PROVIDER=openai
export AI_MODEL=gpt-4
export AI_API_KEY=sk-...
# AI_API_URL not required (uses https://api.openai.com/v1)
```

#### OpenAI-compatible (Ollama - Self-hosted)
```bash
export AI_PROVIDER=openai
export AI_API_URL=http://localhost:11434/v1
export AI_MODEL=llama3.1
export AI_API_KEY=not-needed  # Ollama doesn't require auth
```

#### OpenAI-compatible (vLLM - Self-hosted)
```bash
export AI_PROVIDER=openai
export AI_API_URL=http://localhost:8000/v1
export AI_MODEL=meta-llama/Llama-3.1-70B
export AI_API_KEY=optional
```

#### OpenAI-compatible (LocalAI - Self-hosted)
```bash
export AI_PROVIDER=openai
export AI_API_URL=http://localhost:8080/v1
export AI_MODEL=llama3
export AI_API_KEY=optional
```

### No CLI Arguments

The script runs without any command-line arguments. All configuration is done via environment variables:

```bash
python3 analyze-service.py
```

---

## 💡 Usage Examples

### Anthropic Claude
```bash
cd sentinel/code-critique/scripts
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-your-key
export SERVICE_PATH=/path/to/customer-service
python3 analyze-service.py
```

### OpenAI-compatible (Perplexity)
```bash
cd sentinel/code-critique/scripts
export AI_PROVIDER=openai
export AI_API_URL=https://api.perplexity.ai
export AI_MODEL=llama-3.1-sonar-huge-128k-online
export AI_API_KEY=pplx-your-key
export SERVICE_PATH=/path/to/customer-service
python3 analyze-service.py
```

### OpenAI-compatible (Ollama Self-hosted)
```bash
cd sentinel/code-critique/scripts
export AI_PROVIDER=openai
export AI_API_URL=http://localhost:11434/v1
export AI_MODEL=llama3.1
export AI_API_KEY=not-needed
export SERVICE_PATH=/path/to/customer-service
python3 analyze-service.py
```

### With Custom Confidence Threshold
```bash
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-...
export SERVICE_PATH=/path/to/customer-service
export AI_CONFIDENCE_THRESHOLD=80
python3 analyze-service.py
```

### With Custom Scenarios
```bash
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-...
export SERVICE_PATH=/path/to/customer-service
export TEST_SCENARIOS_PATH=/path/to/custom-scenarios.yml
python3 analyze-service.py
```

---

## 📊 What Gets Analyzed

The AI analyzes your code across **6 comprehensive categories**:

### 1. 🏗️ **Code Architecture & Design**
- SOLID principle violations, unnecessary abstraction layers
- Business logic placement, dependency injection issues
- Method length, class responsibilities, meaningful naming
- Code duplication, magic numbers
- AI-generated code issues (invented classes, fake config keys)
- **Semantic dead code** (logically obsolete methods, unused dependencies, stale config)
- Documentation accuracy

**Focus**: Architectural patterns and code structure requiring semantic understanding

### 2. 🛡️ **Error Handling & Observability**
- Exception handling coverage, empty catch blocks
- Retry logic, error messages, defensive coding
- System.out.println usage, correlation/trace IDs
- Structured logging, distributed tracing spans

**Focus**: Production-readiness and observability

### 3. ⚡ **Performance & Resource Management**
- Algorithmic complexity, memory leaks
- Async/await misuse, N+1 query patterns
- Unbounded resource loading, unnecessary object creation
- Resource cleanup (streams, connections)

**Focus**: Performance bottlenecks requiring flow analysis

### 4. 🤖 **AI Quality Assurance**
- **AI Code Issues**: Hallucinated functions, non-existent libraries, placeholder code
- **Bug Detection**: Race conditions, validation bypass, transaction boundary issues
- **Missing Edge Cases**: Boundary conditions, production risks, silent failures
- **Over-Engineering**: Unnecessary patterns, premature optimization

**Focus**: AI-generated code issues and semantic bug detection

### 5. 🎯 **Domain & Business Logic**
- Domain-specific compliance (DDD, CQRS patterns)
- Business rule validation
- Domain model quality (entities, value objects, aggregates)

**Focus**: Domain patterns and business rules

### 6. 🧪 **Functional Compliance** (Optional)
- Validates code against business requirements in test-scenarios.yml
- Provides evidence-based validation with file paths, line numbers, code snippets
- Reports: PASS ✅ / FAIL ❌ / PARTIAL ⚠️ / CANNOT_VERIFY ❓

**Focus**: Business requirement implementation verification

---

## 🔍 What We Don't Analyze (Avoid Linter/Security Scan Overlap)

**Linters Handle:**
- ❌ Unused imports, unused local variables
- ❌ Simple unreachable code after return
- ❌ Code style violations (Checkstyle/ESLint)
- ❌ Basic complexity metrics (SonarQube)

**Security Scans Handle:**
- ❌ SQL injection patterns (SAST tools)
- ❌ XSS vulnerabilities (SAST tools)
- ❌ Known CVEs in dependencies (Snyk/Dependabot)
- ❌ Hardcoded secrets - basic patterns (GitLeaks)

**Our Focus:**
- ✅ Semantic issues requiring code understanding
- ✅ Business logic bugs and architectural patterns
- ✅ AI-generated code quality
- ✅ Production risks and performance patterns

---

## 🧪 Functional Compliance (Optional)

The framework can validate your code against business requirements defined in a `test-scenarios.yml` file.

### How It Works

1. **Create test-scenarios.yml** in your service directory
2. **Define scenarios** - business requirements to validate
3. **Run analysis** - AI searches code for implementation
4. **Get evidence** - File paths, line numbers, code snippets

### Example test-scenarios.yml

```yaml
service_name: "customer-service"
description: "Business logic validation for customer service"

# Global validations applied to ALL operations
global_validations:
  - "Data stored in database must match the request payload"
  - "All timestamps (createdAt, updatedAt) must be set automatically"
  - "Response data must match what was stored in database"
  - "Proper HTTP status codes returned (200, 201, 404, 400, etc.)"

# Specific business scenarios
scenarios:
  - "If customer does not exist, a new customer is created"
  - "When trying to create duplicate customer, error is thrown"
  - "API should allow deleting existing customer"
  - "Customer age must be 18 or older"
```

### Scenario Status Types

| Status | Icon | Meaning |
|--------|------|---------|
| **PASS** | ✅ | Functionality fully implemented and verified |
| **FAIL** | ❌ | Not implemented or incorrect |
| **PARTIAL** | ⚠️ | Some requirements met, some missing |
| **COULD NOT VERIFY** | ❓ | Insufficient evidence in code |

### Using Scenarios

Test scenarios are loaded **only from the TEST_SCENARIOS_PATH environment variable**:

```bash
# Provide test scenarios via environment variable
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-...
export SERVICE_PATH=/path/to/customer-service
export TEST_SCENARIOS_PATH=/path/to/test-scenarios.yml
python3 analyze-service.py
```

**Note**: The system does NOT look for test-scenarios.yml inside the service directory. You must explicitly provide the path via TEST_SCENARIOS_PATH.

### Report Output

The report includes a dedicated "Test Scenario Compliance" tab showing:
- **Summary stats**: Pass/Fail/Partial/Could Not Verify counts
- **Bug count**: Bugs found in passing scenarios
- **Scenario cards**: Each scenario with evidence (file paths, line numbers, code snippets)
- **Recommendations**: How to fix failing scenarios

---

## 📋 Report Structure

### 1. Overall Summary
- Status badge (Excellent/Good/Needs Work/Critical)
- Critical issues, warnings, files scanned

### 2. Assessment Status
- Compact grid showing all 6 categories
- Status and issue count per category

### 3. Issues by File
- Expandable file list with all issues
- Code snippets and recommendations

### 4. Top Issues
- Most frequent issues by occurrence
- Click to see all instances

### 5. Detailed Category Analysis
- One section per category with comprehensive metrics
- Metrics, findings, recommendations

### 6. Priority Actions
- 🔴 Critical - fix immediately
- 🟡 Warnings - address soon  
- 🔵 Suggestions - nice to have

---

## 🔧 Advanced Configuration

### Customize Analysis

Edit `prompts/code-critique-system-prompt.md`:
- Scoring thresholds
- Metric definitions
- Analysis focus

### Customize Report

Edit `templates/code-critique-template.html`:
- Colors and styling
- Layout
- Sections

### Update Schema

Edit `schemas/code-critique-schema.json`:
- Required fields
- Validation rules
- Data structure

**Keep prompt, template, and schema in sync!**

---

## 📈 CI/CD Integration

### GoCD Pipeline Example

Create a pipeline in GoCD with the following configuration:

#### Pipeline Configuration (YAML)

```yaml
format_version: 10
pipelines:
  code-quality-check:
    group: quality-gates
    label_template: "${COUNT}"
    lock_behavior: unlockWhenFinished
    display_order: -1
    materials:
      git:
        git: https://github.com/your-org/your-repo.git
        branch: main
        destination: source
        auto_update: true
    stages:
      - setup:
          fetch_materials: true
          keep_artifacts: false
          clean_workspace: false
          approval:
            type: success
            allow_only_on_success: false
          jobs:
            install-dependencies:
              tasks:
                - exec:
                    command: bash
                    arguments:
                      - -c
                      - |
                        python3 --version
                        pip3 install anthropic jinja2 jsonschema requests openai
      
      - analyze:
          fetch_materials: true
          keep_artifacts: false
          clean_workspace: false
          approval:
            type: success
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
                        export AI_CONFIDENCE_THRESHOLD=70
                        python3 analyze-service.py
      
      - quality-gate:
          fetch_materials: true
          keep_artifacts: false
          clean_workspace: false
          approval:
            type: success
          jobs:
            check-score:
              tasks:
                - exec:
                    command: bash
                    arguments:
                      - -c
                      - |
                        CRITICAL=$(jq '.summary.critical_count' sentinel/code-critique/reports/customer-service/code-critique-data.json)
                        WARNINGS=$(jq '.summary.warning_count' sentinel/code-critique/reports/customer-service/code-critique-data.json)
                        
                        echo "Critical Issues: $CRITICAL"
                        echo "Warnings: $WARNINGS"
                        
                        # Fail if critical issues found
                        if [ "$CRITICAL" -gt 0 ]; then
                          echo "❌ Pipeline failed: $CRITICAL critical issues found"
                          exit 1
                        fi
                        
                        # Optional: Fail if too many warnings
                        if [ "$WARNINGS" -gt 10 ]; then
                          echo "⚠️  Pipeline failed: $WARNINGS warnings exceed threshold (10)"
                          exit 1
                        fi
                        
                        echo "✅ Quality gate passed"
```

#### Setup Instructions

1. **Add API Key to GoCD Secrets**:
   - Navigate to Admin → Secret Management
   - Create secret: `ai_api_key` with your AI provider API key

2. **Configure Pipeline**:
   - Copy the YAML above to `pipeline.gocd.yaml` in your repo root
   - Or create pipeline via GoCD UI

3. **Agent Requirements**:
   - Python 3.8+
   - jq (for JSON parsing)
   - Internet access (for Claude/Perplexity)

4. **Customize Quality Gates**:
   ```bash
   # Adjust thresholds in quality-gate stage
   CRITICAL_THRESHOLD=0    # Fail if any critical issues
   WARNING_THRESHOLD=10    # Fail if more than 10 warnings
   ```

#### Viewing Reports

Reports are published as artifacts and accessible via:
- **GoCD UI**: Pipeline → Stage → Job → Artifacts tab
- **Custom Tab**: `report` tab shows HTML report directly in GoCD
- **Download**: Full report package available for download
```

---

## 💰 Cost Comparison

### Cloud APIs (per analysis)
- **Claude Opus**: ~$0.04-0.08
- **Claude Sonnet**: ~$0.02-0.04
- **Perplexity**: ~$0.02-0.05

All pricing is approximate and may vary based on actual token usage and API pricing changes.

---

## ⚠️ Important Notes

### Token Limits
- Analyzes all files in one pass
- Adjust `max_tokens` if needed
- Large codebases may need chunking

### File Types Analyzed
- Java (`.java`)
- Python (`.py`)
- JavaScript (`.js`)
- TypeScript (`.ts`)
- Go (`.go`)

**Test files automatically excluded**

---

## 🐛 Troubleshooting

### "AI_PROVIDER environment variable is required"
```bash
# Set required environment variables
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-...
```

### "No API key provided"
```bash
# Set the AI_API_KEY environment variable
export AI_API_KEY=your-key
```

### "anthropic package not installed"
```bash
pip install anthropic jinja2 jsonschema requests openai
```

---

## 📚 Documentation

- **`prompts/code-critique-system-prompt.md`** - Complete analysis guidelines and AI instructions
- **`config.json`** - Configuration reference
- **`schemas/code-critique-schema.json`** - JSON structure

---

## 🔄 Version History

- **v6.0** - Category consolidation and linter overlap removal
  - Consolidated from 9 to 6 comprehensive categories
  - Removed overlap with linters (unused imports, variables, basic dead code)
  - Removed overlap with security scans (SQL injection, XSS, CVEs)
  - Enhanced semantic dead code detection (logically obsolete methods, stale config)
  - Added 65+ detailed metrics across all categories
  - Crystal-clear prompts for any AI model (Claude, GPT, Llama, etc.)
  - Focus on semantic analysis requiring code understanding
  - All checks preserved, better organized

- **v5.1** - No-defaults configuration
  - Removed all default values from environment variables
  - Users must explicitly provide AI_PROVIDER, AI_MODEL, AI_API_KEY
  - Dockerfile requires AI_PROVIDER build argument
  - Only provider-specific packages installed (anthropic OR openai)
  - Enhanced documentation for explicit configuration

- **v5.0** - Unified provider system with self-hosted support
  - Renamed "claude" → "anthropic" for clarity
  - Renamed "perplexity" → "openai" (OpenAI-compatible)
  - Added support for self-hosted models (Ollama, vLLM, LocalAI)
  - Moved temperature, max_tokens, timeout to config.json
  - Simplified to 2 providers: anthropic, openai

- **v4.0** - ENV-only configuration
  - Removed CLI arguments for AI configuration
  - Simplified to environment variables only
  - Cleaner, more Docker-native approach

- **v3.0** - Multi-provider AI support
  - Added Perplexity support
  - Provider-specific optimizations

- **v2.0** - Enhanced interactive reports
  - Top Issues section
  - Issues by File view
  - Clickable drill-down

- **v1.0** - Initial release
  - Claude 3.5 Sonnet
  - 8 category analysis
  - HTML reports

---

## 📄 License

Part of the Sentinel Code Quality Framework

---

## 🆘 Support

For issues:
1. Check `reports/<service>/code-critique-data.json` for raw analysis
2. Verify environment variables are set correctly
3. Check file loading worked
4. Review generated JSON against schema

---

**Ready to analyze? Choose your provider:**

```bash
# Anthropic Claude (Cloud)
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-your-key
export SERVICE_PATH=/path/to/customer-service
python3 analyze-service.py

# OpenAI-compatible: Perplexity (Cloud)
export AI_PROVIDER=openai
export AI_API_URL=https://api.perplexity.ai
export AI_MODEL=llama-3.1-sonar-huge-128k-online
export AI_API_KEY=pplx-your-key
export SERVICE_PATH=/path/to/customer-service
python3 analyze-service.py

# OpenAI-compatible: Ollama (Self-hosted)
export AI_PROVIDER=openai
export AI_API_URL=http://localhost:11434/v1
export AI_MODEL=llama3.1
export AI_API_KEY=not-needed
export SERVICE_PATH=/path/to/customer-service
python3 analyze-service.py
