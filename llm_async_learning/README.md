# llm_async_learning

一个面向学习的 OpenAI API 示例项目，包含：

- asyncio 并发控制（Semaphore）
- Pydantic v2 数据验证
- tenacity 重试机制封装
- OpenAI 核心能力 Demo：Chat / Embedding / Function Calling / Streaming
- tiktoken Token 计数与每次调用记录（仅记录 token，不计算金额）
- pytest + pytest-cov，覆盖率阈值 70%

## 1. 环境要求

- Python 3.12

## 2. 安装

```bash
pip install -e .
pip install -e .[dev]
```

如果你不使用 editable 模式，也可以：

```bash
pip install .
pip install "pytest>=8.3.0" "pytest-asyncio>=0.25.0" "pytest-cov>=6.0.0"
```

## 3. 配置 API

1. 复制 `.env.example` 为 `.env`
2. 手动填写以下字段：

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=
OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_MAX_CONCURRENCY=5
OPENAI_TIMEOUT_SECONDS=30
OPENAI_RETRY_ATTEMPTS=3
OPENAI_RETRY_MIN_SECONDS=1
OPENAI_RETRY_MAX_SECONDS=8
```

## 4. 运行 Demo

在项目根目录执行：

```bash
python run_demos.py --mode all
```

可选模式：

- `chat`
- `embedding`
- `function`
- `stream`
- `all`

示例：

```bash
python run_demos.py --mode chat
```

## 5. 测试与覆盖率

```bash
pytest
```

说明：

- 已配置 `--cov-fail-under=70`
- 默认单元测试全部基于 mock，不依赖真实网络
- 集成测试默认跳过

启用真实 API 集成测试：

```bash
RUN_INTEGRATION=1 pytest -m integration
```

Windows PowerShell 下：

```powershell
$env:RUN_INTEGRATION="1"; pytest -m integration
```

## 6. 项目结构

```text
llm_async_learning/
  src/llm_async_learning/
    client.py              # 异步客户端 + 并发控制 + 重试封装
    config.py              # Pydantic Settings (.env)
    models.py              # 请求/响应与使用记录模型
    token_counter.py       # tiktoken 计数
    usage_tracker.py       # 调用 token 记录汇总
    demos/
      chat_demo.py
      embedding_demo.py
      function_calling_demo.py
      streaming_demo.py
  tests/
    test_client.py
    test_demos.py
    test_token_counter.py
    integration/test_openai_integration.py
  run_demos.py
  .env.example
  pyproject.toml
```

## 7. 关键实现要点

### 7.1 模块职责分层

- `config.py`：配置入口层
  - 使用 `AppSettings(BaseSettings)` 读取 `.env`。
  - 对关键配置做约束（如并发数、超时、重试次数）和 `OPENAI_BASE_URL` 规范化校验。
  - `load_settings()` 是运行脚本与业务客户端的统一配置入口。

- `models.py`：数据契约层（Pydantic v2）
  - 定义 `ChatRequest`、`EmbeddingRequest`、`FunctionCallingRequest` 等请求模型。
  - 定义 `ChatResponse`、`EmbeddingResponse`、`FunctionCallingResponse` 等响应模型。
  - 定义 `TokenUsageRecord` 作为调用统计的统一记录结构。
  - 作用是把“输入合法性校验 + 输出结构约束”前置，避免在业务函数里散落参数检查。

- `client.py`：核心编排层（最关键）
  - `LLMClient.__init__` 初始化 `AsyncOpenAI`、`asyncio.Semaphore`、`TokenCounter`、`UsageTracker`。
  - `_retry_call` 统一封装 tenacity 异步重试策略（指数退避 + 指定异常类型）。
  - `chat` / `embedding` / `function_call` / `stream_chat` 统一遵循以下模板：
    1) 接收并校验请求模型
    2) 进入并发信号量
    3) 发起 OpenAI 兼容请求（带重试）
    4) 提取 usage 或使用 tiktoken 回退估算
    5) 写入 `UsageTracker`
    6) 返回对应响应模型

- `token_counter.py`：Token 估算层
  - 使用 `tiktoken` 实现文本、消息、工具定义的 token 计数。
  - 当服务端响应不含完整 usage 时，作为本地兜底统计。

- `usage_tracker.py`：统计聚合层
  - 负责保存每次调用记录，并按端点/总量聚合。
  - 为运行结束时的 token 汇总输出提供数据来源。

- `demos/*.py`：能力示例层
  - 每个 demo 只关心“构造请求 + 调用 client + 返回核心结果”。
  - 不重复实现重试、并发、计数等横切逻辑。

- `run_demos.py`：运行入口层
  - 解析命令行模式（chat/embedding/function/stream/all）。
  - 构造 `LLMClient` 并调度各 demo。
  - `all` 模式使用 `asyncio.gather` 并发执行，且按任务输出成功/失败，最后打印 token 汇总。

### 7.2 端到端调用链（以 Chat 为例）

1. `run_demos.py` 调用 `run_chat_demo(client)`。
2. `chat_demo.py` 构造 `ChatRequest(messages=[...])`。
3. `client.chat(request)` 执行：
   - 使用 Pydantic 模型确保输入合法。
   - 进入 `Semaphore` 控制并发。
   - 通过 `_retry_call` 包装 `client.chat.completions.create(...)`。
   - 解析响应文本与 usage。
   - usage 缺失时调用 `TokenCounter` 本地估算。
   - 调用 `_record_usage` 写入 `UsageTracker`。
4. 返回 `ChatResponse` 给 demo，入口脚本统一打印。

### 7.3 四类核心功能如何编排

- Chat
  - 请求：`ChatRequest`
  - 客户端方法：`LLMClient.chat`
  - 输出：`ChatResponse(content + token usage)`

- Embedding
  - 请求：`EmbeddingRequest(input_texts)`
  - 客户端方法：`LLMClient.embedding`
  - 输出：`EmbeddingResponse(vectors + token usage)`

- Function Calling
  - 请求：`FunctionCallingRequest(messages + tools + tool_choice)`
  - 客户端方法：`LLMClient.function_call`
  - 输出：`FunctionCallingResponse(tool_name/tool_arguments_json + usage)`

- Streaming
  - 请求：`ChatRequest`
  - 客户端方法：`LLMClient.stream_chat`（异步生成器）
  - 输出：分片 `yield`，并在流结束后记录 token 使用

### 7.4 错误处理与可观测性

- 可重试错误
  - 对超时和限流类错误进行 tenacity 重试，避免短暂故障导致请求直接失败。

- 不可重试错误
  - 如认证失败、模型不存在等，直接抛出，便于尽快定位配置问题。

- 运行可观测性
  - `all` 模式下每个 demo 分别输出成功/失败，避免一个端点失败导致整体中断。
  - 结束时输出 `usage_summary`，便于观察本次运行的 token 消耗。
