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
    return code_files

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

def analyze_with_claude(service_path, code_files, api_key):
    """Analyze code using Anthropic Claude AI."""
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
    
    # Prepare code content (limit to avoid token limits)
    max_files = 20
    files_to_analyze = code_files[:max_files]
    
    code_content = "\n\n" + "="*70 + "\n\n".join([
        f"FILE: {f['path']}\n{'-'*70}\n{f['content']}" 
        for f in files_to_analyze
    ])
    
    if len(code_files) > max_files:
        print(f"   ⚠️  Analyzing first {max_files} files (token limit)\n")
    
    # Load prompts
    system_prompt = load_system_prompt()
    guidelines = load_guidelines()
    
    # Call Claude API
    client = anthropic.Anthropic(api_key=api_key)
    
    print("   🚀 Sending to Claude API...\n")
    
    # Start progress indicator in background thread
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=show_progress, args=(stop_event,))
    progress_thread.daemon = True
    progress_thread.start()
    
    try:
        # Reduce input, maximize output tokens
        prompt = f"""{system_prompt}

CODE TO ANALYZE:
{code_content[:15000]}

CRITICAL INSTRUCTIONS:
1. Output ONLY valid JSON (no markdown wrappers)
2. Include ALL 8 categories with full metrics
3. Keep descriptions concise (under 80 chars)
4. List ALL issues found (no artificial limits)
5. Code snippets max 2 lines each
6. MUST output COMPLETE valid JSON

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
        
        # Ensure files_scanned is accurate
        analysis_data['metadata']['files_scanned'] = len(code_files)
        analysis_data['summary']['files_scanned'] = len(code_files)
        
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
