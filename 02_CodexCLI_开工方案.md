# Codex CLI 开工方案：AI 竞品调研 Agent（最小 MVP）

> 交付对象：**Codex CLI（技术方案 + 编码 + 调试 + 测试唯一负责人）**  
> 监督对象：**Grok Bot（只监控、只验收、不写代码）**  
> 版本：MVP V1.0｜2026-10-16

## 1. 项目目标

开发一个**单页 AI 竞品调研工具**：用户输入研究主题及 2~3 个竞品 → 在线采集公开资料 → 生成横向对比表、建议和来源链接。

**一句话验收：** 我输入“AI Agent 开发平台”以及“Dify、FastGPT、Langflow”，点击按钮后，能获得有来源可核查的功能/定位、定价/商业模式、差异化分析结果；查不到的事实写“待核实”。

### 目标用户与价值

- 用户：AI 产品经理及需要做初步竞品研究的人员。
- 痛点：逐个找官网、对比功能与价格、写竞品报告耗时且难追溯来源。
- MVP 验证假设：真实在线研究是否能减少重复信息整理工作，并提供可核查的结构化结果。

## 2. 采用的 GitHub 开源项目（只用最小组合）

| 项目 | 官方仓库 | 本项目作用 | V1 使用方式 |
|---|---|---|---|
| **GPT Researcher** | <https://github.com/assafelovic/gpt-researcher> | 在线研究、搜索、归纳、提供来源 | **使用 Python SDK**；必要时阅读/固定对应版本的源码 |
| **Streamlit** | <https://github.com/streamlit/streamlit> | 极简 Web 界面 | 一个 `app.py` 页面，输入框/按钮/表格/结果下载 |
| **OpenAI Codex CLI** | <https://github.com/openai/codex> | 唯一开发执行器：方案、代码、测试和修复 | 云服务器终端运行，由 Grok Bot 派任务并检查输出 |
| Crawl4AI（备选，V1 不装） | <https://github.com/unclecode/crawl4ai> | 复杂网页采集 | 第一版明确不启用，默认先用 GPT Researcher 内置检索/采集 |

**授权提醒：** Streamlit 为 Apache-2.0；GPT Researcher 主仓库的 LICENSE 为 Apache-2.0，但部分包元数据标注 MIT，且有第三方依赖许可问题需要发布前检查。Codex 应在所选版本上核验完整许可证和依赖授权，不得在未核实时承诺商业化无风险。

官方参考：
- GPT Researcher SDK：<https://github.com/assafelovic/gpt-researcher/blob/main/docs/docs/gpt-researcher/gptr/pip-package.md>
- Streamlit 启动命令：<https://docs.streamlit.io/develop/api-reference/cli/run>
- Codex CLI 非交互模式：<https://learn.chatgpt.com/docs/non-interactive-mode>

## 3. 功能范围（P0：只做 3 项）

### F1 输入竞品

- 页面上有研究主题输入框。
- 输入 2~3 个竞品名称（分隔输入或多输入框）。
- 点击「开始调研」。
- 缺失输入、超出 3 个竞品、有重复名称时提示错误。

### F2 AI 自动研究

- 使用 **GPT Researcher SDK** 调用真实模型和检索器。
- 对每个竞品研究三个固定维度：
  1. 产品定位与核心功能
  2. 定价或商业模式
  3. 竞争特点和差异化
- 优先引用官网、官方文档、官方 GitHub；需要时补充其他公开可信来源。
- 显示“研究中”与失败提示。LLM 产出的事实必须被来源核验，不能仅凭模型记忆。

### F3 生成报告

- 一张横向对比表：列为竞品，行为固定三个维度。
- 简短结论：主要竞争差异 + 对目标产品的 2~3 条建议。
- 每条重要事实有 URL 或“待核实”；区分事实和推断。
- 结果能复制或下载为 Markdown 文本。

### 严格排除（V2 再说）

用户账号、数据库、历史报告、PDF/PPT、爬虫中台、定时监控、邮件通知、数据图表、复杂多 Agent、LangGraph、Next.js、FastAPI、向量库、部署到公网。不要因为觉得“更专业”而主动添加。

## 4. 产品流程与页面

```text
[输入研究主题 + 2~3 竞品]
             ↓
       [开始调研]
             ↓
    [GPT Researcher SDK]
     ├─ 搜索公开资料
     ├─ 提取对应维度
     └─ 收集原始 URL
             ↓
    [标准化/校验结果]
     ├─ 保留来源链接
     ├─ 不足信息标待核实
     └─ 生成横向对比表
             ↓
       [展示分析结果]
     ├─ 竞品对比表
     ├─ AI 建议
     └─ Markdown 下载
```

**界面：只有一个 Streamlit 页面。** 上半部分为输入；运行中显示状态；下半部分为表格、分析结论、来源链接、下载按钮。

