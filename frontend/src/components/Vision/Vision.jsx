import { useState } from "react";

function Vision() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (!selectedFile) return;

    setFile(selectedFile);

    if (selectedFile.type.startsWith("image/")) {
      setPreview(URL.createObjectURL(selectedFile));
    } else {
      setPreview(null);
    }
  };

  const clearFile = () => {
    setFile(null);
    setPreview(null);
  };

  return (
    <div className="vision-container">
      <div className="vision-header">
        <h2>P&ID Visual Analysis</h2>
        <p>Upload an engineering image for local visual analysis.</p>
      </div>

      <div className="upload-box">
        {!file ? (
          <>
            <div className="upload-icon">⬆</div>

            <h3>Upload P&ID Image</h3>

            <p>
              Select an image containing a Process & Instrumentation Diagram.
            </p>

            <label className="upload-button">
              Choose image
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                hidden
              />
            </label>
          </>
        ) : (
          <div className="selected-file">
            <h3>{file.name}</h3>

            <p>
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>

            {preview && (
              <img
                src={preview}
                alt="P&ID preview"
                className="vision-preview"
              />
            )}

            <div className="vision-actions">
              <button onClick={clearFile}>Remove</button>

              <button disabled>
                Analyze image
              </button>
            </div>

            <small>
              Analysis will be connected to the backend when the vision API is
              available.
            </small>
          </div>
        )}
      </div>
    </div>
  );
}

export default Vision;