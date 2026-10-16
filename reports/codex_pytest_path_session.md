已完成最小范围修复，改动文件：

- `pytest.ini`：设置 `pythonpath = .`。
- `README.md`：写明推荐测试命令及两种入口均可。
- `reports/FIX_PYTEST_PATH.md`：记录根因、改动和验收结果。

项目根实测：

- `.venv/bin/python -m pytest -q`：14 passed，退出码 0。
- `.venv/bin/pytest -q`：14 passed，退出码 0。

未修改业务逻辑或 `G4_RESULT.md`，未运行付费研究、修改 DNS/代理或部署公网。