# G4 交付结果（监工验收）

总状态：**CONDITIONAL**。

日期：2026-10-16（Asia/Shanghai）。解释器：`.venv/bin/python`（Python 3.13）。pytest 主机实测版本：`8.4.2`。

## 状态理由

- **通过**：离线测试 14 项（pytest）、结构校验、G3 六维 HTTP 重核（UA 修复后）、Streamlit `127.0.0.1:8501` health/root 200、AppTest 下载控件与同源 Markdown 落盘证据、README 可按步骤本地运行说明齐全。
- **未宣称完全 PASS**：未重新付费跑三竞品在线研究；未做真实浏览器人手点击下载；未做全新空目录 venv 从零重装全套依赖的独立复现；来源权威性/时效/维度归类仍需人工复核。

## Codex 本关改动

见 [G4_CODEX_NOTES.md](G4_CODEX_NOTES.md)。主要文件：

- `tests/test_inputs.py`
- `tests/test_comparison.py`
- `tests/test_research_errors.py`
- `tests/test_app.py`
- `tests/test_fetch_ua.py`（G3 UA 修复已有，本关保留）
- `requirements-dev.txt`
- `README.md`

业务代码 `comparison.py` / `app.py` / `researcher.py` 在 G4 未改（UA 修复属 G3 收尾，见 [FIX_FETCH_UA.md](FIX_FETCH_UA.md)）。

## 主机实测命令与退出码

| 命令 | 退出码 | 摘要 |
| --- | --- | --- |
| `.venv/bin/python -m pip install -r requirements-dev.txt` | 0 | 安装 `pytest==8.4.2` |
| `.venv/bin/python -m pytest --version` | 0 | `pytest 8.4.2` |
| `.venv/bin/python -m pip check` | 0 | No broken requirements |
| `.venv/bin/python -m pytest -q` | 0 | **14 passed** in ~0.49s |
| `.venv/bin/python comparison.py --validate reports/g3/comparison.json` | 0 | `STRUCTURE_VALID` |
| `.venv/bin/python comparison.py --validate reports/g4/comparison.json` | 0 | `STRUCTURE_VALID` |
| `.venv/bin/python reports/g3/verify_minimal.py` | 0 | PASS（离线） |
| `.venv/bin/python reports/g3/reverify_fetch.py --timeout 15` | 0 | 六维 `excerpt_matched`（G3 收尾） |
| `curl http://127.0.0.1:8501/_stcore/health` | 0 | HTTP 200；进程已监听，复用未重启 |
| `curl http://127.0.0.1:8501/` | 0 | HTTP 200 |

未执行付费：`run_comparison` / `researcher.py --query` / DeepSeek 研究调用。

## 产物路径

| 路径 | 说明 |
| --- | --- |
| `http://127.0.0.1:8501/` | 本机 Streamlit（仅回环） |
| `reports/g3/comparison.json` / `.md` | 主题「AI Agent 开发平台」，Dify+FastGPT；UA 重核后六维 fact |
| `reports/g4/comparison.json` / `.md` | 自 G3 复制的离线交付样本（未重新研究） |
| `reports/g4/download_competitor-comparison.md` | 与 `markdown(result)` 一致的下载内容（3608 字节） |
| `reports/g4/download_evidence.json` | AppTest：下载按钮 1 个、标签「下载 Markdown」、页面 Markdown 同源 |
| `reports/FIX_FETCH_UA.md` | UA 修复说明 |
| `reports/G3_RESULT.md` | G3 更新结论 |

## Dify/FastGPT 字段（交付样本）

| 竞品 | 维度 | kind | pending | fetch_status |
| --- | --- | --- | --- | --- |
| Dify | 产品定位与功能 | fact | false | excerpt_matched |
| Dify | 定价/商业模式 | fact | false | excerpt_matched |
| Dify | 差异化特点 | fact | false | excerpt_matched |
| FastGPT | 产品定位与功能 | fact | false | excerpt_matched |
| FastGPT | 定价/商业模式 | fact | false | excerpt_matched |
| FastGPT | 差异化特点 | fact | false | excerpt_matched |

## 仍未解决 / 人工边界

1. 真实浏览器点击「下载 Markdown」并核对落盘文件：仅有 AppTest 控件 + 同源内容证据，非人手点击。
2. 未跑 Langflow 第三竞品付费在线样本（输入校验已覆盖 3 竞品；避免重复 DeepSeek 费用）。
3. 全新机器从零 `venv` 全量安装复现未独立执行（当前宿主 `.venv` 已 `pip check` + pytest 绿）。
4. `excerpt_matched` ≠ 来源权威/时效/维度归类正确；FastGPT 商业模式来自第三方博客，采购前须对照官方。
5. 无完整传递依赖 lock；仅直接依赖 pin。

## 结论

G4 记 **CONDITIONAL**：测试、README、本机页面、下载控件证据与 G3 六维核验齐备，可演示；不以离线绿测冒充完整在线三竞品浏览器人手验收 PASS。

## 监工复核：pytest 两种入口（2026-10-16 约 20:59 CST）

### 复现失败（修复前）
- `.venv/bin/python -m pytest -q` → **14 passed**，exit 0
- `.venv/bin/pytest -q` → 收集失败：`ModuleNotFoundError: No module named 'comparison'`（`test_app` / `test_comparison`）

根因：项目根未进入 `sys.path`；`python -m` 与直接 `pytest` 入口行为不同。此前 G4 仅宣称 14 passed，忽略了可复现的第二种入口失败。详见 [FIX_PYTEST_PATH.md](FIX_PYTEST_PATH.md)。

### Codex 修复
- 新增 `pytest.ini`：`[pytest]` / `pythonpath = .`
- 更新 `README.md`：推荐 `.venv/bin/python -m pytest -q`，并注明 `.venv/bin/pytest -q` 亦可

未改业务/抓取语义，未付费研究。

### 修复后监工验收（项目根实测）

| 命令 | 输出摘要 | 退出码 |
| --- | --- | --- |
| `.venv/bin/python -m pytest -q` | 14 passed in 0.56s | 0 |
| `.venv/bin/pytest -q` | 14 passed in 0.54s | 0 |

两种入口现均 **14 passed**。

