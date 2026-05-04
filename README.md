# My Agent

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English Version

### ✨ Features

- 🚀 **Simple & Intuitive** - Clean API design for rapid development
- 🔧 **Function Calling** - Full support for OpenAI-standard tool calls with automatic parsing and execution
- 📝 **Streaming Output** - Real-time streaming responses with tool call progress indicators
- 💾 **History Management** - Automatic conversation history with JSON save/load
- 🎯 **JSON Mode** - Enforce JSON output for structured data extraction
- 🔌 **Flexible Configuration** - Global defaults and per-instance settings
- 📦 **Lightweight** - Only depends on `openai`

### 📦 Installation

Follow these steps to install `my_agent`:

1.  **Clone the repository**
    ```bash
    git clone https://github.com/Leabots/my_agent.git
    ```

2.  **Navigate into the project directory**
    ```bash
    cd my_agent
    ```

3.  **Install in editable mode**
    The `-e` flag installs the package in "editable" mode. This creates a symlink to your source code, so any changes you make to the source files are immediately reflected in your Python environment without needing to reinstall.
    ```bash
    pip install -e .
    ```

This command will also automatically install the library's only dependency, `openai`.

### 🚀 Quick Start

#### Basic Conversation

```python
from my_agent import Agent

agent = Agent(
    base_url="https://api.openai.com/v1",
    model="gpt-3.5-turbo",
    api_key="your-api-key"
)

response = agent.complete("Hello, please introduce yourself")
print(response["content"])
```

#### Global Default Configuration

```python
Agent.set_default(
    base_url="https://api.deepseek.com",
    model="deepseek-chat",
    api_key="your-api-key"
)

agent = Agent()  # uses the defaults
response = agent.complete("Hello!")
```

#### Streaming Output

```python
for chunk in agent.stream_complete("Tell me a short story"):
    if chunk.get("delta"):
        print(chunk["delta"], end="", flush=True)
```

#### JSON Output

```python
response = agent.json_output("List 3 fruits, return JSON format")
print(response["content"])  # Already a Python dict
```

### 🔧 Function Calling

#### Register a Tool (auto-extract from docstring)

```python
def get_weather(city: str, unit: str = "celsius"):
    """Get current weather for a city.
    
    :param city: City name, e.g., Beijing, Shanghai
    :param unit: Temperature unit, celsius or fahrenheit
    :return: Dictionary with weather information
    """
    return {"city": city, "temperature": 24, "unit": unit, "condition": "Sunny"}

agent.register_tool("get_weather", "Get current weather for a city", get_weather)

response = agent.complete("What's the weather like in Beijing today?")
print(response["content"])
```

#### Manual Parameter Descriptions

```python
agent.register_tool(
    "get_weather",
    "Get current weather for a city",
    get_weather,
    param_descriptions={
        "city": "City name, e.g., Beijing, Shanghai",
        "unit": "Temperature unit: celsius or fahrenheit"
    },
    return_description="Dictionary containing city, temperature, unit, and condition"
)
```

#### Streaming with Tool Call Messages

```python
tool_messages = {
    "get_weather": "[🌤️ Fetching weather information...]",
    "get_location": "[📍 Getting location...]"
}

for chunk in agent.stream_complete("What's the weather like here?", tool_call_messages=tool_messages):
    if chunk.get("delta"):
        print(chunk["delta"], end="", flush=True)
```

### 💾 Conversation History

```python
# Save history to file
agent.save_history("my_conversation")

# Load history from file
agent.load_history("my_conversation")

# List all saved histories
print(agent.list_saved_histories())

# Clear current history
agent.clear_history()
```

### 📖 API Reference

#### Agent Initialization

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | `str` | `None` | API base URL |
| `model` | `str` | `None` | Model name |
| `api_key` | `str` | `None` | API key |
| `system_prompt` | `str` | `"You are a helpful assistant."` | System prompt |
| `temperature` | `float` | `0.5` | Sampling temperature |
| `max_tokens` | `int` | `4096` | Max tokens to generate |

#### Main Methods

- `complete(user_input, record=True, max_iterations=10)` - Send message, return full response (auto tool handling)
- `stream_complete(user_input, record=True, tool_call_messages=None, max_iterations=5)` - Streaming version with tool progress
- `json_output(user_input, record=True)` - Force JSON output
- `register_tool(name, description, handler, param_descriptions=None, return_description=None)` - Register a tool
- `clear_history()`, `save_history()`, `load_history()`, `list_saved_histories()` - History management

#### Response Format

Both `complete()` and `json_output()` return a dict with:

```python
{
    "id": "chatcmpl-xxx",
    "content": "Response text",
    "model": "model-name",
    "created": 1234567890,
    "usage": {...},
    "completion_tokens": 150,
    "prompt_tokens": 50,
    "total_tokens": 200,
    "finish_reason": "stop",
    "system_fingerprint": "..."
}
```

### 🧪 Testing

```python
from my_agent import test

# Run basic tests
test.test(base_url, model, api_key)

# Run JSON output test
test.json_output_test(base_url, model, api_key)
```

### 📄 License

MIT License - completely free to use, no restrictions.

### 🤝 Contributing

Issues and Pull Requests are welcome!

---

<a name="chinese"></a>
## 中文版本

### ✨ 特性

