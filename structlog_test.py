import structlog
import logging

# 配置日志系统
logging.basicConfig(level=logging.INFO, format="%(message)s")
log = structlog.get_logger()

# 记录一些日志消息
log = log.bind(module="main")  # 绑定上下文信息，避免多次传递同样的参数
log.info("Program started", event="start")
log.info("Performing task", task="data_processing", status="in_progress")

# 模拟一个错误并记录
try:
    result = 10 / 0  # 这会引发 ZeroDivisionError
except ZeroDivisionError as e:
    log.error("Error occurred", error=str(e), context="task_execution")

# 记录完成任务的日志
log.info("Task completed", task="data_processing", status="completed")