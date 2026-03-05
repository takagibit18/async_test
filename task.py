import asyncio
import time
async def print_odd_numbers():
    for i in range(1, 10, 2):  # 1, 3, 5, 7, 9
        print(f"奇数: {i}")
        await asyncio.sleep(0.5)

async def print_even_numbers():
    for i in range(0, 10, 2):  # 0, 2, 4, 6, 8
        print(f"偶数: {i}")
        await asyncio.sleep(0.5)

async def main():
    start_time = time.time()
    await asyncio.gather(
        print_odd_numbers(),
        print_even_numbers()  
    )
    end_time = time.time()
    print(f"总耗时: {end_time - start_time:.2f} 秒")
if __name__== '__main__':
    asyncio.run(main())
