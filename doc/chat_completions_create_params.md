# `client.chat.completions.create` 参数说明

> 来源：[OpenAI API Reference — Create chat completion](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)
> 整理日期：2026-06-24

---

## 必填参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `messages` | `array[ChatCompletionMessageParam]` | 对话消息列表，构成本次会话上下文。每条消息包含 `role`（`system` / `developer` / `user` / `assistant` / `tool` / `function`）和 `content`。支持文本、图片、音频等多种模态（取决于模型）。 |
| `model` | `string` | 用于生成回复的模型 ID，如 `gpt-4o`、`o3`。不同模型在能力、性能、价格上有差异。 |

---

## 可选参数

### 生成质量 / 随机性控制

| 参数 | 类型 | 范围 | 默认值 | 说明 |
|------|------|------|--------|------|
| `temperature` | `number` | 0 ~ 2 | 1 | 采样温度。值越高（如 0.8）输出越随机；值越低（如 0.2）越确定聚焦。**不建议与 `top_p` 同时调整。** |
| `top_p` | `number` | 0 ~ 1 | 1 | 核采样（nucleus sampling）。仅考虑累积概率在 `top_p` 以内的 token。例如 `0.1` 表示只考虑概率最高的前 10% token。**不建议与 `temperature` 同时调整。** |
| `frequency_penalty` | `number` | -2 ~ 2 | 0 | 频率惩罚。正值根据 token 在已生成文本中出现的频率降低其再次被选中的概率，减少重复输出。 |
| `presence_penalty` | `number` | -2 ~ 2 | 0 | 存在惩罚。正值对已出现过的 token 施加惩罚，鼓励模型讨论新话题。 |
| `reasoning_effort` | `string` | `none`/`minimal`/`low`/`medium`/`high`/`xhigh` | `medium` | 推理模型（如 o 系列）的推理深度。降低推理深度可减少 token 消耗并加快响应。仅推理模型支持。 |
| `verbosity` | `string` | `low`/`medium`/`high` | — | 控制回复的详细程度。`low` 更简洁，`high` 更详尽。 |
| `n` | `number` | 1 ~ 128 | 1 | 每次请求生成的候选回复数量。**注意：多个候选会按比例增加 token 消耗，建议保持为 1 以控制成本。** |
| `seed` | `number` | — | — | （Beta）指定种子值以尽量获得确定性输出。相同种子 + 相同参数的重复请求应返回相同结果（不保证绝对确定性，可结合 `system_fingerprint` 监控后端变化）。**已弃用，不推荐新项目使用。** |

### Token 数量限制

| 参数 | 类型 | 说明 |
|------|------|------|
| `max_completion_tokens` | `number` | 本次生成允许的最大 token 数（含可见输出 token 和推理 token）。**推荐使用此参数替代 `max_tokens`。** |
| `max_tokens` | `number` | **已弃用**，由 `max_completion_tokens` 替代。与 o 系列推理模型不兼容。 |

### 停止条件

| 参数 | 类型 | 说明 |
|------|------|------|
| `stop` | `string` \| `array[string]` | 最多 4 个停止序列。模型在生成该序列时停止，返回内容不包含停止序列本身。不支持最新推理模型（o3、o4-mini）。 |

### 输出格式控制

| 参数 | 类型 | 说明 |
|------|------|------|
| `response_format` | `ResponseFormatText` \| `ResponseFormatJSONSchema` \| `ResponseFormatJSONObject` | 指定输出格式：`{"type":"text"}`（默认）、`{"type":"json_object"}`（JSON 模式，保证输出是合法 JSON）、`{"type":"json_schema","json_schema":{...}}`（结构化输出，严格遵守指定 JSON Schema）。 |
| `modalities` | `array["text"\|"audio"]` | 输出模态，默认 `["text"]`。支持音频输出的模型可指定 `["text","audio"]`。 |
| `logprobs` | `boolean` | 是否返回各 token 的对数概率。启用后，`choices[].logprobs` 包含详细数据。 |
| `top_logprobs` | `number` | 0 ~ 20 | 每个 token 位置返回概率最高的 N 个 token 及其对数概率。需要先开启 `logprobs: true`。 |

### 工具调用（Function Calling）

