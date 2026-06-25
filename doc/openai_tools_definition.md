# OpenAI API 工具（Tools）定义规则

> 来源：OpenAI [Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)、[Chat Completions API Reference](https://platform.openai.com/docs/api-reference/chat/create)
> 整理日期：2026-06-24

---

## 一、概述

OpenAI Chat Completions API 通过 `tools` 参数让模型能够调用外部函数/工具。核心流程：

1. 在请求中定义工具（`tools` 参数）
2. 模型决定是否调用某个工具，返回 `tool_calls`
3. 开发者执行工具逻辑，将结果通过 `role: "tool"` 消息传回
4. 模型结合工具结果生成最终回复

---

## 二、`tools` 参数结构

`tools` 是一个数组，每个元素描述一个工具：

```json
{
  "type": "function",
  "function": {
    "name": "function_name",
    "description": "Description of the function",
    "parameters": { ... },
    "strict": true | false
  }
}
```

### 顶层字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | `string` | ✅ | 目前必须是 `"function"` |
| `function` | `object` | ✅ | 函数定义对象 |

### `function` 对象字段

| 字段 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `name` | `string` | ✅ | — | 函数名称，模型据此识别要调用的函数 |
| `description` | `string` | ❌ | `""` | 帮助模型理解何时调用此函数，建议描述清晰 |
| `parameters` | `object` | ✅ | — | 函数参数定义，遵循 JSON Schema |
| `strict` | `boolean` | ❌ | `false` | 是否启用 Structured Outputs 严格模式 |

#### `name` 约束

- 允许字符：`a-z`, `A-Z`, `0-9`, 下划线 `_`, 连字符 `-`
- 长度上限：**64 个字符**
- 建议使用蛇形命名法（snake_case），如 `get_weather`

#### `description` 建议

- 描述函数的功能及其副作用
- 说明何时应该调用该函数
- 如果参数中存在其他函数（如 SQL 查询、API 请求），建议在描述中说明用途
- 好的描述能显著提升模型正确调用工具的准确率

---

## 三、`parameters` — JSON Schema 规则

`parameters` 遵循 **JSON Schema** 标准（OpenAI 主要使用 Draft 2020-12 子集）。

### 基础格式

```json
{
  "type": "object",
  "properties": {
    "param_name": {
      "type": "string",
      "description": "What this parameter does"
    }
  },
  "required": ["param_name"],
  "additionalProperties": false
}
```

### 支持的类型

| JSON 类型 | 对应 Python 类型 | 说明 |
|-----------|-----------------|------|
| `string` | `str` | 文本字符串 |
| `number` | `float` | 浮点数 |
| `integer` | `int` | 整数 |
| `boolean` | `bool` | 布尔值 |
| `array` | `list` | 数组，需配合 `items` 定义元素类型 |
| `object` | `dict` | 嵌套对象，需配合 `properties` 定义子字段 |

### 常用约束字段

| 字段 | 适用类型 | 说明 |
|------|---------|------|
| `description` | 所有 | 参数说明，帮助模型正确传参 |
| `enum` | `string`, `integer` | 限制取值为枚举值列表 |
| `items` | `array` | 数组元素的类型定义 |
| `minItems` / `maxItems` | `array` | 数组长度范围 |
| `minimum` / `maximum` | `number`, `integer` | 数值范围 |
| `minLength` / `maxLength` | `string` | 字符串长度范围 |
| `pattern` | `string` | 正则表达式约束 |
| `default` | 所有 | 默认值 |
| `nullable` | 所有 | 是否可为 `null` |

### 嵌套对象示例

```json
{
  "type": "object",
  "properties": {
    "user": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "age": { "type": "integer" },
        "tags": {
          "type": "array",
          "items": { "type": "string" }
        }
      },
      "required": ["name"]
    }
  },
  "required": ["user"],
  "additionalProperties": false
}
```

---

## 四、Strict 模式（Structured Outputs）

当 `strict: true` 时，模型保证输出严格符合 JSON Schema。这可以**消除幻觉字段、类型错误、缺失必填字段**等问题。

### 启用条件

```json
{
  "strict": true,
  "parameters": {
    "type": "object",
    "properties": { ... },
    "required": [ ... ],
    "additionalProperties": false
  }
}
```

### 要求

1. **所有属性必须有 `type` 字段**（不能省略）
2. **顶级对象必须有 `type: "object"`**
3. **必须设置 `additionalProperties: false`**
4. **必须声明 `required` 字段**（即使是空数组 `[]`）
5. **不支持以下 JSON Schema 特性**（启用 strict 时不能使用）：
   - `$ref`（引用）
   - `allOf` / `anyOf` / `oneOf` / `not`
   - `if` / `then` / `else`
   - `const`
   - `contains`
   - `patternProperties`
   - `propertyNames`
   - `minProperties` / `maxProperties`
   - `dependentRequired` / `dependentSchemas`
   - `uniqueItems`（在数组上）
   - `definitions`
   - `format`（如 `"email"`、`"date-time"`）
6. **支持以下特性**（即使 strict 模式下也可用）：
   - `enum`
   - `minLength` / `maxLength`
   - `minimum` / `maximum`
   - `pattern`（正则）
   - `items` / `minItems` / `maxItems`
   - `nullable`

### 可用模型

| 模型家族 | 说明 |
|---------|------|
| `gpt-4o` / `gpt-4o-mini` | 全系列支持 |
| `gpt-4.1` / `gpt-4.1-mini` / `gpt-4.1-nano` | 支持 |
| `o3` / `o4-mini` | 推理系列支持 |
| `gpt-4-turbo` / `gpt-4` 后续版本 | 部分支持 |

> **注意**：strict 模式仅在 `"type": "function"` 工具和 `response_format` 的 `json_schema` 模式下有效。不支持 `json_object` 模式。

---

## 五、`tool_choice` — 工具调用控制

| 取值 | 类型 | 说明 |
|------|------|------|
| `"auto"` | `string` | **默认。** 模型自主决定是否调用工具 |
| `"required"` | `string` | 强制模型**每次回复都调用工具**（可多个） |
| `"none"` | `string` | 不调用任何工具，即使定义了工具 |
| `{"type": "function", "function": {"name": "my_func"}}` | `object` | 强制调用**指定函数** |

### Python 示例

```python
# 强制调用特定工具
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "get_weather"}}
)
```

---

## 六、`parallel_tool_calls` — 并行调用

- 类型：`boolean`
- 默认：`true`
- 设为 `false` 时，模型一次只会调用一个工具

---

## 七、完整的请求-响应流程

### 请求示例

```python
import json
from openai import OpenAI

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and state, e.g. Boston, MA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "default": "celsius"
                    }
                },
                "required": ["location"],
                "additionalProperties": false
            },
            "strict": True
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Boston?"}],
    tools=tools,
    tool_choice="auto"
)
```

### 响应中的 `tool_calls`

```json
{
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"location\": \"Boston, MA\", \"unit\": \"celsius\"}"
        }
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

> `finish_reason` 为 `"tool_calls"` 表示模型决定调用工具。

### 返回工具结果

```python
# 遍历 tool_calls，执行实际逻辑
for tool_call in response.choices[0].message.tool_calls:
    if tool_call.function.name == "get_weather":
        args = json.loads(tool_call.function.arguments)
        result = get_weather(args["location"], args["unit"])

        # 将结果返回给模型
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })

