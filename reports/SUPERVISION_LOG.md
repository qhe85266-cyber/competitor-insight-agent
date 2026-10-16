# SUPERVISION_LOG

## [2026-10-16 20:16 Asia/Shanghai | 阶段 G0]

状态：PASS（方案文档） / 运行环境备注 BLOCKED 风险已写入计划

Codex 已完成：
- 项目目录 `/workspace/competitor-insight-agent` 已建，Git 已 init
- 两份方案已落盘：`01_GrokBot_监工方案.md`、`02_CodexCLI_开工方案.md`
- 完整技术方案：`reports/CODEX_PLAN.md`（约 31KB；首轮仅摘要已 FAIL 退回后返工）
- 未创建功能代码（无 app.py / researcher.py / comparison.py / tests）
- 未安装依赖、未调用计费模型、未泄露密钥

执行验证：
- `wc -c reports/CODEX_PLAN.md` → 31434
- 监工主机侧 `curl`：pypi.org / github.com / cloudflare 均可 HTTP 200
- Codex 沙箱内 HTTPS 解析失败（Errno -3），计划中标为后续 G1 网络风险
- `DEEPSEEK_API_KEY` 存在且非空；`TAVILY_API_KEY` 未设置

当前问题：无（G0 文档关通过）。进入 G1 前需用户批准：安装依赖、DeepSeek 真实调用（可能产生费用）、是否提供 Tavily 或先用 DuckDuckGo。

风险或费用：G1 将产生 DeepSeek API 费用；沙箱联网策略可能阻碍 pip/检索。

下一步：等待用户明确批准后再启动 G1。


## [2026-10-16 20:22 Asia/Shanghai | 阶段 G1]

状态：BLOCKED（部分推进，未宣称 PASS）

Codex 已完成：
- 写出 `researcher.py`、`requirements.txt`、`.venv`；首轮因沙箱 DNS 标 BLOCKED（属实）
- 监工在主机侧（用户已批准装依赖）安装成功：gpt-researcher==0.16.1、langchain-deepseek==1.1.1、python-dotenv==1.2.4、ddgs==9.16.0
- `SDK_IMPORT_OK`；`--check-config` 通过（runtime_verified=false）
- 真实调用曾发生：DuckDuckGo 有命中；DeepSeek 有费用日志约 $0.014；来源 URL 列表非空

执行验证（失败点）：
- 抓取阶段全部跳过：`URL host resolves to a non-public address (198.18.0.1)`；SDK 提示可设 `ALLOW_PRIVATE_URLS=true`
- 报告正文为“无法采集来源”，上下文为空；不能算有效研究报告

当前问题：本机 DNS/代理把公网域名解析到 198.18.0.1，触发 GPT Researcher SSRF 防护，页面抓取 0 页。

风险或费用：已产生少量 DeepSeek 调用费用；放开 `ALLOW_PRIVATE_URLS` 会降低 SSRF 防护，需用户明确批准。

下一步：等待用户是否批准设置 `ALLOW_PRIVATE_URLS=true` 后复测；未批准则保持 G1=BLOCKED，不进入 G2。


## [2026-10-16 20:25 Asia/Shanghai | 阶段 G1 复测]

状态：PASS

Codex 已完成：`ALLOW_PRIVATE_URLS=true` 写入 researcher.py；requirements 固定 ddgs==9.16.0；G1_RESULT 更新为 PASS。

执行验证：主机复测 query=`Dify AI pricing`，exit 0，report_chars=7576，来源 5 条，耗时 52.114s，model=deepseek-flash，retriever=duckduckgo；`--check-config` exit 0。

当前问题：无。未进入 G2。

风险或费用：已有 DeepSeek 调用费用；ALLOW_PRIVATE_URLS 仅本项目进程内开启。

下一步：等待用户批准是否进入 G2（Streamlit 单页输入）。


## [2026-10-16 20:29 Asia/Shanghai | 阶段 G2]

状态：PASS

Codex 已完成：`app.py` Streamlit 输入页；离线校验脚本；requirements 固定 streamlit==1.50.0（沙箱装包失败后由监工主机补装）。

执行验证：`http://127.0.0.1:8501/` 与 `/_stcore/health` 均为 HTTP 200；页面可见主题/竞品输入与「开始调研」；offline verify PASS。未进入 G3，未跑长研究。

当前问题：无。

风险或费用：页面含手动触发真实研究（30s 上限），可能产生 DeepSeek 费用。

下一步：等待用户批准是否进入 G3。


## [2026-10-16 20:42 Asia/Shanghai | 阶段 G3]

状态：PASS（含待核实字段，非全格已核验事实）

Codex 已完成：comparison.py + app 展示/下载；离线校验通过。

执行验证：主机生成 Dify/FastGPT 对比 JSON+MD；FastGPT 三维原文匹配；Dify 三维 fetch_failed→待核实；建议 3 条；页面仍 127.0.0.1:8501。

当前问题：Dify 官方页二次抓取核验失败（内容仍有来源链接）。

风险或费用：本关产生 DeepSeek 研究调用费用。

下一步：等待用户是否批准 G4。

## 2026-10-16 20:58 CST — UA 修复 + G4 CONDITIONAL

用户授权：直接做完并测试，监工不对就让 Codex 修，不再逐步确认。

A. Codex（gpt-6.1-sol）修 `fetch_text` UA；`tests/test_fetch_ua.py`；`reports/g3/reverify_fetch.py`；`FIX_FETCH_UA.md`。
B. 主机重核：Dify 三维 + FastGPT 三维均为 `excerpt_matched`/`fact`；更新 `G3_RESULT.md`，提升 reverified 为 g3 交付物。
C. Codex G4：tests×4 + requirements-dev + README；主机 `pip install pytest==8.4.2`，`pytest -q` → 14 passed；8501 health 200；`reports/g4/` 下载证据；`G4_RESULT.md` = CONDITIONAL。

## 2026-10-16 20:59 CST — pytest 双入口修复
复现 `.venv/bin/pytest` ModuleNotFoundError；Codex 加 pytest.ini pythonpath=.；双入口均 14 passed exit 0；更新 G4_RESULT / FIX_PYTEST_PATH。
