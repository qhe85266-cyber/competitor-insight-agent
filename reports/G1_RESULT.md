# G1 验收结果

**最终结论：PASS**（2026-10-16，依据监工主机侧真实复测产物及用户确认）。

仅完成 G1 最小修改；未实现 G2/G3/G4，未修改方案文档。未打印或保存密钥。

## 安装成功证据

监工主机侧安装成功记录见 `reports/SUPERVISION_LOG.md` 的 G1 条目，包含 `SDK_IMPORT_OK` 与配置检查通过。本轮通过 `.venv/bin/python` 的 `importlib.metadata.version()` 再次确认实际已安装版本：

```text
gpt-researcher==0.16.1
langchain-deepseek==1.1.1
python-dotenv==1.2.4
ddgs==9.16.0
```

`requirements.txt` 已将 ddgs 固定为 `ddgs==9.16.0`，其余包版本未变；这是直接依赖清单，不是完整传递依赖锁文件。

## 首轮阻碍与主机复测路径

首轮沙箱 DNS 解析失败（`Temporary failure in name resolution`），安装和真实研究验收为 **BLOCKED**。随后监工在主机侧完成安装，搜索及模型调用可用，但本机 DNS/代理将公网域名解析到 `198.18.0.1`，触发 SDK 的非公网地址检查，抓取被跳过；该轮无有效正文，仍为 BLOCKED。

用户已明确批准仅本项目开启 `ALLOW_PRIVATE_URLS=true`。监工据此在主机侧复测成功；`researcher.py` 的 `configure()` 现设置此进程环境变量并注明依据，未修改系统 DNS 或系统全局环境配置。

主机复测命令（项目目录 `/workspace/competitor-insight-agent`）：

```bash
ALLOW_PRIVATE_URLS=true .venv/bin/python researcher.py --query 'Dify official documentation pricing' --timeout 300 > /tmp/g1-retest-out.json 2> /tmp/g1-retest-err.txt
```

## 真实报告证据

读取主机复测产物 `/tmp/g1-retest-out.json`，结果如下；错误输出文件 `/tmp/g1-retest-err.txt` 为空。本轮未重复调用计费模型。

- `report_chars`: **7576**；本轮重新计算 `len(report)` 同为 **7576**，与用户所述约 7.5KB 报告对应（字符数不等于 UTF-8 字节数）。
- 来源 URL 数量：**5**。
- `elapsed_seconds`: **52.114** 秒。
- 输出记录的模型名：`deepseek-flash`（CLI 配置模型名，不冒充 API 响应中的模型标识）。
- 检索器：`duckduckgo`。

来源 URL 列表（直接取自复测产物）：

- https://dify-hosting.com/en/guides/dify-pricing/
- https://dify.ai/pricing
- https://www.architjn.com/blog/dify-cloud-pricing-plans-open-source-guide-2026-full-breakdown
- https://aipriceradar.com/tool/dify-pricing
- https://dify.ai/pricing/dify-cloud

以上 PASS 依据为已生成真实报告及非空来源列表，不代表对报告全部事实逐条核验。

## 修改后配置检查

按用户要求执行：

```bash
ALLOW_PRIVATE_URLS=true .venv/bin/python researcher.py --check-config
```

退出码 **0**，输出：

```json
{"credential_present": true, "sdk_version": "0.16.1", "context_filter": "keyword", "runtime_verified": false, "model": "deepseek-flash", "retriever": "duckduckgo", "elapsed_seconds": 0.016}
```

`runtime_verified=false` 是配置检查自身的输出语义；该命令不执行在线研究，在线通过证据来自上述主机复测。
