# AI 竞品调研 Agent：G0 完整技术方案

日期：2026-10-16（Asia/Shanghai）。工作目录：`/workspace/competitor-insight-agent`。本方案依据仓库中的《01_GrokBot_监工方案.md》《02_CodexCLI_开工方案.md》及本次用户验收要求制定。

本轮交付范围为 G0 文档返工：实测环境和网络，确定模型、检索、结构化报告方案，给出 G1–G4 的文件、命令与证据要求。本文中的安装、开发和验收命令均为后续执行计划，除明确标为“实测”的命令外，本轮没有执行。没有编写功能代码，没有安装依赖，没有调用收费模型，没有启动服务。方案文档是否通过 G0 由监工依据本文验收；运行环境存在阻碍，不据此宣称 G1 通过。

## 1. 环境实测结果

### 1.1 执行边界与时间

实测时间为 `2026-10-16T12:12:12.563621+00:00`，即北京时间 20:12 左右。执行环境为当前 `workspace-write` 沙箱，允许修改本项目及 `/tmp`，网络受限，不能提权。项目中未发现适用的 `AGENTS.md`。原始需求文档、`.env.example`、`.gitignore` 和 reports 目录均已存在；本次检查时完整的 `reports/CODEX_PLAN.md` 不存在，reports 中有约 1KB 的 `CODEX_PLAN_summary_incomplete.md`。该摘要保留为历史材料，本文件直接承载完整方案。

### 1.2 实际命令与结果

| 检查项 | 实测命令 | 实测输出或结论 |
|---|---|---|
| Python | `python3 --version` | `Python 3.13.5` |
| Git | `git --version` | `git version 2.47.3` |
| Codex CLI | `codex --version` | `codex-cli 0.160.1` |
| Codex 是否已登录 | `codex login status`，原始输出不展示 | 是 |
| 项目所在磁盘 | `df -h .` | overlay 总容量 126G，已用 8.8G，可用 111G，使用率 8% |
| DeepSeek 变量是否非空 | Python 仅读取存在性 | `DEEPSEEK_API_KEY` 已存在且非空 |
| Tavily 变量是否非空 | Python 仅读取存在性 | `TAVILY_API_KEY` 未设置或为空 |
| 研究 SDK | `importlib.metadata.version('gpt-researcher')` | 当前解释器未安装 |
| UI | `importlib.metadata.version('streamlit')` | 当前解释器未安装 |
| DeepSeek 适配包 | `importlib.metadata.version('langchain-deepseek')` | 当前解释器未安装 |

Codex 版本命令附带“无法创建 PATH aliases，文件系统只读”的警告，但能输出版本。登录检查只记录“是”，不展示账号、认证方式、凭证内容或登录文件。环境变量检查也仅记录存在性；不执行 `env`、`printenv`、`set -x` 或输出配置对象。Git 已有仓库，存在未跟踪的输入文档和配置文件，不能把它们当作可删除的临时文件，也不能用 `git reset --hard` 或 `git clean` 清理。

磁盘目前没有显著容量阻碍，但不代表内存、CPU、浏览器依赖或所有 Python 轮子已验证。G1 优先使用现有 Python 3.13.5 的独立 `.venv`，由实际依赖解析、安装和导入决定兼容性；若某依赖无可用轮子，不立即改系统 Python。当前未完成真实安装，因此“Python 可执行”和“SDK 可运行”必须分开记录。

## 2. “外网 DNS”沙箱内重新实测

### 2.1 本次执行方法与原始结果

本次直接在当前工作目录、当前 workspace-write 沙箱内运行 Python 标准库 HTTPS 请求，没有切换到沙箱外，没有使用特权网络。实际测试脚本如下，可在 G1 前原样复测：

```bash
python3 - <<'PY'
import urllib.request
for url in ('https://pypi.org', 'https://github.com'):
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            print(url, 'PASS', response.status)
    except Exception as exc:
        print(url, 'BLOCKED', type(exc).__name__, str(exc))
PY
```

