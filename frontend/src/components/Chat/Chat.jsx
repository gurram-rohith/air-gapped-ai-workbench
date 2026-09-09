import { useState } from "react";
import { sendChatMessage } from "../../services/api";

function Chat() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I'm your Sovereign AI Assistant. How can I help you?",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    const text = input.trim();

    if (!text || loading) return;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: text,
      },
      {
        role: "assistant",
        content: "",
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      await sendChatMessage(text, (_, fullResponse) => {
        setMessages((prev) => {
          const updated = [...prev];

          updated[updated.length - 1] = {
            role: "assistant",
            content: fullResponse,
          };

          return updated;
        });
      });
    } catch (error) {
      console.error(error);

      setMessages((prev) => {
        const updated = [...prev];

        updated[updated.length - 1] = {
          role: "assistant",
          content:
            "Unable to connect to the backend. Please check the server connection.",
        };

        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div>
          <span className="chat-header-label">
            LOCAL MODEL
          </span>

          <h3>AI Assistant</h3>

          <p>
            Private inference through the air-gapped
            environment
          </p>
        </div>

        <div className="model-badge">
          <span className="model-dot"></span>
          phi3.5
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message-row ${
              message.role === "user"
                ? "user-row"
                : "assistant-row"
            }`}
          >
            <div className="message-avatar">
              {message.role === "user" ? "U" : "AI"}
            </div>

            <div
              className={`message ${
                message.role === "user"
                  ? "user-message"
                  : "assistant-message"
              }`}
            >
              <div className="message-role">
                {message.role === "user"
                  ? "You"
                  : "Sovereign AI"}
              </div>

              <div className="message-content">
                {message.content}
              </div>
            </div>
          </div>
        ))}

        {loading &&
          messages[messages.length - 1]?.content === "" && (
            <div className="message-row assistant-row">
              <div className="message-avatar">AI</div>

              <div className="message assistant-message">
                <div className="message-role">
                  Sovereign AI
                </div>

                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
      </div>

      <div className="chat-input-wrapper">
        <div className="chat-input-area">
          <textarea
            value={input}
            onChange={(event) =>
              setInput(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask Sovereign AI anything..."
            rows={2}
            disabled={loading}
          />

          <button
            className="send-button"
            onClick={handleSend}
            disabled={loading || !input.trim()}
          >
            {loading ? "..." : "↑"}
          </button>
        </div>

        <div className="input-footer">
          <span>Enter to send</span>
          <span>Shift + Enter for new line</span>
        </div>
      </div>
    </div>
  );
}

export default Chat;