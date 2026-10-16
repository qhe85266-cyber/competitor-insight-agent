"""Offline HTTP gate: reject default urllib UA, accept browser UA."""
import copy
import importlib.util
import io
import json
from email.message import Message
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from comparison import DIMENSIONS, fetch_text, normalize, parse_fields

spec = importlib.util.spec_from_file_location('reverify_fetch', ROOT / 'reports/g3/reverify_fetch.py')
recheck = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recheck)
URL = 'https://example.com/product'
QUOTE = '这是用于离线验证的来源逐字摘录，必须精确匹配。'


def gated_response(request, timeout):
    ua = request.get_header('User-agent') if isinstance(request, urllib.request.Request) else ''
    if not ua or not ua.startswith('Mozilla/5.0'):
        raise HTTPError(URL, 403, 'Browser UA required', {}, None)
    assert request.get_header('Accept')
    assert request.get_header('Accept-language')
    assert timeout == 3
    response = io.BytesIO(('<html><script>hidden</script><p>' + QUOTE + '</p></html>').encode())
    response.url = URL
    response.headers = Message()
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response


class FetchUATest(unittest.TestCase):
    @patch('comparison.urllib.request.urlopen', side_effect=gated_response)
    def test_browser_ua_unlocks_exact_match(self, opener):
        with self.assertRaises(HTTPError):
            urllib.request.urlopen(URL, timeout=3)
        page = fetch_text(URL, 3)
        self.assertIn(normalize(QUOTE), normalize(page))
        self.assertNotIn('hidden', page)
        report = json.dumps({'fields': {d: {'url': URL, 'quote': QUOTE} for d in DIMENSIONS}})
        fields = parse_fields(report, [URL], lambda url: fetch_text(url, 3))
        self.assertTrue(all(f['kind'] == 'fact' and not f['pending'] for f in fields.values()))
        fields = parse_fields(report, [URL], lambda url: urllib.request.urlopen(url, timeout=3))
        self.assertTrue(all(f['pending'] and f['fetch_status'] == 'fetch_failed' for f in fields.values()))

    def test_reverify_saved_json_without_research(self):
        result = json.loads((ROOT / 'reports/g3/comparison.json').read_text())
        original = copy.deepcopy(result)
        pages = {}
        for competitor in result['competitors']:
            for field in competitor['fields'].values():
                pages.setdefault(field['source_urls'][0], []).append(field['quote'])
        with patch.object(recheck, 'fetch_text', side_effect=lambda url, timeout: ' '.join(pages[url])), \
                patch('comparison.subprocess.run', side_effect=AssertionError('Research forbidden')):
            checked = recheck.reverify(result)
        self.assertTrue(all(not f['pending'] for c in checked['competitors'] for f in c['fields'].values()))
        for competitor in checked['competitors']:
            for field in competitor['fields'].values():
                field.update(kind='fact', pending=False, fetch_status='excerpt_matched')
        with patch.object(recheck, 'fetch_text', side_effect=OSError('offline')):
            failed = recheck.reverify(checked)
        for before, after in zip(original['competitors'], failed['competitors']):
            self.assertEqual(before['raw_report'], after['raw_report'])
            for dimension in DIMENSIONS:
                a, b = before['fields'][dimension], after['fields'][dimension]
                for key in ('text', 'quote', 'source_urls'):
                    self.assertEqual(a[key], b[key])
                self.assertEqual(b['kind'], 'unverified')
                self.assertTrue(b['pending'])
                self.assertEqual(b['fetch_status'], 'fetch_failed')


if __name__ == '__main__':
    unittest.main()