本次实际输出：

```text
https://pypi.org BLOCKED URLError <urlopen error [Errno -3] Temporary failure in name resolution>
https://github.com BLOCKED URLError <urlopen error [Errno -3] Temporary failure in name resolution>
```

结论：**当前 workspace-write 沙箱内，两站均为 BLOCKED，原因是名称解析失败。** 请求未获得 HTTP 响应，不能声称遇到 HTTP 403、证书失败或站点宕机。该结论只覆盖本次环境和时点，不等于云服务器宿主机、其他容器或外部文档工具也无法联网。测试脚本捕获异常后进程可正常退出，因此不能用它的进程退出码 0 作为联网通过的证据，必须检查每个 URL 的结果。

### 2.2 文档查阅与运行网络的区别

本轮通过独立的网页查阅工具读取了 GPT Researcher、DeepSeek、Tavily 的官方资料。该工具可读取文档不构成本地 `pip`、Git、搜索和模型 API 联通的证明。DeepSeek 首页的直接抓取曾超时，但其模型与价格文档成功读取。本文同时保留本地网络 BLOCKED 与官方文档依据，两类证据互不替代。

### 2.3 对 G1 的影响与恢复条件

现阶段无法承诺从 PyPI 下载依赖，也无法承诺 GitHub 原始来源可访问。即使以后这两个首页返回成功，还需分别验证包文件下载、DeepSeek API、DuckDuckGo 检索和目标竞品官网；首页成功只是初步条件。不得关闭 TLS 校验、写死站点 IP、擅改 `/etc/resolv.conf`、改系统代理或请求绕过沙箱作为默认修复。

恢复条件为：在获准的同一运行环境内重新执行 HTTPS 检查并留存时间、站点、状态；随后完成依赖解析和真实在线调用。可供用户或环境管理员选择的处理方法是修复受控环境的 DNS/出站策略，或提供有来源、版本及哈希的离线依赖包。离线包只能解决安装，不解决在线模型和搜索访问。网络仍失败时，在 G1 报告写明 `BLOCKED: NETWORK_DNS`，记录异常、受影响步骤、已尝试次数和恢复条件，不能换成静态结果宣布通过。

## 3. DeepSeek 接入 gpt-researcher 的配置方案

### 3.1 官方资料与模型名冲突处理

