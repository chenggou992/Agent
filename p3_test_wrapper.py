import json
import m1_llm_wrapper as llm

# ────────────────────────────────────────────────
# 测试 1：基础对话（无系统提示）
# ────────────────────────────────────────────────
def test_basic_chat():
    print("=" * 50)
    print("测试 1：基础对话")
    messages = llm.build_messages("用一句话介绍你自己")
    response = llm.chat(messages)
    reply = llm.get_reply(response)
    print("回复：", reply)
    print("Token 消耗：", response.usage.total_tokens)


# ────────────────────────────────────────────────
# 测试 2：带系统提示 + 历史记录
# ────────────────────────────────────────────────
def test_chat_with_system_and_history():
    print("=" * 50)
    print("测试 2：带系统提示 + 历史记录")
    history = [
        {"role": "user",      "content": "我叫小明"},
        {"role": "assistant", "content": "你好，小明！有什么我可以帮你的吗？"},
    ]
    messages = llm.build_messages(
        content="你还记得我叫什么吗？",
        system="你是一个友善的助手，记忆力很好。",
        history=history,
    )
    response = llm.chat(messages)
    reply = llm.get_reply(response)
    print("回复：", reply)


# ────────────────────────────────────────────────
# 测试 3：工具调用（模拟天气查询）
# ────────────────────────────────────────────────
# 模拟本地工具实现
def get_weather(city: str) -> str:
    fake_data = {
        "北京": "晴，26°C",
        "上海": "多云，23°C",
        "广州": "小雨，28°C",
    }
    return fake_data.get(city, f"{city} 的天气数据暂不可用")


# 工具定义（OpenAI function calling 格式）
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的实时天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海",
                    }
                },
                "required": ["city"],
            },
        },
    }
]


def test_tool_call():
    print("=" * 50)
    print("测试 3：工具调用（天气查询）")
    messages = llm.build_messages("北京今天天气怎么样？")

    # 第一轮：模型决定是否调用工具
    response = llm.chat(messages, tools=TOOLS)
    tool_calls = llm.get_tools_call(response)

    if not tool_calls:
        # 模型直接回答，未触发工具调用
        print("回复（直接）：", llm.get_reply(response))
        return

    print(f"模型请求调用 {len(tool_calls)} 个工具：")

    # 将模型的 assistant 消息追加到历史
    messages.append(response.choices[0].message)

    # 执行每个工具调用并将结果追加到消息
    for tc in tool_calls:
        fn_name = tc.function.name
        fn_args = json.loads(tc.function.arguments)

        if fn_name == "get_weather":
            result = get_weather(**fn_args)
        else:
            result = "未知工具"

        print(f"    工具返回：{result}")
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": result,
        })

    # 第二轮：模型根据工具结果生成最终回复
    response2 = llm.chat(messages, tools=TOOLS)
    print("最终回复：", llm.get_reply(response2))


# ────────────────────────────────────────────────
# 主入口
# ────────────────────────────────────────────────
if __name__ == "__main__":
    test_basic_chat()
    test_chat_with_system_and_history()
    test_tool_call()
