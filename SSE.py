
import asyncio
from typing import AsyncGenerator, Optional

from fastapi import FastAPI
from fastapi.responses import StreamingResponse


# ===========================================================
# 1. 本文件目标：用 FastAPI + SSE 实现「流式打字机」效果
# ===========================================================
# 你将学到：
# - 如何用 FastAPI 提供一个 text/event-stream 接口
# - 如何用异步生成器（async generator）一段一段地推送数据
# - 为什么这种方式在高耗时 LLM 场景下更高效（非阻塞、易扩展）

app = FastAPI(title="Async LLM SSE Demo")


# ===========================================================
# 2. 模拟一个「逐字输出」的大模型回复
# ===========================================================
async def fake_llm_typewriter(prompt: str) -> AsyncGenerator[str, None]:
    """
    模拟一个大模型逐字打字的过程。
    实际项目中，这里可以替换成真实的 LLM 流式接口（如 OpenAI / 自建服务）。
    """
    # 为了便于观察效果，生成一段固定文案
    full_text = f"收到你的问题：{prompt}。下面是通过 FastAPI + SSE 实现的流式打字机效果示例。"

    for ch in full_text:
        # 模拟 LLM 生成下一 token 的耗时
        await asyncio.sleep(0.05)
        # 每次只返回一个「小片段」
        yield ch


# ===========================================================
# 3. SSE 协议格式化工具：把文本包装成 SSE 消息
# ===========================================================
def format_sse(data: str, event: Optional[str] = None) -> str:
    """
    把普通字符串包装成 SSE 协议格式：
        event: <事件名>   # 可选
        data: <数据行>   # 可以多行

    消息之间用一个空行分隔。
    """
    msg = ""
    if event:
        msg += f"event: {event}\n"

    # SSE 要求每一行都以 data: 开头
    for line in data.splitlines() or [""]:
        msg += f"data: {line}\n"

    # 空行表示一条消息结束
    msg += "\n"
    return msg


# ===========================================================
# 4. 核心：异步生成器 + StreamingResponse 构造 SSE 流
# ===========================================================
async def sse_chat_stream(prompt: str) -> AsyncGenerator[bytes, None]:
    """
    这是一个异步生成器：
    - 每次 async for 迭代，生成一条 SSE 消息（bytes）
    - FastAPI 会把这些消息「一边生成、一边发送」给前端
    """
    # ① 持续从「大模型」流式拿到小片段
    async for chunk in fake_llm_typewriter(prompt):
        # ② 把小片段封装成 SSE 消息并编码为 bytes
        yield format_sse(chunk).encode("utf-8")

    # ③ 约定一个结束标记，方便前端知道流已结束
    yield format_sse("[DONE]", event="end").encode("utf-8")


# ===========================================================
# 5. FastAPI 路由：对外暴露 /chat_stream SSE 接口
# ===========================================================
@app.get("/chat_stream")
async def chat_stream(prompt: str):
    """
    后端 SSE 接口说明：
    - 请求方式：GET /chat_stream?prompt=你好
    - 响应头：Content-Type: text/event-stream
    - 响应体：按 SSE 协议持续推送多条消息

    ⚠️ 重点：这个接口是非阻塞的。
       多个客户端并发连接时，每条连接对应一个协程，
       互不阻塞，充分利用 asyncio 的并发能力。
    """
    return StreamingResponse(
        sse_chat_stream(prompt),
        media_type="text/event-stream",
    )


# ===========================================================
# 6. 本地启动说明（开发调试用）
# ===========================================================
# 在命令行运行：
#   uvicorn SSE:app --reload --host 0.0.0.0 --port 8000
#
# 前端（或浏览器）可以这样连接：
#   const es = new EventSource("http://127.0.0.1:8000/chat_stream?prompt=你好");
#   es.onmessage = (event) => {
#       // event.data 就是后端推来的「一小段」文本
#       console.log(event.data);
#   };
#   es.addEventListener("end", () => {
#       console.log("流式传输结束");
#       es.close();
#   });
#
# 通过这个小例子，你已经掌握：
# - 如何设计一个基于 FastAPI 的 SSE 流式接口
# - 如何用异步生成器 + StreamingResponse 构建高并发、非阻塞的响应链路
# - 如何把它应用到 LLM 的流式打字机场景中