| 参数 | 类型 | 说明 |
|------|------|------|
| `tools` | `array[ChatCompletionTool]` | 模型可调用的工具列表，支持函数工具（`function`）和自定义工具（`custom`）。 |
| `tool_choice` | `"none"` \| `"auto"` \| `"required"` \| `ChatCompletionNamedToolChoice` | 控制工具调用策略：`none` 禁止调用工具；`auto` 由模型决定；`required` 强制调用至少一个工具；指定对象则强制调用特定工具。无工具时默认 `none`，有工具时默认 `auto`。 |
| `parallel_tool_calls` | `boolean` | 是否允许并行调用多个工具（默认 `true`）。 |
| `prediction` | `ChatCompletionPredictionContent` | 提供静态预测输出内容（如文件重新生成场景），可降低延迟和 token 消耗。 |
| `functions` ⚠️ | `array` | **已弃用**，请改用 `tools`。 |
| `function_call` ⚠️ | `string` \| object | **已弃用**，请改用 `tool_choice`。 |

### 流式输出

| 参数 | 类型 | 说明 |
|------|------|------|
| `stream` | `boolean` | 设为 `true` 时以 SSE（Server-Sent Events）流式返回数据，每个数据块为 `ChatCompletionChunk` 对象。 |
| `stream_options` | `ChatCompletionStreamOptions` | 流式模式下的额外选项（`include_usage` 等），仅在 `stream: true` 时有效。 |

### 音频支持

| 参数 | 类型 | 说明 |
|------|------|------|
| `audio` | `ChatCompletionAudioParam` | 请求音频输出时所需的参数（`format`、`voice`）。需配合 `modalities: ["audio"]` 使用。 |

### 缓存与成本优化

| 参数 | 类型 | 说明 |
|------|------|------|
| `prompt_cache_key` | `string` | 用于优化缓存命中率的稳定标识符，替代 `user` 字段。 |
| `prompt_cache_retention` | `"in_memory"` \| `"24h"` | 提示缓存的保留策略。`24h` 可将缓存前缀保留最长 24 小时。 |
| `store` | `boolean` | 是否存储本次对话输出，用于模型蒸馏或评估产品。支持文本和图片输入（超过 8MB 的图片将被丢弃）。 |

### 服务与安全

| 参数 | 类型 | 说明 |
|------|------|------|
| `service_tier` | `"auto"` \| `"default"` \| `"flex"` \| `"priority"` | 处理服务等级：`default` 标准定价；`flex` 弹性处理；`priority` 优先处理；`auto` 使用项目配置（默认）。 |
| `moderation` | `{ model }` | 对输入和输出开启内容审核。 |
| `safety_identifier` | `string` | 最长 64 字符的用户稳定标识（建议使用哈希值），用于检测违规行为。替代 `user` 字段。 |
| `metadata` | `map` | 最多 16 个 key-value 对，附加到对象上，便于检索和管理（key ≤ 64 字符，value ≤ 512 字符）。 |
| `logit_bias` | `map[number]` | token ID 到偏置值（-100 ~ 100）的映射。影响特定 token 的采样概率，-100 等效于禁止该 token，100 等效于强制选择。 |
| `web_search_options` | `{ search_context_size, user_location }` | 启用联网搜索工具，模型可搜索互联网以获取相关结果。 |
| `user` ⚠️ | `string` | **已弃用**，请改用 `safety_identifier` 和 `prompt_cache_key`。 |

---

## 对话效果速查

| 目标 | 推荐参数 |
|------|---------|
| 回答更有创意/随机 | 提高 `temperature`（如 0.8~1.2） |
| 回答更确定/聚焦 | 降低 `temperature`（如 0.1~0.3） |
| 减少重复内容 | 增大 `frequency_penalty`（如 0.5~1.0） |
| 鼓励讨论新话题 | 增大 `presence_penalty`（如 0.5~1.0） |
| 强制输出 JSON | `response_format: {"type":"json_object"}` |
| 严格按 Schema 输出 | `response_format: {"type":"json_schema",...}` |
| 调用外部工具（搜索/天气等） | 配置 `tools` + `tool_choice: "auto"` |
| 控制最大回复长度 | 设置 `max_completion_tokens` |
| 流式输出（打字机效果） | `stream: true` |
| 推理模型节省 token | 降低 `reasoning_effort`（如 `low`） |
