# my_agent

[English](#english) | [中文](#中文)

---

## English

A lightweight Python library for building AI Agents with OpenAI-compatible APIs and seamless conversation history management.

### ✨ Features

- 🚀 **Easy to use**: Clean API design, get started in minutes
- 🔌 **OpenAI compatible**: Works with any service that follows OpenAI API format
- 💾 **Conversation history management**: Built-in save/load/management for conversation history
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
from my_agent.urls import DEEPSEEK_URL

# Set global default configuration with DeepSeek
Agent.set_default(
    base_url=DEEPSEEK_URL,
    model="deepseek-chat",
    api_key="your-deepseek-api-key-here"
)

# Create an agent
agent = Agent(system_prompt="You are a helpful assistant.")

# Send a request and get response
response = agent.complete("Hello! Introduce yourself please.")
print(response['content'])
print(f"Token usage: {response['total_tokens']}")
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

#### 2. Get JSON Output

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

#### 3. Streaming Response

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

#### 4. Conversation History Management

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

#### `Agent.complete(user_input, record=True)`
Send a non-streaming request.

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

一个轻量级的 Python 库，用于使用 OpenAI 兼容的 API 构建 AI Agent，提供易于使用的对话历史管理。

### ✨ 功能特性

- 🚀 **简单易用**: 简洁的 API 设计，几分钟即可上手
- 🔌 **OpenAI 兼容**: 支持任何与 OpenAI API 格式兼容的服务
- 💾 **对话历史管理**: 内置便捷的历史记录保存、加载和管理功能
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
from my_agent.urls import DEEPSEEK_URL

# 设置全局默认配置（使用DeepSeek）
Agent.set_default(
    base_url=DEEPSEEK_URL,
    model="deepseek-chat",
    api_key="your-deepseek-api-key-here"
)

# 创建一个 agent
agent = Agent(system_prompt="你是一个乐于助人的助手。")

# 发送请求并获取响应
response = agent.complete("你好！请介绍一下你自己。")
print(response['content'])
print(f"Token 使用: {response['total_tokens']}")
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

#### 2. 获取 JSON 格式输出

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

#### 3. 流式响应

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

#### 4. 对话历史管理

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

#### `Agent.complete(user_input, record=True)`
发送一个非流式请求。

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