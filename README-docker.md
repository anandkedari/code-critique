# Docker Setup Guide - Code Critique Framework

This framework supports **two deployment environments**:
- **TW (ThoughtWorks/Public)**: For external/open-source usage with public Docker registries
- **IDFC (Enterprise)**: For internal IDFC Bank usage with corporate artifactory and proxies

---

## 📂 File Structure

```
sentinel/code-critique/
├── Dockerfile.tw              # Public Docker setup
├── Dockerfile.idfc            # Enterprise Docker setup with artifactory
├── docker-compose.tw.yml      # Public compose configuration
├── docker-compose.idfc.yml    # Enterprise compose configuration
├── Makefile.tw                # Public build/run workflow
├── Makefile.idfc              # Enterprise build/publish workflow
└── infrastructure/
    └── IDFCBANKCA.pem        # Corporate CA certificate (IDFC only)
```

---

## 🌍 Option 1: TW/Public Setup (External Usage)

### Prerequisites
- Docker and Docker Compose installed
- AI API key (Anthropic or OpenAI)
- No corporate proxy or artifactory needed

### Setup Steps

1. **Set Environment Variables**
```bash
export AI_PROVIDER=anthropic              # or openai
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-your-key-here
export SERVICE_PATH=/path/to/your/service
```

2. **Build the Image**
```bash
make -f Makefile.tw build AI_PROVIDER=anthropic
```

3. **Run Analysis**
```bash
make -f Makefile.tw run
```

4. **View Results**
```bash
open reports/$(basename $SERVICE_PATH)/code-critique-report.html
```

### Quick Example
```bash
# Analyze a Spring Boot service
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-api123456789
export SERVICE_PATH=/Users/developer/projects/customer-service

cd sentinel/code-critique
make -f Makefile.tw build AI_PROVIDER=anthropic
make -f Makefile.tw run
```

---

## 🏢 Option 2: IDFC/Enterprise Setup (Internal Usage)

### Prerequisites
- Docker and Docker Compose installed
- IDFC Bank network access
- Artifactory credentials
- Corporate CA certificate (replace placeholder in `infrastructure/IDFCBANKCA.pem`)
- AI API key (Anthropic or OpenAI)

### Setup Steps

1. **Configure CA Certificate** (One-time setup)
```bash
# Replace the placeholder with actual IDFC Bank CA certificate
# Contact IT Security team for the certificate
vim sentinel/code-critique/infrastructure/IDFCBANKCA.pem
```

2. **Set Environment Variables**
```bash
# Artifactory credentials
export ARTIFACTORY_USER=your.username
export ARTIFACTORY_PASSWORD=your.token

# Proxy settings (if required)
export http_proxy=http://10.169.48.5:3128
export https_proxy=http://10.169.48.5:3128

# AI configuration
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-your-key-here

# Service configuration
export SERVICE_PATH=/path/to/your/service
export SERVICE_NAME=customer-service

# Optional: GoCD pipeline variables (auto-set in CI/CD)
export GO_REVISION_CODE_CRITIQUE=1.2.3
export GO_PIPELINE_NAME=code-quality
export GO_PIPELINE_LABEL=123
```

3. **Build & Publish to Artifactory**
```bash
cd sentinel/code-critique

# Show available commands
make -f Makefile.idfc help

# Build the Docker image
make -f Makefile.idfc build

# Publish to artifactory (for team-wide use)
make -f Makefile.idfc publish

# Generate metadata
make -f Makefile.idfc metadata
```

4. **Run Analysis**
```bash
# Run code analysis
make -f Makefile.idfc analyze

# Validate JSON output
make -f Makefile.idfc validate

# Clean up containers
make -f Makefile.idfc analyze_clean
```

5. **View Results**
```bash
open reports/customer-service/code-critique-report.html
```

### CI/CD Integration (GoCD)

Add to your GoCD pipeline:

```yaml
stages:
  - code-quality:
      jobs:
        code-critique:
          tasks:
            - exec:
                command: make
                arguments:
                  - -f
                  - Makefile.idfc
                  - ci-build-publish
            - exec:
                command: make
                arguments:
                  - -f
                  - Makefile.idfc
                  - ci-analyze
```

