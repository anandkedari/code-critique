#!/usr/bin/env python3
"""Test script to verify template rendering works with the sorting fix."""

import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Load the JSON data
data_path = Path(__file__).parent.parent / "reports" / "Calculator-master" / "code-critique-data.json"
with open(data_path, 'r') as f:
    data = json.load(f)

# Set up Jinja2 environment
template_dir = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(template_dir)))
template = env.get_template('code-critique-template.html')

# Try to render the template
try:
    html = template.render(**data)
    print("✅ Template rendered successfully!")
    print(f"   Generated HTML length: {len(html)} characters")
    
    # Save to a test file
    output_path = Path(__file__).parent.parent / "reports" / "Calculator-master" / "test-report.html"
    with open(output_path, 'w') as f:
        f.write(html)
    print(f"✅ Test report saved to: {output_path}")
    
except Exception as e:
    print(f"❌ Template rendering failed: {e}")
    import traceback
    traceback.print_exc()
