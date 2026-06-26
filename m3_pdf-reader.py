import os
import json
import PyPDF2
from openai.types.chat import ChatCompletionMessageToolCall

# ── 配置 ──────────────────────────────────────────────────


# ── Tool Definition（供 LLM function calling 使用）────────
TOOL_DEF: dict = {
    "type": "function",
    "function": {
        "name": "read_pdf",
        "description": (
            "读取 PDF 文件并提取其中的文本内容。"
            "当用户上传了 PDF 文件或需要从 PDF 中获取信息时调用此工具。"
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "PDF 文件的完整路径",
                },
            },
            "required": ["file_path"],
            "additionalProperties": False,
        },
    },
}


# ── PDF 读取实现 ─────────────────────────────────────────
def read_pdf(file_path: str) -> str:
    if not file_path:
        return "错误：未提供文件路径。"

    if not os.path.exists(file_path):
        return f"错误：文件不存在 — {file_path}"

    if not file_path.lower().endswith(".pdf"):
        return f"错误：文件不是 PDF 格式 — {file_path}"

    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            num_pages = len(reader.pages)
            if num_pages == 0:
                return f"文件「{os.path.basename(file_path)}」为空 PDF，没有可提取的页面。"

            lines = [f"文件名：{os.path.basename(file_path)}", f"总页数：{num_pages}\n"]

            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text and text.strip():
                    lines.append(f"── 第 {i} 页 ──")
                    lines.append(text.strip())
                    lines.append("")

            result = "\n".join(lines).strip()
            return result if result else f"文件「{os.path.basename(file_path)}」中未提取到文本内容（可能为扫描件或图片型 PDF）。"

    except PyPDF2.errors.PdfReadError as e:
        return f"错误：PDF 文件损坏或无法解析 — {e}"
    except PermissionError:
        return f"错误：没有权限读取文件 — {file_path}"
    except Exception as e:
        return f"错误：读取 PDF 时发生异常 — {e}"


# ── Tool Call 分发 ────────────────────────────────────────
def handle_tool_call(tool_call: ChatCompletionMessageToolCall) -> str:
    if tool_call.function.name != "read_pdf":
        return f"未知工具：{tool_call.function.name}"

    try:
        args = json.loads(tool_call.function.arguments)
    except (json.JSONDecodeError, TypeError):
        return "错误：工具参数解析失败。"

    file_path = args.get("file_path", "")

    if not file_path:
        return "错误：文件路径不能为空。"

    return read_pdf(file_path)
