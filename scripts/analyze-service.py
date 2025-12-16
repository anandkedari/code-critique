#!/usr/bin/env python3
"""
Code Critique Report Generator with Multi-Provider AI Support

Analyzes code using AI (Anthropic, OpenAI-compatible APIs) and generates standardized reports.
Configuration is done entirely through environment variables.

Usage:
    python3 analyze-service.py

Examples:
    # Anthropic (Claude)
    export AI_PROVIDER=anthropic
    export AI_MODEL=claude-sonnet-4-5-20250929
    export AI_API_KEY=sk-ant-...
    export SERVICE_PATH=/path/to/service
    python3 analyze-service.py
    
    # OpenAI-compatible (Perplexity)
    export AI_PROVIDER=openai
    export AI_API_URL=https://api.perplexity.ai
    export AI_MODEL=llama-3.1-sonar-huge-128k-online
    export AI_API_KEY=pplx-...
    export SERVICE_PATH=/path/to/service
    python3 analyze-service.py
    
    # OpenAI-compatible (Ollama self-hosted)
    export AI_PROVIDER=openai
    export AI_API_URL=http://localhost:11434/v1
    export AI_MODEL=llama3.1
    export AI_API_KEY=optional
    export SERVICE_PATH=/path/to/service
    python3 analyze-service.py
    
    # With test scenarios (optional)
    export TEST_SCENARIOS_PATH=/path/to/test-scenarios.yml
    python3 analyze-service.py

Required Environment Variables:
    AI_PROVIDER - AI provider (anthropic|openai)
    AI_MODEL - Model name/ID
    AI_API_KEY - API authentication key
    SERVICE_PATH - Path to service directory to analyze

Optional Environment Variables:
    AI_API_URL - API endpoint (defaults: anthropic→https://api.anthropic.com, openai→https://api.openai.com/v1)
    AI_CONFIDENCE_THRESHOLD - Confidence threshold 0-100 (default: 70)
    TEST_SCENARIOS_PATH - Path to test-scenarios.yml (if provided, enables functional compliance check)
    SERVICE_NAME - Service name for reports (defaults to directory name)
    
Note: max_tokens, temperature, and timeout are configured in config.json
"""

import sys
import os
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from jinja2 import Environment, FileSystemLoader
import jsonschema

# File patterns configuration
INCLUDE_PATTERNS = ['**/*.java', '**/*.py', '**/*.js', '**/*.ts', '**/*.go']
EXCLUDE_DIRS = ['build', 'target', 'node_modules', '.git', 'venv', 'dist', 'gradle']
PRIORITY_KEYWORDS = ['controller', 'service', 'repository', 'config', 'application', 'main', 'entity', 'model']

def load_code_files(service_path):
    """Load all relevant source code files from the service."""
    service_path = Path(service_path)
    code_files = []
    
    print(f"📁 Loading code files from: {service_path.name}")
    
    for pattern in INCLUDE_PATTERNS:
        for file_path in service_path.glob(pattern):
            if any(excluded in file_path.parts for excluded in EXCLUDE_DIRS):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    relative_path = file_path.relative_to(service_path)
                    code_files.append({
                        'path': str(relative_path),
                        'content': content,
                        'size': len(content)
                    })
                    print(f"   ✓ {relative_path}")
            except Exception as e:
                print(f"   ✗ Error: {file_path}: {e}")
    
    print(f"   Total: {len(code_files)} files loaded\n")
    
    # CRITICAL: Sort files by path to ensure deterministic order
    code_files.sort(key=lambda x: x['path'])
    
    return code_files

def load_config():
    """Load configuration including confidence threshold."""
    script_dir = Path(__file__).parent
    config_file = script_dir.parent / 'config.json'
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  Config file not found, using default confidence threshold: 70%")
        return {"confidence_threshold": 70}

def load_system_prompt():
    """Load the structured system prompt."""
    script_dir = Path(__file__).parent
    prompt_file = script_dir.parent / 'prompts' / 'code-critique-system-prompt.md'
    with open(prompt_file, 'r') as f:
        return f.read()

