import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

import discover_tools as discovery

ROOT = Path(__file__).resolve().parents[1]

class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'docs/tool-discovery.json').read_text())
        self.inventory = json.loads((ROOT / 'docs/REPOSITORY_INVENTORY_50.json').read_text())
        self.catalog = json.loads((ROOT / 'docs/tool-catalog.json').read_text())
    def check(self, data=None):
        return discovery.validate(self.data if data is None else data, self.inventory, self.catalog)
    def test_exact_fixed_coverage(self):
        self.assertEqual(self.check(), [])
    def test_boolean_schema_version_is_rejected(self):
        self.data['schema_version'] = True
        self.assertTrue(self.check())

    def test_missing_duplicate_and_extra_tools_rejected(self):
        for entries in (self.data['tools'][:-1], self.data['tools']+[self.data['tools'][0]],
                        [self.data['tools'][0]]*50):
            data=copy.deepcopy(self.data);data['tools']=entries
            self.assertTrue(self.check(data))
    def test_identity_group_link_and_command_mutations_rejected(self):
        changes=[('repository_id',0),('repository','other/repo'),('guidance_group','maximal'),
                 ('source_revision','main'),('readme_url','https://example.test/'),('summary',''),
                 ('requirements',''),('skill_url','https://example.test/'),('category','unknown'),
                 ('external_network_at_runtime',True)]
        for field,value in changes:
            with self.subTest(field=field):
                data=copy.deepcopy(self.data);data['tools'][0][field]=value
                self.assertTrue(self.check(data))
        for key,value in [('argv',[]),('argv',['sh','-c','unsafe']),('expected_exit',True),('local_validation','')]:
            data=copy.deepcopy(self.data);data['tools'][0]['smoke'][key]=value
            self.assertTrue(self.check(data))
    def test_both_inventories_cannot_silently_change_fixed_identity(self):
        self.inventory['repositories'][0]['repository_id']=123
        self.data['tools'][0]['repository_id']=123
        self.catalog['tools'][0]['repository_id']=123
        self.assertIn('fixed inventory identity/group fingerprint changed',self.check())
    def test_search_is_case_insensitive_and_supports_category(self):
        self.assertEqual([e['slug'] for e in discovery.search(self.data['tools'],'COOKIE')],['cookie-scope-audit'])
        self.assertEqual(discovery.search(self.data['tools'],'definitely-no-match'),[])
        self.assertTrue(all(e['category']=='data' for e in discovery.search(self.data['tools'],category='data')))
    def test_frozen_offline_task_queries(self):
        # Manually constructed local simulations, not evidence of natural adoption.
        # Queries were frozen before inspection; three exposed missing core task
        # terms in metadata. Keep the same queries rather than tuning the search.
        cases = {
            'Content-Disposition': ['content-disposition-filename-kit'],
            'cookie scope': ['cookie-scope-audit'],
            'CORS preflight': ['cors-response-audit'],
            'Link pagination': ['http-link-header-kit'],
            'multipart boundary': ['multipart-boundary-fixtures'],
            'cache age': ['http-cache-age-lab'],
            'retry deadline': ['retry-budget-lab'],
            'csv schema': ['csv-schema-contract'],
            'zip traversal': ['zip-member-preflight'],
            'translation placeholders': ['translation-placeholder-contract'],
            'lsp edits': ['lsp-position-edit-kit'],
            'resize png': [],
            'production deploy': [],
        }
        for query, expected in cases.items():
            with self.subTest(query=query):
                self.assertEqual([entry['slug'] for entry in discovery.search(
                    self.data['tools'], query)], expected)

    def test_cli_validation_and_search_from_other_directory(self):
        for args,count in [(['--query','cookie'],1),([],50)]:
            result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/discover_tools.py'),*args],cwd=ROOT.parent,capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['count'],count)
        result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/discover_tools.py'),'--validate'],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(json.loads(result.stdout)['valid'])

if __name__ == '__main__':
    unittest.main()
