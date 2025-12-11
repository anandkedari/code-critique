# Code Critique System with Multi-Provider AI Support

Automated code quality analysis using AI (Claude, Ollama, Perplexity) with standardized, reproducible HTML reports.

## 🎯 Features

- ✅ **Multi-Provider AI Support** - Claude, Ollama (Qwen3-Coder), Perplexity
- ✅ **Flexible Configuration** - CLI args, environment variables, or config file
- ✅ **Local & Cloud** - Use free local models or cloud APIs
- ✅ **8 Categories** - Architecture, Security, Code Quality, Performance, Error Handling, Logging, Self-Critique, Domain-Specific
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
pip install anthropic jinja2 jsonschema

# Optional: For Ollama support
pip install requests

# Optional: For Perplexity support
pip install openai
```

### 2. Choose Your AI Provider

#### Option A: Claude (Cloud, Best Quality)
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
python3 analyze-service.py ../../../customer-service
```

#### Option B: Ollama (Local, Free, Private)
```bash
# Start Ollama
ollama pull qwen2.5-coder:32b-instruct
python3 analyze-service.py ../../../customer-service --provider ollama
```

#### Option C: Perplexity (Cloud, Web-Enhanced)
```bash
export PERPLEXITY_API_KEY="pplx-your-key-here"
python3 analyze-service.py ../../../customer-service --provider perplexity
```

### 3. View Report

```bash
open ../reports/customer-service/code-critique-report.html
```

---

## 🤖 AI Provider Comparison

| Provider | Cost | Privacy | Speed | Quality | Best For |
|----------|------|---------|-------|---------|----------|
| **Claude Opus** | $$$$ | Cloud | Slow | ⭐⭐⭐⭐⭐ | Production, critical analysis |
| **Claude Sonnet** | $$ | Cloud | Fast | ⭐⭐⭐⭐ | **Default**, balanced |
| **Ollama (Qwen3-Coder)** | Free | Local | Medium | ⭐⭐⭐⭐ | Development, on-premise |
| **Perplexity** | $$ | Cloud | Fast | ⭐⭐⭐ | Web-enhanced analysis |

---

## ⚙️ Configuration Options

### Priority Order
1. **CLI Arguments** (highest priority)
2. **Environment Variables**
3. **config.json** (default)

### Configuration File (config.json)

```json
{
  "ai_provider": "claude",
  "confidence_threshold": 70,
  "providers": {
    "claude": {
      "model": "claude-sonnet-4-5-20250929",
      "api_url": "https://api.anthropic.com",
      "max_tokens": 20000,
      "temperature": 0,
      "timeout": 180.0
    },
    "ollama": {
      "model": "qwen2.5-coder:32b-instruct",
      "api_url": "http://localhost:11434",
      "max_tokens": 20000,
      "temperature": 0,
      "timeout": 300.0
    },
    "perplexity": {
      "model": "llama-3.1-sonar-huge-128k-online",
      "api_url": "https://api.perplexity.ai",
      "max_tokens": 20000,
      "temperature": 0,
      "timeout": 180.0
    }
  }
}
```

### CLI Arguments

```bash
python3 analyze-service.py <service-path> [OPTIONS]

Options:
  --provider TEXT          AI provider (claude|perplexity|ollama)
  --model TEXT             Model name/ID
  --api-url TEXT           API endpoint URL
  --api-key TEXT           API authentication key
  --max-tokens INTEGER     Maximum response tokens
  --temperature FLOAT      Sampling temperature (0-1)
  --timeout FLOAT          API timeout in seconds
  --confidence INTEGER     Confidence threshold (0-100)
```

### Environment Variables

```bash
# Provider Selection
export AI_PROVIDER=ollama
export AI_MODEL=qwen2.5-coder:32b-instruct
export AI_API_URL=http://localhost:11434

# API Keys
export AI_API_KEY=your-key
export ANTHROPIC_API_KEY=sk-ant-...
export PERPLEXITY_API_KEY=pplx-...

# Model Parameters
export AI_MAX_TOKENS=30000
export AI_TEMPERATURE=0.1
export AI_TIMEOUT=300

# Analysis Settings
export AI_CONFIDENCE_THRESHOLD=75
```

---

## 💡 Usage Examples

### Default (Claude from config.json)
```bash
cd sentinel/code-critique/scripts
export ANTHROPIC_API_KEY="your-key"
python3 analyze-service.py ../../../customer-service
```

### Ollama with Qwen3-Coder
```bash
# Start Ollama
ollama pull qwen2.5-coder:32b-instruct
ollama serve

# Run analysis
python3 analyze-service.py ../../../customer-service --provider ollama
```

### Custom Model
```bash
python3 analyze-service.py ../../../customer-service \
  --provider ollama \
  --model qwen2.5-coder:14b \
  --max-tokens 30000
```

### Using Environment Variables
```bash
export AI_PROVIDER=ollama
export AI_MODEL=qwen2.5-coder:32b-instruct
export AI_CONFIDENCE_THRESHOLD=80
python3 analyze-service.py ../../../customer-service
```

