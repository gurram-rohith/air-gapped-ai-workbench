import httpx
from backend.config import settings


def get_formatted_ollama_url() -> str:
    """Sanitizes the Ollama host string and ensures a valid HTTP protocol scheme."""
    host = settings.ollama_host.strip()

    # Replace 0.0.0.0 binding with LAN IP host if needed
    if "0.0.0.0" in host:
        host = host.replace("0.0.0.0", "192.168.137.212")

    if not host.startswith("http://") and not host.startswith("https://"):
        host = f"http://{host}"

    return host.rstrip("/")


async def generate_response(
    prompt: str, model: str = None, temperature: float = 0.7
) -> dict:
    selected_model = model or getattr(settings, "default_model", "llama3")
    base_url = get_formatted_ollama_url()
    url = f"{base_url}/api/generate"

    payload = {
        "model": selected_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
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
                "error": f"Cannot connect to host Ollama server at {base_url}. Ensure Ollama is running on host GPU.",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


async def analyze_image(
    prompt: str, image_base64: str, model: str = "moondream"
) -> dict:
    """Multimodal vision task endpoint."""
    base_url = get_formatted_ollama_url()
    url = f"{base_url}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "images": [image_base64],
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
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
        except Exception as e:
            return {"success": False, "error": str(e)}


async def generate_embeddings(
    text: str, model: str = "nomic-embed-text"
) -> dict:
    """Vector embedding generation endpoint for RAG tasks."""
    base_url = get_formatted_ollama_url()
    url = f"{base_url}/api/embed"

    payload = {"model": model, "input": text}

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            embeddings = data.get("embeddings", [[]])[0]
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
        except Exception as e:
            return {"success": False, "error": str(e)}