import json

from m1_llm_wrapper import(
    build_messages,
    chat,
    get_reply,
    get_tools_call,
)

from m2_baidu_search import (
    TOOL_DEF,
    baidu_search,
    handle_tool_call,
)

SYSTEM_PROMPT = '''
# 角色
你是一个充满正能量的赞美鼓励机器人，时刻用温暖的话语给予人们赞美和鼓励，让他们充满自信与动力。

## 技能
### 技能 1：赞美个人优点
1. 当用户提到自己的某个特点或行为时，挖掘其中的优点进行赞美。回复示例：你真的很[优点]，比如[具体事例说明优点]。
2. 如果用户没有明确提到自己的特点，可以主动询问一些问题，了解用户后进行赞美。回复示例：我想先了解一下你，你觉得自己最近做过最棒的事情是什么呢？

### 技能 2：鼓励面对困难
1. 当用户提到遇到困难时，给予鼓励和积极的建议。回复示例：这确实是个挑战，但我相信你有足够的能力去克服它。你可以[具体建议]。
2. 如果用户没有提到困难但情绪低落，可以询问是否有不开心的事情，然后给予鼓励。回复示例：你看起来有点不开心，是不是遇到什么事情了呢？不管怎样，你都很坚强，一定可以度过难关。
    
### 技能 3：回答专业问题
当用户问到最新的时事新闻或者你回答不了的专业问题，必须调用baidu_search工具搜索答案并返回
    
## 限制
- 只输出赞美和鼓励的话语，拒绝负面评价。
- 所输出的内容必须按照给定的格式进行组织，不能偏离框架要求。
'''

def chat_loop():

    print("="*50)
    print("Usar Input:")
    user_input : str = input()

    messages = build_messages(
        content=user_input,
        system=SYSTEM_PROMPT,
    )

    response1 = chat(messages, tools=[TOOL_DEF])

    tool_calls = get_tools_call(response1)

    for tool_call in tool_calls:
        if tool_call.function.name == "baidu_search":
            search_result = handle_tool_call(tool_call)

            print(f"  - 调用 baidu_search({tool_call.function.arguments})")
            print(f"    搜索结果（前200字）：{search_result[:200]}…")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": search_result,
            })

    response2 = chat(messages, tools=[TOOL_DEF])
    print("-"*50)
    print("最终回复:")
    print(get_reply(response2))

if __name__ == "__main__":
    while True:
        chat_loop()

