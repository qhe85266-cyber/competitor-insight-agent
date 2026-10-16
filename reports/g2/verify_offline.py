"""Offline function checks only: no Streamlit rendering or real API calls."""
import ast
from pathlib import Path
import subprocess
from unittest.mock import patch

root = Path(__file__).resolve().parents[2]
tree = ast.parse((root / "app.py").read_text())
# Load actual imports/functions without requiring the unavailable UI dependency.
tree.body = [node for node in tree.body if
             (isinstance(node, (ast.Import, ast.ImportFrom)) and
              not (isinstance(node, ast.Import) and node.names[0].name == "streamlit"))
             or (isinstance(node, ast.FunctionDef) and node.name != "main")]
namespace = {"__file__": str(root / "app.py")}
exec(compile(tree, str(root / "app.py"), "exec"), namespace)
validate = namespace["validate_inputs"]
cases = [
    ("", "A,B", False), ("  ", "A,B", False),
    ("主题", "", False), ("主题", "A", False),
    ("主题", "A,B,C,D", False), ("主题", "Dify, dify", False),
    ("主题", "Ａ,A", False), ("主题", "A, ,B", True),
    (" 主题 ", " Dify、FastGPT ", True),
    ("主题", "A；B\nC", True),
]
for topic, names, expected in cases:
    try:
        result = validate(topic, names)
        actual = True
        assert result[0] == topic.strip()
    except ValueError:
        actual = False
    assert actual == expected
print("PASS: 10 input cases (missing/count/duplicates/separators/trim)")
invoke = namespace["invoke_researcher"]
for code, expected in [(0, None), (3, RuntimeError), (124, TimeoutError)]:
    with patch("subprocess.run", return_value=subprocess.CompletedProcess([], code)) as run:
        try:
            invoke("主题", ["A", "B"])
            assert expected is None
        except Exception as exc:
            assert expected is not None and isinstance(exc, expected)
        assert run.call_args.kwargs["timeout"] == 35
        assert run.call_args.kwargs["stdout"] == subprocess.DEVNULL
        assert run.call_args.args[0][-2:] == ["--timeout", "30"]
with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("mock", 35)):
    try:
        invoke("主题", ["A", "B"])
        raise AssertionError("Expected timeout")
    except subprocess.TimeoutExpired:
        pass
print("PASS: 4 mocked engine paths; zero real research calls")
print("NOT TESTED: Streamlit rendering, buttons, running/error UI, local HTTP")
