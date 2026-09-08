import { useState } from "react";

function AuditLogs() {
  const [logs] = useState([
    {
      id: 1,
      action: "AI response generated",
      source: "Local AI model",
      time: "Just now",
      status: "Verified",
    },
    {
      id: 2,
      action: "Trust evaluation completed",
      source: "Trust Layer",
      time: "Just now",
      status: "Verified",
    },
    {
      id: 3,
      action: "System initialized",
      source: "AI Workbench",
      time: "Session start",
      status: "Verified",
    },
  ]);

  return (
    <div className="audit-logs">
      <div className="audit-header">
        <h2>Audit Logs</h2>
        <p>Inspect system activity and cryptographic provenance.</p>
      </div>

      <div className="audit-summary">
        <div className="audit-summary-card">
          <span>Total Events</span>
          <strong>{logs.length}</strong>
        </div>

        <div className="audit-summary-card">
          <span>Verified</span>
          <strong>
            {logs.filter((log) => log.status === "Verified").length}
          </strong>
        </div>

        <div className="audit-summary-card">
          <span>Integrity</span>
          <strong>✓ Valid</strong>
        </div>
      </div>

      <div className="audit-list">
        {logs.map((log) => (
          <div className="audit-entry" key={log.id}>
            <div className="audit-icon">✓</div>

            <div className="audit-content">
              <h3>{log.action}</h3>

              <p>
                Source: <strong>{log.source}</strong>
              </p>

              <small>{log.time}</small>
            </div>

            <div className="audit-status">{log.status}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AuditLogs;