### Quick Example (IDFC)
```bash
# Set credentials
export ARTIFACTORY_USER=anand.kedari
export ARTIFACTORY_PASSWORD=AKCp8k...
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-api123456789
export SERVICE_PATH=/projects/customer-service
export GO_REVISION_CODE_CRITIQUE=1.2.3

# Build, publish, and analyze
cd sentinel/code-critique
make -f Makefile.idfc build
make -f Makefile.idfc publish
make -f Makefile.idfc analyze
```

---

## 🔧 Advanced Configuration

### Custom Confidence Threshold
```bash
# Only report issues with >80% confidence
export AI_CONFIDENCE_THRESHOLD=80
```

### Functional Compliance Testing
```bash
# Include test scenarios validation
export TEST_SCENARIOS_PATH=/path/to/test-scenarios.yml
```

### Multiple AI Providers

**Anthropic (Claude)**
```bash
export AI_PROVIDER=anthropic
export AI_MODEL=claude-sonnet-4-5-20250929
export AI_API_KEY=sk-ant-...
```

**OpenAI**
```bash
export AI_PROVIDER=openai
export AI_API_URL=https://api.openai.com/v1
export AI_MODEL=gpt-4
export AI_API_KEY=sk-...
```

**Perplexity**
```bash
export AI_PROVIDER=openai
export AI_API_URL=https://api.perplexity.ai
export AI_MODEL=llama-3.1-sonar-huge-128k-online
export AI_API_KEY=pplx-...
```

---

## 🐛 Troubleshooting

### TW/Public Issues

**Docker build fails**
```bash
# Check Docker is running
docker ps

# Rebuild without cache
docker build -f Dockerfile.tw --no-cache -t code-critique:latest .
```

**AI API errors**
```bash
# Verify API key
echo $AI_API_KEY

# Test API connection
curl -H "x-api-key: $AI_API_KEY" https://api.anthropic.com/v1/messages
```

### IDFC/Enterprise Issues

**Artifactory login fails**
```bash
# Test credentials manually
docker login -u $ARTIFACTORY_USER -p $ARTIFACTORY_PASSWORD artifactory.idfcbank.com/docker

# Check proxy settings
echo $http_proxy
echo $https_proxy
```

**CA certificate errors**
```bash
# Verify certificate file exists and is valid
cat sentinel/code-critique/infrastructure/IDFCBANKCA.pem

# The file should contain actual certificate, not placeholder
```

**Build fails behind proxy**
```bash
# Ensure proxy variables are set
export http_proxy=http://10.169.48.5:3128
export https_proxy=http://10.169.48.5:3128
export no_proxy=artifactory.idfcbank.com

# Rebuild with proxy args
make -f Makefile.idfc build
```

---

## 📊 Output Files

Both setups generate the same output structure:

```
reports/
└── {service-name}/
    ├── code-critique-report.html    # Human-readable HTML report
    └── code-critique-data.json      # Machine-readable JSON data
```

---

## 🔐 Security Best Practices

### For TW/Public
- Never commit API keys to git
- Use environment variables or `.env` files (gitignored)
- Rotate API keys regularly

### For IDFC/Enterprise
- Never commit artifactory credentials
- Never commit the actual CA certificate to public repos
- Use GoCD secret management for API keys
- Rotate tokens quarterly
- Store CA certificate securely (internal repo only)

---

## 📝 Makefile Commands Reference

### TW/Public (Makefile.tw)
```bash
make -f Makefile.tw build    # Build Docker image
make -f Makefile.tw run      # Run analysis
```

### IDFC/Enterprise (Makefile.idfc)
```bash
make -f Makefile.idfc docker_login      # Login to artifactory
make -f Makefile.idfc build             # Build image
make -f Makefile.idfc publish           # Publish to artifactory
make -f Makefile.idfc analyze           # Run analysis
```

---

## 🤝 Support

- **TW/Public Issues**: Open GitHub issue
- **IDFC/Enterprise Issues**: Contact DevOps team or #code-quality Slack channel

---

## 📜 License

See main repository LICENSE file.
