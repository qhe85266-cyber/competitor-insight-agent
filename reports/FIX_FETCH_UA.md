# 抓取 User-Agent 修复

根因：原 `comparison.py:fetch_text` 直接用 URL 调用 urlopen，未设置浏览器式 User-Agent。监工已核验 Dify 无 UA 返回 403、Mozilla/5.0 返回 200，且现有三条摘录经 normalize 均能匹配。FastGPT 此前未拦截该请求。

改动：仅给 fetch_text 构造标准库 Request，增加 Mozilla/5.0 浏览器式 User-Agent、Accept、Accept-Language；保留超时、读取上限、重定向 safe_url、页面解析及所有 normalize / exact excerpt / pending / unverified 规则。不新增依赖，不修改网络、DNS、代理或产品范围。

## 离线验收

在仓库根目录执行：

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_fetch_ua.py' -v
.venv/bin/python reports/g3/verify_minimal.py
```

本沙箱两项均退出 0。UA 测试使用 mock HTTP gate：默认 urllib 请求返回 403，新 fetch_text 的请求必须带浏览器 UA 和 Accept / Accept-Language 才返回页面；随后通过原 parse_fields 核验摘录。另覆盖现有 JSON 重核成功、抓取失败后事实降级、原摘录与来源保留，并禁止 subprocess 研究调用。测试数据不构成线上证据。

## 免费重核现有 JSON

```bash
.venv/bin/python reports/g3/reverify_fetch.py --input reports/g3/comparison.json --output-dir reports/g3/reverified --timeout 10
.venv/bin/python comparison.py --validate reports/g3/reverified/comparison.json
```

仅读取现有字段 quote 和 source_urls（当前每项一个 URL），按竞品来源白名单、safe_url、原摘录长度限制及原 parse_fields 的 fetch_text + normalize 精确匹配规则更新 kind / pending / fetch_status。其余字段保留，Markdown 用现有 markdown() 生成。同一竞品重复 URL 复用抓取结果。默认输入、输出与上述命令相同，可从任意目录直接运行脚本。

输出为 `reports/g3/reverified/comparison.json` 和 `comparison.md`，默认不覆盖原报告。可显式设置 `--output-dir reports/g3` 覆盖原 JSON/MD；建议监工先审核另存结果。脚本没有 DeepSeek、researcher.py 或 run_comparison 调用，不需要模型密钥或付费研究。

本沙箱已执行重核并生成上述另存文件，退出 0，但 HTTP 请求因 `URLError: [Errno -3] Temporary failure in name resolution` 无法完成，六项均保守标为 fetch_failed / unverified / pending。退出 0 仅表示结果文件成功生成，不表示所有摘录已匹配；终端逐项输出 fetch_status。原始 reports/g3/comparison.json 与 .md 未覆盖。请监工在可联网主机执行上面的两条重核命令，核对 Dify 三项是否为 excerpt_matched；若来源页面变化或抓取失败，仍保留待核实。
