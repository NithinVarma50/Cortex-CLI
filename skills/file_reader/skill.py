import os
from pathlib import Path
from skills.base_skill import BaseSkill


class FileReaderSkill(BaseSkill):
    name: str = "file_reader"
    description: str = "Reads text, markdown, csv, and standard files from the local filesystem."
    version: str = "1.0.0"

    def execute(self, input_text: str, **kwargs) -> str:
        if not self.validate_input(input_text):
            return "Invalid file path."
            
        filepath = Path(input_text.strip())
        
        # Security: basic check to prevent reading sensitive root files trivially
        allowed_extensions = {".txt", ".md", ".csv", ".json", ".yaml", ".yml", ".py", ".log"}
        if filepath.suffix not in allowed_extensions and filepath.suffix != "":
            return f"Error: Cannot read file type {filepath.suffix}. Allowed types: {', '.join(allowed_extensions)}"
            
        if not filepath.exists():
            return f"Error: File '{filepath}' does not exist."
            
        if not filepath.is_file():
            return f"Error: '{filepath}' is not a file."
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Truncate if too long (e.g. max 5000 chars)
            if len(content) > 5000:
                content = content[:5000] + "\n...[Content truncated due to length]..."
                
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"
