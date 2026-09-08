const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://192.168.10.190:8000";

export async function checkBackend() {
  try {
    const response = await fetch(`${API_BASE_URL}/`);

    if (!response.ok) {
      throw new Error("Backend unavailable");
    }

    return await response.json();
  } catch (error) {
    console.error("Backend connection error:", error);
    return null;
  }
}

export async function sendChatMessage(prompt, onChunk) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.status}`);
  }

  if (
    response.body &&
    response.headers.get("content-type")?.includes("text")
  ) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let fullResponse = "";

    while (true) {
      const { value, done } = await reader.read();

      if (done) break;

      const chunk = decoder.decode(value, {
        stream: true,
      });

      fullResponse += chunk;

      if (onChunk) {
        onChunk(chunk, fullResponse);
      }
    }

    return {
      response: fullResponse,
    };
  }

  const data = await response.json();

  const answer =
    data.response ||
    data.answer ||
    data.message ||
    "";

  if (onChunk && answer) {
    onChunk(answer, answer);
  }

  return data;
}

export { API_BASE_URL };