# 继续生成回复
final_response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools
)
```

---

## 八、`role: "tool"` 消息规范

将工具执行结果返回给模型时，消息格式如下：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `role` | `string` | ✅ | 固定为 `"tool"` |
| `tool_call_id` | `string` | ✅ | 对应 `tool_calls` 中的 `id` 值 |
| `content` | `string` | ✅ | 工具执行结果（字符串形式） |

---

## 九、最佳实践

### 1. 工具设计

- **每个工具做一件事**：单一职责原则，不要一个工具做多件事
- **命名清晰**：`search_database` 优于 `sd` 或 `func1`
- **参数尽量少**：推荐每个函数不超过 5-6 个参数
- **提供 enum 约束**：比自由文本更准确
- **填写描述**：给所有参数写 description，帮助模型正确传参

### 2. 使用 strict 模式

```python
{
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }
}
```

### 3. 工具数量

- 通常建议一次最多定义 **20-30 个工具**
- 超过这个数量模型可能混淆
- 考虑将相关工具分组或使用路由策略

### 4. 错误处理

- 工具执行失败时，返回有意义的错误信息
- 让模型自行决策如何处理错误（重试、解释、换方法）

### 5. 安全考虑

- **永远不要信任模型生成的参数**：始终在执行前验证
- 对工具执行进行授权和速率限制
- 敏感操作需要用户确认

---

## 十、新旧 API 格式对比

| 方面 | Chat Completions API | Responses API |
|------|---------------------|---------------|
| 工具定义 | 嵌套结构 `{type, function: {name, parameters}}` | 扁平结构 `{type, name, parameters}` |
| 工具调用返回 | `message.tool_calls[]` | 顶层 output items |
| 结果回传 | `role: "tool", tool_call_id` | `type: "function_call_output"` |
| 内置工具 | 不支持（仅自定义 function） | 支持 Code Interpreter, File Search, Web Search, Computer |

---

## 十一、常见错误

| 错误 | 原因 |
|------|------|
| `"tools.0.function.parameters.type: field required"` | `parameters` 缺少 `type: "object"` |
| `"Additional properties are not allowed (got 'format')"` | strict 模式下使用了不支持的 JSON Schema 特性 |
| `"tools.0.function.name: string does not match pattern"` | 函数名包含非法字符 |
| `"messages with role 'tool' must have a tool_call_id"` | 工具结果消息缺少 `tool_call_id` |
| `"An assistant message with 'tool_calls' must be followed by tool messages"` | tool_calls 之后的助手消息必须是 `role: "tool"` |

---

## 十二、完整示例：多工具调用

```python
import json
from openai import OpenAI

client = OpenAI()

# 定义工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform mathematical calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression"}
                },
                "required": ["expression"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]

messages = [{"role": "user", "content": "Search for latest AI news and calculate 3847 * 9521"}]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    parallel_tool_calls=True  # 可并行调用多个工具
)

# 处理并行工具调用
if response.choices[0].message.tool_calls:
    for tc in response.choices[0].message.tool_calls:
        args = json.loads(tc.function.arguments)
        if tc.function.name == "search_web":
            result = search_web(args["query"])
        elif tc.function.name == "calculate":
            result = eval(args["expression"])  # 仅示例，实际应用需安全处理
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": json.dumps({"result": result})
        })
```
