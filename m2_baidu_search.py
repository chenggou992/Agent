import os
import json
import requests
from openai.types.chat import ChatCompletionMessageToolCall

# ── 配置 ──────────────────────────────────────────────────
API_KEY = os.environ.get("BAIDU_AI_SEARCH_API_KEY", "")
API_URL = "https://qianfan.baidubce.com/v2/ai_search"


# ── Tool Definition（供 LLM function calling 使用）────────
TOOL_DEF: dict = {
    "type": "function",
    "function": {
        "name": "baidu_search",
        "description": (
            "使用百度AI搜索引擎检索互联网上的实时信息。"
            "当需要获取最新资讯、事实查询或不确定的知识时调用此工具。"
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "要搜索的关键词或问题",
                },
                "num_results": {
                    "type": ["integer", "null"],
                    "description": "返回的搜索结果条数，默认为 5，最大为 10",
                },
            },
            "required": ["query", "num_results"],
            "additionalProperties": False,
        },
    },
}


# ── 搜索实现 ──────────────────────────────────────────────
def baidu_search(query: str, num_results: int = 5) -> str:
    if not API_KEY:
        return "错误：未找到环境变量 BAIDU_AI_SEARCH_API_KEY，请先配置 API Key。"

    num_results = max(1, min(10, num_results))

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "messages": [{"role": "user", "content": query}],
    }

    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.Timeout:
        return "错误：百度搜索请求超时，请稍后重试。"
    except requests.exceptions.HTTPError as e:
        return f"错误：HTTP {e.response.status_code} — {e.response.text}"
    except requests.exceptions.RequestException as e:
        return f"错误：网络请求失败 — {e}"
    except ValueError:
        return "错误：响应内容无法解析为 JSON。"

    return _format_results(query, data, num_results)


def _format_results(query: str, data: dict, num_results: int = 5) -> str:
    references = (
        data.get("references")
        or data.get("results")
        or data.get("data")
        or []
    )
    references = references[:num_results]
    if not references:
        return f"搜索「{query}」未找到相关结果。"

    lines = [f"搜索关键词：{query}\n"]
    for i, item in enumerate(references, 1):
        title   = item.get("title", "（无标题）")
        url     = item.get("url", "")
        snippet = item.get("content") or item.get("snippet") or item.get("summary", "")
        date    = item.get("date", "")
        lines.append(f"[{i}] {title}")
        if date:
            lines.append(f"    日期：{date}")
        if url:
            lines.append(f"    链接：{url}")
        if snippet:
            lines.append(f"    摘要：{snippet[:300]}")
        lines.append("")

    return "\n".join(lines).strip()


# ── Tool Call 分发 ────────────────────────────────────────
def handle_tool_call(tool_call: ChatCompletionMessageToolCall) -> str:
    if tool_call.function.name != "baidu_search":
        return f"未知工具：{tool_call.function.name}"

    try:
        args = json.loads(tool_call.function.arguments)
    except (json.JSONDecodeError, TypeError):
        return "错误：工具参数解析失败。"

    query = args.get("query", "")
    num_results = int(args.get("num_results") or 5)

    if not query:
        return "错误：搜索关键词不能为空。"

    return baidu_search(query, num_results)
