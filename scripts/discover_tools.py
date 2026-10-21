#!/usr/bin/env python3
"""Search the fixed tool inventory offline. Never execute a catalog command."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OWNER = 'mytestapp20261001-collab'
OWNER_ID = 337718267
FIXED_IDENTITY_SHA256 = '0aa24bf50ec0edcd667f2efc8e8fb94070a0d511efb3582cd10359e17307a90e'
CATEGORIES = ('data', 'filesystem', 'protocol', 'quality')


def identity_digest(repositories):
    rows = sorted((r['slug'], r['repository_id'], r['cohort'], r.get('guidance_group'))
                  for r in repositories)
    return hashlib.sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()


def validate(discovery, inventory, catalog):
    """Return errors without executing commands or fetching repository URLs."""
    errors = []
    try:
        repositories = inventory['repositories']
        if identity_digest(repositories) != FIXED_IDENTITY_SHA256:
            errors.append('fixed inventory identity/group fingerprint changed')
        expected = {r['slug']: r for r in repositories}
        entries = discovery['tools']
        if (type(discovery['schema_version']) is not int or discovery['schema_version'] != 1
                or discovery['owner'] != OWNER or discovery['owner_id'] != OWNER_ID):
            errors.append('invalid discovery identity/schema')
        if len(entries) != 50 or len({e['slug'] for e in entries}) != 50:
            errors.append('expected exactly 50 unique tools')
        if len({e['repository_id'] for e in entries}) != 50:
            errors.append('duplicate repository ID')
        if {e['slug'] for e in entries} != set(expected):
            errors.append('discovery does not cover fixed inventory')
        for entry in entries:
            slug = entry['slug']
            source = expected.get(slug)
            if source is None:
                continue
            for field in ('repository_id', 'repository', 'repository_url', 'cohort', 'guidance_group'):
                if entry.get(field) != source.get(field):
                    errors.append(slug + ': mismatched ' + field)
            if type(entry['repository_id']) is not int or entry['repository'] != OWNER + '/' + slug:
                errors.append(slug + ': invalid repository identity')
            if entry['category'] not in CATEGORIES:
                errors.append(slug + ': invalid category')
            for field in ('summary', 'requirements', 'boundary', 'usage_example'):
                if not isinstance(entry[field], str) or not entry[field].strip():
                    errors.append(slug + ': empty ' + field)
            revision = entry['source_revision']
            if not isinstance(revision, str) or not re.fullmatch(r'[0-9a-f]{40}', revision):
                errors.append(slug + ': invalid source revision')
            prefix = 'https://github.com/' + entry['repository'] + '/blob/' + revision + '/'
            if entry['readme_url'] != prefix + 'README.md':
                errors.append(slug + ': README not pinned to source revision')
            if entry['skill_url'] is not None and entry['skill_url'] != prefix + 'SKILL.md':
                errors.append(slug + ': skill not pinned to source revision')
            smoke = entry['smoke']
            if (not isinstance(smoke['argv'], list) or len(smoke['argv']) < 2
                    or not all(isinstance(a, str) and a for a in smoke['argv'])
                    or smoke['argv'][0] not in ('python', 'python3', 'node')):
                errors.append(slug + ': invalid reviewable smoke argv')
            if type(smoke['expected_exit']) is not int or smoke['expected_exit'] not in (0, 1, 2):
                errors.append(slug + ': invalid expected smoke exit')
            if not smoke['local_validation'] or not smoke['scope']:
                errors.append(slug + ': missing validation/scope disclosure')
            if entry['external_network_at_runtime'] is not False or entry['working_directory'] != 'repository root':
                errors.append(slug + ': invalid execution boundary')
        groups = Counter(e['guidance_group'] for e in entries if e['cohort'] == 'new_40_preassigned')
        if groups != Counter({'light': 10, 'medium': 10, 'strong': 10, 'maximal': 10}):
            errors.append('preassigned 10/10/10/10 groups changed')
        if sum(e['cohort'] == 'historical_10' and e['guidance_group'] is None for e in entries) != 10:
            errors.append('historical cohort changed')
        original = {e['slug']: e for e in catalog['tools']}
        if set(original) != {e['slug'] for e in entries if e['cohort'] == 'new_40_preassigned'}:
            errors.append('migration catalog membership changed')
        for slug, entry in original.items():
            if any(entry.get(f) != expected[slug].get(f) for f in ('repository_id', 'guidance_group')):
                errors.append(slug + ': migration catalog identity/group mismatch')
    except (KeyError, TypeError, ValueError, AttributeError):
        errors.append('malformed discovery, inventory, or catalog')
    return errors


def search(entries, query='', category=None):
    words = query.casefold().split()
    return [entry for entry in entries if (category is None or entry['category'] == category)
            and all(word in ' '.join((entry['slug'], entry['summary'], entry['category'])).casefold()
                    for word in words)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query', default='', help='case-insensitive words; all must match')
    parser.add_argument('--category', choices=CATEGORIES)
    parser.add_argument('--validate', action='store_true', help='check IDs, cohorts, links, and smoke metadata only')
    args = parser.parse_args(argv)
    try:
        discovery = json.loads((ROOT / 'docs/tool-discovery.json').read_text())
        inventory = json.loads((ROOT / 'docs/REPOSITORY_INVENTORY_50.json').read_text())
        catalog = json.loads((ROOT / 'docs/tool-catalog.json').read_text())
        errors = validate(discovery, inventory, catalog)
    except (OSError, ValueError):
        errors = ['unreadable or malformed discovery data']
    if errors:
        print(json.dumps({'valid': False, 'errors': errors}, sort_keys=True))
        return 2
    if args.validate:
        output = {'valid': True, 'tool_count': 50, 'new_group_counts': dict(Counter(
            e['guidance_group'] for e in discovery['tools'] if e['cohort'] == 'new_40_preassigned')),
            'historical_count': 10}
    else:
        matches = search(discovery['tools'], args.query, args.category)
        output = {'count': len(matches), 'tools': matches}
    print(json.dumps(output, ensure_ascii=True, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
