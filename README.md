# Competitor Insight Agent

本地单页竞品调研工具：输入主题与 2～3 个竞品，经 GPT Researcher 检索，输出产品定位与功能、定价/商业模式、差异化特点三个维度、2～3 条 AI 推断建议和来源，并下载 UTF-8 Markdown。缺少证据的字段保留“待核实”。修改输入会清除旧结果；校验输入后还需手动点击调用研究引擎。

G1 提供研究 CLI、配置检查和超时控制；G2 提供输入校验、运行状态和错误提示；G3 提供逐项摘录匹配、结构校验、对比表及下载。历史证据见 [G1](reports/G1_RESULT.md)、[G2](reports/G2_RESULT.md)、[G3](reports/G3_RESULT.md)。G4 实测与限制见 [G4_CODEX_NOTES](reports/G4_CODEX_NOTES.md)。

从零安装（已用 Python 3.13 验证现有运行环境）：

```bash
cd /path/to/competitor-insight-agent
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pip check
```

直接运行依赖已固定版本，但 `requirements.txt` 不是完整传递依赖锁，不能保证新机器解析出完全相同的环境。G4 沙箱 DNS 阻止安装 pytest；`requirements-dev.txt` 固定的 8.4.2 为待主机验证版本，尚不能声称已安装验证。不要通过修改 DNS、代理或关闭 TLS 校验规避安装错误。

在本机安全的进程环境中配置 `DEEPSEEK_API_KEY`（不要把真实值写进仓库、命令记录或聊天）。程序沿用现有进程变量，不自动加载 `.env`。免费配置检查：

```bash
.venv/bin/python researcher.py --check-config
```

此命令检查凭证存在性和 SDK 版本，不调用模型，也不证明余额、网络或在线研究可用。引擎使用 DeepSeek 原生 provider 的 `deepseek-flash`、DuckDuckGo 检索和本地 keyword 过滤，无需 Tavily 或 embedding key。真实研究可能产生费用，模型 usage/金额并非可靠硬上限；请先确认账户预算。SDK 调试输出被抑制，CLI 错误不输出凭证和第三方异常正文。既有运行配置包含项目内 `ALLOW_PRIVATE_URLS=true` 兼容项，来源仍需人工检查。

启动单页（复用已有同地址服务；不要结束无关进程）：

```bash
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
```

浏览器打开 `http://127.0.0.1:8501`。仅监听回环地址，不部署公网。页面的“开始调研”只校验输入；随后手动调用引擎才会触发真实研究，任务总计最多约 300 秒。单查询 API 为 `await researcher.research(query, timeout=300)`，返回报告文本与来源 URL。单查询 CLI 支持 `--query` 与 `--timeout 1..300`；这是可能收费的操作，不属于下面的 G4 验收步骤。

离线测试与已有证据验证（无付费请求）：在项目根推荐运行 `.venv/bin/python -m pytest -q`，也可运行 `.venv/bin/pytest -q`，两种入口均可；`pytest.ini` 将项目根加入测试导入路径。

```bash
.venv/bin/python -m pytest -q
.venv/bin/python comparison.py --validate reports/g3/comparison.json
.venv/bin/python reports/g3/verify_minimal.py
```

测试用替身覆盖 SDK 异常、超时、空结果、输入、摘录匹配与失败、非法/未知 URL、结构、Markdown 转义、页面下载控件和旧结果清除。AppTest 直接使用已有 G3 JSON，未重新研究。没有 pytest 时可临时执行同一组 unittest 兼容用例：

```bash
.venv/bin/python -m unittest discover -s tests -v
```

AppTest 证明页面输出和下载控件存在，不证明真实浏览器点击后文件落盘。需要人工点击证据时，可在本机浏览器对已有结果点击下载并核对内容；G4 不为此重新发起研究。

免费重新抓取并核对 G3 已有摘录（需 HTTP 网络，不调用 DeepSeek、研究器或结构化研究流程）：

```bash
.venv/bin/python reports/g3/reverify_fetch.py --input reports/g3/comparison.json --output-dir reports/g3/reverified --timeout 15
.venv/bin/python comparison.py --validate reports/g3/reverified/comparison.json
```

默认另存，不覆盖 G3 原件。检查终端每个字段的 `fetch_status`；退出 0 只表示产物生成成功，DNS/403/超时仍会使字段降为待核实。`excerpt_matched` 仅证明摘录匹配本次页面文本，结构校验也不证明来源权威性、时效或维度归类。特别是现有 FastGPT 商业模式使用第三方描述，采购前需对照官方来源。抓取保留浏览器式 UA；不以抓取失败推断竞品缺少能力。
