import { useState } from "react";

function Documents() {
  const [documents, setDocuments] = useState([]);

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (!file) return;

    setDocuments((prev) => [
      ...prev,
      {
        id: Date.now(),
        name: file.name,
        size: file.size,
        type: file.type || "Document",
        extension:
          file.name.split(".").pop()?.toUpperCase() ||
          "FILE",
        status: "Ready",
      },
    ]);

    event.target.value = "";
  };

  const removeDocument = (id) => {
    setDocuments((prev) =>
      prev.filter((document) => document.id !== id)
    );
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="documents-page">
      <div className="documents-header">
        <div>
          <span className="section-label">
            KNOWLEDGE BASE
          </span>

          <h2>Documents</h2>

          <p>
            Manage documents available to the local AI
            knowledge system.
          </p>
        </div>

        <label className="document-upload-button">
          + Add document

          <input
            type="file"
            accept=".pdf,.txt,.md,.doc,.docx"
            onChange={handleFileChange}
            hidden
          />
        </label>
      </div>

      <div className="documents-content">
        <label className="document-dropzone">
          <div className="document-icon">
            ▤
          </div>

          <h3>Add a document</h3>

          <p>
            Upload a document to prepare it for local
            retrieval and analysis.
          </p>

          <span className="document-select-button">
            Choose document
          </span>

          <small>
            PDF · TXT · MD · DOC · DOCX
          </small>

          <input
            type="file"
            accept=".pdf,.txt,.md,.doc,.docx"
            onChange={handleFileChange}
            hidden
          />
        </label>

        <div className="documents-list-section">
          <div className="documents-list-header">
            <div>
              <span className="card-label">
                LOCAL DOCUMENTS
              </span>

              <h3>Knowledge sources</h3>
            </div>

            <span className="document-count">
              {documents.length} documents
            </span>
          </div>

          {documents.length === 0 ? (
            <div className="documents-empty">
              <div>□</div>

              <h3>No documents yet</h3>

              <p>
                Uploaded documents will appear here.
              </p>
            </div>
          ) : (
            <div className="documents-list">
              {documents.map((document) => (
                <div
                  className="document-entry"
                  key={document.id}
                >
                  <div className="document-file-icon">
                    {document.extension}
                  </div>

                  <div className="document-info">
                    <h3>{document.name}</h3>

                    <div className="document-meta">
                      <span>
                        {formatSize(document.size)}
                      </span>

                      <span>
                        {document.type}
                      </span>
                    </div>
                  </div>

                  <div className="document-ready">
                    <span>✓</span>
                    {document.status}
                  </div>

                  <button
                    className="document-remove"
                    onClick={() =>
                      removeDocument(document.id)
                    }
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="documents-notice">
          <div className="documents-notice-icon">
            ✓
          </div>

          <div>
            <strong>
              Local document processing
            </strong>

            <p>
              Documents remain within the air-gapped
              environment. Backend indexing will be
              connected when the document API is available.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Documents;