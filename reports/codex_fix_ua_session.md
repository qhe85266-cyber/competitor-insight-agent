已完成，未调用付费研究路径。

改动文件：

- `comparison.py`：抓取请求增加浏览器 UA、Accept、Accept-Language，其余核验逻辑不变。
- `tests/test_fetch_ua.py`：离线覆盖无浏览器 UA 失败、有 UA 可匹配，以及重核状态更新。
- `reports/g3/reverify_fetch.py`：读取现有 JSON，免费重核并输出 JSON/Markdown。
- `reports/FIX_FETCH_UA.md`：修复说明及操作命令。
- `reports/g3/reverified/comparison.{json,md}`：沙箱重核输出，原报告未覆盖。

验收：离线测试、`verify_minimal.py` 均退出 0。实际抓取受沙箱 DNS 失败影响，重核输出六项均保守保持待核实，需主机侧联网重跑。

关键命令：

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_fetch_ua.py' -v
.venv/bin/python reports/g3/verify_minimal.py
.venv/bin/python reports/g3/reverify_fetch.py --timeout 10
.venv/bin/python comparison.py --validate reports/g3/reverified/comparison.json
```