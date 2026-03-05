import asyncio
import time


# 定义一个异步函数（协程），使用 async def
async def download_file(name, duration):
    print(f"[{time.strftime('%X')}] 开始下载: {name} (需要 {duration} 秒)...")

    # await 的作用是“交出控制权”。
    # asyncio.sleep 模拟耗时的I/O操作（比如下载文件、请求网页）
    # 在 sleep 的这段时间里，程序不会傻等，而是会去执行其他的任务。
    await asyncio.sleep(duration)

    print(f"[{time.strftime('%X')}] 下载完成: {name}!")
    return f"{name}的内容"


# 定义主程序的异步入口
async def main():
    print("--- 任务开始 ---")
    start_time = time.time()

    # 方式：使用 asyncio.gather 同时运行多个异步任务
    # 我们同时开始下载 文件A (耗时2秒) 和 文件B (耗时3秒)
    result = await asyncio.gather(
        download_file("文件A", 2),
        download_file("文件B", 3)
    )

    end_time = time.time()
    print(f"--- 任务结束 ---")

    print(f"总共耗时: {end_time - start_time:.2f} 秒")
    print(f"最终结果: {result}")


# 启动异步程序的标准写法
if __name__ == "__main__":
    asyncio.run(main())