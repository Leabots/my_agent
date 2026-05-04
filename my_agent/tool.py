from typing import Dict, Any, Callable, Optional, Union
import json
import inspect
import re


class Tool:
    """Tool class for function calling."""
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        handler: Callable, 
        param_descriptions: Optional[Dict[str, str]] = None,
        return_description: Optional[str] = None
    ):
        """Initialize a Tool from a function.
        
        Args:
            name: Tool name (must be unique)
            description: Tool description for the model
            handler: Function to execute when tool is called
            param_descriptions: Optional dict mapping parameter names to descriptions
            return_description: Optional description of the return value
        """
        self.name = name
        self.description = description
        self.handler = handler
        self.param_descriptions = param_descriptions or {}
        self.return_description = return_description
        self.parameters = self._infer_parameters(handler)
        self.required_params = self._infer_required_params(handler)
        self.return_schema = self._infer_return_schema(handler)
    
    def _infer_parameters(self, handler: Callable) -> Dict[str, Any]:
        """Infer parameter schema from function signature and docstring."""
        sig = inspect.signature(handler)
        params = {}
        
        # Extract parameter descriptions from docstring (as fallback)
        docstring = handler.__doc__ or ""
        docstring_descriptions = self._parse_docstring_params(docstring)
        
        # Type mapping from Python types to JSON schema types
        type_mapping = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object"
        }
        
        for param_name, param in sig.parameters.items():
            # Skip 'self' parameter for methods
            if param_name == 'self':
                continue
            
            # Determine parameter type
            if param.annotation != inspect.Parameter.empty:
                param_type = type_mapping.get(param.annotation, "string")
            else:
                param_type = "string"
            
            # Get parameter description - priority: manual > docstring > default
            if param_name in self.param_descriptions:
                description = self.param_descriptions[param_name]
            elif param_name in docstring_descriptions:
                description = docstring_descriptions[param_name]
            else:
                description = f"Parameter {param_name}"
            
            # Build parameter schema
            param_schema = {
                "type": param_type,
                "description": description
            }
            
            # Handle default values for enums or specific values
            if param.default != inspect.Parameter.empty:
                if isinstance(param.default, str) and param.default in ['celsius', 'fahrenheit']:
                    param_schema["enum"] = ['celsius', 'fahrenheit']
            
            params[param_name] = param_schema
        
        return params
    
    def _infer_return_schema(self, handler: Callable) -> Optional[Dict[str, Any]]:
        """Infer return value schema from docstring."""
        docstring = handler.__doc__ or ""
        
        # Priority: manual > docstring > None
        if self.return_description is not None:
            return {
                "type": "object",
                "description": self.return_description
            }
        
        # Try to extract return description from docstring
        return_desc = self._parse_docstring_return(docstring)
        if return_desc:
            return {
                "type": "object",
                "description": return_desc
            }
        
        return None
    
    def _parse_docstring_params(self, docstring: str) -> Dict[str, str]:
        """Parse parameter descriptions from docstring.
        
        Supports formats:
            :param name: description
            Args:
                name: description
        """
        param_descriptions = {}
        
        # Pattern for :param name: description
        pattern1 = r':param\s+(\w+):\s*(.+?)(?=\n:|$|\n\s*\n)'
        for match in re.finditer(pattern1, docstring, re.DOTALL):
            param_descriptions[match.group(1)] = match.group(2).strip()
        
        # Pattern for Args: block
        if 'Args:' in docstring or 'Parameters:' in docstring:
            # Find the Args block
            args_section = re.search(r'(?:Args|Parameters):\s*\n(.*?)(?=\n\s*\n|\n\w+:)', docstring, re.DOTALL)
            if args_section:
                lines = args_section.group(1).split('\n')
                for line in lines:
                    # Match patterns like "    name: description" or "    name (type): description"
                    match = re.match(r'\s+(\w+)\s*:\s*(.+?)$', line)
                    if match:
                        param_descriptions[match.group(1)] = match.group(2).strip()
                    # Match patterns like "        name: description"
                    match2 = re.match(r'\s+(\w+)\s*\([^)]+\)\s*:\s*(.+?)$', line)
                    if match2:
                        param_descriptions[match2.group(1)] = match2.group(2).strip()
        
        return param_descriptions
    
    def _parse_docstring_return(self, docstring: str) -> Optional[str]:
        """Parse return value description from docstring.
        
        Supports formats:
            :return: description
            Returns:
                description
        """
        # Pattern for :return: description
        pattern1 = r':return:\s*(.+?)(?=\n:|$|\n\s*\n)'
        match1 = re.search(pattern1, docstring, re.DOTALL)
        if match1:
            return match1.group(1).strip()
        
        # Pattern for :returns: description
        pattern2 = r':returns:\s*(.+?)(?=\n:|$|\n\s*\n)'
        match2 = re.search(pattern2, docstring, re.DOTALL)
        if match2:
            return match2.group(1).strip()
        
        # Pattern for Returns: block
        if 'Returns:' in docstring:
            returns_section = re.search(r'Returns:\s*\n(.*?)(?=\n\s*\n|\n\w+:)', docstring, re.DOTALL)
            if returns_section:
                # Get the first line of returns section
                lines = returns_section.group(1).strip().split('\n')
                if lines:
                    return lines[0].strip()
        
        return None
    
    def _infer_required_params(self, handler: Callable) -> list:
        """Infer required parameters (those without default values)."""
        sig = inspect.signature(handler)
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        return required
    
    @property
    def definition(self) -> Dict[str, Any]:
        """Get the tool definition for OpenAI API."""
        # Build parameters schema
        parameters_schema = {
            "type": "object",
            "properties": self.parameters,
            "required": self.required_params
        }
        
        # Add return schema to description if available
        final_description = self.description
        if self.return_schema:
            final_description += f"\n\nReturns: {self.return_schema['description']}"
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": final_description,
                "parameters": parameters_schema
            }
        }
    
    def execute(self, **kwargs) -> str:
        """Execute the tool with given arguments."""
        try:
            result = self.handler(**kwargs)
            if isinstance(result, (dict, list)):
                return json.dumps(result, ensure_ascii=False)
            return str(result)
        except Exception as e:
            return f"Error executing tool '{self.name}': {str(e)}"
    
    def __str__(self) -> str:
        return f"Tool(name={self.name}, params={list(self.parameters.keys())})"


