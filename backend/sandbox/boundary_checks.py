import re

# Hardcoded operational limits and forbidden operations
FORBIDDEN_PATTERNS = [
    r"\bos\b",              # Prevent OS system calls
    r"\bsys\b",             # Prevent sys module manipulation
    r"\bsubprocess\b",      # Prevent spawning sub-processes inside sandbox
    r"\bimportlib\b",       # Prevent dynamic imports
    r"open\s*\(",           # Prevent arbitrary file reads/writes
    r"eval\s*\(",           # Prevent unsafe code evaluation
    r"exec\s*\(",           # Prevent dynamic execution
    r"__import__",          # Prevent hidden imports
]

def validate_code_boundaries(code_str: str) -> dict:
    """
    Validates Python code against hardcoded deterministic limits.
    Returns success status and reasoning if a boundary is violated.
    """
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, code_str):
            clean_name = pattern.replace(r"\b", "").replace(r"\s*\(", "")
            return {
                "passed": False,
                "error": f"Boundary Violation: Access to '{clean_name}' is restricted in air-gapped sandbox."
            }
    
    return {"passed": True, "error": None}