## 5. 技术落地要求（由 Codex 最终确定细节）

### 极简技术栈

- Python：优先 3.12+，具体以选用 GPT Researcher 版本依赖为准。
- UI：Streamlit；入口 `app.py`。
- AI：`gpt-researcher` Python 包。
- 搜索：先从 GPT Researcher 支持的检索器中选一种，建议有合适账户时用 Tavily；也可以评估 DuckDuckGo。
- 模型：需选择 GPT Researcher 支持且可**程序化调用**的模型。模型服务可为 API 提供商或已部署的兼容本地服务。
- 无数据库；保存输出可仅用页面内状态及 Markdown 下载。

**成本与凭证说明（必须先说清）：**

- Codex CLI 的登录/订阅凭证，只用于让 Codex 做开发，**不等于**产品里的 GPT Researcher 自动获得模型调用权限。
- 运行时在线模型、搜索工具可能需单独的 API Key/服务额度；不可擅自创建收费账户或让用户把密钥直接发送给 Grok Bot 聊天消息。
- 若坚持完全不接付费 API，Codex 必须先验证可用的本地模型和搜索方案、内存/CPU 能力；如不可行，应报告阻碍，不可用 mock 结果伪装在线工作正常。

### 推荐代码结构

```text
competitor-insight-agent/
├── app.py                       # 唯一 Streamlit 页面
├── researcher.py                # GPT Researcher SDK 适配
├── comparison.py                # 字段归一化、来源对应与报告结构
├── requirements.txt             # 锁定/声明主要依赖版本
├── .env.example                 # 变量名占位，不填真实密钥
├── .gitignore                   # 忽略 .env、日志及临时文件
├── tests/
│   ├── test_inputs.py           # 输入和边界校验
│   └── test_comparison.py       # 输出结构与来源校验
├── reports/                     # Codex 计划与各关验收产物
├── README.md                    # 安装、运行和验证说明
├── 01_GrokBot_监工方案.md
└── 02_CodexCLI_开工方案.md
```

如无需独立 `comparison.py` 即可实现，也可简化，但必须保持测试可执行、业务逻辑与页面逻辑基本隔离。

### GPT Researcher SDK 验证思路

下面是要由 Codex **先验证版本兼容性**的最小代码思路，不代表已经在你的服务器运行成功：

```python
import asyncio
from gpt_researcher import GPTResearcher

async def research(query: str):
    agent = GPTResearcher(query=query, report_type="research_report")
    await agent.conduct_research()
    report = await agent.write_report()
    sources = agent.get_source_urls()
    return report, sources

# asyncio.run(research("研究 Dify 与 FastGPT 的产品定位、定价和差异"))
```

SDK 默认报告为自由文本，**不能假设它天然输出三列对比表、每个字段精确溯源**。Codex 必须增加结构化处理与不确定性标记；结构化结果的事实内容要对应实际来源证据。来源 URL 列表不等于每个字段已经获得核验。

## 6. Codex 的里程碑计划与验收

### G0：环境与方案（先做）

Codex 行动：

1. 检查服务器 Python 版本、网络可用性、磁盘空间、Git、Codex CLI 版本与登录状态（仅报告是否已登录，不打印凭证）。
2. 核对 GPT Researcher 当前 SDK 文档、Python 版本要求与实际安装兼容性。
3. 确认模型/检索器方案、可用凭证状态、可能费用与预算未知点。
4. 将最简单、可执行的落地方案保存为 `reports/CODEX_PLAN.md`，供 Grok Bot 验收。

交付条件：有环境检查结果、开发方案、风险和下阶段执行命令。此关**不做功能编码**。

### G1：真实研究引擎

Codex 行动：安装 SDK、编写可调用的 `researcher.py`；测试至少一个公开研究任务，保存报告与来源 URL。

验收：真实调用有执行证据；报告非空；来源 URL 可见。若没有可用模型/搜索凭证，标记 `BLOCKED`，不伪造 PASS。

### G2：单页输入界面

Codex 行动：构建 `app.py`，支持主题、2~3 个竞品、开始按钮、状态信息、异常提示。

验收：可以用 `streamlit run app.py --server.address 127.0.0.1 --server.port 8501` 本机启动；浏览器能输入并发起任务；未获得授权不得监听 `0.0.0.0` 对公网开放。

### G3：对比表、来源和建议

Codex 行动：规范竞品字段、来源匹配、待核实标记；生成三行横向对比表、2~3 条建议和 Markdown 下载。

验收：至少一组包含两家竞品的真实结果；三维字段完整（允许“待核实”）；信息有可点开的证据链接；结论不冒充事实。

### G4：测试与交付

Codex 行动：覆盖输入验证、结果缺失、模型/API 异常、引用为空等测试场景；整理启动脚本/README/日志和版本依赖；验收 G0~G3。

