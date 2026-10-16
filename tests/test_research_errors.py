"""Only a fake SDK is used: no model, subprocess or network requests."""
import asyncio
import contextlib
import io
import json
import sys
import types
import unittest
from unittest.mock import AsyncMock, Mock, patch
import researcher


class ResearchErrorsTest(unittest.TestCase):
    def test_sdk_errors_empty_results_and_timeout(self):
        cases = [('empty report', '', ['https://example.com'], None, 'EMPTY_REPORT'),
                 ('empty sources', 'report', [], None, 'EMPTY_SOURCES'),
                 ('unsafe sources', 'report', ['file:///tmp/a'], None, 'EMPTY_SOURCES'),
                 ('authentication', 'report', [], RuntimeError('401 fake'), '401 fake'),
                 ('rate limit', 'report', [], RuntimeError('429 fake'), '429 fake'),
                 ('timeout', 'report', [], TimeoutError(), None)]
        for label, report, urls, error, message in cases:
            with self.subTest(label=label):
                agent = Mock(conduct_research=AsyncMock(side_effect=error),
                             write_report=AsyncMock(return_value=report), get_source_urls=Mock(return_value=urls))
                sdk = types.SimpleNamespace(GPTResearcher=Mock(return_value=agent))
                with patch.object(researcher, 'configure'), patch.dict(sys.modules, gpt_researcher=sdk):
                    with self.assertRaises((RuntimeError, TimeoutError)) as caught:
                        asyncio.run(researcher.research('offline query', 1))
                if message:
                    self.assertEqual(str(caught.exception), message)

    def test_validation_before_sdk(self):
        for query, timeout in [(' ', 1), ('q', 0), ('q', 301)]:
            with patch.object(researcher, 'configure') as configure, self.assertRaises(ValueError):
                asyncio.run(researcher.research(query, timeout))
            configure.assert_not_called()

    def test_cli_sanitizes_failure(self):
        for error, expected in [(RuntimeError('MISSING_CREDENTIAL'), 'MISSING_CREDENTIAL'),
                                (RuntimeError('private fake authentication detail'), 'RESEARCH_ERROR'),
                                (TimeoutError(), 'TIMEOUT'),
                                (ModuleNotFoundError('fake dependency'), 'DEPENDENCY_MISSING')]:
            output = io.StringIO()
            with patch.object(sys, 'argv', ['researcher.py', '--check-config']), \
                    patch.object(researcher, 'configure', side_effect=error), \
                    contextlib.redirect_stderr(output):
                self.assertEqual(researcher.main(), 3)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload['error'], expected)
            self.assertNotIn('private fake', output.getvalue())