def load_test_scenarios(service_path, scenarios_path=None):
    """Load test scenarios from TEST_SCENARIOS_PATH environment variable only."""
    if not scenarios_path:
        # No scenarios path provided - skip functional compliance
        return None
    
    scenarios_file = Path(scenarios_path)
    print(f"📋 Loading test scenarios from: {scenarios_file}")
    
    if not scenarios_file.exists():
        print(f"   ✗ File not found: {scenarios_file}\n")
        return None
    
    try:
        with open(scenarios_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract service name from the YAML to verify correct file loaded
            service_name_in_file = "unknown"
            for line in content.split('\n')[:10]:
                if 'service_name:' in line:
                    service_name_in_file = line.split('service_name:')[1].strip().strip('"\'')
                    break
            print(f"   ✓ Test scenarios loaded ({len(content)} characters)")
            print(f"   ✓ Service in file: {service_name_in_file}")
            print(f"   ✓ File path: {scenarios_file}\n")
            return content
    except Exception as e:
        print(f"   ✗ Error loading scenarios: {e}\n")
        return None

def show_progress(stop_event):
    """Show periodic progress updates with elapsed time (Docker-friendly)."""
    categories = [
        "🏗️  Code Architecture & Design",
        "🛡️  Error Handling & Observability",
        "⚡ Performance & Resource Management",
        "🤖 AI Quality Assurance",
        "🎯 Domain & Business Logic",
        "🧪 Functional Compliance"
    ]
    
    print("\n🤖 Analyzing code with AI...")
    print("   This may take 2-5 minutes depending on codebase size\n")
    
    start_time = time.time()
    idx = 0
    last_update = 0
    
    while not stop_event.is_set():
        elapsed = int(time.time() - start_time)
        
        # Print update every 10 seconds
        if elapsed >= last_update + 10 and elapsed > 0:
            minutes = elapsed // 60
            seconds = elapsed % 60
            category = categories[idx % len(categories)]
            print(f"   ⏱️  {minutes:02d}:{seconds:02d} - Analyzing: {category}")
            idx += 1
            last_update = elapsed
        
        time.sleep(1)
    
    elapsed = int(time.time() - start_time)
    minutes = elapsed // 60
    seconds = elapsed % 60
    print(f"   ✓ Analysis complete! (took {minutes}m {seconds}s)\n")

def extract_file_structure(file_path, content):
    """Extract high-level structure from a file (classes, methods, imports)."""
    structure = {
        'file': file_path,
        'imports': [],
        'classes': [],
        'methods': [],
        'key_concepts': []
    }
    
    lines = content.split('\n')
    for line in lines[:100]:  # First 100 lines for structure
        line = line.strip()
        
        # Java/Kotlin
        if line.startswith('import ') or line.startswith('from ') or line.startswith('require'):
            structure['imports'].append(line[:80])
        elif 'class ' in line or 'interface ' in line or 'enum ' in line:
            structure['classes'].append(line[:100])
        elif 'public ' in line or 'private ' in line or 'protected ' in line:
            if '(' in line and ')' in line:
                structure['methods'].append(line[:100])
        
        # Python
        elif line.startswith('def ') or line.startswith('async def '):
            structure['methods'].append(line[:100])
        elif line.startswith('class '):
            structure['classes'].append(line[:100])
        
        # JavaScript/TypeScript
        elif 'function ' in line or 'const ' in line or 'let ' in line:
            if '(' in line:
                structure['methods'].append(line[:100])
        elif 'export ' in line or 'module.exports' in line:
            structure['key_concepts'].append(line[:100])
    
    return structure

def build_codebase_context(code_files):
    """Build high-level context of entire codebase."""
    print("📋 Building codebase context...")
    context = {
        'total_files': len(code_files),
        'file_structures': [],
        'packages': set(),
        'key_files': []
    }
    
    for file_info in code_files:
        structure = extract_file_structure(file_info['path'], file_info['content'])
        context['file_structures'].append(structure)
        
        # Extract package/module name
        path_parts = Path(file_info['path']).parts
        if len(path_parts) > 1:
            context['packages'].add(path_parts[0])
        
        # Identify key files
        if any(keyword in file_info['path'].lower() for keyword in PRIORITY_KEYWORDS):
            context['key_files'].append(file_info['path'])
    
    context['packages'] = sorted(list(context['packages']))
    print(f"   ✓ Context built: {len(context['file_structures'])} files, {len(context['packages'])} packages\n")
    return context

def validate_and_correct_counts(data):
    """Validate AI counts match actual issues and correct if needed."""
    print("\n🔍 Validating issue counts...")
    
    # Check for metric-issue mismatches
    print("\n🔍 Checking metric-issue alignment...")
    for category in data.get('categories', []):
        category_name = category.get('name', 'Unknown')
        issue_count = len(category.get('issues', []))
        
        # Check if metrics reference violations but issues are missing
        for metric in category.get('metrics', []):
            metric_value = metric.get('value', '')
            if 'violation' in metric_value.lower() and issue_count == 0:
                print(f"   ⚠️  {category_name}: Metric '{metric.get('label')}' shows violations but no issues found")
    
    # Count actual issues by severity across all categories
    # EXCLUDE Functional Compliance from bug counts
    actual_critical = 0
    actual_warning = 0
    actual_info = 0
    actual_compliant = 0
    
    for category in data.get('categories', []):
        # Skip Functional Compliance category for bug counts
        if category.get('name') == 'Functional Compliance':
            continue
        
        for issue in category.get('issues', []):
            severity = issue.get('severity', '').lower()
            if severity == 'critical':
                actual_critical += 1
            elif severity == 'warning':
                actual_warning += 1
            elif severity == 'info':
                actual_info += 1
        
        # Count compliant items
        for item in category.get('items', []):
            assessment = item.get('assessment', '').lower()
            if assessment == 'compliant':
                actual_compliant += 1
    
    # Get reported counts
    reported_critical = data['summary'].get('critical_count', 0)
    reported_warning = data['summary'].get('warning_count', 0)
    reported_info = data['summary'].get('info_count', 0)
    reported_compliant = data['summary'].get('success_count', 0)
    
    # Check for mismatches
    corrections_made = False
    
    if reported_critical != actual_critical:
        print(f"   ⚠️  Critical count mismatch: AI said {reported_critical}, actual is {actual_critical}")
        data['summary']['critical_count'] = actual_critical
        corrections_made = True
    
    if reported_warning != actual_warning:
        print(f"   ⚠️  Warning count mismatch: AI said {reported_warning}, actual is {actual_warning}")
        data['summary']['warning_count'] = actual_warning
        corrections_made = True
    
    if reported_info != actual_info:
        print(f"   ⚠️  Info count mismatch: AI said {reported_info}, actual is {actual_info}")
        data['summary']['info_count'] = actual_info
        corrections_made = True
    
    if reported_compliant != actual_compliant:
        print(f"   ⚠️  Success count mismatch: AI said {reported_compliant}, actual is {actual_compliant}")
        data['summary']['success_count'] = actual_compliant
        corrections_made = True
    
    if corrections_made:
        print("   ✓ Counts corrected to match actual issues")
    else:
        print("   ✓ All counts accurate!")
    
    return data

def analyze_with_ai(service_path, code_files, config, scenarios_path=None):
    """Route to appropriate AI provider based on configuration."""
    provider = config['provider']
    
    if provider == 'anthropic':
        return _analyze_with_anthropic(service_path, code_files, config, scenarios_path)
    elif provider == 'openai':
        return _analyze_with_openai(service_path, code_files, config, scenarios_path)
    else:
        print(f"❌ Unknown provider: {provider}")
        print("   Supported providers: anthropic, openai")
        sys.exit(1)

def _analyze_with_anthropic(service_path, code_files, config, scenarios_path=None):
    """Analyze with Anthropic (Claude)."""
    try:
        import anthropic
    except ImportError:
        print("❌ Error: anthropic package not installed")
        print("   Run: pip install anthropic")
        sys.exit(1)
    
    # Build codebase context and prepare prompt
    codebase_context = build_codebase_context(code_files)
    system_prompt = load_system_prompt()
    detailed_content = _prepare_code_content(code_files)
    test_scenarios = load_test_scenarios(service_path, scenarios_path)
    
    # Start progress indicator
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=show_progress, args=(stop_event,))
    progress_thread.daemon = True
    progress_thread.start()
    
    try:
        prompt = _build_analysis_prompt(system_prompt, codebase_context, detailed_content, config, test_scenarios)
        
        client = anthropic.Anthropic(api_key=config['api_key'])
        response = client.messages.create(
            model=config['model'],
            max_tokens=config['max_tokens'],
            temperature=config['temperature'],
            timeout=config['timeout'],
            messages=[{"role": "user", "content": prompt}]
        )
        
        stop_event.set()
        progress_thread.join(timeout=1)
        
        print("\n   ✓ Received response from Claude\n")
        return _parse_ai_response(response.content[0].text, code_files, config)
        
    except Exception as e:
        stop_event.set()
        progress_thread.join(timeout=1)
        print(f"\n❌ Error: {e}")
        sys.exit(1)

