import { useState } from "react";

function Vision() {
  const [selectedFile, setSelectedFile] =
    useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (!file) return;

    setSelectedFile(file);
  };

  return (
    <div className="vision-page">
      <div className="vision-header">
        <div>
          <span className="section-label">
            COMPUTER VISION
          </span>

          <h2>P&ID Visual Analysis</h2>

          <p>
            Analyze engineering diagrams using the local
            vision pipeline.
          </p>
        </div>

        <div className="vision-status">
          <span></span>
          Local processing
        </div>
      </div>

      <div className="vision-content">
        {!selectedFile ? (
          <label className="vision-upload">
            <div className="vision-upload-icon">
              ◫
            </div>

            <h3>Upload engineering image</h3>

            <p>
              Select a P&ID or engineering diagram for
              visual analysis.
            </p>

            <span className="vision-select">
              Choose image
            </span>

            <small>
              PNG · JPG · JPEG · WEBP
            </small>

            <input
              type="file"
              accept="image/png,image/jpeg,image/webp"
              onChange={handleFileChange}
              hidden
            />
          </label>
        ) : (
          <div className="vision-preview-card">
            <div className="vision-preview-header">
              <div>
                <span className="card-label">
                  SELECTED IMAGE
                </span>

                <h3>{selectedFile.name}</h3>
              </div>

              <button
                onClick={() => setSelectedFile(null)}
              >
                Remove
              </button>
            </div>

            <div className="vision-image-wrapper">
              <img
                src={URL.createObjectURL(selectedFile)}
                alt="Selected engineering diagram"
              />
            </div>

            <div className="vision-analysis-bar">
              <div>
                <span>File type</span>
                <strong>
                  {selectedFile.type || "Image"}
                </strong>
              </div>

              <div>
                <span>Size</span>
                <strong>
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </strong>
              </div>

              <button disabled>
                Analyze image
              </button>
            </div>

            <div className="vision-info">
              <span>✓</span>

              <div>
                <strong>Ready for local analysis</strong>

                <p>
                  Vision API integration will be connected
                  when the backend endpoint is available.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Vision;