### Override Everything via CLI
```bash
python3 analyze-service.py ../../../customer-service \
  --provider ollama \
  --model qwen2.5-coder:14b \
  --api-url http://192.168.1.100:11434 \
  --max-tokens 30000 \
  --temperature 0.1 \
  --timeout 600 \
  --confidence 75
```

---

## 📊 What Gets Analyzed

The AI analyzes your code across **8 categories**:

1. ✨ **Code Quality** - Method length, complexity, duplication, naming, SOLID principles
2. 🔍 **Custom Critique** - Pre-commit checklist, code review, technical debt
3. 🔒 **Security** - PII handling, input validation, SQL injection, hardcoded secrets
4. 🛡️ **Error Handling** - Exception handling, error responses, retry mechanisms
5. 🏗️ **Architecture & Design** - Layer violations, business logic, dependencies
6. ⚡ **Performance** - N+1 queries, pagination, caching, database optimization
7. 📝 **Logging** - Framework usage, correlation IDs, sensitive data in logs
8. 🎯 **Domain-Specific** - Service patterns, business logic, domain model quality

---

## 📋 Report Structure

### 1. Overall Summary
- Status badge (Excellent/Good/Needs Work/Critical)
- Critical issues, warnings, files scanned

### 2. Assessment Status
- Compact grid showing all 8 categories
- Status and issue count per category

### 3. Issues by File
- Expandable file list with all issues
- Code snippets and recommendations

### 4. Top Issues
- Most frequent issues by occurrence
- Click to see all instances

### 5. Detailed Category Analysis
- One section per category
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

### GitHub Actions Example

```yaml
name: Code Quality Check
on: [push, pull_request]

jobs:
  code-critique:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install Dependencies
        run: pip install anthropic jinja2 jsonschema requests
      
      - name: Run with Ollama (Self-Hosted Runner)
        run: |
          cd sentinel/code-critique/scripts
          python3 analyze-service.py ../../../customer-service --provider ollama
      
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: code-critique-report
          path: sentinel/code-critique/reports/
      
      - name: Quality Gate
        run: |
          score=$(jq '.summary.overall_score' sentinel/code-critique/reports/customer-service/code-critique-data.json)
          if [ "$score" -lt 70 ]; then exit 1; fi
```

---

## 💰 Cost Comparison

### Cloud APIs (per analysis)
- **Claude Opus**: ~$0.04-0.08
- **Claude Sonnet**: ~$0.02-0.04
- **Perplexity**: ~$0.02-0.05

### Local (Ollama)
- **Qwen3-Coder**: Free!
- Hardware: 16GB RAM minimum, 32GB recommended
- GPU: Optional but recommended for speed

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

### "No API key provided"
```bash
# For Claude
export ANTHROPIC_API_KEY="sk-ant-..."

# For Perplexity
export PERPLEXITY_API_KEY="pplx-..."

# Or use CLI
python3 analyze-service.py <path> --api-key your-key
```

### "anthropic package not installed"
```bash
pip install anthropic jinja2 jsonschema
```

### "requests package not installed" (Ollama)
```bash
pip install requests
```

### "openai package not installed" (Perplexity)
```bash
pip install openai
```

### Ollama Connection Error
```bash
# Check Ollama is running
ollama list

# Start Ollama
ollama serve

# Check endpoint
curl http://localhost:11434/api/tags
```

---

## 📚 Documentation

- **`code_critique.md`** - Complete analysis guidelines
- **`config.json`** - Configuration reference
- **`schemas/code-critique-schema.json`** - JSON structure

---

## 🔄 Version History

- **v3.0** - Multi-provider AI support
  - Added Ollama (Qwen3-Coder) support
  - Added Perplexity support
  - Comprehensive CLI and ENV configuration
  - Provider-specific optimizations
  - Simplified codebase (removed 240+ lines)

- **v2.0** - Enhanced interactive reports
  - Top Issues section
  - Issues by File view
  - Clickable drill-down
  - Responsive layouts

- **v1.0** - Initial release
  - Claude 3.5 Sonnet
  - 8 category analysis
  - HTML reports
  - JSON validation

---

## 📄 License

Part of the Sentinel Code Quality Framework

---

## 🆘 Support

For issues:
1. Check `reports/<service>/code-critique-data.json` for raw analysis
2. Verify configuration (CLI > ENV > config.json)
3. Check file loading worked
4. Review generated JSON against schema

---

**Ready to analyze? Choose your provider:**

```bash
# Claude (Cloud)
export ANTHROPIC_API_KEY="your-key"
python3 analyze-service.py customer-service

# Ollama (Local)
ollama pull qwen2.5-coder:32b-instruct
python3 analyze-service.py customer-service --provider ollama

# Perplexity (Cloud)
export PERPLEXITY_API_KEY="your-key"
python3 analyze-service.py customer-service --provider perplexity