def _analyze_with_openai(service_path, code_files, config, scenarios_path=None):
    """Analyze with OpenAI-compatible API (Perplexity, Ollama, vLLM, LocalAI, etc.)."""
    try:
        import openai
    except ImportError:
        print("❌ Error: openai package not installed")
        print("   Run: pip install openai")
        sys.exit(1)
    
    # Build codebase context and prepare prompt
    codebase_context = build_codebase_context(code_files)
    system_prompt = load_system_prompt()
    detailed_content = _prepare_code_content(code_files)
    test_scenarios = load_test_scenarios(service_path, scenarios_path)
    
    # Start progress indicator
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=show_progress, args=(stop_event,))
    progress_thread.daemon = True
    progress_thread.start()
    
    try:
        prompt = _build_analysis_prompt(system_prompt, codebase_context, detailed_content, config, test_scenarios)
        
        client = openai.OpenAI(api_key=config['api_key'], base_url=config['api_url'])
        response = client.chat.completions.create(
            model=config['model'],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=config['max_tokens'],
            temperature=config['temperature'],
            timeout=config['timeout']
        )
        
        stop_event.set()
        progress_thread.join(timeout=1)
        
        print("\n   ✓ Received response from OpenAI-compatible API\n")
        return _parse_ai_response(response.choices[0].message.content, code_files, config)
        
    except Exception as e:
        stop_event.set()
        progress_thread.join(timeout=1)
        print(f"\n❌ Error: {e}")
        sys.exit(1)