- 🚀 **简单易用** - 简洁的 API 设计，快速上手
- 🔧 **工具调用** - 支持 OpenAI 标准的 Function Calling，自动解析和执行工具
- 📝 **流式输出** - 支持流式响应，实时显示生成内容，可显示工具调用进度
- 💾 **历史管理** - 自动保存对话历史，支持保存/加载到 JSON 文件
- 🎯 **JSON 输出** - 强制模型返回 JSON 格式，便于结构化数据提取
- 🔌 **灵活配置** - 支持全局默认配置和实例级配置
- 📦 **轻量依赖** - 仅依赖 `openai`

### 📦 安装

请按照以下步骤安装 `my_agent`：

1.  **克隆仓库**
    ```bash
    git clone https://github.com/Leabots/my_agent.git
    ```

2.  **进入项目目录**
    ```bash
    cd my_agent
    ```

3.  **执行可编辑安装**
    `-e` 标志以“可编辑”模式安装包。这会在你的 Python 环境和项目源码之间创建一个链接，你对源码做的任何修改都会立刻生效，无需重新安装。
    ```bash
    pip install -e .
    ```
    
这个命令也会自动安装库的唯一依赖 `openai`。

### 🚀 快速开始

#### 基础对话

```python
from my_agent import Agent

agent = Agent(
    base_url="https://api.openai.com/v1",
    model="gpt-3.5-turbo",
    api_key="your-api-key"
)

response = agent.complete("你好，请介绍一下自己")
print(response["content"])
```

#### 全局默认配置

```python
Agent.set_default(
    base_url="https://api.deepseek.com",
    model="deepseek-chat",
    api_key="your-api-key"
)

agent = Agent()  # 使用默认配置
response = agent.complete("你好！")
```

#### 流式输出

```python
for chunk in agent.stream_complete("讲一个短故事"):
    if chunk.get("delta"):
        print(chunk["delta"], end="", flush=True)
```

#### JSON 输出

```python
response = agent.json_output("列出3种水果，返回JSON格式")
print(response["content"])  # 已经是 Python 字典
```

### 🔧 工具调用

#### 注册工具（自动从 docstring 提取描述）

```python
def get_weather(city: str, unit: str = "celsius"):
    """获取指定城市的天气信息
    
    :param city: 城市名称，如北京、上海
    :param unit: 温度单位，celsius 或 fahrenheit
    :return: 天气信息字典
    """
    return {"city": city, "temperature": 24, "unit": unit, "condition": "晴"}

agent.register_tool("get_weather", "获取指定城市的天气信息", get_weather)

response = agent.complete("北京今天天气怎么样？")
print(response["content"])
```

#### 手动指定参数描述

```python
agent.register_tool(
    "get_weather",
    "获取指定城市的天气信息",
    get_weather,
    param_descriptions={
        "city": "城市名称，例如：北京、上海",
        "unit": "温度单位：celsius（摄氏度）或 fahrenheit（华氏度）"
    },
    return_description="包含城市、温度、单位和天气状况的字典"
)
```

#### 带工具调用提示的流式输出

```python
tool_messages = {
    "get_weather": "[🌤️ 正在获取天气信息...]",
    "get_location": "[📍 正在获取位置信息...]"
}

for chunk in agent.stream_complete("我这里天气怎么样？", tool_call_messages=tool_messages):
    if chunk.get("delta"):
        print(chunk["delta"], end="", flush=True)
```

### 💾 对话历史管理

```python
# 保存历史到文件
agent.save_history("my_conversation")

# 从文件加载历史
agent.load_history("my_conversation")

# 列出所有保存的历史
print(agent.list_saved_histories())

# 清空当前历史
agent.clear_history()
```

### 📖 API 参考

#### Agent 初始化参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `base_url` | `str` | `None` | API 基础 URL |
| `model` | `str` | `None` | 模型名称 |
| `api_key` | `str` | `None` | API 密钥 |
| `system_prompt` | `str` | `"You are a helpful assistant."` | 系统提示词 |
| `temperature` | `float` | `0.5` | 采样温度 |
| `max_tokens` | `int` | `4096` | 最大生成 token 数 |

#### 主要方法

- `complete(user_input, record=True, max_iterations=10)` - 发送消息并返回完整响应（自动处理工具调用）
- `stream_complete(user_input, record=True, tool_call_messages=None, max_iterations=5)` - 流式版本，支持工具调用提示
- `json_output(user_input, record=True)` - 强制返回 JSON 格式
- `register_tool(name, description, handler, param_descriptions=None, return_description=None)` - 注册工具
- `clear_history()` / `save_history()` / `load_history()` / `list_saved_histories()` - 历史管理

#### 返回格式

`complete()` 和 `json_output()` 返回字典，包含以下字段：

```python
{
    "id": "chatcmpl-xxx",
    "content": "回复内容",
    "model": "模型名称",
    "created": 1234567890,
    "usage": {...},
    "completion_tokens": 150,
    "prompt_tokens": 50,
    "total_tokens": 200,
    "finish_reason": "stop",
    "system_fingerprint": "..."
}
```

### 🧪 测试

```python
from my_agent import test

# 运行基础测试
test.test(base_url, model, api_key)

# 运行 JSON 输出测试
test.json_output_test(base_url, model, api_key)
```

### 📄 许可证

MIT License - 完全自由使用，无任何限制。

### 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**Happy Coding!** 🎉