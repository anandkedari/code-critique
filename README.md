# Code Critique System with Real AI Analysis

Automated code quality analysis using Anthropic Claude AI with standardized, reproducible HTML reports.

## 🎯 Features

- ✅ **Real AI Analysis** - Uses Anthropic Claude to analyze your actual code
- ✅ **8 Categories** - Architecture, Security, Code Quality, Performance, Error Handling, Logging, Self-Critique, Domain-Specific
- ✅ **Consistent Reports** - Fixed HTML structure for reproducibility
- ✅ **Actionable Insights** - Specific issues with code snippets and fixes
- ✅ **JSON Schema Validation** - Ensures output consistency

---

## 📁 Structure

```
code-critique/
├── scripts/
│   └── analyze-service.py          # Main analysis script (with AI)
├── schemas/
│   └── code-critique-schema.json   # JSON schema for validation
├── prompts/
│   └── code-critique-system-prompt.md  # AI system prompt
├── templates/
│   └── code-critique-template.html # Jinja2 HTML template
├── reports/
│   └── <service-name>/
│       ├── code-critique-report.html
│       └── code-critique-data.json
├── code_critique.md                # Complete guidelines
└── CODE_CRITIQUE_USAGE.md          # Detailed documentation
```

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.8+ required
python3 --version

# Install dependencies
cd sentinel
source venv/bin/activate  # If you have venv
pip install anthropic jinja2 jsonschema
```

### 2. Get API Key

Sign up at [Anthropic](https://console.anthropic.com/) and get your API key.

### 3. Set API Key

**Option A: Environment Variable (Recommended)**
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Option B: Command Line Argument**
```bash
python3 analyze-service.py <path> --api-key sk-ant-your-key
```

### 4. Run Analysis

```bash
cd sentinel/code-critique/scripts
python3 analyze-service.py ../../../customer-service
```

### 5. View Report

```bash
open ../reports/customer-service/code-critique-report.html
```

---

## 📊 What Gets Analyzed

The AI analyzes your code across **8 categories**:

### 1. 🏗️ Architecture & Design
- Layer violations
- Business logic placement
- Dependency management
- Design patterns

### 2. 🔒 Security
- PII data handling
- Input validation
- SQL injection risks
- Hardcoded secrets
- Authentication/authorization

### 3. ✨ Code Quality
- Method length
- Cyclomatic complexity
- Code duplication
- Naming conventions
- Code coverage

### 4. ⚡ Performance
- N+1 queries
- Pagination
- Caching strategy
- Database optimization

### 5. 🛡️ Error Handling
- Exception handling
- Error responses
- Logging of errors
- Retry mechanisms

### 6. 📝 Logging
- Logging framework usage
- Correlation IDs
- Log levels
- Sensitive data in logs

### 7. 🔍 Self-Critique
- Pre-commit checklist
- Code review process
- Technical debt tracking

### 8. 🎯 Domain-Specific
- Service-specific patterns
- Business logic validation
- Domain model quality

---

## 💡 Usage Examples

### Basic Analysis
```bash
python3 analyze-service.py ../../../customer-service
```

### With API Key Argument
```bash
python3 analyze-service.py ../../../customer-service --api-key sk-ant-...
```

### From Different Directory
```bash
cd /path/to/sentinel/code-critique/scripts
python3 analyze-service.py /absolute/path/to/customer-service
```

---

## 📋 Report Structure

The generated HTML report follows this exact order:

1. **Overall Summary**
   - Score (0-100)
   - Critical issues count
   - Warnings count
   - Files scanned

2. **Category Table**
   - All 8 categories with scores and status

3. **Detailed Analysis** (for each category)
   - Metrics tracked
   - Assessment items (✅/⚠️/❌)
   - Specific issues with:
     - File path
     - Code snippet
     - Recommendation
     - Fix example

4. **Priority Actions**
   - 🔴 Critical (fix immediately)
   - 🟡 Warnings (address soon)
   - 🔵 Suggestions (nice to have)

5. **Final Assessment**
   - Overall grade
   - Strengths
   - Key improvements
   - Next steps

---

## 🔧 Configuration

### Customize Analysis

Edit `prompts/code-critique-system-prompt.md` to adjust:
- Scoring thresholds
- Metric definitions
- Analysis focus areas

### Customize Report

Edit `templates/code-critique-template.html` to change:
- Colors and styling
- Layout
- Sections displayed

### Update Schema

Edit `schemas/code-critique-schema.json` to modify:
- Required fields
- Validation rules
- Data structure

**Important:** Keep prompt, template, and schema in sync!

---

## 🎯 Output Files

```
reports/<service-name>/
├── code-critique-report.html    # Beautiful HTML report (open in browser)
└── code-critique-data.json      # Raw JSON data (for automation/tracking)
```

### Use JSON for:
- CI/CD integration
- Quality metrics tracking
- Automated quality gates
- Historical comparison

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
        run: |
          pip install anthropic jinja2 jsonschema
      
      - name: Run Code Critique
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          cd sentinel/code-critique/scripts
          python3 analyze-service.py ../../../customer-service
      
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: code-critique-report
          path: sentinel/code-critique/reports/
      
      - name: Check Quality Gate
        run: |
          score=$(jq '.summary.overall_score' sentinel/code-critique/reports/customer-service/code-critique-data.json)
          if [ "$score" -lt 70 ]; then
            echo "Quality gate failed: score $score < 70"
            exit 1
          fi
```

---

## ⚠️ Important Notes

### Token Limits
- Analyzes first 20 files by default (to stay within API limits)
- Adjust `max_files` in script if needed
- For large codebases, consider analyzing modules separately

### API Costs
- Uses Claude 3.5 Sonnet
- ~8000 tokens per analysis
- Monitor usage in Anthropic console
- Estimated cost: ~$0.02-0.05 per analysis

### File Types Analyzed
- Java (`.java`)
- Python (`.py`)
- JavaScript (`.js`)
- TypeScript (`.ts`)
- Go (`.go`)

**Test files are excluded automatically**

---

## 🐛 Troubleshooting

### "No API key provided"
```bash
# Set environment variable
export ANTHROPIC_API_KEY="sk-ant-your-key"

# Or use command line
python3 analyze-service.py <path> --api-key sk-ant-...
```

### "anthropic package not installed"
```bash
pip install anthropic
```

### "No code files found"
- Check service path is correct
- Verify files have supported extensions
- Check if files are in excluded directories

### "JSON validation failed"
- AI response may not match schema
- Check `code-critique-data.json` for issues
- Report continues anyway, check HTML

---

## 📚 Documentation

- **`code_critique.md`** - Complete analysis guidelines
- **`CODE_CRITIQUE_USAGE.md`** - Detailed usage guide
- **`schemas/code-critique-schema.json`** - JSON structure reference

---

## 🔄 Version History

- **v1.0** - Initial release with real AI integration
  - Anthropic Claude 3.5 Sonnet
  - 8 category analysis
  - Consistent HTML reports
  - JSON schema validation

---

## 🆘 Support

For issues:
1. Check `reports/<service>/code-critique-data.json` for raw analysis
2. Verify API key is correct
3. Check file loading worked (should see file list)
4. Review generated JSON against schema

---

## 📄 License

Part of the Sentinel Code Quality Framework

---

**Ready to analyze your code? Run:**
```bash
cd sentinel/code-critique/scripts
export ANTHROPIC_API_KEY="your-key"
python3 analyze-service.py ../../../customer-service
