import { useState } from "react";

import Chat from "./components/Chat/Chat";
import Vision from "./components/Vision/Vision";
import ReviewGate from "./components/ReviewGate/ReviewGate";
import AuditLogs from "./components/AuditLogs/AuditLogs";

function App() {
  const [activeTab, setActiveTab] = useState("chat");

  const renderComponent = () => {
    if (activeTab === "chat") {
      return <Chat />;
    }

    if (activeTab === "vision") {
      return <Vision />;
    }

    if (activeTab === "review") {
      return <ReviewGate />;
    }

    if (activeTab === "audit") {
      return <AuditLogs />;
    }

    return <Chat />;
  };

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
          onClick={() => setActiveTab("chat")}
        >
          + New conversation
        </button>

        <nav className="navigation">

          <button
            className={`nav-item ${
              activeTab === "chat" ? "active" : ""
            }`}
            onClick={() => setActiveTab("chat")}
          >
            <span>💬</span>
            AI Assistant
          </button>

          <button
            className={`nav-item ${
              activeTab === "vision" ? "active" : ""
            }`}
            onClick={() => setActiveTab("vision")}
          >
            <span>🖼</span>
            Vision
          </button>

          <button
            className={`nav-item ${
              activeTab === "review" ? "active" : ""
            }`}
            onClick={() => setActiveTab("review")}
          >
            <span>✓</span>
            Review Gate
          </button>

          <button
            className={`nav-item ${
              activeTab === "audit" ? "active" : ""
            }`}
            onClick={() => setActiveTab("audit")}
          >
            <span>▤</span>
            Audit Logs
          </button>

          <button className="nav-item">
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
            </h2>

            <p>
              {activeTab === "chat" && "Secure local intelligence"}
              {activeTab === "vision" && "Engineering image analysis"}
              {activeTab === "review" &&
                "Human approval and confidence verification"}
              {activeTab === "audit" &&
                "System activity and cryptographic provenance"}
            </p>
          </div>

          <div className="connection">
            <span className="online-dot"></span>
            Frontend ready
          </div>

        </header>


        {/* CONTENT */}
        <section className="workspace">

          <div className="chat-section">
            {renderComponent()}
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
              <p>
                <strong>Model:</strong> phi3.5
              </p>

              <p>
                <strong>Runtime:</strong> Ollama
              </p>

              <p>
                <strong>Network:</strong> LAN
              </p>

              <p>
                <strong>Mode:</strong> Air-gapped
              </p>
            </div>

          </aside>

        </section>

      </main>

    </div>
  );
}

export default App;