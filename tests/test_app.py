"""Render the existing G3 artifact; research is always replaced or forbidden."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from comparison import markdown

ROOT = Path(__file__).resolve().parents[1]


class AppTestOffline(unittest.TestCase):
    def test_saved_g3_download_and_stale_result(self):
        result = json.loads((ROOT / 'reports/g3/comparison.json').read_text())
        with patch('comparison.run_comparison', side_effect=AssertionError('Paid research forbidden')):
            app = AppTest.from_file(str(ROOT / 'app.py')).run()
            app.text_input[0].set_value(result['topic'])
            app.text_area[0].set_value('Dify,FastGPT').run()
            app.session_state['comparison'] = result
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.get('download_button')), 1)
            self.assertEqual(app.get('download_button')[0].proto.label, '下载 Markdown')
            self.assertTrue(any(m.value.strip() == markdown(result).strip() for m in app.markdown))
            app.text_input[0].set_value('changed').run()
            self.assertEqual(len(app.get('download_button')), 0)
            self.assertNotIn('comparison', app.session_state)

    def test_failed_task_consumes_pending_and_clears_old_result(self):
        for error in [TimeoutError(), RuntimeError('offline failure')]:
            with self.subTest(error=type(error).__name__), patch('comparison.run_comparison', side_effect=error) as runner:
                app = AppTest.from_file(str(ROOT / 'app.py')).run()
                app.text_input[0].set_value('topic')
                app.text_area[0].set_value('A,B')
                app.button[0].click().run()
                runner.assert_not_called()
                app.button[1].click().run()
                self.assertFalse(app.exception)
                self.assertTrue(app.error)
                self.assertNotIn('pending', app.session_state)
                self.assertEqual(len(app.get('download_button')), 0)
                app.run()
                self.assertEqual(runner.call_count, 1)