验收：基础测试均有实际命令与退出码；至少一组真实端到端调研结果；README 能指导新机器配置并运行；无密钥泄漏。

## 7. 给 Codex 的完整开工指令（可以直接粘贴）

> 你是 Competitor Insight Agent 项目的**唯一技术方案负责人、编码执行者和测试执行者**。Grok Bot 是监工，不写代码，也不替你做技术决策；它不懂的地方，你应主动提供技术方案、验证方法和证据。
>
> 请阅读本文件 `02_CodexCLI_开工方案.md` 与 `01_GrokBot_监工方案.md`。项目目标是开发仅有一个 Streamlit 页面、三个 P0 功能的 AI 竞品调研 Agent：输入研究主题/2~3 个竞品 → 基于 GPT Researcher SDK 真实检索公开资料 → 输出产品定位与功能、定价/商业模式、差异化三个维度的竞品对比表、2~3 条建议和来源 URL，且找不到信息时写“待核实”。
>
> 现在只执行 **G0 环境检查与技术方案**，先不要实现功能代码。请检查 Python/Git/Codex CLI、依赖兼容、模型和检索配置、运行时 API 需要哪些凭证，核实公开项目的许可证和使用限制。然后将技术方案、目录结构、按 G1~G4 的开发顺序、验收命令、依赖成本和风险写入 `reports/CODEX_PLAN.md`，给出可核查的命令输出和下一步建议。
>
> 每做完一关，产出 `reports/Gx_RESULT.md`，附变更清单、真实运行/测试证据、退出码、风险和下一关建议；不许只说“完成”。由 Grok Bot 验收后再执行下一关。涉及费用、系统级修改、开放公网、删除非项目文件等事项必须停下并申请用户批准。不要额外加登录、数据库、复杂多 Agent、PDF/PPT、定时监控和部署平台。

## 8. 开始执行前：服务器准备命令

由**具有权限的操作者**在云服务器受限项目目录运行（不要在系统目录乱执行；如果已有项目仓库，Codex 先确认它是否含有未提交的重要改动）。

```bash
# 1. 环境检查
python3 --version
git --version
codex --version
codex exec --help

# 2. 建立独立项目目录（仅限新项目）
mkdir -p ~/projects/competitor-insight-agent
cd ~/projects/competitor-insight-agent

# 3. 如果是全新空目录，初始化 Git
# 若已经有仓库，不要重复初始化
git init

# 4. 将这两份 Markdown 文件放到当前项目根目录
# 5. 先向 Codex 索要 G0 技术方案（只读）
mkdir -p reports
codex exec --sandbox read-only -o reports/CODEX_PLAN.md \
  '读取 02_CodexCLI_开工方案.md 和 01_GrokBot_监工方案.md，只执行 G0：核查环境并提出技术方案，不编写功能代码。输出依赖、目录、风险、各里程碑测试方法。'
```

注意：`codex exec` 的只读沙箱下，最终答复可以由 CLI 的 `-o` 写到报告文件，但 Codex 自身不应修改源码。若文件由 Grok Bot 通过上传/复制方式落入项目目录，需要先核对文件名与内容。若 CLI 无法使用订阅登录执行，请先通过官方登录步骤解决，不能默认用模型 API Key 替代订阅。

## 9. MVP 结束后的真实验收演示

示例输入：

- 主题：`AI Agent 开发平台`
- 竞品：`Dify`、`FastGPT`、`Langflow`
- 对比维度（固定）：`产品定位与功能`、`定价/商业模式`、`差异化特点`

预期结果（结构示例，**不是现成的竞品事实**）：

| 维度 | Dify | FastGPT | Langflow |
|---|---|---|---|
| 产品定位与功能 | 事实摘要 + 来源 URL | 事实摘要 + 来源 URL | 事实摘要 + 来源 URL |
| 定价/商业模式 | 事实摘要 / 待核实 | 事实摘要 / 待核实 | 事实摘要 / 待核实 |
| 差异化特点 | 有依据的分析 + 来源 | 有依据的分析 + 来源 | 有依据的分析 + 来源 |

表格之后给出 2~3 条分析建议，并明确“事实”与“AI 推断”。有真正的检索日志、可访问的来源、错误处理和 Markdown 下载，即达到第一版产品目标。

## 10. 注意事项

1. **别让 Codex 自己无限加功能。** 不在 P0 内的一律进入未来待办。
2. **别让 Grok Bot 充当开发者。** 不懂技术，只让 Codex 解释和实施，Grok Bot 核对证据。
3. **别把开发订阅当成业务 API。** Codex CLI 负责写代码；GPT Researcher 的运行另需实际可用的模型与检索方案。
4. **别伪造来源或成果。** 只把实际跑出的结果、测试与项目贡献写进简历。
5. **别开放未加认证的演示服务到公网。** 先本机测试，通过 SSH 隧道等方式安全访问；公网部署须获得用户批准并设计最基本访问控制。
