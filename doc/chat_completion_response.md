# `ChatCompletion` 响应数据结构

> 来源：[OpenAI API Reference — Create chat completion](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)
> 整理日期：2026-06-24

---

## 完整结构示例

```json
{
  "id": "chatcmpl-B9MBs8CjcvOU2jLn4n570S5qMJKcT",
  "object": "chat.completion",
  "created": 1741569952,
  "model": "gpt-4o",
  "service_tier": "default",
  "system_fingerprint": "fp_xxxxxxxxxx",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I assist you today?",
        "refusal": null,
        "tool_calls": null,
        "audio": null,
        "annotations": []
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 10,
    "total_tokens": 29,
    "prompt_tokens_details": {
      "cached_tokens": 0,
      "audio_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "audio_tokens": 0,
      "accepted_prediction_tokens": 0,
      "rejected_prediction_tokens": 0
    }
  }
}
```

---

## 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `string` | 本次对话的唯一标识符，格式为 `chatcmpl-xxx`。 |
| `object` | `string` | 固定值 `"chat.completion"`，标识对象类型。 |
| `created` | `integer` | 请求创建的 Unix 时间戳（秒）。 |
| `model` | `string` | 实际用于生成回复的模型名称（可能与请求的模型别名不同）。 |
| `service_tier` | `string` | 实际处理本次请求的服务等级（`default` / `flex` / `priority`）。 |
| `system_fingerprint` | `string` | 后端配置指纹。当此值变化时，说明后端配置发生改变，可能影响确定性输出（配合 `seed` 参数使用）。 |
| `choices` | `array[Choice]` | 生成的候选回复列表。通常只有一条（`n=1` 时），数量由请求参数 `n` 决定。 |
| `usage` | `CompletionUsage` | Token 使用量统计。 |

---

## `choices[]` — 候选回复

每个元素为一个 `Choice` 对象：

| 字段 | 类型 | 说明 |
|------|------|------|
| `index` | `integer` | 候选回复的序号，从 `0` 开始。 |
| `message` | `ChatCompletionMessage` | 模型生成的消息对象（见下节）。 |
| `finish_reason` | `string` | 生成停止的原因（见下表）。 |
| `logprobs` | `object \| null` | 各 token 的对数概率，仅在请求时指定 `logprobs: true` 后才有值，否则为 `null`。 |

### `finish_reason` 枚举值

| 值 | 含义 |
|----|------|
| `"stop"` | 正常结束：模型生成完毕，或触发了 `stop` 参数中指定的停止序列。 |
| `"length"` | 达到 `max_completion_tokens` 或 `max_tokens` 限制而截断。 |
| `"tool_calls"` | 模型决定调用一个或多个工具（函数调用）。 |
| `"content_filter"` | 触发内容过滤策略，输出被截断或拒绝。 |
| `"function_call"` | **已弃用**，同 `tool_calls`，旧版函数调用使用。 |

---

## `choices[].message` — 消息对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `role` | `string` | 固定为 `"assistant"`，表示这是模型生成的消息。 |
| `content` | `string \| null` | 模型回复的文本内容。若模型选择调用工具则为 `null`（此时看 `tool_calls`）。 |
| `refusal` | `string \| null` | 模型拒绝回答时的拒绝理由文本；正常回答时为 `null`。 |
| `tool_calls` | `array[ToolCall] \| null` | 模型请求调用的工具列表（见下节）。无工具调用时为 `null`。 |
| `audio` | `ChatCompletionAudio \| null` | 音频输出数据（仅在请求了音频模态时非 null）。包含 `id`、`data`（base64 音频）、`expires_at`、`transcript`。 |
| `annotations` | `array` | 模型对回复内容的标注（如引用来源等）。 |

---

## `choices[].message.tool_calls[]` — 工具调用

当 `finish_reason == "tool_calls"` 时，此数组包含一个或多个工具调用请求：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `string` | 本次工具调用的唯一 ID，回传结果时需要用此 ID 关联。 |
| `type` | `string` | 工具类型，目前为 `"function"` 或 `"custom"`。 |
| `function` | `object` | 函数调用信息（`type == "function"` 时有效）。 |
| `function.name` | `string` | 模型要调用的函数名称。 |
| `function.arguments` | `string` | 函数调用参数的 JSON 字符串（需自行 `json.loads` 解析）。 |

### 工具调用完整流程

```
请求（携带 tools 定义）
    ↓
response.choices[0].finish_reason == "tool_calls"
    ↓
解析 response.choices[0].message.tool_calls[]
    ↓
本地执行对应函数，获取结果
    ↓
将 tool 结果以 {"role": "tool", "tool_call_id": ..., "content": ...} 追加到 messages
    ↓
再次调用 chat() → 获得最终文本回复
```

---

## `usage` — Token 统计

| 字段 | 类型 | 说明 |
|------|------|------|
| `prompt_tokens` | `integer` | 输入（prompt）消耗的 token 数。 |
| `completion_tokens` | `integer` | 输出（completion）消耗的 token 数。 |
| `total_tokens` | `integer` | 总消耗 token 数 = `prompt_tokens + completion_tokens`。 |
| `prompt_tokens_details.cached_tokens` | `integer` | 命中提示缓存（Prompt Cache）的 token 数，这部分按折扣价计费。 |
| `prompt_tokens_details.audio_tokens` | `integer` | 输入中音频类型消耗的 token 数。 |
| `completion_tokens_details.reasoning_tokens` | `integer` | 推理模型内部推理过程消耗的 token 数（不可见，但计入费用）。 |
| `completion_tokens_details.audio_tokens` | `integer` | 输出中音频类型消耗的 token 数。 |
| `completion_tokens_details.accepted_prediction_tokens` | `integer` | 预测内容（`prediction` 参数）中被采纳的 token 数。 |
| `completion_tokens_details.rejected_prediction_tokens` | `integer` | 预测内容中被拒绝的 token 数（仍按全价计费）。 |

---

## `logprobs` — 对数概率（可选）

仅在请求时指定 `logprobs: true` 才会返回，结构为：

```python
choices[0].logprobs.content  # list[ChatCompletionTokenLogprob]
```

每个 `ChatCompletionTokenLogprob`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `token` | `string` | 该位置实际被选中的 token。 |
| `logprob` | `float` | 该 token 的对数概率（越接近 0 概率越高）。 |
| `bytes` | `array[int]` | token 对应的 UTF-8 字节序列。 |
| `top_logprobs` | `array` | 该位置概率最高的 N 个候选 token 及其对数概率（由 `top_logprobs` 参数控制数量）。 |

---

## Python 快速访问路径

```python
response = chat(messages)

# 文本回复
text = response.choices[0].message.content

# 停止原因
reason = response.choices[0].finish_reason  # "stop" / "length" / "tool_calls" / ...

# 工具调用列表
tool_calls = response.choices[0].message.tool_calls or []
for tc in tool_calls:
    name = tc.function.name          # 函数名
    args = tc.function.arguments     # JSON 字符串，需 json.loads()
    call_id = tc.id                  # 回传结果时用

# Token 消耗
total = response.usage.total_tokens
reasoning = response.usage.completion_tokens_details.reasoning_tokens
cached = response.usage.prompt_tokens_details.cached_tokens
```
