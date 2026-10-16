# G2 验收结果

**总状态：最终 PASS。首轮沙箱验收因依赖安装受阻记为 BLOCKED；主机侧补装与 HTTP 复验已完成。**

执行日期：2026-10-16（Asia/Shanghai）。解释器：`/workspace/competitor-insight-agent/.venv/bin/python`。本次遵照用户最新范围，仅实现 G2 输入页；未进入 G3/G4。未运行真实在线研究，未打印或提交密钥，未监听公网地址，未修改现有 researcher.py。

## 实际交付

- `app.py`：研究主题、竞品分隔输入、开始调研；主题去空白、2～3 个非空名称、忽略大小写和全角差异的重复检查；错误提示、校验中与研究中状态。
- 开始调研通过校验后显示“将调用研究引擎”，明确尚未发起网络请求。编辑输入即清除旧任务；拒绝输入不会调用引擎。
- 独立的“手动调用研究引擎（30 秒上限）”按钮，默认接现有 `researcher.py` CLI，不用 mock 代替真实引擎。使用当前虚拟环境解释器，CLI 限时 30 秒，外层子进程限时 35 秒。任务在调用前消费，页面重跑不会自动再次收费；失败需重新提交。
- 子进程输出丢弃；页面只展示通用失败/超时提示，不展示 SDK 原始异常。成功仅显示引擎调用完成，不展示或保存报告。
- `requirements.txt` 新增固定版本 `streamlit==1.50.0`。该固定版本已由用户确认在主机侧装入项目 `.venv`。未重装任何无关大包，也未生成未经验证的依赖锁文件。
- `reports/g2/verify_offline.py` 为本关验收脚本，直接从 app.py 提取实际函数做离线校验。它不模拟页面，不证明 Streamlit 交互可用。

没有实现对比结构化、建议、Markdown 下载或完整研究输出。

## 命令、退出码及证据

以下为首轮沙箱执行记录（历史 BLOCKED 证据），均在项目目录执行。首轮两次安装均失败；后续主机恢复结果见下节。

| 实际命令 | 退出码 | 实际结果 |
|---|---:|---|
| `.venv/bin/python -m pip show streamlit` | 1 | Package(s) not found: streamlit |
| `.venv/bin/python -m pip install --disable-pip-version-check --retries 0 --timeout 15 streamlit==1.50.0` | 1 | Could not find a version that satisfies the requirement；from versions: none |
| `.venv/bin/python -m pip install --index-url https://pypi.org/simple --disable-pip-version-check --retries 0 --timeout 15 streamlit==1.50.0` | 1 | No matching distribution found |
| `.venv/bin/python -m py_compile app.py` | 0 | 语法编译成功 |
| `.venv/bin/python reports/g2/verify_offline.py` | 0 | 10 个输入案例、4 个 mock 引擎路径通过；真实研究调用数为 0 |
| `.venv/bin/python -m pip check` | 0 | No broken requirements found（只覆盖已安装依赖，不代表 Streamlit 已安装） |
| `git diff --check` | 0 | 无输出；新增未跟踪文件不由该命令覆盖 |
| 激活 .venv 后执行下列规定启动命令 | 127 | streamlit: command not found |
| `curl --fail --max-time 5 http://127.0.0.1:8501/` | 7 | Failed to connect to 127.0.0.1 port 8501；Could not connect to server |

额外 DNS 诊断（Python 捕获异常，进程退出码 0，不代表联网通过）：`socket.getaddrinfo('pypi.org', 443)` 返回 `gaierror errno -3`。仅检查 PIP_NO_INDEX 是否启用，结果 False；未输出其他 pip 环境变量或凭证。安装错误本身不能证明版本不存在。

离线脚本关键原始输出：

```text
PASS: 10 input cases (missing/count/duplicates/separators/trim)
PASS: 4 mocked engine paths; zero real research calls
NOT TESTED: Streamlit rendering, buttons, running/error UI, local HTTP
```

HTTP 失败证据：

```text
curl: (7) Failed to connect to 127.0.0.1 port 8501 after 0 ms: Could not connect to server
```

## 主机侧恢复与最终复验

2026-10-16，用户提供主机侧恢复结果：

| 检查项 | 主机侧结果 |
|---|---|
| 项目 `.venv` 依赖 | `streamlit==1.50.0` 已安装 |
| 服务地址 | 服务已在 `127.0.0.1:8501` 运行 |
| `GET /` | HTTP 200 |
| `GET /_stcore/health` | HTTP 200，响应正文 `ok` |
| `.venv/bin/python reports/g2/verify_offline.py` | 仍为 PASS |

以上为用户提供的主机侧证据，不冒充本轮沙箱重新执行所得。首轮沙箱的依赖安装与 HTTP 失败记录保留作为过程证据，已不构成最终阻塞。

项目目录下的启动命令：

```bash
source .venv/bin/activate
streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

启动参数已将监听地址限制为 `127.0.0.1`，无需修改功能代码。本地 URL：`http://127.0.0.1:8501/`。

主机侧 HTTP 与离线复验命令：

```bash
curl --fail --max-time 10 -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8501/
curl --fail --max-time 10 -w '\n%{http_code}\n' http://127.0.0.1:8501/_stcore/health
.venv/bin/python reports/g2/verify_offline.py
```

依据主机补装、两项 HTTP 200、health 正文 `ok` 以及离线脚本持续 PASS，G2 最终判定为 **PASS**。HTTP 证据覆盖服务可达性与健康检查；未提供浏览器或 AppTest 的逐项交互证据，不将其表述为已执行，也未运行真实在线研究。

本轮仅更新 `reports/G2_RESULT.md`，不修改功能代码，**不进入 G3**。
