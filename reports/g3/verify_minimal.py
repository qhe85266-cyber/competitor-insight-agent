"""Small G3 offline helper; fixtures are not online research evidence."""
import json
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from comparison import DIMENSIONS, markdown, parse_fields, run_comparison
from streamlit.testing.v1 import AppTest

url = 'https://example.com/product'
quote = '这是用于离线验证的来源摘录，包含竖线 | 与 **格式**。'
report = json.dumps({'fields': {d: {'quote': quote, 'url': url} for d in DIMENSIONS}}, ensure_ascii=False)
fields = parse_fields(report, [url], lambda _: '<data> ' + quote)
assert all(not f['pending'] for f in fields.values())
assert all(f['pending'] for f in parse_fields(report, [], lambda _: quote).values())
assert all(f['pending'] for f in parse_fields(report, [url], lambda _: 'other page').values())
assert all(f['pending'] for f in parse_fields('non JSON report', [url], lambda _: quote).values())
def fail(_):
    raise OSError('offline')
assert all(f['pending'] for f in parse_fields(report, [url], fail).values())
result = {'topic': '离线样本 | <b>', 'created_at': 'offline fixture',
          'competitors': [{'name': n, 'fields': fields, 'source_urls': [url]} for n in ('A', 'B')],
          'suggestions': ['AI 推断：离线建议'] * 3}
content = markdown(result)
assert '\\|' in content and '&lt;b&gt;' in content
assert all(d in content for d in DIMENSIONS)
assert content.count('| 产品定位与功能 |') == 1
assert '[来源](<https://example.com/product>)' in content
# Exercise actual subprocess adapter with an offline CLI-shaped response.
from subprocess import CompletedProcess
with patch('comparison.subprocess.run', return_value=CompletedProcess([], 0, json.dumps({'report': report, 'source_urls': [url]}), '')) as runner, patch('comparison.fetch_text', return_value=quote):
    adapted = run_comparison('topic', ['A', 'B'])
    assert runner.call_count == 2
    assert len(adapted['suggestions']) == 3
    assert len(adapted['competitors']) == 2

app = AppTest.from_file(str(ROOT / 'app.py')).run()
assert not app.exception
app.text_input[0].set_value('topic')
app.text_area[0].set_value('A,B')
app.button[0].click().run()
with patch('comparison.run_comparison', return_value=result):
    app.button[1].click().run()
assert not app.exception
assert app.session_state['comparison'] == result
rendered = app.get('download_button')
assert len(rendered) == 1
assert rendered[0].proto.label == '下载 Markdown'
assert any(content.strip() == m.value.strip() for m in app.markdown)
app.text_input[0].set_value('changed').run()
assert len(app.get('download_button')) == 0
print('PASS: G3 evidence matching/missing/unknown/mismatch/fetch-failure, Markdown escaping, CLI adapter, page output/download control and stale-result clearing')
print('OFFLINE ONLY: no real API calls; browser download click and real two-competitor evidence remain unverified')
