# G4 Codex 交付记录

本轮仅测试与复现文档；验收结论由监工填写。未创建 `G4_RESULT.md`。未重新调用 DeepSeek、研究 CLI 或真实 run_comparison；指定的 verify_minimal.py 内部只运行 subprocess/fetch 替身。G3 JSON/Markdown 原件、业务逻辑及 fetch UA 均未修改，未部署、未更改 DNS/代理、未操作已有服务进程。

## 改动

- `tests/test_inputs.py`：空主题、1/4 个竞品、大小写/全角/空白重复、合法 2/3 个及分隔符。
- `tests/test_comparison.py`：摘录匹配/不匹配/抓取失败、缓存、未知 URL 不抓取、缺失/异常字段、非法 URL、Markdown 转义、既有 JSON/MD 一致及结构拒绝路径。
- `tests/test_research_errors.py`：fake SDK 的认证/限流/失败/超时、空报告/空来源、参数校验及 CLI 错误脱敏。
- `tests/test_app.py`：直接加载既有 G3 JSON 的 AppTest；下载控件及同源 Markdown、旧结果清除、失败/超时提示与 pending 消费后不重复调用。所有研究入口均被替换或禁止。
- `requirements-dev.txt`：仅 pytest 精确版本候选 `8.4.2`。**安装被 DNS 阻止，此版本未在当前 venv 实际安装，尚未满足“固定实际安装版本”的要求**；主机安装后需核实版本。没有添加其他重依赖。
- `README.md`：从零 venv、免费配置检查、回环启动、测试、费用/密钥、免费重核及证据边界。
- 原有 `tests/test_fetch_ua.py` 保持不变，包含在完整测试内。

## 实际命令与退出码

以下均在 `/workspace/competitor-insight-agent` 执行；测试解释器为 `.venv/bin/python`（Python 3.13）。

| 命令 | 退出码 | 结果 |
| --- | --- | --- |
| `.venv/bin/python -m pip show pytest` | 1 | 初始未安装 |
| `.venv/bin/python -m pip install pytest` | 1 | 名称解析失败，无法访问包索引 |
| `.venv/bin/python -m pip install -r requirements-dev.txt` | 1 | 同上，日志为 `/tmp/g4-pip-install.log` |
| `.venv/bin/python -m pip check` | 0 | No broken requirements found |
| `.venv/bin/python -m pytest -q` | 1 | No module named pytest |
| `.venv/bin/python -m unittest discover -s tests -v` | 0 | 14 tests，OK；含已有 UA 两项；复测仍 14 项通过 |
| `.venv/bin/python comparison.py --validate reports/g3/comparison.json` | 0 | STRUCTURE_VALID |
| `.venv/bin/python reports/g3/verify_minimal.py` | 0 | 离线匹配、替身适配、页面/下载控件与清除检查通过 |
| `.venv/bin/python researcher.py --check-config` | 0 | credential_present=true，sdk_version=0.16.1；无模型调用 |
| `git diff --check` | 0 | 无输出；当前项目文件多为未跟踪，不能据此声称覆盖未跟踪文件的差异 |
| `git ls-files .env` | 0 | 无输出，未跟踪 `.env` |
| `curl --fail --max-time 5 http://127.0.0.1:8501/_stcore/health` | 7 | 当前沙箱无法连接；未更改/重启服务 |

用 Python 对 README、requirements-dev 及 tests 共 7 个文件扫描当前非空 DeepSeek/Tavily 密钥值，仅输出文件计数/命中数：exit 0，命中文件数 0；没有输出密钥。日志 `/tmp/g4-unittest.log` 为本机临时测试输出，无付费研究产物。

## 限制与主机侧复现

`NETWORK_DNS` 阻止 pytest 安装，因此不能宣称 pytest 已通过，也未完成全新 venv 依赖重装验证。14 项 unittest 通过只证明离线逻辑。AppTest 不证明浏览器实际点击下载后文件落盘。现有六维 excerpt_matched 为历史 G3 证据，来源权威性、时效、归类仍需人工复核（尤其 FastGPT 商业模式第三方来源）。运行依赖仅固定直接版本，没有已验证的完整传递依赖锁。

可联网主机执行（不触发付费研究）：

```bash
cd /workspace/competitor-insight-agent
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest --version
.venv/bin/python -m pip check
.venv/bin/python -m pytest -q
.venv/bin/python comparison.py --validate reports/g3/comparison.json
.venv/bin/python reports/g3/verify_minimal.py
curl --fail --max-time 10 http://127.0.0.1:8501/_stcore/health
```

如需新环境复现，在独立项目内 venv 安装 `requirements.txt` 与 `requirements-dev.txt` 后重跑上述离线检查。服务存在则复用，仅在确认未运行时按 README 的 `127.0.0.1:8501` 命令启动。免费 HTTP 重核为可选步骤，使用 README 中另存路径，不覆盖现有 G3 原件；本轮未再次联网重核或生成 g4 研究样本。
