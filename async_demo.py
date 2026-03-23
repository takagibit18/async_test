import asyncio
import time
import random

# 定义一个异步函数（协程），模拟下载文件
async def download_file(name, duration):
    print(f"[{time.strftime('%X')}] 开始下载: {name} (需要 {duration} 秒)...")
    await asyncio.sleep(duration)
    print(f"[{time.strftime('%X')}] 下载完成: {name}!")
    return f"{name}的内容"

# 定义一个模拟的网络请求任务
async def fetch_data(api_url, duration):
    print(f"[{time.strftime('%X')}] 请求开始: {api_url} (需要 {duration} 秒)...")
    await asyncio.sleep(duration)
    response = {"url": api_url, "data": f"Response from {api_url}"}
    print(f"[{time.strftime('%X')}] 请求完成: {api_url}")
    return response

# 定义一个带有异常的异步任务，模拟任务失败
async def download_with_error(name, duration, should_fail=False):
    print(f"[{time.strftime('%X')}] 开始下载 (可能失败): {name} (需要 {duration} 秒)...")
    await asyncio.sleep(duration)
    if should_fail:
        raise ValueError(f"下载失败: {name}")
    print(f"[{time.strftime('%X')}] 下载完成: {name}")
    return f"{name}的内容"

# 限制并发任务数（限制同时运行的最大任务数量）
async def limited_concurrent_download():
    semaphore = asyncio.Semaphore(3)  # 限制最多同时执行3个任务

    async def sem_download(name, duration):
        async with semaphore:  # 进入信号量，限制并发数
            return await download_file(name, duration)

    # 启动多个任务
    tasks = [
        sem_download("文件A", 2),
        sem_download("文件B", 3),
        sem_download("文件C", 1),
        sem_download("文件D", 5),
        sem_download("文件E", 4)
    ]
    return await asyncio.gather(*tasks)

# 添加超时控制
async def fetch_data_with_timeout(api_url, duration, timeout):
    try:
        print(f"[{time.strftime('%X')}] 请求开始: {api_url} (需要 {duration} 秒)...")
        # 模拟超时
        result = await asyncio.wait_for(fetch_data(api_url, duration), timeout)
        return result
    except asyncio.TimeoutError:
        print(f"[{time.strftime('%X')}] 请求超时: {api_url}")
        return None

# 定义主程序的异步入口
async def main():
    print("--- 任务开始 ---")
    start_time = time.time()

    result = None  # 先声明 result，防止异常时访问未定义的变量
    try:
        # 使用 asyncio.gather 同时运行多个异步任务
        result = await asyncio.gather(
            download_file("文件A", 2),
            fetch_data("https://api.example.com", 3),
            download_with_error("文件B", 2, should_fail=True),  # 这个任务会失败
            limited_concurrent_download(),  # 并发限制
            fetch_data_with_timeout("https://api.example.com/timeout", 5, timeout=3)  # 超时任务
        )
    except Exception as e:
        print(f"发生错误: {e}")

    end_time = time.time()
    print(f"--- 任务结束 ---")

    print(f"总共耗时: {end_time - start_time:.2f} 秒")
    print(f"最终结果: {result}")  # 如果 result 在异常时也定义了，输出时就不会出错



# 启动异步程序的标准写法
if __name__ == "__main__":
    asyncio.run(main())

# import asyncio
# import time


# # 定义一个异步函数（协程），使用 async def
# async def download_file(name, duration):
#     print(f"[{time.strftime('%X')}] 开始下载: {name} (需要 {duration} 秒)...")

#     # await 的作用是“交出控制权”。
#     # asyncio.sleep 模拟耗时的I/O操作（比如下载文件、请求网页）
#     # 在 sleep 的这段时间里，程序不会傻等，而是会去执行其他的任务。
#     await asyncio.sleep(duration)

#     print(f"[{time.strftime('%X')}] 下载完成: {name}!")
#     return f"{name}的内容"

# async def task(name, duration, semaphore):
#     async with semaphore:  # 在信号量的控制下执行
#         print(f"任务 {name} 开始，预计 {duration} 秒")
#         await asyncio.sleep(duration)
#         print(f"任务 {name} 完成")

# # 定义主程序的异步入口
# async def main():
#     print("--- 任务开始 ---")
#     start_time = time.time()

#     # 方式：使用 asyncio.gather 同时运行多个异步任务
#     # 我们同时开始下载 文件A (耗时2秒) 和 文件B (耗时3秒)
#     result = await asyncio.gather(
#         download_file("文件A", 2),
#         download_file("文件B", 3)
#     )

#     end_time = time.time()
#     print(f"--- 任务结束 ---")

#     print(f"总共耗时: {end_time - start_time:.2f} 秒")
#     print(f"最终结果: {result}")
#     semaphore = asyncio.Semaphore(2)  # 限制最多同时执行2个任务
#     tasks = [
#         task("A", 3, semaphore),
#         task("B", 1, semaphore),
#         task("C", 2, semaphore),
#         task("D", 4, semaphore),
#     ]
#     await asyncio.gather(*tasks)
    


# # 启动异步程序的标准写法
# if __name__ == "__main__":
#     asyncio.run(main())