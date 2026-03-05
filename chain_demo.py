import asyncio
import time
from langchain_core.runnables import RunnableLambda


# ==========================================
# 1. 准备工作：模拟一个 LangChain 的大模型处理链 (Chain)
# ==========================================
async def simulate_llm(inputs: dict) -> str:
    """模拟大模型生成文本的过程，固定耗时 2 秒"""
    topic = inputs.get("topic")
    style = inputs.get("style")

    print(f"[{time.strftime('%X')}] 🤖 AI 开始构思【{style}】风格的【{topic}】...")
    # 模拟网络请求大模型的耗时
    await asyncio.sleep(2)
    print(f"[{time.strftime('%X')}] ✅ 【{style}】构思完成！")

    return f"这是一篇完美的{style}文案！"


# 将普通函数包装成 LangChain 标准的 Runnable（运行组件）
# 包装后，它就拥有了 LangChain 专属的 .invoke() 和 .ainvoke() 方法
llm_chain = RunnableLambda(simulate_llm)


# ==========================================
# 2. 传统做法：同步生成（我已帮你写好，作为对照组）
# ==========================================
async def sync_generate(topic: str, styles: list):
    print("\n--- 🐌 开始【同步】生成 ---")
    start_time = time.time()

    results = []
    for style in styles:
        # 注意：这里使用的是同步的 invoke
        res = await llm_chain.ainvoke({"topic": topic, "style": style})
        results.append(res)

    print(f"🐌 同步生成总耗时: {time.time() - start_time:.2f} 秒")
    return results


# ==========================================
# 3. 你的考场：异步生成（请补充这里的代码）
# ==========================================
async def async_generate(topic: str, styles: list):
    print("\n--- 🚀 开始【异步】并发生成 ---")
    start_time = time.time()

    # 💡 提示 1：你需要把 styles 列表里的每一个风格，变成一个大模型调用任务。
    # 💡 提示 2：在 LangChain 中，异步调用请使用 llm_chain.ainvoke({...})
    # 💡 提示 3：使用 asyncio.gather(...) 把所有任务打包一起执行，并获取结果。

    # 👇 请在下方写下你的代码：

    tasks = [llm_chain.ainvoke({"topic": topic, "style": style}) for style in styles]
    results = await asyncio.gather(*tasks)
    # results = await asyncio.gather(
    #     写下你的 3 个任务...
    # )

    # 👆 -----------------------

    print(f"🚀 异步生成总耗时: {time.time() - start_time:.2f} 秒")
    return results  # 解开这行的注释


# ==========================================
# 4. 主程序开关
# ==========================================
async def main():
    topic = "一只会穿越时空的猫"
    styles = ["科幻风", "悬疑风", "治愈风"]

    # 先运行同步版本看看有多慢 (约 6 秒)
    # 注意：同步函数直接调用即可
    await sync_generate(topic, styles)

    # 再运行你写的异步版本看看有多快 (期望约 2 秒)
    results = await async_generate(topic, styles) # 写完后解开这行的注释！
    print(results)


if __name__ == "__main__":
    asyncio.run(main())