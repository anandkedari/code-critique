#!/usr/bin/env python3
"""
Code Critique Report Generator with Multi-Provider AI Support

Analyzes code using AI (Claude, Ollama, Perplexity) and generates standardized reports.

Usage:
    python3 analyze-service.py <service-path> [OPTIONS]

Examples:
    # Use default provider (Claude)
    python3 analyze-service.py ../../customer-service
    
    # Use Ollama with Qwen3-Coder
    python3 analyze-service.py ../../customer-service --provider ollama
    
    # Full customization
    python3 analyze-service.py ../../customer-service --provider ollama --model qwen2.5-coder:14b

Environment Variables:
    AI_PROVIDER, AI_MODEL, AI_API_URL, AI_API_KEY
    ANTHROPIC_API_KEY, PERPLEXITY_API_KEY
"""

import sys
import os
import json
import argparse
import time
import threading
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from jinja2 import Environment, FileSystemLoader
import jsonschema

def load_code_files(service_path):
    """Load all relevant source code files from the service."""
    service_path = Path(service_path)
    code_files = []
    
    print(f"📁 Loading code files from: {service_path.name}")
    
    include_patterns = ['**/*.java', '**/*.py', '**/*.js', '**/*.ts', '**/*.go']
    exclude_dirs = ['build', 'target', 'node_modules', '.git', 'venv', 'dist', 'gradle']
    
    for pattern in include_patterns:
        for file_path in service_path.glob(pattern):
            if any(excluded in file_path.parts for excluded in exclude_dirs):
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

def show_progress(stop_event):
    """Show animated progress indicator."""
    categories = [
        "🏗️  Architecture & Design",
        "🔒 Security", 
        "✨ Code Quality",
        "⚡ Performance",
        "🛡️  Error Handling",
        "📝 Logging",
        "🔍 Self-Critique",
        "🎯 Domain-Specific"
    ]
    
    idx = 0
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    spin_idx = 0
    
    while not stop_event.is_set():
        category = categories[idx % len(categories)]
        print(f"\r   {spinner[spin_idx]} Analyzing: {category}   ", end='', flush=True)
        spin_idx = (spin_idx + 1) % len(spinner)
        time.sleep(0.1)
        
        # Change category every 10 iterations (1 second)
        if spin_idx == 0:
            idx += 1
    
    print("\r   ✓ Analysis complete!                                ", flush=True)

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
        if any(keyword in file_info['path'].lower() for keyword in 
               ['controller', 'service', 'repository', 'config', 'application', 'main']):
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
    actual_critical = 0
    actual_warning = 0
    actual_info = 0
    actual_compliant = 0
    
    for category in data.get('categories', []):
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
    
    # Validate category count
    expected_categories = 9
    actual_categories = len(data.get('categories', []))
    if actual_categories != expected_categories:
        print(f"   ⚠️  Category count: Expected {expected_categories}, got {actual_categories}")
    
    return data

def analyze_with_ai(service_path, code_files, config):
    """Route to appropriate AI provider based on configuration."""
    provider = config['provider']
    
    if provider == 'claude':
        return _analyze_with_claude(service_path, code_files, config)
    elif provider == 'ollama':
        return _analyze_with_ollama(service_path, code_files, config)
    elif provider == 'perplexity':
        return _analyze_with_perplexity(service_path, code_files, config)
    else:
        print(f"❌ Unknown provider: {provider}")
        print("   Supported providers: claude, ollama, perplexity")
        sys.exit(1)

def _analyze_with_claude(service_path, code_files, config):
    """Analyze with Claude (Anthropic)."""
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
    
    # Start progress indicator
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=show_progress, args=(stop_event,))
    progress_thread.daemon = True
    progress_thread.start()
    
    try:
        prompt = _build_analysis_prompt(system_prompt, codebase_context, detailed_content, config)
        
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
        return _parse_ai_response(response.content[0].text, code_files)
        
    except Exception as e:
        stop_event.set()
        progress_thread.join(timeout=1)
        print(f"\n❌ Error: {e}")
        sys.exit(1)