class ToolRegistry:
    """Registry for managing multiple tools."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(
        self, 
        name: str, 
        description: str, 
        handler: Callable, 
        param_descriptions: Optional[Dict[str, str]] = None,
        return_description: Optional[str] = None
    ):
        """Register a function as a tool.
        
        Args:
            name: Tool name (must be unique)
            description: Tool description for the model
            handler: Function to execute when tool is called
            param_descriptions: Optional dict mapping parameter names to descriptions
            return_description: Optional description of the return value
        """
        if name in self._tools:
            raise ValueError(f"Tool '{name}' already registered")
        
        tool = Tool(name, description, handler, param_descriptions, return_description)
        self._tools[name] = tool
    
    def get_definitions(self) -> list:
        """Get all tool definitions for API."""
        return [tool.definition for tool in self._tools.values()]
    
    def execute(self, name: str, arguments: str) -> str:
        """Execute a tool by name with JSON arguments string."""
        tool = self._tools.get(name)
        if not tool:
            return f"Tool '{name}' not found"
        
        try:
            args = json.loads(arguments) if arguments else {}
        except json.JSONDecodeError:
            return f"Invalid arguments for tool '{name}': {arguments}"
        
        return tool.execute(**args)
    
    def remove(self, name: str):
        """Remove a tool by name."""
        if name in self._tools:
            del self._tools[name]
    
    def clear(self):
        """Remove all tools."""
        self._tools.clear()
    
    def __contains__(self, name: str) -> bool:
        return name in self._tools
    
    def __len__(self) -> int:
        return len(self._tools)
    
    def __iter__(self):
        return iter(self._tools.values())