"""G1 single-query GPT Researcher adapter (no web server)."""

import argparse
import asyncio
import contextlib
import json
import os
import sys
import time
from urllib.parse import urlsplit

MODEL = "deepseek-flash"


def configure():
    """Use only the existing process credential; never persist its value."""
    if not os.environ.get("DEEPSEEK_API_KEY", "").strip():
        raise RuntimeError("MISSING_CREDENTIAL")
    # 本机 DNS 将公网解析到 198.18.0.1，用户已批准仅本项目开启。
    os.environ["ALLOW_PRIVATE_URLS"] = "true"
    for role in ("FAST_LLM", "SMART_LLM", "STRATEGIC_LLM"):
        os.environ[role] = f"deepseek:{MODEL}"
    os.environ.update(
        RETRIEVER="duckduckgo", CONTEXT_FILTER="keyword", LANGUAGE="chinese",
        MAX_ITERATIONS="1", MAX_SEARCH_RESULTS_PER_QUERY="3",
        TOTAL_WORDS="300", IMAGE_GENERATION_ENABLED="false",
        LANGCHAIN_TRACING_V2="false", LANGSMITH_TRACING="false",
    )


def redact(text):
    key = os.environ.get("DEEPSEEK_API_KEY")
    return text.replace(key, "[REDACTED]") if key else text


async def research(query: str, timeout: float = 300) -> tuple[str, list[str]]:
    """Return real report text and collected HTTP(S) URLs or raise an error.

    SDK compatibility and online behavior require validation after installation.
    The standalone CLI also imposes a process-wide deadline.
    """
    if not query.strip():
        raise ValueError("EMPTY_QUERY")
    if not 0 < timeout <= 300:
        raise ValueError("INVALID_TIMEOUT")
    configure()
    # Do not retain third-party debug output or exception bodies containing keys.
    with open(os.devnull, "w") as sink:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            from gpt_researcher import GPTResearcher

            async def run():
                agent = GPTResearcher(query=query.strip(), report_type="research_report", verbose=False)
                await agent.conduct_research()
                report = await agent.write_report()
                sources = agent.get_source_urls()
                urls = []
                for url in sources or []:
                    if not isinstance(url, str):
                        continue
                    parsed = urlsplit(url)
                    if parsed.scheme in ("https", "http") and parsed.hostname and not parsed.username and not parsed.password:
                        if url not in urls:
                            urls.append(url)
                if not isinstance(report, str) or not report.strip():
                    raise RuntimeError("EMPTY_REPORT")
                if not urls:
                    raise RuntimeError("EMPTY_SOURCES")
                return redact(report), [redact(url) for url in urls]

            return await asyncio.wait_for(run(), timeout=timeout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query")
    parser.add_argument("--check-config", action="store_true")
    parser.add_argument("--timeout", type=int, default=300, choices=range(1, 301), metavar="1..300")
    args = parser.parse_args()
    if not args.check_config and not (args.query and args.query.strip()):
        parser.error("provide a nonempty --query or --check-config")
    started = time.monotonic()
    try:
        configure()
        if args.check_config:
            from importlib.metadata import version
            result = {"credential_present": True, "sdk_version": version("gpt-researcher"),
                      "context_filter": "keyword", "runtime_verified": False}
        else:
            # asyncio cancellation cannot interrupt a synchronous SDK network call.
            import signal
            def deadline(signum, frame):
                os.write(2, b'{"error":"TIMEOUT"}\n')
                os._exit(124)
            signal.signal(signal.SIGALRM, deadline)
            signal.alarm(args.timeout)
            try:
                report, sources = asyncio.run(research(args.query, args.timeout))
            finally:
                signal.alarm(0)
            result = {"report": report, "source_urls": sources, "report_chars": len(report)}
        result.update(model=MODEL, retriever="duckduckgo", elapsed_seconds=round(time.monotonic()-started, 3))
        print(redact(json.dumps(result, ensure_ascii=False)))
        return 0
    except Exception as exc:
        from importlib.metadata import PackageNotFoundError
        if isinstance(exc, (ModuleNotFoundError, PackageNotFoundError)):
            code = "DEPENDENCY_MISSING"
        elif isinstance(exc, TimeoutError):
            code = "TIMEOUT"
        elif str(exc) in ("MISSING_CREDENTIAL", "EMPTY_REPORT", "EMPTY_SOURCES", "EMPTY_QUERY", "INVALID_TIMEOUT"):
            code = str(exc)
        else:
            code = "RESEARCH_ERROR"
        # Intentionally omit SDK error messages, headers and traceback locals.
        print(json.dumps({"error": code, "exception_type": type(exc).__name__, "model": MODEL,
                          "elapsed_seconds": round(time.monotonic()-started, 3)}), file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
