import os
import json


class History:
    """History class for managing conversation history with JSON storage."""
    
    SAVES_DIR = "saves"

    def __init__(self):
        """Initialize a History instance."""
        self.history = []
        # Create saves directory if it doesn't exist
        os.makedirs(self.SAVES_DIR, exist_ok=True)

    def push(self, role: str, content: str):
        """Add a message to the history.
        
        Args:
            role: Role of the message sender ('user' or 'assistant')
            content: Text content of the message
        """
        self.history.append({"role": role, "content": content})

    def clear(self):
        """Clear the conversation history."""
        self.history = []

    def __str__(self):
        """Return string representation of the history."""
        res: str = ""
        for i in self.history:
            res += "%s: %s \n" % (i["role"], i["content"])
        return res

    def save(self, name: str):
        """Save the history to a JSON file.
        
        Args:
            name: Name of the save file (without extension)
            
        Returns:
            Path to the saved file
        """
        filename = f"{name}.json"
        filepath = os.path.join(self.SAVES_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

        return filepath

    def get_saves(self):
        """Get list of all saved history files.
        
        Returns:
            List of save file names
        """
        if not os.path.exists(self.SAVES_DIR):
            return []
        
        saves = []
        for file in os.listdir(self.SAVES_DIR):
            if file.endswith('.json'):
                saves.append(file[:-5])  # Remove .json extension

        return sorted(saves)

    def load(self, name: str):
        """Load history from a JSON file.
        
        Args:
            name: Name of the save file (without extension)
            
        Returns:
            True if loaded successfully, False otherwise
        """
        filename = f"{name}.json"
        filepath = os.path.join(self.SAVES_DIR, filename)

        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded_history = json.load(f)

            # Convert old format to new format if needed
            self.history = []
            for item in loaded_history:
                if isinstance(item, dict):
                    # Handle old format with 'text' field
                    if 'text' in item and 'content' not in item:
                        new_item = item.copy()
                        new_item['content'] = new_item.pop('text')
                        self.history.append(new_item)
                    else:
                        self.history.append(item)
                else:
                    self.history.append(item)

            return True
        except (json.JSONDecodeError, IOError):
            return False