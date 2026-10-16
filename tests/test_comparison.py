"""Offline matching and validation; saved G3 data is historical evidence."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import Mock
from comparison import DIMENSIONS, escape, markdown, parse_fields, safe_url, validate_result

ROOT = Path(__file__).resolve().parents[1]


class ComparisonTest(unittest.TestCase):
    def test_matching_states_and_fetch_cache(self):
        url = 'https://example.com/product'
        quote = '用于离线测试的足够长逐字原文摘录。'
        report = json.dumps({'fields': {d: {'quote': quote, 'url': url} for d in DIMENSIONS}})
        for page, error, expected in [(quote, None, 'excerpt_matched'),
                                      ('different', None, 'excerpt_not_matched'),
                                      (None, OSError('offline'), 'fetch_failed')]:
            fetch = Mock(return_value=page, side_effect=error)
            fields = parse_fields(report, [url], fetch)
            self.assertEqual(fetch.call_count, 1)
            for field in fields.values():
                self.assertEqual(field['fetch_status'], expected)
                self.assertEqual(field['pending'], expected != 'excerpt_matched')
                self.assertEqual(field['quote'], quote)
        fetch = Mock(side_effect=AssertionError('unknown URL must not be fetched'))
        self.assertTrue(all(f['pending'] for f in parse_fields(report, [], fetch).values()))
        fetch.assert_not_called()

    def test_missing_and_malformed_fields(self):
        for report in ['not json', '{}', '{"fields":[]}', '{"fields":{"产品定位与功能":null}}']:
            with self.subTest(report=report):
                fields = parse_fields(report, [], Mock(side_effect=AssertionError('no fetch')))
                self.assertEqual(set(fields), set(DIMENSIONS))
                self.assertTrue(all(f['pending'] for f in fields.values()))

    def test_unsafe_urls(self):
        for url in ['javascript:alert(1)', 'file:///tmp/a', 'https://u:p@example.com',
                    'https://example.com/<x>', 'https://example.com/ a', None]:
            self.assertFalse(safe_url(url))
        self.assertTrue(safe_url('https://example.com/product'))

    def test_markdown_escaping_and_saved_artifact(self):
        self.assertEqual(escape('|\n<b>*[x]'), r'\| &lt;b&gt;\*\[x\]')
        result = json.loads((ROOT / 'reports/g3/comparison.json').read_text())
        self.assertEqual(markdown(result), (ROOT / 'reports/g3/comparison.md').read_text())
        result['topic'] = 'topic |\n<script>'
        rendered = markdown(result)
        self.assertIn(r'topic \| &lt;script&gt;', rendered)
        self.assertNotIn('<script>', rendered)

    def test_structure_rejects_invalid_reports(self):
        original = json.loads((ROOT / 'reports/g3/comparison.json').read_text())
        self.assertIs(validate_result(original), original)
        def field(r):
            return r['competitors'][0]['fields'][DIMENSIONS[0]]
        mutations = [
            lambda r: r.update(competitors=r['competitors'][:1]),
            lambda r: r.update(topic=' '),
            lambda r: r.update(suggestions=[]),
            lambda r: r['competitors'][0].update(source_urls=[]),
            lambda r: r['competitors'][0].update(source_urls=['file:///tmp/a']),
            lambda r: r['competitors'][0]['fields'].pop(DIMENSIONS[0]),
            lambda r: field(r).update(text=42),
            lambda r: field(r).update(pending='false'),
            lambda r: field(r).update(source_urls=['https://unknown.example/']),
            lambda r: field(r).update(fetch_status='fetch_failed'),
            lambda r: field(r).update(text='unsupported claim'),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                result = copy.deepcopy(original)
                mutate(result)
                with self.assertRaises(ValueError):
                    validate_result(result)
