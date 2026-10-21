import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function App() {
  return (
    <main className="app-shell">
      <section className="workspace">
        <aside className="panel sources-panel" aria-label="Sources">
          <div>
            <p className="eyebrow">Mini NotebookLM</p>
            <h1>Study Q&A workspace</h1>
          </div>
          <div className="placeholder-list">
            <div className="placeholder-row" />
            <div className="placeholder-row short" />
            <div className="placeholder-row" />
          </div>
        </aside>

        <section className="panel chat-panel" aria-label="Chat">
          <div className="message assistant">
            <span className="message-label">Assistant</span>
            <p>
              Skeleton is ready. Phase 2 will add notebooks, sources, and mock
              chat history.
            </p>
          </div>
          <form className="composer">
            <input
              aria-label="Question"
              disabled
              placeholder="Chat arrives in Phase 2"
            />
            <button disabled type="button">
              Send
            </button>
          </form>
        </section>

        <aside className="panel evidence-panel" aria-label="Evidence">
          <span className="message-label">Evidence</span>
          <p>Citations and source chunks will appear here in the MVP flow.</p>
        </aside>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
