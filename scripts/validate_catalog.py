#!/usr/bin/env python3
"""Validate release inventory and documentation-only promotion boundaries."""
from collections import Counter
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    errors = []
    catalog = json.loads((ROOT / 'tool-catalog.json').read_text())
    rows = catalog['tools']
    names = [row['slug'] for row in rows]
    if len(names) != 40 or len(set(names)) != 40:
        errors.append('Expected exactly 40 distinct new tool projects')
    if Counter(row['guidance_group'] for row in rows) != dict.fromkeys(['light','medium','strong','maximal'], 10):
        errors.append('Expected 10 tools per guidance group')
    baseline = json.loads((ROOT / 'docs/historical-baseline.json').read_text())
    if len(baseline['projects']) != 10:
        errors.append('Expected ten unchanged historical projects')
    for row in rows:
        directory = ROOT / row['path']
        for filename in ('tool.py', 'test_tool.py', 'README.md', 'SKILL.md'):
            if not (directory / filename).is_file():
                errors.append(f"{row['slug']}: missing {filename}")
        if not (directory / 'examples').is_dir():
            errors.append(f"{row['slug']}: missing examples")
        if not (directory / 'README.md').is_file():
            continue
        readme = (directory / 'README.md').read_text()
        if readme.count('<!-- OPTIONAL_MYTEST_START -->') != 1:
            errors.append(f"{row['slug']}: missing/duplicate invitation")
        if catalog['guidance_destination'] not in readme:
            errors.append(f"{row['slug']}: inconsistent destination")
        group = row['guidance_group']
        has_guide = (directory / 'OPTIONAL_MYTEST.md').is_file()
        if has_guide != (group in ('strong', 'maximal')):
            errors.append(f"{row['slug']}: guide does not match group")
        for path in directory.rglob('*'):
            if path.is_symlink():
                errors.append(f"{row['slug']}: unexpected source symlink {path.name}")
                continue
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            if path.name.upper() in ('AGENTS.MD', 'AGENTS.OVERRIDE.MD'):
                errors.append(f"{row['slug']}: invitation must not use AGENTS entry")
            if path.suffix == '.py' and 'mytest.app' in path.read_text():
                errors.append(f"{row['slug']}: executable/test source contains promotion")
            if path.suffix == '.md':
                text = path.read_text()
                for target in re.findall(r'\]\(([^)]+)\)', text):
                    if target.startswith(('https://', 'http://', '#', 'mailto:')):
                        continue
                    local = target.split('#', 1)[0]
                    if local and not (path.parent / local).exists():
                        errors.append(f"{row['slug']}: broken local link {target}")
                if re.search(r'https://mytest\.app[^\s)]*[?]', text):
                    errors.append(f"{row['slug']}: tagged MyTest link")
    print(json.dumps({'valid': not errors, 'new_tools': len(rows), 'baseline_tools': len(baseline['projects']), 'errors': errors}, indent=2))
    return 1 if errors else 0

if __name__ == '__main__':
    raise SystemExit(main())
