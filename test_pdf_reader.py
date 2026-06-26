#!D:\anaconda3\envs\agent2\python.exe
"""测试 m3_pdf-reader.py 的 PDF 文本提取工具"""

import importlib.util
import json
import os

# ── 动态导入（文件名带横线，无法用标准 import）───────────
_MODULE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "m3_pdf-reader.py")
_spec = importlib.util.spec_from_file_location("m3_pdf_reader", _MODULE_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

read_pdf = _mod.read_pdf
handle_tool_call = _mod.handle_tool_call
TOOL_DEF = _mod.TOOL_DEF

# ── 测试用 PDF ───────────────────────────────────────────
PDF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "简历.pdf")
SEPARATOR = "=" * 60


def test_tool_def():
    """验证 TOOL_DEF 结构完整性"""
    print(SEPARATOR)
    print("【测试 1】TOOL_DEF 结构检查")
    assert TOOL_DEF["type"] == "function"
    assert TOOL_DEF["function"]["name"] == "read_pdf"
    assert "file_path" in TOOL_DEF["function"]["parameters"]["properties"]
    assert TOOL_DEF["function"]["parameters"]["required"] == ["file_path"]
    print("  [OK] TOOL_DEF 结构正确")
    print(f"  工具名称: {TOOL_DEF['function']['name']}")
    print(f"  描述: {TOOL_DEF['function']['description']}")
    print()


def test_read_pdf_success():
    """测试正常读取 PDF"""
    print(SEPARATOR)
    print("【测试 2】正常读取 PDF — 简历.pdf")

    if not os.path.exists(PDF_PATH):
        print(f"  [SKIP] 测试文件不存在: {PDF_PATH}")
        return

    result = read_pdf(PDF_PATH)
    print(f"  返回结果长度: {len(result)} 字符")
    # 打印前 500 字符
    preview = result[:500]
    print(f"  预览:\n{preview}")
    print()

    # 验证基本格式
    assert "文件名：" in result
    assert "总页数：" in result
    print("  [OK] 包含文件信息")
    print()


def test_read_pdf_file_not_found():
    """测试文件不存在"""
    print(SEPARATOR)
    print("【测试 3】文件不存在")
    result = read_pdf("/path/to/nonexistent.pdf")
    assert "错误：文件不存在" in result
    print(f"  结果: {result}")
    print()


def test_read_pdf_empty_path():
    """测试空路径"""
    print(SEPARATOR)
    print("【测试 4】空文件路径")
    result = read_pdf("")
    assert "错误：未提供文件路径" in result
    print(f"  结果: {result}")
    print()


def test_read_pdf_non_pdf():
    """测试非 PDF 文件（用本脚本自身）"""
    print(SEPARATOR)
    print("【测试 5】非 PDF 文件")
    result = read_pdf(__file__)  # 传入 .py 文件
    assert "错误：文件不是 PDF 格式" in result
    print(f"  结果: {result}")
    print()


def test_handle_tool_call_normal():
    """测试 handle_tool_call 正常分发"""
    print(SEPARATOR)
    print("【测试 6】handle_tool_call 正常调用")

    if not os.path.exists(PDF_PATH):
        print(f"  [SKIP] 测试文件不存在: {PDF_PATH}")
        return

    # 模拟 LLM 发出的 tool_call
    mock_call = _make_mock_tool_call("read_pdf", {"file_path": PDF_PATH})
    result = handle_tool_call(mock_call)
    assert "文件名：" in result
    assert "总页数：" in result
    print(f"  返回结果长度: {len(result)} 字符")
    print(f"  预览:\n{result[:300]}")
    print("  [OK] 分发正常")
    print()


def test_handle_tool_call_unknown():
    """测试未知工具名称"""
    print(SEPARATOR)
    print("【测试 7】handle_tool_call 未知工具")
    mock_call = _make_mock_tool_call("unknown_tool", {})
    result = handle_tool_call(mock_call)
    assert "未知工具" in result
    print(f"  结果: {result}")
    print()


def test_handle_tool_call_bad_json():
    """测试参数 JSON 解析失败"""
    print(SEPARATOR)
    print("【测试 8】handle_tool_call 参数 JSON 异常")
    mock_call = _make_mock_tool_call("read_pdf", "not-json", raw_args=True)
    result = handle_tool_call(mock_call)
    assert "错误：工具参数解析失败" in result
    print(f"  结果: {result}")
    print()


def test_handle_tool_call_empty_path():
    """测试 handle_tool_call 空路径"""
    print(SEPARATOR)
    print("【测试 9】handle_tool_call 空文件路径")
    mock_call = _make_mock_tool_call("read_pdf", {"file_path": ""})
    result = handle_tool_call(mock_call)
    assert "错误：文件路径不能为空" in result
    print(f"  结果: {result}")
    print()


# ── 辅助 ──────────────────────────────────────────────────
def _make_mock_tool_call(name: str, args, raw_args: bool = False):
    """构造一个模拟的 ChatCompletionMessageToolCall 对象"""
    from unittest.mock import MagicMock

    mock = MagicMock()
    mock.function.name = name
    mock.function.arguments = json.dumps(args) if not raw_args else args
    mock.id = "call_mock_001"
    mock.type = "function"
    return mock


# ── 入口 ──────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n--- PDF 读取工具测试 ---\n")

    test_tool_def()
    test_read_pdf_success()
    test_read_pdf_file_not_found()
    test_read_pdf_empty_path()
    test_read_pdf_non_pdf()
    test_handle_tool_call_normal()
    test_handle_tool_call_unknown()
    test_handle_tool_call_bad_json()
    test_handle_tool_call_empty_path()

    print(SEPARATOR)
    print("\n*** 所有测试完成 ***\n")