def _prepare_code_content(code_files):
    """Prepare code content for analysis."""
    priority_files = []
    other_files = []
    
    for file_info in code_files:
        if any(keyword in file_info['path'].lower() for keyword in PRIORITY_KEYWORDS):
            priority_files.append(file_info)
        else:
            other_files.append(file_info)
    
    priority_files.sort(key=lambda x: x['path'])
    other_files.sort(key=lambda x: x['path'])
    
    print("📦 Preparing full codebase for analysis...")
    
    detailed_content = "COMPLETE CODEBASE - ALL FILES WITH FULL CONTENT:\n" + "="*70 + "\n\n"
    detailed_content += f"PRIORITY FILES ({len(priority_files)} files):\n" + "-"*70 + "\n\n"
    for f in priority_files:
        detailed_content += f"FILE: {f['path']}\n{'-'*70}\n{f['content']}\n\n"
    
    detailed_content += f"\n\nOTHER FILES ({len(other_files)} files):\n" + "-"*70 + "\n\n"
    for f in other_files:
        detailed_content += f"FILE: {f['path']}\n{'-'*70}\n{f['content']}\n\n"
    
    total_chars = len(detailed_content)
    estimated_tokens = total_chars // 4
    print(f"   📊 Total content: {total_chars:,} characters (~{estimated_tokens:,} tokens)")
    print(f"   📁 Priority files: {len(priority_files)} (full content)")
    print(f"   📁 Other files: {len(other_files)} (full content)")
    
    if estimated_tokens > 180000:
        print(f"   ⚠️  Warning: Content size ({estimated_tokens:,} tokens) is large")
    
    return detailed_content

