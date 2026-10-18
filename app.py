"""Single local G3 research and comparison page."""

import re
import subprocess
import unicodedata
from pathlib import Path

from comparison import run_comparison, markdown

import streamlit as st


def validate_inputs(topic, raw_names):
    topic = topic.strip()
    names = [name.strip() for name in re.split(r"[,，、;；\n]+", raw_names) if name.strip()]
    if not topic:
        raise ValueError("请输入研究主题。")
    if not 2 <= len(names) <= 3:
        raise ValueError("请输入 2～3 个竞品，不能少于 2 个或超过 3 个。")
    normalized = [unicodedata.normalize("NFKC", name).casefold() for name in names]
    if len(set(normalized)) != len(names):
        raise ValueError("竞品名称不能重复（忽略大小写及全角差异）。")
    return topic, names


def invoke_researcher(topic, names):
    """Keep G1 calls in bounded subprocesses and retain the resulting evidence."""
    return run_comparison(topic, names)


def main():
    st.set_page_config(page_title="竞澜研究 · Jinglan Insight", page_icon="🔎")
    st.title("竞澜研究")
    st.image(str(Path(__file__).parent / "assets/brand-cover.jpg"), caption="竞澜研究 · 原创品牌插图")
    st.caption("输入 2～3 个竞品，生成三维对比、建议及 Markdown。真实研究需手动触发，总计最多约 300 秒。")
    topic = st.text_input("研究主题", placeholder="例如：AI Agent 开发平台")
    raw_names = st.text_area("竞品名称（2～3 个）", placeholder="Dify、FastGPT、Langflow",
                             help="支持逗号、顿号、分号或换行分隔。")
    current = (topic, raw_names)
    if st.session_state.get("input_snapshot") != current:
        st.session_state.pop("pending", None)
        st.session_state.pop("comparison", None)
        st.session_state["input_snapshot"] = current

    if st.button("开始调研", type="primary"):
        st.session_state.pop("comparison", None)
        st.session_state.pop("pending", None)
        try:
            with st.spinner("正在校验输入…"):
                st.session_state["pending"] = validate_inputs(topic, raw_names)
        except ValueError as exc:
            st.error(str(exc))
        except Exception:
            st.error("输入处理失败，请重新填写后重试。")

    pending = st.session_state.get("pending")
    if pending:
        st.info("将调用研究引擎：输入已通过校验，尚未发起网络请求。")
        st.write(f"主题：{pending[0]}")
        st.write("竞品：" + "、".join(pending[1]))
        st.caption("手动调用会使用现有模型凭证，可能产生 API 费用。仅在本次会话保存报告。")
        if st.button("手动调用研究引擎（300 秒上限）"):
            # Consume the pending task so a rerun cannot repeat a paid request.
            st.session_state.pop("pending", None)
            with st.status("研究中，请稍候…", expanded=True) as status:
                try:
                    st.session_state["comparison"] = invoke_researcher(*pending)
                except (TimeoutError, subprocess.TimeoutExpired):
                    status.update(label="研究超时，已停止本次调用。", state="error")
                    st.error("研究超过时间上限，请重新提交后重试。")
                except Exception:
                    status.update(label="研究失败", state="error")
                    st.error("研究引擎调用失败，请检查本机依赖、凭证和网络后重新提交。")
                else:
                    status.update(label="研究引擎调用完成", state="complete")
                    st.success("本次研究完成；待核实内容请勿当作已确认事实。")

    result = st.session_state.get("comparison")
    if result:
        if all(field["pending"] for competitor in result["competitors"]
               for field in competitor["fields"].values()):
            st.warning("全部字段待核实：本次未获得可证实的逐项事实，不能作为有效对比结论。")
        content = markdown(result)
        st.markdown(content)
        st.download_button("下载 Markdown", data=content.encode("utf-8"),
                           file_name="competitor-comparison.md", mime="text/markdown")


if __name__ == "__main__":
    main()
