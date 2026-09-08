import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://192.168.10.190:8000";

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I'm your Sovereign AI Assistant. Ask me something or upload a document to get started.",
    },
  ]);

  const [input, setInput] = useState("");
  const [isConnected, setIsConnected] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  const [trustData, setTrustData] = useState({
    score: null,
    grounded: null,
    sources: [],
  });

  // Check backend connection
  const checkConnection = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/`, {
        method: "GET",
        signal: AbortSignal.timeout(3000),
      });

      setIsConnected(response.ok);
    } catch {
      setIsConnected(false);
    }
  };

  useEffect(() => {
    checkConnection();

    const interval = setInterval(checkConnection, 10000);

    return () => clearInterval(interval);
  }, []);

  // Send chat message
  const sendMessage = async () => {
    const text = input.trim();

    if (!text || isSending) return;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: text,
      },
    ]);

    setInput("");
    setIsSending(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: text,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();

      const answer =
        data.response ||
        data.answer ||
        data.message ||
        "The backend returned an empty response.";

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: answer,
        },
      ]);

      // Read trust information if backend provides it
      setTrustData({
        score:
          data.confidence_score ??
          data.trust_score ??
          data.confidence ??
          null,
        grounded: data.is_grounded ?? data.grounded ?? null,
        sources: data.sources ?? data.context_sources ?? [],
      });
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I couldn't connect to the backend. Please check that the FastAPI server is running on the host machine.",
        },
      ]);
    } finally {
      setIsSending(false);
      checkConnection();
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (file) {
      setSelectedFile(file);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
  };

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">◈</div>

          <div>
            <h1>Sovereign AI</h1>
            <span>Workbench</span>
          </div>
        </div>

        <button className="new-chat" onClick={() => setMessages([])}>
          <span>＋</span>
          New conversation
        </button>

        <nav className="navigation">
          <div className="nav-title">WORKSPACE</div>

          <button className="nav-item active">
            <span>▣</span>
            AI Assistant
          </button>

          <button className="nav-item">
            <span>▤</span>
            Documents
          </button>

          <button className="nav-item">
            <span>⚙</span>
            Tools
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="offline-card">
            <div className="offline-dot"></div>

            <div>
              <strong>Air-gapped mode</strong>
              <span>No external APIs</span>
            </div>
          </div>

          <div className="version">Sovereign Workbench v1.0</div>
        </div>
      </aside>

      {/* Main area */}
      <main className="main">
        {/* Header */}
        <header className="topbar">
          <div>
            <div className="page-label">WORKBENCH</div>
            <h2>AI Assistant</h2>
          </div>

          <div className="connection">
            <span
              className={`status-dot ${
                isConnected ? "online" : "offline"
              }`}
            ></span>

            <span>
              {isConnected ? "Backend connected" : "Backend offline"}
            </span>

            <button className="refresh-button" onClick={checkConnection}>
              ↻
            </button>
          </div>
        </header>

        {/* Content */}
        <div className="workspace">
          {/* Chat */}
          <section className="chat-section">
            <div className="messages">
              {messages.length === 0 && (
                <div className="empty-state">
                  <div className="empty-icon">◈</div>
                  <h3>Start a new conversation</h3>
                  <p>
                    Ask the local AI model a question or provide a document
                    for context.
                  </p>
                </div>
              )}

              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`message ${
                    message.role === "user" ? "user-message" : ""
                  }`}
                >
                  <div
                    className={`avatar ${
                      message.role === "user" ? "user-avatar" : ""
                    }`}
                  >
                    {message.role === "user" ? "U" : "AI"}
                  </div>

                  <div className="message-body">
                    <div className="message-name">
                      {message.role === "user"
                        ? "You"
                        : "Sovereign Assistant"}
                    </div>

                    <div className="message-content">
                      {message.content}
                    </div>
                  </div>
                </div>
              ))}

              {isSending && (
                <div className="message">
                  <div className="avatar">AI</div>

                  <div className="message-body">
                    <div className="message-name">
                      Sovereign Assistant
                    </div>

                    <div className="typing">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="input-area">
              {selectedFile && (
                <div className="file-preview">
                  <span>📄</span>
                  <span>{selectedFile.name}</span>

                  <button onClick={removeFile}>×</button>
                </div>
              )}

              <div className="input-box">
                <label className="upload-button" title="Upload document">
                  📎
                  <input
                    type="file"
                    accept=".pdf,.txt,.md,.doc,.docx"
                    onChange={handleFileChange}
                  />
                </label>

                <textarea
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask the local AI assistant..."
                  rows="1"
                />

                <button
                  className="send-button"
                  onClick={sendMessage}
                  disabled={!input.trim() || isSending}
                >
                  ↑
                </button>
              </div>

              <div className="input-hint">
                Enter to send · Shift + Enter for a new line · Local inference
              </div>
            </div>
          </section>

          {/* Right panel */}
          <aside className="right-panel">
            <div className="panel-card">
              <div className="panel-header">
                <div>
                  <span className="panel-eyebrow">TRUST LAYER</span>
                  <h3>Grounding</h3>
                </div>

                <span className="shield">✓</span>
              </div>

              <div className="trust-score">
                <div className="score-circle">
                  <strong>
                    {trustData.score !== null
                      ? `${Math.round(trustData.score * 100)}%`
                      : "--"}
                  </strong>

                  <span>confidence</span>
                </div>
              </div>

              <div className="grounding-status">
                <span
                  className={`status-icon ${
                    trustData.grounded === true
                      ? "verified"
                      : trustData.grounded === false
                      ? "warning"
                      : ""
                  }`}
                >
                  {trustData.grounded === true
                    ? "✓"
                    : trustData.grounded === false
                    ? "!"
                    : "—"}
                </span>

                <div>
                  <strong>
                    {trustData.grounded === true
                      ? "Grounded response"
                      : trustData.grounded === false
                      ? "Needs verification"
                      : "Awaiting response"}
                  </strong>

                  <span>
                    {trustData.grounded === true
                      ? "Answer supported by local context"
                      : "Trust information will appear here"}
                  </span>
                </div>
              </div>
            </div>

            <div className="panel-card">
              <div className="panel-header">
                <div>
                  <span className="panel-eyebrow">RAG PIPELINE</span>
                  <h3>Sources</h3>
                </div>

                <span className="source-count">
                  {trustData.sources.length}
                </span>
              </div>

              {trustData.sources.length === 0 ? (
                <div className="no-sources">
                  <span>◇</span>
                  <p>No retrieved sources yet.</p>
                </div>
              ) : (
                <div className="sources">
                  {trustData.sources.map((source, index) => (
                    <div className="source" key={index}>
                      <span>📄</span>
                      <span>{source.name || source}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="panel-card system-card">
              <div className="panel-header">
                <div>
                  <span className="panel-eyebrow">SYSTEM</span>
                  <h3>Infrastructure</h3>
                </div>
              </div>

              <div className="system-row">
                <span>Inference</span>
                <strong>phi3.5</strong>
              </div>

              <div className="system-row">
                <span>Runtime</span>
                <strong>Ollama</strong>
              </div>

              <div className="system-row">
                <span>Network</span>
                <strong>LAN</strong>
              </div>

              <div className="system-row">
                <span>Mode</span>
                <strong>Air-gapped</strong>
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}

export default App;