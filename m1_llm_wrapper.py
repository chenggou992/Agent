import os
from openai import OpenAI

# ── 固定配置 ──────────────────────────────────────────────
BASE_URL    = "https://api.siliconflow.cn/v1"
MODEL       = "nex-agi/Nex-N2-Pro"
TEMPERATURE = 0.7
MAX_TOKENS  = 4096

client = OpenAI(
    api_key=os.environ.get("SILICONFLOW_API_KEY"),
    base_url=BASE_URL,
)


# ── 消息构建 ──────────────────────────────────────────────
def build_messages(content, system=None, history=None):
    """
    构建 messages 列表。
    :param content:  本轮用户输入内容（必填）
    :param system:   系统提示词，传入则插入 system message（可选）
    :param history:  历史消息列表 [{"role":..., "content":...}, ...]（可选）
    :return:         messages list
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": content})
    return messages


# ── 创建会话 ──────────────────────────────────────────────
def chat(messages, tools=None):
    """
    发起对话请求，固定模型、温度、最大 token。
    :param messages: build_messages 返回的消息列表
    :param tools:    工具定义列表（如搜索引擎、天气查询等），不传则纯文本对话
    :return:         ChatCompletion 对象
    """
    params = dict(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    if tools:
        params["tools"] = tools
        params["tool_choice"] = "auto"

    return client.chat.completions.create(**params)


# ── 提取回复 ──────────────────────────────────────────────
def get_reply(response):
    """
    从 ChatCompletion 响应中提取文本回复。
    :param response: chat() 的返回值
    :return:         助手回复字符串，若无内容则返回空字符串
    """
    content = response.choices[0].message.content
    return content or ""


# ── 提取工具调用列表 ──────────────────────────────────────
def get_tools_call(response):
    """
    从 ChatCompletion 响应中提取工具调用列表。
    :param response: chat() 的返回值
    :return:         list[ChatCompletionMessageToolCall]，无工具调用则返回空列表
    """
    tool_calls = response.choices[0].message.tool_calls
    return tool_calls if tool_calls else []