def _analyze_with_ollama(service_path, code_files, config):
    """Analyze with Ollama (local models like Qwen3-Coder)."""
    try:
        import requests
    except ImportError:
        print("❌ Error: requests package not installed")
        print("   Run: pip install requests")
        sys.exit(1)
    
    # Build codebase context and prepare prompt
    codebase_context = build_codebase_context(code_files)
    system_prompt = load_system_prompt()
    detailed_content = _prepare_code_content(code_files)
    
    # Start progress indicator
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=show_progress, args=(stop_event,))
    progress_thread.daemon = True
    progress_thread.start()
    
    try:
        prompt = _build_analysis_prompt(system_prompt, codebase_context, detailed_content, config)
        
        # Ollama API call
        response = requests.post(
            f"{config['api_url']}/api/generate",
            json={
                "model": config['model'],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": config['temperature'],
                    "num_predict": config['max_tokens']
                }
            },
            timeout=config['timeout']
        )
        response.raise_for_status()
        
        stop_event.set()
        progress_thread.join(timeout=1)
        
        print("\n   ✓ Received response from Ollama\n")
        return _parse_ai_response(response.json()['response'], code_files)
        
    except Exception as e:
        stop_event.set()
        progress_thread.join(timeout=1)
        print(f"\n❌ Error: {e}")
        sys.exit(1)

def _analyze_with_perplexity(service_path, code_files, config):
    """Analyze with Perplexity (OpenAI-compatible API)."""
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
    
    # Start progress indicator
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=show_progress, args=(stop_event,))
    progress_thread.daemon = True
    progress_thread.start()
    
    try:
        prompt = _build_analysis_prompt(system_prompt, codebase_context, detailed_content, config)
        
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
        
        print("\n   ✓ Received response from Perplexity\n")
        return _parse_ai_response(response.choices[0].message.content, code_files)
        
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
        if any(keyword in file_info['path'].lower() for keyword in 
               ['controller', 'service', 'repository', 'config', 'application', 'main', 'entity', 'model']):
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

def _build_analysis_prompt(system_prompt, codebase_context, detailed_content, config):
    """Build analysis prompt for AI."""
    context_summary = {
        'total_files': codebase_context['total_files'],
        'packages': codebase_context['packages'],
        'key_files': codebase_context['key_files']
    }
    
    return f"""{system_prompt}

CONFIGURATION:
- **CONFIDENCE_THRESHOLD**: {config['confidence_threshold']}%
- You MUST have >{config['confidence_threshold']}% confidence to report ANY issue or metric violation
- If confidence is <={config['confidence_threshold']}%, skip the metric entirely or mark as "✅ Compliant"

CODEBASE OVERVIEW:
Total Files: {context_summary['total_files']}
Packages/Modules: {', '.join(context_summary['packages'])}
Key Files: {', '.join(context_summary['key_files'][:10])}

COMPLETE CODEBASE CONTENT:
{detailed_content}

CRITICAL INSTRUCTIONS:
1. Output ONLY valid JSON (no markdown wrappers)
2. Include ALL 9 categories with full metrics (including LLM as a Judge)
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

def _parse_ai_response(response_text, code_files):
    """Parse AI response and extract JSON."""
    # Handle markdown code blocks
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()
    
    # Parse JSON
    analysis_data = json.loads(response_text)
    
    # Update timestamp
    ist_now = datetime.now(ZoneInfo('Asia/Kolkata'))
    analysis_data['metadata']['generated_at'] = ist_now.strftime('%Y-%m-%d %H:%M:%S IST')
    analysis_data['metadata']['files_scanned'] = len(code_files)
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
        print(f"❌ Validation failed: {e.message}")
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
    parser = argparse.ArgumentParser(
        description='Code Critique Analysis with AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Use default provider from config.json
  python3 analyze-service.py customer-service
  
  # Specify provider
  python3 analyze-service.py customer-service --provider ollama
  
  # Full customization
  python3 analyze-service.py customer-service --provider ollama --model qwen2.5-coder:14b --api-url http://localhost:11434
  
  # Using environment variables
  export AI_PROVIDER=ollama
  export AI_MODEL=qwen2.5-coder:32b-instruct
  python3 analyze-service.py customer-service
        '''
    )
    
    # Required arguments
    parser.add_argument('service_path', help='Path to service directory')
    
    # Provider selection
    parser.add_argument('--provider', help='AI provider (claude|perplexity|ollama)')
    parser.add_argument('--model', help='Model name/ID')
    parser.add_argument('--api-url', help='API endpoint URL')
    parser.add_argument('--api-key', help='API authentication key')
    
    # Model parameters
    parser.add_argument('--max-tokens', type=int, help='Maximum response tokens')
    parser.add_argument('--temperature', type=float, help='Sampling temperature (0-1)')
    parser.add_argument('--timeout', type=float, help='API timeout in seconds')
    
    # Analysis settings
    parser.add_argument('--confidence', type=int, help='Confidence threshold (0-100)')
    
    args = parser.parse_args()
    
    # Load base configuration
    config = load_config()
    
    # Resolve provider configuration (CLI > ENV > config.json)
    provider = args.provider or os.environ.get('AI_PROVIDER') or config.get('ai_provider', 'claude')
    
    # Get provider-specific config from config.json
    provider_configs = config.get('providers', {})
    provider_config = provider_configs.get(provider, {})
    
    # Merge configuration with priority: CLI > ENV > config.json
    final_config = {
        'provider': provider,
        'model': args.model or os.environ.get('AI_MODEL') or provider_config.get('model'),
        'api_url': args.api_url or os.environ.get('AI_API_URL') or provider_config.get('api_url'),
        'max_tokens': args.max_tokens or int(os.environ.get('AI_MAX_TOKENS', 0)) or provider_config.get('max_tokens', 20000),
        'temperature': args.temperature if args.temperature is not None else float(os.environ.get('AI_TEMPERATURE', -1)) if os.environ.get('AI_TEMPERATURE') else provider_config.get('temperature', 0),
        'timeout': args.timeout or float(os.environ.get('AI_TIMEOUT', 0)) or provider_config.get('timeout', 180.0),
        'confidence_threshold': args.confidence or int(os.environ.get('AI_CONFIDENCE_THRESHOLD', 0)) or config.get('confidence_threshold', 70),
    }
    
    # Get API key
    api_key_env = provider_config.get('api_key_env')
    final_config['api_key'] = args.api_key or os.environ.get('AI_API_KEY') or (os.environ.get(api_key_env) if api_key_env else None)
    
    # Validate required API key for cloud providers
    if provider in ['claude', 'perplexity'] and not final_config['api_key']:
        print(f"❌ Error: No API key provided for {provider}")
        print(f"   Option 1: export {api_key_env}='your-key'")
        print(f"   Option 2: export AI_API_KEY='your-key'")
        print(f"   Option 3: --api-key your-key")
        sys.exit(1)
    
    service_path = Path(args.service_path).resolve()
    if not service_path.exists():
        print(f"❌ Service path does not exist: {service_path}")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print("🔍 Code Critique Analysis with Real AI")
    print(f"{'='*70}\n")
    
    script_dir = Path(__file__).parent
    code_critique_dir = script_dir.parent
    
    # Paths
    schema_path = code_critique_dir / 'schemas' / 'code-critique-schema.json'
    template_path = code_critique_dir / 'templates' / 'code-critique-template.html'
    output_dir = code_critique_dir / 'reports' / service_path.name
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
    
    # Analyze with AI (route to appropriate provider)
    analysis_data = analyze_with_ai(service_path, code_files, final_config)
    
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
    print(f"\n🌐 View Report:")
    print(f"   open {output_html}\n")

if __name__ == '__main__':
    main()
