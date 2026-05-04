from openai import OpenAI
from .history import History
from .tool import ToolRegistry


class Agent:
    """Agent class for interacting with OpenAI-compatible APIs."""
    
    default_base_url: str = ""
    default_model: str = ""
    default_api_key: str = ""

    @classmethod
    def set_default(cls, base_url, model, api_key):
        """Set default values for all Agent instances.
        
        Args:
            base_url: Default base URL for API requests
            model: Default model to use
            api_key: Default API key
        """
        cls.default_base_url = base_url
        cls.default_model = model
        cls.default_api_key = api_key

    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        api_key: str = None,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 0.5,
        max_tokens: int = 4096
    ):
        """Initialize an Agent instance.
        
        Args:
            base_url: Base URL for API requests
            model: Model to use for completions
            api_key: API key for authentication
            system_prompt: System prompt for the agent
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.base_url = base_url if base_url is not None else self.default_base_url
        self.model = model if model is not None else self.default_model
        self.api_key = api_key if api_key is not None else self.default_api_key
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.history = History()
        self.tool_registry = ToolRegistry()

    def register_tool(self, name: str, description: str, handler, param_descriptions: dict = None, return_description: str = None):
        """Register a function as a tool.
        
        Args:
            name: Tool name (must be unique)
            description: Tool description for the model
            handler: Function to execute when tool is called
            param_descriptions: Optional dict mapping parameter names to descriptions
            return_description: Optional description of the return value
        """
        self.tool_registry.register(name, description, handler, param_descriptions, return_description)

    def complete(self, user_input: str, record: bool = True, max_iterations: int = 10):
        """Send a completion request to the Agent with automatic tool call handling.
        
        Args:
            user_input: User message to send
            record: Whether to record the interaction in history
            max_iterations: Maximum number of tool call iterations to prevent infinite loops
            
        Returns:
            The assistant's response
        """
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        messages = (
            [{"role": "system", "content": self.system_prompt}]
            + self.history.history
            + [{"role": "user", "content": user_input}]
        )
        
        tools = self.tool_registry.get_definitions()
        final_response = None
        
        # Loop to handle multiple rounds of tool calls
        for iteration in range(max_iterations):
            # Make API call
            if tools:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    tools=tools
                )
            else:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            
            message = response.choices[0].message
            
            # Check if there are tool calls
            if not hasattr(message, 'tool_calls') or not message.tool_calls:
                # No tool calls, this is the final response
                final_response = response
                break
            
            # Has tool calls, add assistant message to conversation
            messages.append(message)
            
            # Execute all tool calls
            for tool_call in message.tool_calls:
                result = self.tool_registry.execute(
                    tool_call.function.name,
                    tool_call.function.arguments
                )
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
            
            # Continue loop to let model process tool results
        
        # If we exited loop without a final response (shouldn't happen normally)
        if final_response is None:
            final_response = response
        
        # Format response
        res = {
            "id": final_response.id,
            "content": final_response.choices[0].message.content,
            "model": final_response.model,
            "created": final_response.created,
            "usage": final_response.usage,
            "completion_tokens": final_response.usage.completion_tokens,
            "prompt_tokens": final_response.usage.prompt_tokens,
            "total_tokens": final_response.usage.total_tokens,
            "finish_reason": final_response.choices[0].finish_reason,
            "system_fingerprint": final_response.system_fingerprint
        }
        
        # Add completion_tokens_details if available
        if hasattr(final_response.usage, 'completion_tokens_details') and final_response.usage.completion_tokens_details is not None:
            if hasattr(final_response.usage.completion_tokens_details, 'audio_tokens'):
                res['completion_tokens_audio_tokens'] = final_response.usage.completion_tokens_details.audio_tokens
        
        # Add prompt_tokens_details if available
        if hasattr(final_response.usage, 'prompt_tokens_details') and final_response.usage.prompt_tokens_details is not None:
            if hasattr(final_response.usage.prompt_tokens_details, 'audio_tokens'):
                res['prompt_tokens_audio_tokens'] = final_response.usage.prompt_tokens_details.audio_tokens
            if hasattr(final_response.usage.prompt_tokens_details, 'cached_tokens'):
                res['prompt_tokens_cached_tokens'] = final_response.usage.prompt_tokens_details.cached_tokens
        
        if record:
            self.history.push("user", user_input)
            self.history.push("assistant", final_response.choices[0].message.content)
        
        return res

    def json_output(self, user_input: str, record: bool = True):
        """Send a completion request to the Agent and get JSON output.
        
        Args:
            user_input: User message to send
            record: Whether to record the interaction in history
            
        Returns:
            The assistant's response with content as a Python JSON object
        """
        import json
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        messages = (
            [{"role": "system", "content": self.system_prompt}]
            + self.history.history
            + [{"role": "user", "content": user_input}]
        )
        
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"}
        )
        
        res = {
            "id": response.id,
            "model": response.model,
            "created": response.created,
            "usage": response.usage,
            "completion_tokens": response.usage.completion_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "total_tokens": response.usage.total_tokens,
            "finish_reason": response.choices[0].finish_reason,
            "system_fingerprint": response.system_fingerprint
        }
        
        # Add completion_tokens_details if available
        if hasattr(response.usage, 'completion_tokens_details') and response.usage.completion_tokens_details is not None:
            if hasattr(response.usage.completion_tokens_details, 'audio_tokens'):
                res['completion_tokens_audio_tokens'] = response.usage.completion_tokens_details.audio_tokens
        
        # Add prompt_tokens_details if available
        if hasattr(response.usage, 'prompt_tokens_details') and response.usage.prompt_tokens_details is not None:
            if hasattr(response.usage.prompt_tokens_details, 'audio_tokens'):
                res['prompt_tokens_audio_tokens'] = response.usage.prompt_tokens_details.audio_tokens
            if hasattr(response.usage.prompt_tokens_details, 'cached_tokens'):
                res['prompt_tokens_cached_tokens'] = response.usage.prompt_tokens_details.cached_tokens
        
        # Parse JSON content
        content_str = response.choices[0].message.content
        try:
            res['content'] = json.loads(content_str)
        except json.JSONDecodeError:
            # If parsing fails, return the raw string
            res['content'] = content_str
        
        if record:
            self.history.push("user", user_input)
            self.history.push("assistant", content_str)
        
        return res

    def __str__(self):
        """Return string representation of the agent."""
        agent_str = f"url: {self.base_url}, model: {self.model}, tools: {len(self.tool_registry)}"
        return agent_str

    def clear_history(self):
        """Clear the conversation history."""
        self.history.clear()

    def save_history(self, name: str):
        """Save the conversation history to a JSON file.
        
        Args:
            name: Name of the save file (without extension)
            
        Returns:
            Path to the saved file
        """
        return self.history.save(name)

    def load_history(self, name: str):
        """Load conversation history from a JSON file.
        
        Args:
            name: Name of the save file (without extension)
            
        Returns:
            True if loaded successfully, False otherwise
        """
        return self.history.load(name)

    def list_saved_histories(self):
        """Get list of all saved conversation histories.
        
        Returns:
            List of save file names
        """
        return self.history.get_saves()

    def stream_complete(self, user_input: str, record: bool = True, tool_call_messages: dict = None, max_iterations: int = 5):
        """Send a streaming completion request to the Agent with tool call support."""
        import re
        import json
        
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        messages = (
            [{"role": "system", "content": self.system_prompt}]
            + self.history.history
            + [{"role": "user", "content": user_input}]
        )
        
        tools = self.tool_registry.get_definitions()
        tool_call_messages = tool_call_messages or {}
        
        if tools:
            for iteration in range(max_iterations):
                # 第一次调用：检测是否有 tool_calls
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    tools=tools
                )
                
                message = response.choices[0].message
                content = message.content or ""
                
                # 检查是否包含文本格式的 tool_calls
                tool_call_pattern = r'<｜｜DSML｜｜tool_calls>.*?</｜｜DSML｜｜tool_calls>'
                has_text_tool_calls = re.search(tool_call_pattern, content, re.DOTALL)
                has_standard_tool_calls = hasattr(message, 'tool_calls') and message.tool_calls
                
                if has_text_tool_calls or has_standard_tool_calls:
                    # 有工具调用：解析并执行
                    if has_text_tool_calls:
                        tool_calls_section = re.search(r'<｜｜DSML｜｜tool_calls>(.*?)</｜｜DSML｜｜tool_calls>', content, re.DOTALL)
                        if tool_calls_section:
                            invoke_pattern = r'<｜｜DSML｜｜invoke name="(\w+)">(.*?)</｜｜DSML｜｜invoke>'
                            tool_calls_data = re.findall(invoke_pattern, tool_calls_section.group(1), re.DOTALL)
                            
                            for tool_name, params_str in tool_calls_data:
                                if tool_name in tool_call_messages:
                                    yield {
                                        "type": "tool_call",
                                        "tool_name": tool_name,
                                        "delta": tool_call_messages[tool_name],
                                    }
                                
                                param_pattern = r'<｜｜DSML｜｜parameter name="(\w+)" string="true">(.*?)</｜｜DSML｜｜parameter>'
                                params = {}
                                for param_name, param_value in re.findall(param_pattern, params_str, re.DOTALL):
                                    params[param_name] = param_value
                                
                                result = self.tool_registry.execute(tool_name, json.dumps(params))
                                
                                messages.append({"role": "assistant", "content": content})
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": f"call_{tool_name}",
                                    "content": result
                                })
                    
                    elif has_standard_tool_calls:
                        for tool_call in message.tool_calls:
                            tool_name = tool_call.function.name
                            if tool_name in tool_call_messages:
                                yield {
                                    "type": "tool_call",
                                    "tool_name": tool_name,
                                    "delta": tool_call_messages[tool_name],
                                }
                        
                        messages.append(message)
                        
                        for tool_call in message.tool_calls:
                            result = self.tool_registry.execute(
                                tool_call.function.name,
                                tool_call.function.arguments
                            )
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": result
                            })
                    
                    # 继续下一轮
                    continue
                
                # 没有 tool_calls：这是最终回复，使用流式 API 输出
                # 关键：使用流式 API，不要直接输出静态 content
                stream_response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=True
                )
                
                full_content = ""
                response_id = None
                model_name = None
                created = None
                system_fingerprint = None
                
                for chunk in stream_response:
                    if response_id is None:
                        response_id = chunk.id
                        model_name = chunk.model
                        created = chunk.created
                        system_fingerprint = chunk.system_fingerprint
                    
                    delta = chunk.choices[0].delta
                    if delta.content:
                        chunk_res = {
                            "type": "response",
                            "delta": delta.content,
                        }
                        full_content += delta.content
                        yield chunk_res
                
                # 保存到历史
                if record and full_content:
                    self.history.push("user", user_input)
                    self.history.push("assistant", full_content)
                
                yield {"done": True, "final_response": {"content": full_content}}
                return
            
            yield {"done": True, "error": "Max iterations reached"}
            return
        
        # 没有工具，普通流式输出
        stream_response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True
        )
        
        full_content = ""
        for chunk in stream_response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield {"type": "response", "delta": delta.content}
                full_content += delta.content
        
        if record and full_content:
            self.history.push("user", user_input)
            self.history.push("assistant", full_content)
        
        yield {"done": True, "final_response": {"content": full_content}}