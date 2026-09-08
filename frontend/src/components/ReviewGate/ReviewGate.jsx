import { useState } from "react";

function ReviewGate() {
  const [approved, setApproved] = useState(false);

  const confidence = 0.87;

  return (
    <div className="review-gate">
      <div className="review-header">
        <h2>Human Review Gate</h2>
        <p>Review AI-generated results before approval.</p>
      </div>

      <div className="review-card">
        <div className="review-status">
          <span>Review status</span>
          <strong>{approved ? "Approved" : "Pending review"}</strong>
        </div>

        <div className="confidence-section">
          <div className="confidence-header">
            <span>AI Confidence</span>
            <strong>{Math.round(confidence * 100)}%</strong>
          </div>

          <div className="confidence-bar">
            <div
              className="confidence-fill"
              style={{ width: `${confidence * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="review-result">
          <h3>AI Result</h3>

          <p>
            The AI-generated result is ready for human verification.
            Review the information and approve it if it is correct.
          </p>
        </div>

        <div className="review-actions">
          <button
            className="reject-button"
            onClick={() => setApproved(false)}
          >
            Reject
          </button>

          <button
            className="approve-button"
            onClick={() => setApproved(true)}
          >
            Approve
          </button>
        </div>
      </div>
    </div>
  );
}

export default ReviewGate;