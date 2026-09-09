const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://10.133.229.152:8000";

/**
 * Health check endpoint to verify backend connection.
 */
export async function checkBackend() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
      throw new Error("Backend unavailable");
    }

    return await response.json();
  } catch (error) {
    console.error("Backend connection error:", error);
    return null;
  }
}

/**
 * Send chat message to local LLM with streaming support.
 */
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

/**
 * Verify prompt/payload with Trust Layer.
 */
export async function verifyTrustPayload(payload) {
  const response = await fetch(`${API_BASE_URL}/trust/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Trust verification failed: ${response.status}`);
  }

  return await response.json();
}

/**
 * Review human-in-the-loop approval requests.
 */
export async function reviewApproval(requestId, status, comment = "") {
  const response = await fetch(`${API_BASE_URL}/approval/${requestId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status, comment }),
  });

  if (!response.ok) {
    throw new Error(`Approval review failed: ${response.status}`);
  }

  return await response.json();
}

// Add this new function to the bottom of api.js
/**
 * Upload a document to the FastAPI backend for ingestion.
 */
export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file); // "file" must match the FastAPI parameter name

  const response = await fetch(`${API_BASE_URL}/api/ingest`, {
    method: "POST",
    // Note: Do NOT set "Content-Type" manually when sending FormData.
    // The browser will automatically set it to "multipart/form-data" with the correct boundary.
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status}`);
  }

  return await response.json();
}
/**
 * Delete a document from the local vector database/backend storage.
 */
export async function deleteDocument(filename) {
  const response = await fetch(`${API_BASE_URL}/api/documents/${encodeURIComponent(filename)}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error(`Delete failed: ${response.status}`);
  }

  return await response.json();
}

export { API_BASE_URL };