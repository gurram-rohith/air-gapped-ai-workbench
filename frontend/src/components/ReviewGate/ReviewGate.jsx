import { useState } from "react";

function ReviewGate() {
  const [decision, setDecision] = useState(null);

  const confidence = 87;

  return (
    <div className="review-page">
      <div className="review-header">
        <div>
          <span className="section-label">
            HUMAN-IN-THE-LOOP
          </span>

          <h2>Review Gate</h2>

          <p>
            Verify AI-generated results before approval.
          </p>
        </div>

        <div className="review-badge">
          Awaiting review
        </div>
      </div>

      <div className="review-content">
        <div className="review-main-card">
          <div className="review-card-header">
            <div>
              <span className="card-label">
                AI RESULT
              </span>

              <h3>Engineering analysis result</h3>
            </div>

            <span className="demo-label">
              DEMO DATA
            </span>
          </div>

          <div className="confidence-section">
            <div className="confidence-heading">
              <span>Confidence score</span>

              <strong>{confidence}%</strong>
            </div>

            <div className="confidence-bar">
              <div
                style={{
                  width: `${confidence}%`,
                }}
              ></div>
            </div>

            <div className="confidence-levels">
              <span>Low</span>
              <span>Medium</span>
              <span>High</span>
            </div>
          </div>

          <div className="result-box">
            <span>AI SUMMARY</span>

            <p>
              The local AI model has generated an analysis
              that requires human verification before being
              accepted.
            </p>
          </div>

          <div className="review-actions">
            <button
              className="reject-button"
              onClick={() => setDecision("rejected")}
            >
              Reject result
            </button>

            <button
              className="approve-button"
              onClick={() => setDecision("approved")}
            >
              Approve result
            </button>
          </div>

          {decision && (
            <div
              className={`decision-message ${
                decision === "approved"
                  ? "decision-approved"
                  : "decision-rejected"
              }`}
            >
              {decision === "approved"
                ? "✓ Result approved by reviewer"
                : "✕ Result rejected by reviewer"}
            </div>
          )}
        </div>

        <div className="review-side-card">
          <span className="card-label">
            VERIFICATION
          </span>

          <h3>Review checklist</h3>

          <div className="check-item">
            <span>✓</span>
            <p>Review AI confidence</p>
          </div>

          <div className="check-item">
            <span>✓</span>
            <p>Verify generated result</p>
          </div>

          <div className="check-item">
            <span>✓</span>
            <p>Approve or reject output</p>
          </div>

          <div className="demo-warning">
            <strong>Demo interface</strong>

            <p>
              Confidence and result data are currently
              placeholders until the trust-layer API is
              connected.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReviewGate;