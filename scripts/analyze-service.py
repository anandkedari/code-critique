#!/usr/bin/env python3
"""
Code Critique Report Generator with Real AI Analysis

This script analyzes code using Anthropic Claude AI and generates standardized reports.

Usage:
    python3 analyze-service.py <service-path> [--api-key YOUR_KEY]

Example:
    python3 analyze-service.py ../../customer-service
    python3 analyze-service.py ../../customer-service --api-key sk-ant-...

Environment Variable:
    export ANTHROPIC_API_KEY="your-key-here"
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
    
    include_patterns = ['**/*.java', '**/*.py', '**/*.js', '**/*.ts', '**/*.go', '**/*.json', '**/*.yaml', '**/*.xml', '**/*.properties', '**/*.config']
    exclude_dirs = ['build', 'target', 'node_modules', '.git', 'venv', 'dist', 'gradle']
    
    for pattern in include_patterns:
        for file_path in service_path.glob(pattern):
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            path_str = str(file_path).lower()
            if 'test' in path_str and ('src/test' in path_str or 'test.java' in path_str):
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

def load_guidelines():
    """Load code critique guidelines."""
    script_dir = Path(__file__).parent
    guidelines_file = script_dir.parent / 'code_critique.md'
    with open(guidelines_file, 'r') as f:
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

def analyze_with_claude(service_path, code_files, api_key):
    """Analyze code using Anthropic Claude AI with full codebase context."""
    try:
        import anthropic
    except ImportError:
        print("❌ Error: anthropic package not installed")
        print("   Run: pip install anthropic")
        sys.exit(1)
    
    print("🤖 Analyzing code with Anthropic Claude AI...")
    print(f"   Service: {Path(service_path).name}")
    print(f"   Files: {len(code_files)}")
    print(f"   Total size: {sum(f['size'] for f in code_files):,} bytes\n")
    
    # Phase 1: Build full codebase context
    codebase_context = build_codebase_context(code_files)
    
    # Phase 2: Analyze in batches with context
    batch_size = 15  # Analyze 15 files per batch
    total_batches = (len(code_files) + batch_size - 1) // batch_size
    
    print(f"📊 Analysis Plan:")
    print(f"   Batch size: {batch_size} files")
    print(f"   Total batches: {total_batches}")
    print(f"   Strategy: Full context analysis\n")
    
    # Load configuration and prompts
    config = load_config()
    confidence_threshold = config.get('confidence_threshold', 70)
    system_prompt = load_system_prompt()
    guidelines = load_guidelines()
    
    print(f"   📊 Confidence Threshold: {confidence_threshold}%")
    print(f"   (AI will only report issues/metrics with >{confidence_threshold}% confidence)\n")
    
    # Call Claude API
    client = anthropic.Anthropic(api_key=api_key)
    
    print("   🚀 Sending to Claude API...\n")
    
    # Prepare context summary (lightweight)
    context_summary = {
        'total_files': codebase_context['total_files'],
        'packages': codebase_context['packages'],
        'key_files': codebase_context['key_files'],
        'file_list': [s['file'] for s in codebase_context['file_structures']]
    }
    
    # Prepare detailed code content
    # Include structure of ALL files + full content of priority files
    priority_files = []
    other_files = []
    
    for file_info in code_files:
        if any(keyword in file_info['path'].lower() for keyword in 
               ['controller', 'service', 'repository', 'config', 'application', 'main', 'entity', 'model']):
            priority_files.append(file_info)
        else:
            other_files.append(file_info)
    
    # Sort both lists to ensure deterministic order
    priority_files.sort(key=lambda x: x['path'])
    other_files.sort(key=lambda x: x['path'])
    
    # Build detailed content string
    detailed_content = "PRIORITY FILES (Full Content):\n" + "="*70 + "\n\n"
    for f in priority_files[:15]:  # Top 15 priority files
        detailed_content += f"FILE: {f['path']}\n{'-'*70}\n{f['content'][:3000]}\n\n"
    
    detailed_content += "\n\nOTHER FILES (Structure Only):\n" + "="*70 + "\n\n"
    for f in other_files[:30]:  # Structure of 30 more files
        structure = extract_file_structure(f['path'], f['content'])
        detailed_content += f"FILE: {f['path']}\n"
        if structure['imports']:
            detailed_content += f"  Imports: {', '.join(structure['imports'][:5])}\n"
        if structure['classes']:
            detailed_content += f"  Classes: {', '.join(structure['classes'][:3])}\n"
        if structure['methods']:
            detailed_content += f"  Methods: {', '.join(structure['methods'][:5])}\n"
        detailed_content += "\n"
    
    # Start progress indicator in background thread
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=show_progress, args=(stop_event,))
    progress_thread.daemon = True
    progress_thread.start()
    
    try:
        # Construct comprehensive prompt with context and config
        prompt = f"""{system_prompt}

CONFIGURATION:
- **CONFIDENCE_THRESHOLD**: {confidence_threshold}%
- You MUST have >{confidence_threshold}% confidence to report ANY issue or metric violation
- If confidence is <={confidence_threshold}%, skip the metric entirely or mark as "✅ Compliant"

CODEBASE OVERVIEW:
Total Files: {context_summary['total_files']}
Packages/Modules: {', '.join(context_summary['packages'])}
Key Files: {', '.join(context_summary['key_files'][:10])}

DETAILED CODE ANALYSIS:
{detailed_content[:50000]}

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

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=20000,  # Maximum for complete response
            temperature=0,
            timeout=180.0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Stop progress indicator
        stop_event.set()
        progress_thread.join(timeout=1)
        
        print("\n   ✓ Received response from Claude\n")
        
        # Extract JSON from response
        json_text = response.content[0].text
        
        # Handle markdown code blocks
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        analysis_data = json.loads(json_text)
        
        # Update timestamp to current time in IST
        ist_now = datetime.now(ZoneInfo('Asia/Kolkata'))
        analysis_data['metadata']['generated_at'] = ist_now.strftime('%Y-%m-%d %H:%M:%S IST')
        
        # Ensure files_scanned is accurate
        analysis_data['metadata']['files_scanned'] = len(code_files)
        analysis_data['summary']['files_scanned'] = len(code_files)
        
        # CRITICAL: Validate and correct counts
        analysis_data = validate_and_correct_counts(analysis_data)
        
        return analysis_data
        
    except anthropic.APIError as e:
        stop_event.set()
        progress_thread.join(timeout=1)
        print(f"\n❌ API Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        stop_event.set()
        progress_thread.join(timeout=1)
        print(f"\n❌ JSON Parse Error: {e}")
        print("Response was:")
        print(json_text[:500])
        sys.exit(1)
    finally:
        # Ensure progress indicator is stopped
        stop_event.set()

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
    parser = argparse.ArgumentParser(description='Code Critique Analysis with AI')
    parser.add_argument('service_path', help='Path to service directory')
    parser.add_argument('--api-key', help='Anthropic API key (or set ANTHROPIC_API_KEY env var)')
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: No API key provided")
        print("   Option 1: export ANTHROPIC_API_KEY='your-key'")
        print("   Option 2: python3 analyze-service.py <path> --api-key sk-ant-...")
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
    
    # Analyze with AI
    analysis_data = analyze_with_claude(service_path, code_files, api_key)
    
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
