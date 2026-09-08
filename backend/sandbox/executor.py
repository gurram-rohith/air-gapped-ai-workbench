import sys
import subprocess
import tempfile
import time
from pathlib import Path
from backend.sandbox.boundary_checks import validate_code_boundaries

DEFAULT_TIMEOUT = 10  # Seconds

def execute_python_code(code_str: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """
    Executes Python code in an isolated subprocess with boundary checks and strict timeouts.
    """
    # 1. Phase 2: Run Boundary Checks
    boundary_result = validate_code_boundaries(code_str)
    if not boundary_result["passed"]:
        return {
            "success": False,
            "stdout": "",
            "stderr": boundary_result["error"],
            "execution_time": 0.0
        }

    # 2. Prepare temporary script for execution
    temp_dir = Path("data/temp_scripts")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    start_time = time.time()
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", dir=temp_dir, delete=False) as temp_file:
        temp_file.write(code_str)
        temp_file_path = temp_file.name

    try:
        # 3. Execute in isolated subprocess
        result = subprocess.run(
            [sys.executable, temp_file_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        execution_time = round(time.time() - start_time, 4)
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time": execution_time
        }

    except subprocess.TimeoutExpired:
        execution_time = round(time.time() - start_time, 4)
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution Timed Out: Script exceeded the strict threshold of {timeout} seconds.",
            "execution_time": execution_time
        }
    except Exception as e:
        execution_time = round(time.time() - start_time, 4)
        return {
            "success": False,
            "stdout": "",
            "stderr": f"System Execution Error: {str(e)}",
            "execution_time": execution_time
        }
    finally:
        # Clean up temporary script
        Path(temp_file_path).unlink(missing_ok=True)