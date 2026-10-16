# pytest 导入路径修复

根因：直接执行 `.venv/bin/pytest` 时，项目根未进入 `sys.path`，导致 test_app / test_comparison 收集时无法导入 `comparison`；`python -m pytest` 的入口行为不同。

改动：新增标准配置 `pytest.ini`，设置 `[pytest]` 下的 `pythonpath = .`，统一两种入口的测试导入路径；README 写明推荐命令及两种入口均可。未改动抓取语义、comparison.py 业务逻辑或 G4_RESULT.md，未运行付费研究，也未修改 DNS/代理或部署公网。

在 `/workspace/competitor-insight-agent` 验收：

| 命令 | 结果 | 退出码 |
| --- | --- | --- |
| `.venv/bin/python -m pytest -q` | 14 passed in 0.47s | 0 |
| `.venv/bin/pytest -q` | 14 passed in 0.45s | 0 |
