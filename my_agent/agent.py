from openai import OpenAI
from .history import History


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

    def complete(self, user_input: str, record: bool = True):
        """Send a completion request to the Agent.
        
        Args:
            user_input: User message to send
            record: Whether to record the interaction in history
            
        Returns:
            The assistant's response
        """
        res = {}
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
            max_tokens=self.max_tokens
        )
        
        res = {
            "id": response.id,
            "content": response.choices[0].message.content,
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
        
        if record:
            self.history.push("user", user_input)
            self.history.push("assistant", response.choices[0].message.content)
        
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
        res = {}
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
        agent_str = f"url: {self.base_url}, model: {self.model}"
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

    def stream_complete(self, user_input: str, record: bool = True):
        """Send a streaming completion request to the Agent.
        
        This method yields response chunks as they arrive from the API.
        After the complete response is received, it will be saved to history.
        
        Args:
            user_input: User message to send
            record: Whether to record the interaction in history
            
        Yields:
            Chunks of the assistant's response with metadata
        """
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
            stream=True
        )
        
        full_content = ""
        response_id = None
        model_name = None
        created = None
        system_fingerprint = None
        total_completion_tokens = 0
        total_prompt_tokens = 0
        usage = None
        
        for chunk in response:
            chunk_res = {}
            
            # Capture metadata from first chunk
            if response_id is None:
                response_id = chunk.id
                model_name = chunk.model
                created = chunk.created
                system_fingerprint = chunk.system_fingerprint
            
            chunk_res['id'] = chunk.id
            chunk_res['model'] = chunk.model
            chunk_res['created'] = chunk.created
            chunk_res['system_fingerprint'] = chunk.system_fingerprint
            
            # Get content delta
            delta = chunk.choices[0].delta
            if delta.content is not None:
                chunk_res['delta'] = delta.content
                full_content += delta.content
            else:
                chunk_res['delta'] = ""
            
            chunk_res['full_content'] = full_content
            chunk_res['finish_reason'] = chunk.choices[0].finish_reason
            
            # Handle usage information (some providers send this in the last chunk)
            if hasattr(chunk, 'usage') and chunk.usage is not None:
                usage = chunk.usage
                chunk_res['usage'] = chunk.usage
                chunk_res['completion_tokens'] = chunk.usage.completion_tokens
                chunk_res['prompt_tokens'] = chunk.usage.prompt_tokens
                chunk_res['total_tokens'] = chunk.usage.total_tokens
                total_completion_tokens = chunk.usage.completion_tokens
                total_prompt_tokens = chunk.usage.prompt_tokens
            
            yield chunk_res
        
        # After streaming completes, save to history if requested
        if record and full_content:
            self.history.push("user", user_input)
            self.history.push("assistant", full_content)
        
        # Create a final response with complete information
        final_res = {
            "id": response_id,
            "content": full_content,
            "model": model_name,
            "created": created,
            "finish_reason": "stop",
            "system_fingerprint": system_fingerprint,
            "completion_tokens": total_completion_tokens,
            "prompt_tokens": total_prompt_tokens,
            "total_tokens": total_completion_tokens + total_prompt_tokens
        }
        
        # Add extra usage details if available
        if usage is not None:
            # Add completion_tokens_details if available for streaming
            if hasattr(usage, 'completion_tokens_details') and usage.completion_tokens_details is not None:
                if hasattr(usage.completion_tokens_details, 'audio_tokens'):
                    final_res['completion_tokens_audio_tokens'] = usage.completion_tokens_details.audio_tokens
            
            # Add prompt_tokens_details if available for streaming
            if hasattr(usage, 'prompt_tokens_details') and usage.prompt_tokens_details is not None:
                if hasattr(usage.prompt_tokens_details, 'audio_tokens'):
                    final_res['prompt_tokens_audio_tokens'] = usage.prompt_tokens_details.audio_tokens
                if hasattr(usage.prompt_tokens_details, 'cached_tokens'):
                    final_res['prompt_tokens_cached_tokens'] = usage.prompt_tokens_details.cached_tokens
        
        yield {"done": True, "final_response": final_res}
