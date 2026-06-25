import json
import m1_llm_wrapper as llm
from m2_baidu_search import TOOL_DEF, handle_tool_call


# ────────────────────────────────────────────────
# 测试 1：直接调用搜索 API
# ────────────────────────────────────────────────
def test_direct_search():
    from m2_baidu_search import baidu_search
    print("=" * 50)
    print("测试 1：直接调用 baidu_search()")
    result = baidu_search("2024年诺贝尔物理学奖得主", num_results=3)
    print(result)


# ────────────────────────────────────────────────
# 测试 2：LLM 触发 function calling → 搜索 → 汇总回答
# ────────────────────────────────────────────────
def test_llm_with_search():
    print("=" * 50)
    print("测试 2：LLM + 百度搜索（function calling）")

    user_question = "最近有哪些关于人工智能的重大新闻？"
    print(f"用户提问：{user_question}")

    messages = llm.build_messages(
        content=user_question,
        system="你是一个信息助手，遇到需要实时信息的问题请使用搜索工具。",
    )

    # 第一轮：模型决定是否调用工具
    response = llm.chat(messages, tools=[TOOL_DEF])
    tool_calls = llm.get_tools_call(response)

    if not tool_calls:
        print("模型直接回答（未触发搜索）：", llm.get_reply(response))
        return

    print(f"模型请求调用 {len(tool_calls)} 个工具：")

    # 将 assistant 消息追加到历史
    messages.append(response.choices[0].message.model_dump())

    # 执行每个工具调用
    for tc in tool_calls:
        fn_args = json.loads(tc.function.arguments)
        print(f"  - 调用 baidu_search({fn_args})")

        search_result = handle_tool_call(tc)
        print(f"    搜索结果（前200字）：{search_result[:200]}…")

        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": search_result,
        })

    # 第二轮：模型根据搜索结果生成最终回复
    response2 = llm.chat(messages, tools=[TOOL_DEF])
    print("\n最终回复：")
    print(llm.get_reply(response2))


# ────────────────────────────────────────────────
# 测试 3：多轮对话 + 搜索
# ────────────────────────────────────────────────
def test_multi_turn_search():
    print("=" * 50)
    print("测试 3：多轮对话 + 搜索")

    history = []
    questions = [
        "特斯拉最新股价是多少？",
        "和上个月相比涨了还是跌了？",
    ]

    for q in questions:
        print(f"\n用户：{q}")
        messages = llm.build_messages(
            content=q,
            system="你是一个金融信息助手，需要实时数据时请使用搜索工具。",
            history=history,
        )

        response = llm.chat(messages, tools=[TOOL_DEF])
        tool_calls = llm.get_tools_call(response)

        if tool_calls:
            messages.append(response.choices[0].message.model_dump())
            for tc in tool_calls:
                search_result = handle_tool_call(tc)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": search_result,
                })
            response = llm.chat(messages, tools=[TOOL_DEF])

        reply = llm.get_reply(response)
        print(f"助手：{reply}")

        history.append({"role": "user",      "content": q})
        history.append({"role": "assistant", "content": reply})


# ────────────────────────────────────────────────
# 主入口
# ────────────────────────────────────────────────
if __name__ == "__main__":
    test_direct_search()
    test_llm_with_search()
    test_multi_turn_search()
