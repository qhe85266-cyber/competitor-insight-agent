改动文件：

- `tests/test_inputs.py`
- `tests/test_comparison.py`
- `tests/test_research_errors.py`
- `tests/test_app.py`
- `requirements-dev.txt`
- `README.md`
- [reports/G4_CODEX_NOTES.md](/workspace/competitor-insight-agent/reports/G4_CODEX_NOTES.md)

测试结果：unittest 共 **14 项通过**（含原 UA 测试）；`pip check`、G3 JSON 结构校验、`verify_minimal.py` 均退出 0。未改业务代码，未触发付费研究，未创建 `G4_RESULT.md`。

限制：DNS 阻止 pytest 安装，固定的 `8.4.2` 尚待实际安装验证；pytest、新环境复现及真实浏览器下载尚未完成。沙箱内 8501 健康检查连接失败，未操作服务。

主机侧待跑：

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest --version
.venv/bin/python -m pip check
.venv/bin/python -m pytest -q
.venv/bin/python comparison.py --validate reports/g3/comparison.json
.venv/bin/python reports/g3/verify_minimal.py
curl --fail --max-time 10 http://127.0.0.1:8501/_stcore/health
```