def _build_analysis_prompt(system_prompt, codebase_context, detailed_content, config, test_scenarios=None):
    """Build analysis prompt for AI."""
    context_summary = {
        'total_files': codebase_context['total_files'],
        'packages': codebase_context['packages'],
        'key_files': codebase_context['key_files']
    }
    
    # Build test scenarios section if provided
    scenarios_section = ""
    if test_scenarios:
        scenarios_section = f"""

TEST SCENARIOS FOR VALIDATION:
The service includes test-scenarios.yml with business requirements to validate.
You MUST validate ONLY the "scenarios:" list in Category 6 (Functional Compliance).

{test_scenarios}

CRITICAL: Focus ONLY on the "scenarios:" section, NOT "global_validations"!

For each scenario in the "scenarios:" list, you MUST:
1. Create an "items" entry with:
   - title: The exact scenario text from test-scenarios.yml
   - assessment: "compliant" / "critical" / "warning" / "info"
   - description: Brief validation result
2. Search the codebase for relevant implementation
3. Provide FILE PATHS and LINE NUMBERS as evidence
4. Quote actual CODE SNIPPETS in the issues array
5. Mark as ✅ PASS (compliant) / ❌ FAIL (critical) / ⚠️ PARTIAL (warning) / ❓ CANNOT_VERIFY (info)

Example structure:
"items": [
  {{
    "title": "if the customer does not exist, a new customer is created",
    "assessment": "compliant",
    "description": "Verified: CustomerService.createCustomer() creates new customer when not found"
  }}
],
"issues": [
  {{
    "severity": "info",
    "title": "Scenario: if the customer does not exist, a new customer is created",
    "description": "Implementation found and verified",
    "file_path": "CustomerServiceImpl.java",
    "line_number": 42,
    "code_snippet": "Customer customer = customerMapper.toEntity(request);\\ncustomer.setCreatedAt(LocalDateTime.now());"
  }}
]

NEVER assume behavior without seeing actual code!
"""
    
    return f"""{system_prompt}

CONFIGURATION:
- **CONFIDENCE_THRESHOLD**: {config['confidence_threshold']}%
- You MUST have >{config['confidence_threshold']}% confidence to report ANY issue or metric violation
- If confidence is <={config['confidence_threshold']}%, skip the metric entirely or mark as "✅ Compliant"

CODEBASE OVERVIEW:
Total Files: {context_summary['total_files']}
Packages/Modules: {', '.join(context_summary['packages'])}
Key Files: {', '.join(context_summary['key_files'][:10])}
{scenarios_section}
COMPLETE CODEBASE CONTENT:
{detailed_content}

CRITICAL INSTRUCTIONS:
1. Output ONLY valid JSON (no markdown wrappers)
2. Category Requirements:
   - If test scenarios provided: Include ALL 6 categories (1-5 plus Functional Compliance as category 6)
   - If NO test scenarios: Include ONLY 5 categories (1-5, SKIP Functional Compliance entirely)
3. Keep descriptions concise (under 80 chars)
4. List ALL issues found (no artificial limits)
5. Code snippets max 2 lines each
6. MUST output COMPLETE valid JSON
7. DYNAMICALLY COUNT issues - do not use fixed numbers

STATUS VALUES (use these exact values):
- "excellent": Outstanding code quality
- "good": Solid implementation with minor issues
- "needs-work": Significant improvements needed
- "critical": Major problems requiring immediate attention

GRADE VALUES for final_assessment (use ONE of these):
- "Excellent"
- "Good"
- "Needs Work"
- "Critical"

Begin JSON:"""

def _parse_ai_response(response_text, code_files, config):
    """Parse AI response and extract JSON."""
    # Handle markdown code blocks
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()
    
    # Parse JSON
    analysis_data = json.loads(response_text)
    
    # Update timestamp and add AI configuration metadata
    ist_now = datetime.now(ZoneInfo('Asia/Kolkata'))
    analysis_data['metadata']['generated_at'] = ist_now.strftime('%Y-%m-%d %H:%M:%S IST')
    analysis_data['metadata']['files_scanned'] = len(code_files)
    analysis_data['metadata']['ai_provider'] = config['provider']
    analysis_data['metadata']['ai_model'] = config['model']
    analysis_data['metadata']['confidence_threshold'] = config['confidence_threshold']
    analysis_data['summary']['files_scanned'] = len(code_files)
    
    # Validate and correct counts
    return validate_and_correct_counts(analysis_data)

def validate_json(data, schema_path):
    """Validate JSON output against schema."""
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    try:
        jsonschema.validate(instance=data, schema=schema)
        print("✅ JSON validation passed")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"\n⚠️  JSON Validation Warning:")
        print(f"   Path: {' -> '.join(str(p) for p in e.path) if e.path else 'root'}")
        print(f"   Issue: {e.message[:200]}")  # Truncate long messages
        return False

def render_html(data, template_path, output_path):
    """Render HTML report."""
    print("🎨 Rendering HTML report...")
    
    env = Environment(loader=FileSystemLoader(str(template_path.parent)))
    template = env.get_template(template_path.name)
    html = template.render(**data)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Report saved: {output_path}\n")

