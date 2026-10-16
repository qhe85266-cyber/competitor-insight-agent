# G3 交付结果（最终结论）

总状态：**CONDITIONAL（六维原文摘录均已匹配；仍需人工复核来源权威性/时效/维度归类；浏览器下载人工点击证据归 G4）**。

更新日期：2026-10-16（Asia/Shanghai）。主题为 **AI Agent 开发平台**，竞品为 **Dify + FastGPT**。

## 本轮修复（fetch UA）

根因：`fetch_text` 裸 `urlopen` 无 User-Agent，`https://dify.ai/zh` 返回 HTTP 403。Codex 已为请求增加浏览器式 `User-Agent`/`Accept`/`Accept-Language`。详见 [FIX_FETCH_UA.md](FIX_FETCH_UA.md)。

主机侧免费重核（不调用 DeepSeek）：

```bash
.venv/bin/python reports/g3/reverify_fetch.py --timeout 15   # exit 0；六维均为 excerpt_matched
.venv/bin/python comparison.py --validate reports/g3/reverified/comparison.json  # exit 0 STRUCTURE_VALID
.venv/bin/python -m unittest discover -s tests -p 'test_fetch_ua.py' -v  # exit 0，2 tests OK
.venv/bin/python reports/g3/verify_minimal.py  # exit 0 PASS
```

已将 `reports/g3/reverified/comparison.{json,md}` 提升为 `reports/g3/comparison.{json,md}`（JSON/MD 经 `markdown()` 一致；原始 `created_at` 保留为研究采集时间）。

## 交付产物

- [comparison.json](g3/comparison.json)：30,068 字节
- [comparison.md](g3/comparison.md)：3,608 字节
- 研究采集时间：`2026-10-16T12:38:16.448378+00:00`（北京时间 20:38:16）
- UA 重核时间：2026-10-16 约 20:54 CST

## 逐字段核验状态（重核后）

| 竞品 | 维度 | JSON 状态 | 当前结论 |
| --- | --- | --- | --- |
| Dify | 产品定位与功能 | `kind=fact`、`pending=false`、`fetch_status=excerpt_matched` | 原文摘录匹配（来源 `https://dify.ai/zh`） |
| Dify | 定价/商业模式 | `kind=fact`、`pending=false`、`fetch_status=excerpt_matched` | 原文摘录匹配 |
| Dify | 差异化特点 | `kind=fact`、`pending=false`、`fetch_status=excerpt_matched` | 原文摘录匹配 |
| FastGPT | 产品定位与功能 | `kind=fact`、`pending=false`、`fetch_status=excerpt_matched` | 原文摘录匹配 |
| FastGPT | 定价/商业模式 | `kind=fact`、`pending=false`、`fetch_status=excerpt_matched` | 原文摘录匹配（第三方博客许可证描述，须对照官方） |
| FastGPT | 差异化特点 | `kind=fact`、`pending=false`、`fetch_status=excerpt_matched` | 原文摘录匹配 |

`fact/excerpt_matched` 仅表示摘录匹配本次抓取页面文本，不证明来源权威性、时效、维度归类或比较结论正确。

## 验证证据

| 检查 | 结果 | 证据边界 |
| --- | --- | --- |
| UA 离线 unittest | exit 0，2 OK | 不证明真实联网 |
| `verify_minimal.py` | exit 0 PASS | 离线替身 |
| `reverify_fetch.py` 主机联网 | exit 0，六维 `excerpt_matched` | 仅 HTTP 重核，未付费研究 |
| `--validate` | exit 0 `STRUCTURE_VALID` | 结构约束 |
| JSON↔MD 一致 | PASS | `markdown(result)` |
| 主机 8501 | 监听中 | health 另证；浏览器下载归 G4 |

## 关卡边界

G3 功能与六维摘录匹配已具备证据。仍记 **CONDITIONAL**：人工语义复核与浏览器下载验收未在本文件宣称完成；进入 G4 做测试与端到端交付。
