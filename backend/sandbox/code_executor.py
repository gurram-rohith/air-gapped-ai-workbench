import os
import sys
import time
import subprocess
import tempfile
from pathlib import Path

DEFAULT_TIMEOUT = int(os.getenv("SANDBOX_TIMEOUT", 10))

def execute_python_code(code_str: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """
    Safely executes Python code inside an isolated subprocess.
    """
    data_dir = Path("data/temp_scripts")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    start_time = time.perf_counter()
    temp_script_path = None
    
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", 
            suffix=".py", 
            dir=data_dir, 
            delete=False, 
            encoding="utf-8"
        ) as temp_file:
            temp_file.write(code_str)
            temp_script_path = temp_file.name

        result = subprocess.run(
            [sys.executable, temp_script_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        execution_time = round(time.perf_counter() - start_time, 4)
        is_success = (result.returncode == 0)
        
        return {
            "success": is_success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time": execution_time
        }

    except subprocess.TimeoutExpired:
        execution_time = round(time.perf_counter() - start_time, 4)
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution Timed Out: Script exceeded the strict threshold of {timeout} seconds.",
            "execution_time": execution_time
        }

    except Exception as e:
        execution_time = round(time.perf_counter() - start_time, 4)
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Sandbox Runtime Exception: {str(e)}",
            "execution_time": execution_time
        }

    finally:
        if temp_script_path and os.path.exists(temp_script_path):
            try:
                os.remove(temp_script_path)
            except OSError:
                pass
                