def main():
    # Load configuration from config.json
    config = load_config()
    
    # Build configuration from environment variables
    provider = os.environ.get('AI_PROVIDER')
    if not provider:
        print("❌ Error: AI_PROVIDER environment variable is required")
        print("   Set to one of: anthropic, openai")
        print("   Example: export AI_PROVIDER=anthropic")
        sys.exit(1)
    
    model = os.environ.get('AI_MODEL')
    if not model:
        print(f"❌ Error: AI_MODEL environment variable is required")
        print(f"   Example for Anthropic: export AI_MODEL=claude-sonnet-4-5-20250929")
        print(f"   Example for OpenAI: export AI_MODEL=gpt-4")
        print(f"   Example for Perplexity: export AI_MODEL=llama-3.1-sonar-huge-128k-online")
        sys.exit(1)
    
    # Provider-specific defaults for API URLs
    api_url_defaults = {
        'anthropic': 'https://api.anthropic.com',
        'openai': 'https://api.openai.com/v1'
    }
    
    final_config = {
        'provider': provider,
        'model': model,
        'api_url': os.environ.get('AI_API_URL', api_url_defaults.get(provider, '')),
        'api_key': os.environ.get('AI_API_KEY'),
        'max_tokens': config.get('max_tokens', 20000),
        'temperature': config.get('temperature', 0),
        'timeout': config.get('timeout', 180.0),
        'confidence_threshold': int(os.environ.get('AI_CONFIDENCE_THRESHOLD', '0')) or config.get('confidence_threshold', 70),
    }
    
    # Validate required API key
    if not final_config['api_key']:
        print(f"❌ Error: No API key provided")
        print(f"   Set AI_API_KEY environment variable")
        print(f"   Example: export AI_API_KEY='your-key'")
        sys.exit(1)
    
    # Get service path from environment variable
    service_path_str = os.environ.get('SERVICE_PATH')
    if not service_path_str:
        print(f"❌ Error: SERVICE_PATH environment variable is required")
        print(f"   Set SERVICE_PATH to the directory path of the service to analyze")
        print(f"   Example: export SERVICE_PATH=/path/to/service")
        sys.exit(1)
    
    service_path = Path(service_path_str).resolve()
    if not service_path.exists():
        print(f"❌ Service path does not exist: {service_path}")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print("🔍 Code Critique Analysis with Real AI")
    print(f"{'='*70}\n")
    
    script_dir = Path(__file__).parent
    code_critique_dir = script_dir.parent
    
    # Determine service name (prefer env var for Docker compatibility)
    service_name = os.environ.get('SERVICE_NAME') or service_path.name
    
    # Paths
    schema_path = code_critique_dir / 'schemas' / 'code-critique-schema.json'
    template_path = code_critique_dir / 'templates' / 'code-critique-template.html'
    output_dir = code_critique_dir / 'reports' / service_name
    output_html = output_dir / 'code-critique-report.html'
    output_json = output_dir / 'code-critique-data.json'
    
    # Load files
    code_files = load_code_files(service_path)
    if not code_files:
        print("❌ No code files found")
        sys.exit(1)
    
    # Display configuration
    print(f"🤖 Using AI Provider: {final_config['provider'].upper()}")
    print(f"   Model: {final_config['model']}")
    print(f"   API URL: {final_config['api_url']}")
    print(f"   Confidence Threshold: {final_config['confidence_threshold']}%\n")
    
    # Get scenarios path from environment variable
    scenarios_path = os.environ.get('TEST_SCENARIOS_PATH')
    
    # Analyze with AI (route to appropriate provider)
    analysis_data = analyze_with_ai(service_path, code_files, final_config, scenarios_path)
    
    # Save JSON
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump(analysis_data, f, indent=2)
    print(f"📄 JSON saved: {output_json}")
    
    # Validate
    if not validate_json(analysis_data, schema_path):
        print("⚠️  Validation failed but continuing...")
    
    # Render HTML
    render_html(analysis_data, template_path, output_html)
    
    # Summary
    print(f"{'='*70}")
    print("✅ Analysis Complete!")
    print(f"{'='*70}\n")
    print(f"📊 Results:")
    print(f"   Critical Issues: {analysis_data['summary']['critical_count']}")
    print(f"   Warnings: {analysis_data['summary']['warning_count']}")
    print(f"   Files Analyzed: {len(code_files)}")
    
    # Show Functional Compliance stats if available
    functional_compliance = None
    for category in analysis_data.get('categories', []):
        if category.get('name') == 'Functional Compliance':
            functional_compliance = category
            break
    
    if functional_compliance:
        items = functional_compliance.get('items', [])
        pass_count = sum(1 for item in items if item.get('assessment') == 'compliant')
        fail_count = sum(1 for item in items if item.get('assessment') == 'critical')
        partial_count = sum(1 for item in items if item.get('assessment') == 'warning')
        cannot_verify = sum(1 for item in items if item.get('assessment') == 'info')
        
        print(f"\n🧪 Functional Compliance:")
        print(f"   ✅ Pass: {pass_count}")
        print(f"   ❌ Fail: {fail_count}")
        print(f"   ⚠️  Partial: {partial_count}")
        print(f"   ❓ Cannot Verify: {cannot_verify}")
    
    print(f"\n🌐 View Report:")
    print(f"   open {output_html}\n")

if __name__ == '__main__':
    main()
