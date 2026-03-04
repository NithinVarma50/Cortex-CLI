import sys
import subprocess
import tempfile
import os
from skills.base_skill import BaseSkill


class CodeExecutorSkill(BaseSkill):
    name: str = "code_executor"
    description: str = "Executes arbitrary python code in a restricted subprocess."
    version: str = "1.0.0"

    def execute(self, input_text: str, **kwargs) -> str:
        """Executes python code. Enforces no shell execution and 30s timeout."""
        if not self.validate_input(input_text):
            return "Invalid code input."

        code = input_text.strip()
        
        # Strip markdown syntax if LLM passes wrapped code
        if code.startswith("```python"):
            code = code[9:]
        if code.endswith("```"):
            code = code[:-3]
        code = code.strip()

        # Extremely basic regex/string checks to prevent obvious malice
        # Production tools use pypy sandboxing or unshare/docker.
        forbidden = ["os.system", "subprocess", "eval(", "exec(", "pty", "shutil"]
        for f in forbidden:
            if f in code:
                return f"Execution blocked: forbidden library or function '{f}' detected."

        # Write to temp file and execute
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tf:
            tf.write(code)
            temp_path = tf.name

        try:
            # We enforce timeout=30 in subprocess
            result = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = ""
            if result.stdout:
                output += f"--- STDOUT ---\n{result.stdout}\n"
            if result.stderr:
                output += f"--- STDERR ---\n{result.stderr}\n"
                
            if result.returncode != 0:
                output += f"Exited with error code: {result.returncode}\n"
            elif not output:
                output = "Code executed successfully with no output."
                
            return output
            
        except subprocess.TimeoutExpired:
            return "Error: Code execution exceeded 30 second timeout limit."
        except Exception as e:
            return f"Error launching execution: {str(e)}"
        finally:
            # Ensure cleanup
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
