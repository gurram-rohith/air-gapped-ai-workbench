import { useEffect, useState } from "react";

import Chat from "./components/Chat/Chat";
import Vision from "./components/Vision/Vision";
import ReviewGate from "./components/ReviewGate/ReviewGate";
import AuditLogs from "./components/AuditLogs/AuditLogs";
import Documents from "./components/Documents/Documents";

import {
  API_BASE_URL,
  checkBackend,
} from "./services/api";

function App() {
  const [activeTab, setActiveTab] = useState("chat");
  const [backendOnline, setBackendOnline] = useState(false);
  const [chatSessionKey, setChatSessionKey] = useState(0);

  const checkConnection = async () => {
    const result = await checkBackend();
    setBackendOnline(result !== null);
  };

  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">◈</div>
          <div>
            <h1>Sovereign AI</h1>
            <p>Workbench</p>
          </div>
        </div>

        <button
          className="new-chat"
          onClick={() => {
            setActiveTab("chat");
            setChatSessionKey(prev => prev + 1); // Forces chat component to unmount and remount fresh
          }}
        >
          + New conversation
        </button>

        <nav className="navigation">
          <button
            className={`nav-item ${activeTab === "chat" ? "active" : ""}`}
            onClick={() => setActiveTab("chat")}
          >
            <span>💬</span>
            AI Assistant
          </button>

          <button
            className={`nav-item ${activeTab === "vision" ? "active" : ""}`}
            onClick={() => setActiveTab("vision")}
          >
            <span>🖼</span>
            Vision
          </button>

          <button
            className={`nav-item ${activeTab === "review" ? "active" : ""}`}
            onClick={() => setActiveTab("review")}
          >
            <span>✓</span>
            Review Gate
          </button>

          <button
            className={`nav-item ${activeTab === "audit" ? "active" : ""}`}
            onClick={() => setActiveTab("audit")}
          >
            <span>▤</span>
            Audit Logs
          </button>

          <button
            className={`nav-item ${activeTab === "documents" ? "active" : ""}`}
            onClick={() => setActiveTab("documents")}
          >
            <span>📄</span>
            Documents
          </button>

          <button className="nav-item">
            <span>⚙</span>
            Tools
          </button>
        </nav>

        <div className="air-gapped-card">
          <div className="status-dot"></div>
          <div>
            <strong>Air-gapped mode</strong>
            <p>Local processing enabled</p>
          </div>
        </div>
      </aside>

      {/* MAIN */}
      <main className="main-content">
        <header className="topbar">
          <div>
            <h2>
              {activeTab === "chat" && "AI Assistant"}
              {activeTab === "vision" && "P&ID Visual Analysis"}
              {activeTab === "review" && "Human Review Gate"}
              {activeTab === "audit" && "Audit Logs"}
              {activeTab === "documents" && "Documents"}
            </h2>

            <p>
              {activeTab === "chat" && "Secure local intelligence"}
              {activeTab === "vision" && "Engineering image analysis"}
              {activeTab === "review" && "Human approval and verification"}
              {activeTab === "audit" && "Cryptographic provenance and activity"}
              {activeTab === "documents" && "Local knowledge sources"}
            </p>
          </div>

          <div className="connection">
            <span
              className={backendOnline ? "online-dot" : "offline-dot"}
            ></span>

            {backendOnline ? "Backend connected" : "Backend offline"}

            <button onClick={checkConnection}>↻</button>
          </div>
        </header>

        <section className="workspace">
          <div className="chat-section">
            {/* Chat component receives the key so clicking 'New conversation' wipes its history */}
            <div style={{ display: activeTab === "chat" ? "block" : "none", height: "100%" }}>
              <Chat key={chatSessionKey} />
            </div>
            
            <div style={{ display: activeTab === "vision" ? "block" : "none", height: "100%" }}>
              <Vision />
            </div>
            
            <div style={{ display: activeTab === "review" ? "block" : "none", height: "100%" }}>
              <ReviewGate />
            </div>
            
            <div style={{ display: activeTab === "audit" ? "block" : "none", height: "100%" }}>
              <AuditLogs />
            </div>
            
            <div style={{ display: activeTab === "documents" ? "block" : "none", height: "100%" }}>
              <Documents />
            </div>
          </div>

          <aside className="trust-panel">
            <h3>Trust Layer</h3>

            <div className="trust-card">
              <span>Confidence</span>
              <strong>—</strong>
            </div>

            <div className="trust-card">
              <span>Grounding</span>
              <strong>—</strong>
            </div>

            <div className="trust-card">
              <span>Sources</span>
              <strong>—</strong>
            </div>

            <h3>Infrastructure</h3>

            <div className="infrastructure">
              <p><strong>Model:</strong> phi3.5</p>
              <p><strong>Runtime:</strong> Ollama</p>
              <p><strong>Network:</strong> LAN</p>
              <p><strong>Mode:</strong> Air-gapped</p>
            </div>

            <div className="api-info">
              <small>API Gateway</small>
              <p>{API_BASE_URL}</p>
            </div>
          </aside>
        </section>
      </main>
    </div>
  );
}

export default App;