import httpx
from typing import Dict, Any, Optional
from backend.config import settings

# System prompt forcing industrial compliance and explicit math verification
INDUSTRIAL_SYSTEM_PROMPT = """You are an air-gapped industrial AI assistant for critical refinery and plant operations.
Strict Operational Rules:
1. FORMULA DISPLAY: Always state standard engineering formulas explicitly before computing values (e.g., Bending Stress sigma = M / Z).
2. UNIT CONVERSIONS: Show step-by-step unit conversions explicitly (e.g., mm³ to m³, kg to N).
3. SAFETY VERDICTS: Independently calculate values. If calculated stress exceeds material yield strength, you MUST declare the component UNSAFE TO OPERATE.
4. COMPLEX FEA/FATIGUE: For complex non-linear or fatigue problems, explicitly note that numerical finite-element analysis (FEA) verification is mandatory before physical sign-off.
5. EQUIPMENT TAG INTEGRITY: Maintain exact spelling and case for equipment tags (e.g., P-201A, CDU-II, RV-102). Do NOT invent characters or typos."""


def get_formatted_ollama_url() -> str:
    """Sanitizes the Ollama host string and ensures a valid HTTP protocol scheme."""
    host = getattr(settings, "ollama_host", "http://127.0.0.1:11434").strip()

    # Replace 0.0.0.0 binding with LAN/Loopback IP host if needed
    if "0.0.0.0" in host:
        host = host.replace("0.0.0.0", "127.0.0.1")

    if not host.startswith("http://") and not host.startswith("https://"):
        host = f"http://{host}"

    return host.rstrip("/")


async def generate_response(
    prompt: str, model: Optional[str] = None, temperature: float = 0.1
) -> Dict[str, Any]:
    """Generates deterministic LLM responses using Ollama.

    Default temperature is set to 0.1 for high precision and zero-hallucination
    reproducibility.
    """
    selected_model = model or getattr(settings, "default_model", "phi3.5:latest")
    if ":" not in selected_model:
        selected_model = f"{selected_model}:latest"
    base_url = get_formatted_ollama_url()
    url = f"{base_url}/api/generate"

    payload = {
        "model": selected_model,
        "prompt": prompt,
        "system": INDUSTRIAL_SYSTEM_PROMPT,
        "stream": False,
        "keep_alive": "30m",  # Prevents VRAM unloading during live jury demos
        "options": {
            "temperature": temperature,
            "top_p": 0.8,
            "seed": 42,  # Fixed seed ensures reproducible results for jury demos
        },
    }

    # High timeout allowance for complex local inference tasks on GPU/CPU
    timeout_config = httpx.Timeout(300.0, connect=10.0)

    async with httpx.AsyncClient(timeout=timeout_config) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return {
                "success": True,
                "model": selected_model,
                "response": data.get("response", ""),
                "done": data.get("done", True),
            }
        except httpx.ConnectError:
            return {
                "success": False,
                "error": f"Cannot connect to host Ollama server at {base_url}. Ensure Ollama service is active.",
            }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"Ollama HTTP error {e.response.status_code}: {e.response.text}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


async def analyze_image(
    prompt: str, image_base64: str, model: str = "moondream"
) -> Dict[str, Any]:
    """Multimodal vision task endpoint for industrial inspection imagery."""
    base_url = get_formatted_ollama_url()
    url = f"{base_url}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "system": INDUSTRIAL_SYSTEM_PROMPT,
        "images": [image_base64],
        "stream": False,
        "keep_alive": "30m",
        "options": {"temperature": 0.1, "seed": 42},
    }

    timeout_config = httpx.Timeout(180.0, connect=10.0)

    async with httpx.AsyncClient(timeout=timeout_config) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return {
                "success": True,
                "model": model,
                "response": data.get("response", ""),
                "done": data.get("done", True),
            }
        except httpx.ConnectError:
            return {
                "success": False,
                "error": f"Cannot connect to host Ollama server at {base_url}.",
            }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"Ollama HTTP error {e.response.status_code}: {e.response.text}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


async def generate_embeddings(
    text: str, model: str = "nomic-embed-text"
) -> Dict[str, Any]:
    """Vector embedding generation endpoint supporting both legacy and current Ollama API response formats."""
    base_url = get_formatted_ollama_url()
    url = f"{base_url}/api/embed"

    payload = {"model": model, "input": text}
    timeout_config = httpx.Timeout(30.0, connect=5.0)

    async with httpx.AsyncClient(timeout=timeout_config) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            # Handles both single vector 'embedding' and batched 'embeddings' responses
            if "embeddings" in data and len(data["embeddings"]) > 0:
                embeddings = data["embeddings"][0]
            elif "embedding" in data:
                embeddings = data["embedding"]
            else:
                embeddings = []

            return {
                "success": True,
                "model": model,
                "embedding": embeddings,
                "dimension": len(embeddings),
            }
        except httpx.ConnectError:
            return {
                "success": False,
                "error": f"Cannot connect to host Ollama server at {base_url}.",
            }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"Ollama HTTP error {e.response.status_code}: {e.response.text}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}