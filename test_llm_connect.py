"""
LLM 连通性测试程序
平台: 硅基流动 (SiliconFlow)
模型: zai-org/GLM-5.2
"""

# ============================================================
# 1. 导入需要的库
# ============================================================
import os          # os 库：用来读取环境变量（系统级变量，比如 API Key）
import sys         # sys 库：用来修改标准输出的编码
import io          # io 库：用来包装文本流
import requests    # requests 库：用来发送 HTTP 请求（访问网络 API）
import json        # json 库：用来格式化打印返回的数据，好看一些

# 修正 Windows 终端乱码问题
# 强制 stdout 使用 utf-8 输出，避免 GBK 编码无法打印中文字符
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================
# 2. 从环境变量读取 API Key
# ============================================================
# os.environ 是一个字典，存了当前系统的所有环境变量
# .get("KEY") 是字典的 get 方法 —— 如果 KEY 不存在，返回 None 而不会报错
api_key = os.environ.get("SILICONFLOW_API_KEY")

# 如果没取到，打印提示并退出程序
if api_key is None:
    # exit(1) 表示异常退出（非零值表示出错了），给调用者一个信号
    print("[错误] 环境变量 SILICONFLOW_API_KEY 未设置")
    print("   请先设置：export SILICONFLOW_API_KEY='你的key'  (Windows: set SILICONFLOW_API_KEY=xxx)")
    exit(1)

# 也可以用空字符串判断，更稳妥
if api_key == "":
    print("[错误] 环境变量 SILICONFLOW_API_KEY 是空字符串，请检查")
    exit(1)

print("[OK] 成功读取到 API Key (前8位: ", api_key[:8], "...)")

# ============================================================
# 3. 定义请求的地址和数据
# ============================================================

# 硅基流动的 API 地址 —— 和 OpenAI 的 API 格式兼容
url = "https://api.siliconflow.cn/v1/chat/completions"

# 要用的模型 —— zai-org/GLM-5.2
model_name = "zai-org/GLM-5.2"

# 要发的消息 —— 一个列表，里面是字典
# 字典的格式：{"role": "system/user/assistant", "content": "消息内容"}
# role="system" 是系统提示词，告诉 AI 它是什么角色
# role="user" 是用户发的消息
messages = [
    {
        "role": "system",
        "content": "你是一个有用的助手，请用中文回答。"
    },
    {
        "role": "user",
        "content": "你好！请用一句话证明你是 GLM-5.2 模型。"
    }
]

# 请求体 —— 一个字典，会被自动转成 JSON 发送
# - model: 模型名称（字符串）
# - messages: 对话消息列表（列表里套字典）
# - temperature: 输出随机性，0~2 之间，越小越确定，越大越有创意
# - max_tokens: 最多生成多少个 token（一个汉字约 1~2 个 token）
payload = {
    "model": model_name,
    "messages": messages,
    "temperature": 0.7,
    "max_tokens": 512
}

# ============================================================
# 4. 设置请求头（HTTP Headers）
# ============================================================
# 请求头是 HTTP 协议的"信封"，告诉服务器一些元信息
# Authorization: Bearer <key> 是常见的 API 认证方式
# Content-Type: application/json 表示我们发送的是 JSON 数据
headers = {
    "Authorization": f"Bearer {api_key}",       # f-string：Python 3.6+ 的字符串格式化，{变量} 会被替换
    "Content-Type": "application/json"
}

# ============================================================
# 5. 发送请求
# ============================================================
print(f"\n[发送] 正在向 {url} 发送请求...")
print(f"   模型: {model_name}")
print(f"   消息: {messages[-1]['content'][:40]}...")   # 取最后一条消息的前40个字
print("   等待响应中...\n")

# try-except：Python 的异常处理机制
# 把"可能出错的代码"放在 try 块里，出错了会在 except 里捕获，不会让程序崩溃
try:
    # requests.post() —— 发送一个 POST 请求
    # 参数：
    #   url:     请求地址
    #   headers: 请求头字典
    #   json:    请求体（会自动转成 JSON 字符串，并设置 Content-Type）
    #   timeout: 超时时间（秒），超过这个时间没响应就放弃 —— 不设的话可能一直等
    response = requests.post(
        url=url,
        headers=headers,
        json=payload,
        timeout=60
    )

    # ============================================================
    # 6. 检查响应状态
    # ============================================================
    # response.status_code 是 HTTP 状态码
    # 200 表示成功，4xx 表示客户端错误，5xx 表示服务器错误
    print(f"[响应] 收到响应，状态码: {response.status_code}")

    if response.status_code == 200:
        # .json() 方法把返回的 JSON 字符串解析成 Python 字典
        data = response.json()

        # 拿到 AI 的回答
        # 返回的结构是：
        # {
        #   "choices": [
        #       {
        #           "message": {
        #               "content": "AI 回复的内容"
        #           }
        #       }
        #   ]
        # }
        # 所以：data["choices"] 是一个列表，[0] 取第一个，["message"] 取消息，["content"] 取内容
        ai_reply = data["choices"][0]["message"]["content"]

        print(f"\n{'='*60}")
        print("AI 回复:")
        print(f"{'='*60}")
        print(ai_reply)
        print(f"{'='*60}")

        # 打印 token 用量 —— 对 API 计费有用
        # data["usage"] 是一个字典，里面有 prompt_tokens / completion_tokens / total_tokens
        usage = data.get("usage")
        if usage:
            print(f"\n[用量] Token 用量：")
            print(f"   输入 (prompt):     {usage.get('prompt_tokens', 'N/A')} tokens")
            print(f"   输出 (completion): {usage.get('completion_tokens', 'N/A')} tokens")
            print(f"   总计 (total):      {usage.get('total_tokens', 'N/A')} tokens")

        print(f"\n连通性测试通过！")

    else:
        # 不是 200，打印错误信息
        # response.text 是服务器返回的原始文本（未解析的字符串）
        print(f"[错误] 请求失败，错误信息：")
        print(f"   状态码: {response.status_code}")
        print(f"   返回内容: {response.text}")

# 捕获网络层面上的异常
# requests.exceptions.RequestException 是 requests 库所有异常的父类
# 在这里捕获所有的网络超时、连接拒绝、DNS 解析失败等
except requests.exceptions.Timeout:
    print("[错误] 请求超时：服务器在 60 秒内没有响应")
    print("   请检查你的网络连接是否正常")

except requests.exceptions.ConnectionError:
    print("[错误] 网络连接错误：无法连接到硅基流动的 API 服务器")
    print("   请检查：")
    print("   1. 是否能访问外网")
    print("   2. api.siliconflow.cn 是否被防火墙拦截")
    print("   3. 是否需要配置代理")

except requests.exceptions.RequestException as e:
    # 捕获其他 requests 库的异常
    # e 就是异常对象，str(e) 能拿到错误描述的字符串
    print(f"[错误] 请求发生未知错误: {str(e)}")

# 捕获所有其他异常（比如 JSON 解析错误等）
except Exception as e:
    print(f"[错误] 程序运行出错: {str(e)}")
    print(f"   错误类型: {type(e).__name__}")
