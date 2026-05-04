# my_agent

[English](#english) | [中文](#中文)

---

## English

A lightweight Python library for building AI Agents with OpenAI-compatible APIs, seamless conversation history management, and built-in function calling support.

### ✨ Features

- 🚀 **Easy to use**: Clean API design, get started in minutes
- 🔌 **OpenAI compatible**: Works with any service that follows OpenAI API format
- 💾 **Conversation history management**: Built-in save/load/management for conversation history
- 🔧 **Function calling support**: Built-in Tool and ToolRegistry for easy function calling
- 📝 **JSON output support**: Get structured JSON responses with one call
- 🌊 **Streaming response**: Real-time streaming output support
- 🎯 **Detailed usage statistics**: Get complete token usage info, including cached tokens and other advanced stats
- 🛠️ **Highly configurable**: Supports both global defaults and per-instance configuration

### 📦 Installation

Install from source:

```bash
git clone https://github.com/Leabots/my_agent.git
cd my_agent
pip install -e .
```

### 🚀 Quick Start

```python
from my_agent import Agent
from my_agent.tool import ToolRegistry
from my_agent.urls import DEEPSEEK_URL

# Set global default configuration with DeepSeek
Agent.set_default(
    base_url=DEEPSEEK_URL,
    model="deepseek-chat",
    api_key="your-deepseek-api-key-here"
)

# Create tool registry and register tools
def get_current_weather(city: str) -> str:
    """Get the current weather in a given city."""
    # This is a mock implementation
    return f"The weather in {city} is sunny, 25°C."

registry = ToolRegistry()
registry.register(
    name="get_current_weather",
    description="Get the current weather in a given city",
    handler=get_current_weather,
    param_descriptions={
        "city": "The city to get the weather for"
    }
)

# Create an agent with tools
agent = Agent(
    system_prompt="You are a helpful assistant that can check the weather.",
    tool_registry=registry
)

# Send a request, the agent will automatically use tools if needed
response = agent.complete_with_tools("What's the weather like in Beijing?")
print(response['content'])
```

### 📖 Examples

#### 1. Basic Usage

```python
from my_agent import Agent
from my_agent.urls import DEEPSEEK_URL

# Create agent with custom DeepSeek configuration (overrides defaults)
agent = Agent(
    base_url=DEEPSEEK_URL,
    model="deepseek-coder",
    api_key="your-deepseek-api-key-here",
    system_prompt="You are a professional Python development assistant.",
    temperature=0.3,
    max_tokens=4096
)

response = agent.complete("How to handle exceptions in Python?")
print(response['content'])
```

#### 2. Function Calling with Tools

```python
from my_agent import Agent
from my_agent.tool import Tool, ToolRegistry
from my_agent.urls import DEEPSEEK_URL

# Define your functions
def calculate(operation: str, a: float, b: float) -> float:
    """Calculate the result of an arithmetic operation.
    
    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number
    """
    if operation == 'add':
        return a + b
    elif operation == 'subtract':
        return a - b
    elif operation == 'multiply':
        return a * b
    elif operation == 'divide':
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")

def search_web(query: str) -> str:
    """Search the web for information."""
    # This is a mock implementation
    return f"Search results for '{query}': ..."

# Create registry and register tools
registry = ToolRegistry()

# Register with auto-inference from docstring
registry.register(
    name="calculate",
    description="Perform arithmetic calculations",
    handler=calculate
)

# Register with manual parameter descriptions
registry.register(
    name="search_web",
    description="Search the web for information",
    handler=search_web,
    param_descriptions={"query": "The search query"}
)

# Create agent
agent = Agent(
    system_prompt="You are a helpful assistant that can use tools to answer questions.",
    tool_registry=registry,
    base_url=DEEPSEEK_URL,
    api_key="your-deepseek-api-key-here"
)

# The agent will automatically call tools and handle the results
response = agent.complete_with_tools("What is 123 multiplied by 456?")
print(response['content'])
```

#### 3. Get JSON Output

```python
# Request JSON formatted response
response = agent.json_output("""
Please return a JSON object containing user information, 
including three fields: name, age, skills.
""")

# Content is already parsed into a Python object
user_info = response['content']
print(user_info['name'])
print(user_info['skills'])
```

#### 4. Streaming Response

```python
# Stream output, get response chunk by chunk
for chunk in agent.stream_complete("Tell me a story."):
    if 'delta' in chunk:
        print(chunk['delta'], end='', flush=True)
    if chunk.get('done'):
        # The last chunk contains the complete response
        final_response = chunk['final_response']
        print(f"\n\nDone! Total tokens: {final_response['total_tokens']}")
```

#### 5. Conversation History Management

```python
# Conversations are automatically saved to history
agent.complete("My name is John.")
response = agent.complete("What's my name?")
print(response['content'])  # The assistant remembers your name

# Clear history
agent.clear_history()

# Save conversation history to file
agent.save_history("my_conversation")

# Load saved conversation history
agent.load_history("my_conversation")

# List all saved conversations
histories = agent.list_saved_histories()
print(histories)
```

### 🔧 API Reference

#### `Agent.set_default(base_url, model, api_key)`
Set global default configuration, all new Agent instances will use these defaults.

#### `Agent.__init__()`
Create a new Agent instance.

**Parameters:**
- `base_url` (str, optional): API base URL
- `model` (str, optional): Model name
- `api_key` (str, optional): API key
- `system_prompt` (str, default: "You are a helpful assistant."): System prompt
- `temperature` (float, default: 0.5): Sampling temperature
- `max_tokens` (int, default: 4096): Maximum tokens to generate
- `tool_registry` (ToolRegistry, optional): Tool registry with registered tools for function calling

#### `Agent.complete(user_input, record=True)`
Send a non-streaming request without tool calling.

**Parameters:**
- `user_input` (str): User input content
- `record` (bool, default: True): Whether to record in conversation history

**Returns:** Dictionary with complete response information, including:
- `id`: Response ID
- `content`: Response content
- `model`: Model name
- `created`: Creation timestamp
- `completion_tokens`: Number of completion tokens
- `prompt_tokens`: Number of prompt tokens
- `total_tokens`: Total tokens
- `finish_reason`: Finish reason
- And other extended information

#### `Agent.complete_with_tools(user_input, max_tool_calls=5, record=True)`
Send a request with automatic tool calling. The agent will automatically call tools and continue conversation until it gets the final answer.

**Parameters:**
- `user_input` (str): User input content
- `max_tool_calls` (int, default: 5): Maximum number of tool calls to prevent infinite loops
- `record` (bool, default: True): Whether to record in conversation history

**Returns:** Dictionary with the final response information

#### `Agent.json_output(user_input, record=True)`
Send a request and return a parsed JSON object.

Parameters and return values are similar to `complete()`, except `content` is parsed into a Python object.

#### `Agent.stream_complete(user_input, record=True)`
Stream the request, yield chunks in generator mode.

**Parameters:** Same as `complete()`

**Yields:** Each chunk is a dictionary, the last chunk contains `{"done": True, "final_response": ...}`

#### History Management Methods
- `Agent.clear_history()`: Clear conversation history
- `Agent.save_history(name)`: Save history to JSON file, returns save path
- `Agent.load_history(name)`: Load history from file, returns success status
- `Agent.list_saved_histories()`: List all saved histories

---

#### `Tool`
Tool class for function calling. Automatically infers parameter schema from function signature and docstring.

If you do not manually provide `param_descriptions` and `return_description`, the system will automatically try to infer them from the function's docstring. **However, this approach is not recommended** as parsing docstrings can be error-prone, and manually providing descriptions ensures better quality and accuracy for the model.

**Constructor:**
- `name`: Tool name (must be unique)
- `description`: Tool description for the model
- `handler`: Function to execute when tool is called
- `param_descriptions`: Optional dict mapping parameter names to descriptions
- `return_description`: Optional description of the return value

#### `ToolRegistry`
Registry for managing multiple tools.

**Methods:**
- `register(name, description, handler, param_descriptions=None, return_description=None)`: Register a function as a tool
- `get_definitions()`: Get all tool definitions for API
- `execute(name, arguments)`: Execute a tool by name with JSON arguments string
- `remove(name)`: Remove a tool by name
- `clear()`: Remove all tools

### 🌐 Supported API Providers

Since it uses OpenAI-compatible format, you can use `my_agent` with any service that follows the OpenAI API format:

- [DeepSeek](https://www.deepseek.com/)
- [OpenAI](https://openai.com/)
- [Anthropic (via 3rd-party compatibility layer)](https://www.anthropic.com/)
- [Google Gemini (via 3rd-party compatibility layer)](https://ai.google.dev/)
- [Moonshot AI](https://platform.moonshot.cn/)
- [Lingyi Wanwu](https://www.lingyiwanwu.com/)
- [Tongyi Qwen](https://help.aliyun.com/zh/dashscope/)
- [ERNIE](https://cloud.baidu.com/doc/WENXINWORKSHOP/index.html)
- Any other service that provides OpenAI-compatible API

### 📊 Response Fields

All methods return responses containing these fields:

| Field | Description |
|-------|-------------|
| `id` | Unique response ID |
| `content` | Response content |
| `model` | Model used |
| `created` | Creation timestamp |
| `completion_tokens` | Number of completion tokens |
| `prompt_tokens` | Number of prompt tokens |
| `total_tokens` | Total tokens |
| `finish_reason` | Generation finish reason |
| `system_fingerprint` | System fingerprint |
| `prompt_tokens_cached_tokens` | Cached prompt tokens (if supported) |
| `completion_tokens_audio_tokens` | Audio tokens (if supported) |

### 🤝 Contributing

Issues and Pull Requests are welcome!

### 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 中文

一个轻量级的 Python 库，用于使用 OpenAI 兼容的 API 构建 AI Agent，提供易于使用的对话历史管理和内置函数调用支持。

### ✨ 功能特性

- 🚀 **简单易用**: 简洁的 API 设计，几分钟即可上手
- 🔌 **OpenAI 兼容**: 支持任何与 OpenAI API 格式兼容的服务
- 💾 **对话历史管理**: 内置便捷的历史记录保存、加载和管理功能
- 🔧 **工具调用支持**: 内置 Tool 和 ToolRegistry，轻松实现函数调用
- 📝 **JSON 输出支持**: 一键获取结构化的 JSON 响应
- 🌊 **流式响应**: 支持实时流式输出
- 🎯 **详细的使用统计**: 获取完整的 token 使用信息，包括缓存 tokens 等高级统计
- 🛠️ **高度可配置**: 支持全局默认配置和实例级单独配置

### 📦 安装

从源码安装：

```bash
git clone https://github.com/Leabots/my_agent.git
cd my_agent
pip install -e .
```

### 🚀 快速开始

```python
from my_agent import Agent
from my_agent.tool import ToolRegistry
from my_agent.urls import DEEPSEEK_URL

# 设置全局默认配置（使用DeepSeek）
Agent.set_default(
    base_url=DEEPSEEK_URL,
    model="deepseek-chat",
    api_key="your-deepseek-api-key-here"
)

# 创建工具注册表并注册工具
def get_current_weather(city: str) -> str:
    """获取指定城市的当前天气。"""
    # 这是一个模拟实现
    return f"北京当前天气晴朗，温度25°C。"

registry = ToolRegistry()
registry.register(
    name="get_current_weather",
    description="获取指定城市的当前天气",
    handler=get_current_weather,
    param_descriptions={
        "city": "要查询天气的城市名称"
    }
)

# 创建一个支持工具调用的 agent
agent = Agent(
    system_prompt="你是一个乐于助人的助手，可以查询天气。",
    tool_registry=registry
)

# 发送请求，如果需要，agent 会自动使用工具
response = agent.complete_with_tools("北京今天天气怎么样？")
print(response['content'])
```

### 📖 使用示例

#### 1. 基本使用

```python
from my_agent import Agent
from my_agent.urls import DEEPSEEK_URL

# 创建 agent 时单独配置（会覆盖默认配置），使用DeepSeek
agent = Agent(
    base_url=DEEPSEEK_URL,
    model="deepseek-coder",
    api_key="your-deepseek-api-key-here",
    system_prompt="你是一个专业的 Python 开发助手。",
    temperature=0.3,
    max_tokens=4096
)

response = agent.complete("如何在 Python 中处理异常？")
print(response['content'])
```

#### 2. 使用工具调用（Function Calling）

```python
from my_agent import Agent
from my_agent.tool import Tool, ToolRegistry
from my_agent.urls import DEEPSEEK_URL

# 定义你的函数
def calculate(operation: str, a: float, b: float) -> float:
    """计算算术运算的结果。
    
    Args:
        operation: 要执行的操作（add, subtract, multiply, divide）
        a: 第一个数字
        b: 第二个数字
    """
    if operation == 'add':
        return a + b
    elif operation == 'subtract':
        return a - b
    elif operation == 'multiply':
        return a * b
    elif operation == 'divide':
        return a / b
    else:
        raise ValueError(f"未知操作: {operation}")

def search_web(query: str) -> str:
    """搜索网络获取信息。"""
    # 这是一个模拟实现
    return f"搜索 '{query}' 的结果：..."

# 创建注册表并注册工具
registry = ToolRegistry()

# 从文档字符串自动推断参数
registry.register(
    name="calculate",
    description="执行算术计算",
    handler=calculate
)

# 使用手动参数描述
registry.register(
    name="search_web",
    description="搜索网络获取信息",
    handler=search_web,
    param_descriptions={"query": "搜索关键词"}
)

# 创建 agent
agent = Agent(
    system_prompt="你是一个乐于助人的助手，可以使用工具回答问题。",
    tool_registry=registry,
    base_url=DEEPSEEK_URL,
    api_key="your-deepseek-api-key-here"
)

# Agent 会自动调用工具并处理结果
response = agent.complete_with_tools("123乘以456等于多少？")
print(response['content'])
```

#### 3. 获取 JSON 格式输出

```python
# 请求 JSON 格式的响应
response = agent.json_output("""
请返回一个包含用户信息的 JSON 对象，包含 name、age、skills 三个字段。
""")

# 内容已经被解析为 Python 对象
user_info = response['content']
print(user_info['name'])
print(user_info['skills'])
```

#### 4. 流式响应

```python
# 流式输出，逐块获取响应
for chunk in agent.stream_complete("请给我讲一个故事。"):
    if 'delta' in chunk:
        print(chunk['delta'], end='', flush=True)
    if chunk.get('done'):
        # 最后一个 chunk 包含完整的响应信息
        final_response = chunk['final_response']
        print(f"\n\n完成！总 Token 数: {final_response['total_tokens']}")
```

#### 5. 对话历史管理

```python
# 对话会自动保存在历史中
agent.complete("我叫张三。")
response = agent.complete("我叫什么名字？")
print(response['content'])  # 助手记得你的名字

# 清空历史
agent.clear_history()

# 保存对话历史到文件
agent.save_history("my_conversation")

# 加载已保存的对话历史
agent.load_history("my_conversation")

# 列出所有已保存的对话
histories = agent.list_saved_histories()
print(histories)
```

### 🔧 API 参考

#### `Agent.set_default(base_url, model, api_key)`
设置全局默认配置，所有新创建的 Agent 实例都会使用这些默认值。

#### `Agent.__init__()`
创建一个新的 Agent 实例。

**参数：**
- `base_url` (str, optional): API 基础 URL
- `model` (str, optional): 模型名称
- `api_key` (str, optional): API 密钥
- `system_prompt` (str, default: "You are a helpful assistant."): 系统提示词
- `temperature` (float, default: 0.5): 采样温度
- `max_tokens` (int, default: 4096): 最大生成 token 数
- `tool_registry` (ToolRegistry, optional): 注册了工具的工具注册表，用于函数调用

#### `Agent.complete(user_input, record=True)`
发送一个非流式请求，不启用工具调用。

**参数：**
- `user_input` (str): 用户输入内容
- `record` (bool, default: True): 是否记录到对话历史

**返回：** 包含完整响应信息的字典，包括：
- `id`: 响应 ID
- `content`: 响应内容
- `model`: 模型名称
- `created`: 创建时间戳
- `completion_tokens`: 完成 tokens 数量
- `prompt_tokens`: 提示 tokens 数量
- `total_tokens`: 总 tokens 数量
- `finish_reason`: 停止原因
- 以及其他扩展信息

#### `Agent.complete_with_tools(user_input, max_tool_calls=5, record=True)`
发送请求并启用自动工具调用。Agent 会自动调用工具并继续对话直到得到最终答案。

**参数：**
- `user_input` (str): 用户输入内容
- `max_tool_calls` (int, default: 5): 最大工具调用次数，防止无限循环
- `record` (bool, default: True): 是否记录到对话历史

**返回：** 包含最终响应信息的字典

#### `Agent.json_output(user_input, record=True)`
发送请求并返回解析后的 JSON 对象。

参数和返回值与 `complete()` 类似，只是 `content` 被解析为 Python 对象。

#### `Agent.stream_complete(user_input, record=True)`
流式发送请求，生成器模式逐块返回结果。

**参数：** 同 `complete()`

**生成：** 每个块是一个字典，最后一个块包含 `{"done": True, "final_response": ...}`

#### 历史管理方法
- `Agent.clear_history()`: 清空对话历史
- `Agent.save_history(name)`: 保存历史到 JSON 文件，返回保存路径
- `Agent.load_history(name)`: 从文件加载历史，返回成功状态
- `Agent.list_saved_histories()`: 列出所有已保存的历史

---

#### `Tool`
工具类，用于函数调用。自动从函数签名和文档字符串推断参数 schema。

如果你没有手动提供 `param_descriptions` 和 `return_description`，系统会自动尝试从函数的 docstring 中推断它们。**不过不推荐使用这种方式**，因为解析 docstring 可能会出错，手动提供描述可以确保为模型提供更好的质量和准确性。

**构造函数：**
- `name`: 工具名称（必须唯一）
- `description`: 给模型看的工具描述
- `handler`: 工具被调用时执行的函数
- `param_descriptions`: 可选，参数名称到描述的字典映射
- `return_description`: 可选，返回值的描述

#### `ToolRegistry`
用于管理多个工具的注册表。

**方法：**
- `register(name, description, handler, param_descriptions=None, return_description=None)`: 将函数注册为工具
- `get_definitions()`: 获取所有工具定义，用于 API 调用
- `execute(name, arguments)`: 根据名称执行工具，使用 JSON 参数字符串
- `remove(name)`: 根据名称移除工具
- `clear()`: 移除所有工具

### 🌐 支持的 API 提供商

由于使用 OpenAI 兼容格式，你可以将 `my_agent` 与任何遵循 OpenAI API 格式的服务一起使用：

- [DeepSeek](https://www.deepseek.com/)
- [OpenAI](https://openai.com/)
- [Anthropic (通过第三方兼容层)](https://www.anthropic.com/)
- [Google Gemini (通过第三方兼容层)](https://ai.google.dev/)
- [Moonshot AI](https://platform.moonshot.cn/)
- [零一万物](https://www.lingyiwanwu.com/)
- [通义千问](https://help.aliyun.com/zh/dashscope/)
- [文心一言](https://cloud.baidu.com/doc/WENXINWORKSHOP/index.html)
- 任何其他提供 OpenAI 兼容 API 的服务

### 📊 响应字段说明

所有方法返回的响应都包含以下字段：

| 字段 | 说明 |
|------|------|
| `id` | 响应唯一 ID |
| `content` | 响应内容 |
| `model` | 使用的模型 |
| `created` | 创建时间戳 |
| `completion_tokens` | 生成的 token 数 |
| `prompt_tokens` | 输入的 token 数 |
| `total_tokens` | 总 token 数 |
| `finish_reason` | 生成停止原因 |
| `system_fingerprint` | 系统指纹 |
| `prompt_tokens_cached_tokens` | 缓存的提示 token 数（若支持） |
| `completion_tokens_audio_tokens` | 音频 token 数（若支持） |

### 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。