已查阅 [GPT Researcher 模型配置](https://docs.gptr.dev/docs/gpt-researcher/llms)：其 DeepSeek 示例使用 `deepseek:deepseek-chat`，并使用 `DEEPSEEK_API_KEY`。同页也支持通过 OpenAI 兼容协议配置自定义模型。已查阅 [DeepSeek 当前模型与价格页](https://api-docs.deepseek.com/quick_start/pricing/)：本次页面列出的模型为 `deepseek-flash`、`deepseek-v4-pro`，OpenAI 格式的 base URL 为 `https://api.deepseek.com`。

因此本方案不把旧示例中的 `deepseek-chat` 当作已经验证可用的当前服务模型。G1 推荐先选 `deepseek-flash`，三个 LLM 角色先统一使用同一个模型，减少排错变量。`deepseek-v4-pro` 只作为用户批准后可评估的替代选项，不自动升级或同时调用。模型目录随服务变化，G1 必须记录实际模型名和调用结果；若当前账号不支持候选模型，则标 BLOCKED 并更新选型依据，而不是盲猜别名。

### 3.2 首选配置与备选配置

首选为原生 DeepSeek provider，以下仅为后续 G1 配置示意，当前没有导出或调用：

```bash
export FAST_LLM=deepseek:deepseek-flash
export SMART_LLM=deepseek:deepseek-flash
export STRATEGIC_LLM=deepseek:deepseek-flash
export RETRIEVER=duckduckgo
export LANGUAGE=chinese
export CONTEXT_FILTER=keyword
```

继续使用已有 `DEEPSEEK_API_KEY`，不重新索取密钥，不在 `.env.example` 写入真实值。原生 provider 需要的适配依赖候选为 `langchain-deepseek`，实际以选定 SDK 版本的依赖和构造器为准；G1 检查其是否自动读取已有变量、默认 base URL 是否为官方地址。`base_url` 的具体传参必须在锁定版本中核对，不能凭名称发明一个 SDK 不识别的环境变量。若原生 provider 允许明确传入 base URL，则适配层传入 `https://api.deepseek.com`，不得拼接重复的 `/chat/completions`。

如果锁定的原生 provider 对新模型或参数有限制，备选使用 GPT Researcher 已文档化的 OpenAI 兼容路径。仅在业务进程内部把 `OPENAI_API_KEY` 映射为现有 `DEEPSEEK_API_KEY`，设置 `OPENAI_BASE_URL=https://api.deepseek.com`，三个角色改为 `openai:deepseek-flash`。该路径调用的仍是 DeepSeek 服务，不要求新增 OpenAI 密钥。映射不写入 shell 初始化文件，不覆盖用户的全局配置，不把值输出到日志。首选和备选一次只启用一套，避免模型走错端点。兼容协议的参数、结构化输出与错误码仍要真实验证，协议兼容不保证全部高级功能兼容。

### 3.3 Embedding 隐性依赖处理

DeepSeek 聊天 API 不能被直接假定为 embedding 服务。为避免 SDK 默认配置意外要求额外密钥，本 MVP 采用官方 [Context Filter 文档](https://docs.gptr.dev/docs/gpt-researcher/gptr/context-filter) 描述的本地关键词过滤，显式设置 `CONTEXT_FILTER=keyword`，不接向量库、不安装本地大模型、不下载 embedding 权重。G1 必须核对所装版本确实支持该模式，并在真实日志中确认未构造默认远程 embedding。若该版本仍强制初始化其他模型，作为配置兼容阻碍处理，不能填假 key 或悄悄新增收费供应商。

### 3.4 G1 中的调用与故障控制

执行顺序为依赖安装与导入、配置解析、一次低输出的模型探针、一次搜索探针、一次研究任务。模型探针及研究任务均需满足费用批准条件。仅记录请求时间、provider、模型名、响应状态、耗时、可获得的 usage 和脱敏错误，不保存 Authorization 请求头或完整客户端对象。已有 key 只说明配置存在，不说明余额、有效性、地区访问和模型权限正常。

普通 DNS/TLS 错误不反复付费重试；401/403 停止并标记凭证或权限问题；余额不足停止；429/5xx 采用有限退避，最多两次重试且受整任务时限约束。建议起始上限为单次网络请求 60 秒、研究任务总计 300 秒、竞品串行执行、任务不并发堆积。这些是项目控制目标，G1 根据 SDK 实际支持的接口落地。费用未知时不能用请求数上限冒充金额硬上限；没有预算授权就只完成免费预检，并把收费步骤标 BLOCKED。

## 4. 搜索方案：DuckDuckGo 与 Tavily

GPT Researcher 的 [搜索引擎文档](https://docs.gptr.dev/docs/gpt-researcher/search-engines) 支持 `RETRIEVER=duckduckgo` 和默认 Tavily；[Tavily Search API](https://docs.tavily.com/documentation/api-reference/endpoint/search) 使用 API key 并提供结构化检索能力。

| 比较项 | DuckDuckGo 路线 | Tavily 路线 |
|---|---|---|
| 凭证 | 本方案使用免 key 检索器 | 需要 `TAVILY_API_KEY` |
| 当前条件 | 无需新增密钥，但本地连通性未验证 | 当前环境没有非空 key |
| 费用 | 无需购买搜索 API；模型仍可能收费 | 额度、计费和预算需另行确认 |
| 配置 | `RETRIEVER=duckduckgo` | `RETRIEVER=tavily` |
| 工程评估 | 起步配置少，适合先验证最小流程 | 服务接口适合后续需要更明确的检索参数时评估 |
| 风险 | 可能受到限流、反爬、结果波动或依赖变化影响 | 凭证、配额、费用和供应商可用性影响流程 |
| 本项目选择 | G1 首选 | 经批准后作为备选 |

推荐理由是先利用已有 DeepSeek 变量和免 key 搜索，减少新增账号与费用审批。该推荐不是声称 DuckDuckGo 更可靠，也不是声称其已经实测成功。G1 对同一公开查询记录结果数量、标题、真实 URL 和耗时；结果为空时应区分“搜索正常但未找到”与“检索器报错”。若持续不可用，保留 BLOCKED 证据，再提出 Tavily 备选所需的 key、额度和批准事项，不能自动注册服务或暗中切换。

采集策略为官网、官方文档及官方 GitHub 优先，价格优先定价页且标注采集日期、币种、计费周期、套餐对象和自托管/云服务差异。搜索摘要只帮助发现来源，不足以证明具体价格或功能。DuckDuckGo 不依赖未经核实的服务端域名过滤参数，必要时通过查询词和应用侧 URL 校验选择官方来源。无法访问页面时保留失败信息，将受影响字段写“待核实”；全体来源获取失败则研究任务失败，不能输出貌似完整的成功报告。

## 5. 推荐目录、文件职责与数据流

以下是未来分关创建的目标结构，本轮只写本方案：

```text
competitor-insight-agent/
├── app.py                        # G2：唯一 Streamlit 页面和会话状态
├── researcher.py                 # G1：配置、SDK 调用、超时、CLI 研究入口
├── comparison.py                 # G3：字段结构化、逐项证据、Markdown 生成
├── requirements.txt              # G1 起：核实后固定直接依赖版本
├── requirements.lock.txt         # G1 起：当前平台验证后的完整依赖快照
├── requirements-dev.txt          # G4：固定测试依赖
├── .env.example                  # G1：配置项和空密钥占位
├── .gitignore                    # G1：本地环境、凭证、脱敏前日志忽略
├── README.md                     # G1 起草，G4 完善：安装、启动、故障和费用
├── tests/                        # G4：输入、证据、错误路径和页面回归测试
└── reports/
    ├── CODEX_PLAN.md             # 本文，完整 G0 方案
    ├── G1_RESULT.md              # G1 状态、命令、退出码、真实来源核验
    ├── G2_RESULT.md              # G2 本机交互及错误提示证据
    ├── G3_RESULT.md              # G3 逐字段来源与下载证据
    ├── G4_RESULT.md              # G4 测试和真实端到端验收
    └── g1/、g3/、g4/             # 分关脱敏运行产物；实际执行时才创建
```

界面只负责收集主题和 2–3 个名称、提交任务、显示状态、结果及下载，不直接拼接 SDK 的内部配置。研究层接收已校验的主题和竞品，调用 `GPTResearcher`，按 SDK 文档顺序执行 `conduct_research()`、`write_report()` 并获取来源。具体来源方法和返回类型以锁定版本确认；不得假定自由文本天然具有逐字段引用。[SDK 官方说明](https://docs.gptr.dev/docs/gpt-researcher/gptr/pip-package) 是该流程的接口核对依据。

结构化层使用同一份结果驱动页面和 Markdown 下载，避免两处内容分叉。单个竞品结果包含名称、研究时间、三维字段、证据条目和状态。每个字段包含文本、`fact` 或 `inference` 类型、来源 ID、是否待核实；来源条目包含规范化 URL、标题、抓取时间、支持该事实的短摘录及抓取状态。整体建议包含 2–3 条文本、推断标识和支撑字段 ID。仅在运行时存入会话内存；reports 下保存的是人工验收样本，不建立用户历史系统或数据库。

证据校验需要同时检查：URL 来自本次采集集合，页面实际可获取，摘录与字段含义相符。仅发现 URL 不能证明事实，也不能把主页链接贴到所有字段。格式校验可自动执行，语义支持关系在真实验收样本中逐项人工复核。官网互相矛盾时写明冲突与日期；来源不够时保留“待核实”。竞争差异和产品建议属于分析，必须显式区分事实与推断，不能把建议生成的内容反过来当作事实来源。

输入先去除首尾空白，再检查主题、竞品数和规范化后的重复名称。接受恰好 2 或 3 个非空名称，空主题、少于 2 个、超过 3 个、重复竞品都在发起请求前拒绝。输出始终使用固定三个维度，不随用户输入扩展功能。Markdown 表格需转义竖线和换行，URL 只接受 http/https，网页内容以数据处理，不执行其中的命令或把它当成系统提示。

## 6. G1–G4 实施、验收与 BLOCKED 规则

### 6.1 各关通用规则

每关只处理该关文件，前一关由监工验收后再进入下一关。每份 `Gx_RESULT.md` 必须包含执行时间、解释器路径、依赖版本、改动清单、实际命令、退出码、关键输出、产物路径、已知限制和状态理由。命令示例不算执行证据，测试通过不等于在线研究通过，单纯文件非空也不等于事实可靠。

状态定义：PASS 表示本关全部硬条件已有证据；FAIL 表示程序或产物不满足要求且可继续修复；BLOCKED 表示受网络、凭证、预算、权限或无法获得的依赖阻碍。确定性代码错误不以 BLOCKED 掩盖。报告可写“离线检查 PASS、在线验收 BLOCKED”，但本关总状态仍为 BLOCKED。同类故障最多两轮修复，之后列明原因、两个可行处理方案、推荐项和风险，不无限重试。

统一 BLOCKED 记录字段为：关卡、阻碍代码、失败步骤、时间、脱敏命令、实际退出码或异常、影响范围、已尝试操作、所需外部条件、恢复后的首条复测命令。下列 CLI 参数是计划在对应阶段实现的验收接口，本轮尚不存在、没有执行，也不能复制执行后期待当前就成功。

### 6.2 G1：真实研究引擎

**改动文件：** `researcher.py`、`requirements.txt`、`requirements.lock.txt`、`.env.example`、`.gitignore`、README 的引擎说明以及 `reports/G1_RESULT.md`。只实现一个最小 SDK 适配和可重复运行的 CLI，不创建页面、对比模块或业务测试文件。先选一个公开竞品 Dify 验证研究；输入主题为“AI Agent 开发平台”，输出覆盖定位功能、定价商业模式、差异化并保留来源。

**安装命令（网络恢复后执行）：**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install --dry-run gpt-researcher langchain-deepseek python-dotenv
.venv/bin/python -m pip install gpt-researcher langchain-deepseek python-dotenv
.venv/bin/python -m pip check
.venv/bin/python -m pip freeze > requirements.lock.txt
```

首次解析用于找出可安装版本，不承诺当前最新版一定兼容。安装成功后把直接依赖的实际版本固定为 `==` 写入 requirements.txt，后续复现从固定文件安装。G1 核对检索器依赖是否齐全；如需额外 DuckDuckGo 包，仅安装该 SDK 版本实际声明的包并记入依赖，不猜包名反复安装。完整快照对应 Python 3.13 和本机平台，不宣称跨平台通用。若解析失败，保留失败日志与版本约束，最多两轮有依据调整；需要系统编译工具或更换 Python 时停在 BLOCKED，不运行 sudo。

**验收命令（计划接口）：**

```bash
.venv/bin/python -m pip check
.venv/bin/python -c "from gpt_researcher import GPTResearcher; print('SDK_IMPORT_OK')"
.venv/bin/python researcher.py --check-config
.venv/bin/python researcher.py --probe-model
.venv/bin/python researcher.py --probe-search --query "Dify official documentation pricing"
.venv/bin/python researcher.py --topic "AI Agent 开发平台" --competitors "Dify" --output-dir reports/g1
```

`--check-config` 不发收费请求且不输出秘密；探针分别隔离模型和搜索问题。研究入口对外部请求设限，输出真实原文报告、来源集合和脱敏运行记录，并以非零码表示关键阶段失败。报告至少有一条来自实际成功抓取页面且与事实匹配的引用；至少人工核对一条事实，注明核验 URL 和支持内容。usage 可获得时记录，无法获得时明确“费用未知”，不能写 0。

**预期证据：** 实际版本、模型名、provider/base URL、检索器、开始结束时间、请求状态、真实报告、采集到的 URL、至少一条逐事实核验、每条命令退出码。只导入成功或仅有模型回答不满足 G1。G1 不要求完成三列横表，表格属于 G3。

**BLOCKED：** 当前已知为 `NETWORK_DNS`；未来还可能为 `DEPENDENCY_INSTALL`、`MODEL_AUTH`、`MODEL_BUDGET`、`SEARCH_UNAVAILABLE`。key 非空不能解除认证或预算阻碍。模型探针成功但搜索失败时保留前者证据，总关卡仍 BLOCKED。不产生伪造来源，也不通过关闭搜索绕开真实研究要求。

### 6.3 G2：单页输入与研究状态

**前提与改动文件：** G1 通过后，创建 `app.py`，按需调整 `researcher.py` 的状态回调和错误类型，更新两个依赖文件、README、`reports/G2_RESULT.md`。不增加 FastAPI、Next.js、用户系统和数据库。页面上半部是主题与竞品输入，下半部先显示研究原文和来源；G3 再增加标准对比输出。

**安装命令：**

```bash
.venv/bin/python -m pip install streamlit
.venv/bin/python -m pip check
.venv/bin/python -m pip freeze > requirements.lock.txt
```

将实际 Streamlit 版本写入 requirements.txt。**启动与验收命令：**

```bash
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
curl --fail --max-time 10 http://127.0.0.1:8501/_stcore/health
```

启动命令在独立终端运行，健康检查在另一终端执行，验收后正常结束服务。健康响应只证明服务存活，必须另做浏览器交互：空主题被拒绝；1 个和 4 个竞品被拒绝；重复名称被拒绝；合法 2 个及 3 个竞品可提交；运行时可见状态；重复点击不再次收费；模拟的受控错误和真实外部错误有清晰提示。异步 SDK 与页面事件循环的边界要验证，不把任务每次页面重绘都重新发起。新任务不能错误显示为上一任务成功，已有报告若保留必须标明所属输入。

**预期证据：** 本机 URL、服务实际启动记录、健康检查状态和退出码、逐项输入交互记录及截图（工具可用时）、至少一次合法输入实际到达 G1 引擎。截图不展示 key 或内部环境配置；产品页面只显示用户能理解的状态、重试提示和报告内容。输入被拒绝的场景应有零 API 请求证据。

**BLOCKED：** 若沙箱禁止本地监听，记录实际绑定异常为 `LOCAL_BIND`；若浏览器工具不可用，明确交互验收尚未完成，健康检查不能替代。若 UI 可工作但在线研究受网络阻碍，本关在线部分 BLOCKED，不把静态页面当作全关通过。未经批准不改成 `0.0.0.0` 或公网部署来解决验收访问问题。

### 6.4 G3：三维对比、逐项来源和 Markdown 下载

**前提与改动文件：** G2 通过后，创建 `comparison.py`，更新 `app.py`、必要的 `researcher.py` 证据返回结构、README、`reports/G3_RESULT.md`。以两家竞品 Dify、FastGPT 作为最低在线验收样本；支持第三家 Langflow，但不新增维度或历史功能。

**安装命令：** 本关优先复用现有依赖；固定依赖有变化才重新解析并更新快照。

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
```

**验收命令（结构化 CLI 在本关提供）：**

```bash
.venv/bin/python comparison.py --topic "AI Agent 开发平台" --competitors "Dify" "FastGPT" --output-dir reports/g3
.venv/bin/python comparison.py --validate reports/g3/comparison.json
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
```

结构化生成优先利用本次采集文本，在约束的格式中抽取；若需额外模型抽取，要计入同一任务预算。验证器检查竞品集合、恰好三维、字段类型、来源引用完整性、建议数量以及 URL 是否属于本次来源集合。对真实报告人工逐格检查六个单元格：有依据就写事实与链接，无法证实就写“待核实”，分析标为推断。不能为了满足结构完整强行补齐价格，也不能把抓取失败解释成竞品没有该功能。

**预期证据：** 一次真实两竞品报告、JSON 结构、三行两竞品横表、2–3 条建议、逐项来源或待核实、采集时间、人工事实抽查记录。浏览器实际点击下载，确认 UTF-8 Markdown 内容与页面同源，含主题、竞品、三维、建议及引用；保存下载文件并比对内容。仅校验链接语法不代表支持关系已核验，人工核验必须留说明。

**BLOCKED：** 搜索和页面访问受限标 `SOURCE_FETCH`；付费抽取未批准标 `MODEL_BUDGET`。JSON 格式不合法、引用错配、下载内容缺失属于 FAIL，应在本关修复。允许局部字段待核实，但所有字段都是待核实、没有可证实事实时不满足真实比较的验收条件。不得用单元测试里的固定样本冒充该关在线结果。

### 6.5 G4：测试、复现和最终交付

**前提与改动文件：** G3 通过后，添加 `tests/test_inputs.py`、`tests/test_comparison.py`、`tests/test_research_errors.py`，有必要时加入页面测试；完善 `requirements-dev.txt`、README 和 `reports/G4_RESULT.md`。修复确实暴露的问题，不额外扩展业务。测试只在本阶段创建，本轮 G0 不创建 tests 目录。

**安装命令：**

```bash
.venv/bin/python -m pip install pytest
.venv/bin/python -m pip freeze > requirements.lock.txt
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/python -m pip check
```

将实际 pytest 版本固定到 requirements-dev.txt；完整快照可含开发依赖并在 README 说明。**验收命令：**

```bash
.venv/bin/python -m pytest -q
.venv/bin/python comparison.py --topic "AI Agent 开发平台" --competitors "Dify" "FastGPT" "Langflow" --output-dir reports/g4
.venv/bin/python comparison.py --validate reports/g4/comparison.json
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
 git diff --check
 git status --short
```

测试覆盖有实际风险的边界：输入数量和空白重复、部分字段缺失、来源空集合、引用未知 ID、非法 URL、模型/API 超时、认证失败、限流和下载表格转义。离线测试用受控替身注入故障，不联网、不收费，并明确它们不证明真实联网成功。在线端到端样本独立执行，从浏览器输入合法数据直到 Markdown 下载，记录每段证据和实际退出状态。新建项目内验证虚拟环境按锁定依赖安装并运行 `pip check` 与测试，确认 README 指令可复现；如网络阻止重装，复现验收标 BLOCKED。

**预期证据：** pytest 总数及退出码、实际三竞品报告、本机健康与浏览器操作记录、下载文件、依赖版本、复现环境结果、已知限制清单。逐项复核 G0–G3 的通过记录，记录剩余待核实事实。检查本次修改及产物是否含当前秘密值时只输出命中文件名和数量，不输出匹配行；确认 `.env`、认证文件、原始敏感日志没有被 Git 跟踪。若存在泄漏，先停止发布并处理，不能仅把文件加入 ignore 当作已解决。

**BLOCKED：** 在线不可用时，即使全部离线测试通过也不能写最终 PASS；浏览器交互或复现安装未完成也应列明对应阻碍。功能断言失败记 FAIL，留修复与复测记录。最终完成必须同时有真实端到端证据与基础测试证据，不以“理论可运行”代替。

## 7. 风险、许可证与需用户批准事项

| 风险或事项 | 处理策略 | 是否需要用户批准 |
|---|---|---|
| DeepSeek 已有 key，但余额与调用预算未知 | 先做无费用预检，给出有限调用计划；计入模型探针、研究和抽取 | 涉及费用时，按仓库两份任务文档先批准预算；已有明确授权则沿用 |
| Tavily key 缺失 | 默认 DuckDuckGo，确需切换时列明额度与计费条件 | 新 key 接入、注册、购买或收费调用需要批准 |
| 本地 DNS 失败 | 当前标 BLOCKED，提供同环境复测证据 | 改系统 DNS、代理、出站策略需有权限的用户/管理员处理 |
| Python 3.13 或 SDK 依赖冲突 | 独立 venv、先解析、固定已验证版本 | 项目内常规依赖安装随对应关卡授权；系统安装或换系统 Python 需批准 |
| 模型命名及配置文档不同步 | 优先服务方模型目录，锁定 SDK 并做真实探针 | 常规兼容修复无需重复审批；新增服务和费用需批准 |
| 来源受限或价格信息变化 | 标时间、币种、套餐、待核实；不绕过付费墙和登录 | 不自行申请外部账号或购买资料 |
| 未认证页面暴露 | 仅监听 127.0.0.1，不上传研究数据 | 公网开放、防火墙、系统服务或部署需批准 |
| 范围膨胀与无限重试 | 只做 P0，分关验收，两轮同类修复上限 | 新功能与后续关卡按阶段批准 |
| 密钥或私人数据落入日志 | 只读取已有变量，脱敏输出，网页资料按不可信数据处理 | 不索取聊天中的明文 key；不自动把报告发送给他人 |

费用批准要求来自仓库《02_CodexCLI_开工方案.md》第 7 节的“涉及费用、系统级修改、开放公网、删除非项目文件等事项必须停下并申请用户批准”，以及监工方案的角色权限和失败处理规则。当前用户授权是重写 G0 文档，故本轮无需为文档再询问批准，也不把有 key 推断为允许无限制付费调用。此处是后续条件清单，不要求本轮先批准安装或开发。

许可证方面，已打开上游 [GPT Researcher LICENSE](https://github.com/assafelovic/gpt-researcher/blob/master/LICENSE)；[PyPI 包元数据](https://pypi.org/pypi/gpt-researcher/json) 同时出现 MIT 分类及描述中的 Apache 2 声明，不能仅凭包分类给出商业使用无风险结论。G1 锁定版本后保存发行包许可证和上游对应版本依据；G4 核对实际分发依赖、保留必要声明。发布前仍需消除不一致并按实际使用方式判断，不把“开源”直接等同于无条件可商用。此轮没有选定安装版，也没有声称全依赖许可证已审计。

操作方面只修改项目内目标文件，不删除输入文档，不覆盖已有秘密配置，不修改 `.git` 内部文件，不代替用户向 Grok Bot 或其他人发送消息。依赖、SDK 内部可能存在多步骤研究流程，但本项目不引入额外多 Agent 框架或新服务。没有数据库、账号、历史、PDF/PPT、定时调度或 Crawl4AI。

## 8. 下一步仅 G1

G0 文档返工到此为止，等待监工对本文内容验收；不在本轮创建 `app.py`、`researcher.py`、`comparison.py` 或 tests 业务实现。下一次获准推进时只执行 G1，不连带执行 G2–G4。

G1 的第一步是用第 2 节脚本复测当前沙箱 DNS/HTTPS，并检查 Python venv 和依赖解析条件。若仍出现相同错误，优先形成 `reports/G1_RESULT.md` 的 `BLOCKED: NETWORK_DNS` 证据，说明安装和在线研究尚未完成；不为制造进展绕过沙箱或假装联网。网络恢复后，按第 6.2 节隔离安装、锁定版本、检查配置和适配接口；费用授权满足后，才运行最小模型/搜索探针与一次真实 Dify 研究。

G1 的交付终点是可复查的真实报告、实际来源、脱敏调用记录和明确关卡状态。监工未验收 G1 前不进入 UI 开发。若 G1 被阻碍，给出具体恢复条件；若 G1 通过，报告建议“提交 G1 验收”，不擅自开始 G2。
