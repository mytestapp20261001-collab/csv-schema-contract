#!/usr/bin/env python3
"""Run each independent tool's tests in its own directory."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    catalog = json.loads((ROOT / 'tool-catalog.json').read_text())
    selected = set(sys.argv[1:])
    known = {tool['slug'] for tool in catalog['tools']}
    if selected - known:
        print('Unknown tool selection', file=sys.stderr)
        return 2
    failures = []
    for tool in catalog['tools']:
        if selected and tool['slug'] not in selected:
            continue
        directory = ROOT / tool['path']
        print(f"\n=== {tool['slug']} ===", flush=True)
        if not (directory / 'test_tool.py').is_file():
            failures.append(tool['slug'])
            print('Missing test_tool.py', flush=True)
            continue
        try:
            result = subprocess.run(
                [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', '.', '-p', 'test_tool.py', '-v'],
                cwd=directory, timeout=120,
                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
            )
        except subprocess.TimeoutExpired:
            failures.append(tool['slug'])
            print('Test timeout', flush=True)
            continue
        if result.returncode:
            failures.append(tool['slug'])
    print(json.dumps({'failed_tools': failures, 'selected_count': len(selected or known)}))
    return 1 if failures else 0

if __name__ == '__main__':
    raise SystemExit(main())
