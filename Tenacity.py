from tenacity import retry, stop_after_attempt, wait_fixed
import random

# # 定义一个可能会失败的操作
# @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))# 失败后最多重试3次，每次间隔2秒
# def unreliable_operation():
#     if random.random() < 0.7:
#         raise ValueError("Random failure!")
#     return "Success!"

# # 调用函数
# try:
#     result = unreliable_operation()
#     print(result)
# except ValueError as e:
#     print(f"Operation failed after 3 attempts: {e}")


#自定义异常层次
class MyAppError(Exception):
    """基类异常"""
    pass

class DatabaseError(MyAppError):
    """数据库操作异常"""
    pass

class NetworkError(MyAppError):
    """网络请求异常"""
    pass

def perform_task():# 模拟一个可能抛出网络错误的任务
    raise NetworkError("Network issue occurred!")

def perform_MyAppError_task():# 模拟一个可能抛出 MyAppError 的任务
    raise MyAppError("A general MyAppError occurred!")

try:
    perform_task()
    perform_MyAppError_task()# 这行不会执行，因为上面已经抛出了 NetworkError
except NetworkError as e:
    print(f"Handled network error: {e}")
except MyAppError as e: #python 的异常处理是从上到下匹配的，所以 MyAppError 的 except 块放在 NetworkError 之后，这样 NetworkError 就不会被 MyAppError 捕获了。
    print(f"Unhandled MyAppError: {e}")