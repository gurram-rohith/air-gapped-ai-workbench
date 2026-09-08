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

export async function sendChatMessage(prompt) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.status}`);
  }

  return await response.json();
}

export { API_BASE_URL };