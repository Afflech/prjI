import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const EMPTY_PASTE_FORM = { title: "", content: "" };
const ACCEPTED_SOURCE_TYPES = [
  ".txt",
  ".md",
  ".markdown",
  ".pdf",
  ".pptx",
  "text/plain",
  "text/markdown",
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.presentationml.presentation",
].join(",");
const COLLAPSIBLE_MESSAGE_LENGTH = 360;
const EMPTY_LOADING = {
  notebooks: false,
  workspace: false,
  createNotebook: false,
  renameNotebook: false,
  deleteNotebook: false,
  sourceAction: false,
  chat: false,
  evidence: false,
};

async function apiRequest(path, options = {}) {
  const { json, ...requestOptions } = options;
  const headers = new Headers(requestOptions.headers || {});
  let body = requestOptions.body;

  if (json !== undefined) {
    headers.set("content-type", "application/json");
    body = JSON.stringify(json);
  }

  const response = await fetch(path, { ...requestOptions, headers, body });
  const text = await response.text();
  let payload = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }

  if (!response.ok) {
    throw new Error(errorMessage(payload, response.status));
  }

  return payload;
}

function errorMessage(payload, status) {
  if (payload?.detail?.message) return payload.detail.message;
  if (typeof payload?.detail === "string") return payload.detail;
  if (Array.isArray(payload?.detail) && payload.detail[0]?.msg) {
    return payload.detail[0].msg;
  }
  if (typeof payload === "string") return payload;
  return `Yêu cầu thất bại (${status})`;
}

function sourceTypeLabel(type) {
  const labels = {
    pasted_text: "Dán",
    text_file: "TXT",
    markdown_file: "MD",
    pdf_file: "PDF",
    pptx_file: "PPTX",
  };
  return labels[type] || type;
}

function sourceStatusLabel(status) {
  const labels = {
    ready: "sẵn sàng",
    failed: "lỗi",
    processing: "đang xử lý",
  };
  return labels[status] || status;
}

function roleLabel(role) {
  return role === "user" ? "Bạn" : "Trợ lý";
}

function citationLabel(citation) {
  const page = citation.page ? ` · p.${citation.page}` : "";
  return `${citation.source_title} · đoạn ${citation.chunk_id}${page}`;
}

function App() {
  const [notebooks, setNotebooks] = useState([]);
  const [selectedNotebookId, setSelectedNotebookId] = useState(null);
  const [sources, setSources] = useState([]);
  const [messages, setMessages] = useState([]);
  const [evidence, setEvidence] = useState(null);
  const [selectedCitation, setSelectedCitation] = useState(null);
  const [newNotebookTitle, setNewNotebookTitle] = useState("");
  const [renameTitle, setRenameTitle] = useState("");
  const [pasteForm, setPasteForm] = useState(EMPTY_PASTE_FORM);
  const [question, setQuestion] = useState("");
  const [error, setError] = useState("");
  const [evidenceError, setEvidenceError] = useState("");
  const [expandedMessageIds, setExpandedMessageIds] = useState(new Set());
  const [loading, setLoading] = useState(EMPTY_LOADING);
  const [sourceActionId, setSourceActionId] = useState(null);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const selectedNotebook = useMemo(
    () => notebooks.find((notebook) => notebook.id === selectedNotebookId),
    [notebooks, selectedNotebookId],
  );

  useEffect(() => {
    loadNotebooks();
  }, []);

  useEffect(() => {
    if (!selectedNotebookId) {
      setSources([]);
      setMessages([]);
      setEvidence(null);
      setSelectedCitation(null);
      setRenameTitle("");
      return;
    }
    loadNotebookWorkspace(selectedNotebookId);
  }, [selectedNotebookId]);

  useEffect(() => {
    setRenameTitle(selectedNotebook?.title || "");
  }, [selectedNotebook?.id, selectedNotebook?.title]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading.chat]);

  async function run(task, action, onError = setError) {
    setLoading((current) => ({ ...current, [task]: true }));
    onError("");
    try {
      return await action();
    } catch (requestError) {
      onError(requestError.message);
      return null;
    } finally {
      setLoading((current) => ({ ...current, [task]: false }));
    }
  }

  async function loadNotebooks(preferredId) {
    const loaded = await run("notebooks", () => apiRequest("/api/notebooks"));
    if (!loaded) return;
    setNotebooks(loaded);
    const preferredExists = loaded.some((notebook) => notebook.id === preferredId);
    const selectedExists = loaded.some(
      (notebook) => notebook.id === selectedNotebookId,
    );
    if (preferredExists) {
      setSelectedNotebookId(preferredId);
    } else if (!selectedExists) {
      setSelectedNotebookId(loaded[0]?.id || null);
    }
  }

  async function loadNotebookWorkspace(notebookId) {
    const workspace = await run("workspace", async () => {
      const [loadedSources, loadedMessages] = await Promise.all([
        apiRequest(`/api/notebooks/${notebookId}/sources`),
        apiRequest(`/api/notebooks/${notebookId}/messages`),
      ]);
      return { loadedSources, loadedMessages };
    });

    if (workspace) {
      const { loadedSources, loadedMessages } = workspace;
      setSources(loadedSources);
      setMessages(loadedMessages);
      setEvidence(null);
      setSelectedCitation(null);
      setEvidenceError("");
    }
  }

  async function loadSources(notebookId) {
    const loadedSources = await run("sourceAction", () =>
      apiRequest(`/api/notebooks/${notebookId}/sources`),
    );
    if (loadedSources) {
      setSources(loadedSources);
      const sourceStillExists = loadedSources.some(
        (source) => source.id === selectedCitation?.source_id,
      );
      if (selectedCitation && !sourceStillExists) {
        setEvidence(null);
        setSelectedCitation(null);
        setEvidenceError("");
      }
    }
  }

  async function createNotebook(event) {
    event.preventDefault();
    const title = newNotebookTitle.trim();
    if (!title) return;
    const notebook = await run("createNotebook", () =>
      apiRequest("/api/notebooks", {
        method: "POST",
        json: { title },
      }),
    );
    if (notebook) {
      setNewNotebookTitle("");
      await loadNotebooks(notebook.id);
    }
  }

  async function renameNotebook(event) {
    event.preventDefault();
    if (!selectedNotebook) return;
    const title = renameTitle.trim();
    if (!title || title === selectedNotebook.title) return;
    const updated = await run("renameNotebook", () =>
      apiRequest(`/api/notebooks/${selectedNotebook.id}`, {
        method: "PATCH",
        json: { title },
      }),
    );
    if (updated) {
      setNotebooks((current) =>
        current.map((notebook) =>
          notebook.id === updated.id ? updated : notebook,
        ),
      );
    }
  }

  async function deleteNotebook() {
    if (!selectedNotebook) return;
    const confirmed = window.confirm(`Xóa "${selectedNotebook.title}"?`);
    if (!confirmed) return;
    const deleted = await run("deleteNotebook", async () => {
      await apiRequest(`/api/notebooks/${selectedNotebook.id}`, {
        method: "DELETE",
      });
      return true;
    });
    if (deleted) {
      await loadNotebooks();
    }
  }

  async function addPastedSource(event) {
    event.preventDefault();
    if (!selectedNotebook) return;
    const title = pasteForm.title.trim();
    const content = pasteForm.content.trim();
    if (!title || !content) return;
    const source = await run("sourceAction", () =>
      apiRequest(`/api/notebooks/${selectedNotebook.id}/sources`, {
        method: "POST",
        json: { title, content },
      }),
    );
    if (source) {
      setPasteForm(EMPTY_PASTE_FORM);
      await loadSources(selectedNotebook.id);
    }
  }

  async function uploadSource(event) {
    const file = event.target.files?.[0];
    if (!file || !selectedNotebook) return;
    const params = new URLSearchParams({ filename: file.name });
    const source = await run("sourceAction", async () => {
      const content = await file.arrayBuffer();
      return apiRequest(
        `/api/notebooks/${selectedNotebook.id}/sources/upload?${params}`,
        {
          method: "POST",
          headers: {
            "content-type": file.type || "text/plain; charset=utf-8",
          },
          body: content,
        },
      );
    });
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    if (source) {
      await loadSources(selectedNotebook.id);
    }
  }

  async function toggleSource(source) {
    setSourceActionId(source.id);
    const updated = await run("sourceAction", () =>
      apiRequest(`/api/sources/${source.id}`, {
        method: "PATCH",
        json: { enabled: !source.enabled },
      }),
    );
    setSourceActionId(null);
    if (updated) {
      setSources((current) =>
        current.map((item) => (item.id === updated.id ? updated : item)),
      );
    }
  }

  async function deleteSource(source) {
    const confirmed = window.confirm(`Xóa "${source.title}"?`);
    if (!confirmed || !selectedNotebook) return;
    setSourceActionId(source.id);
    const deleted = await run("sourceAction", async () => {
      await apiRequest(`/api/sources/${source.id}`, { method: "DELETE" });
      return true;
    });
    setSourceActionId(null);
    if (deleted) {
      await loadSources(selectedNotebook.id);
    }
  }

  async function sendQuestion(event) {
    event.preventDefault();
    if (!selectedNotebook) return;
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) return;
    const tempUserMessage = {
      id: `tmp-${Date.now()}`,
      notebook_id: selectedNotebook.id,
      role: "user",
      content: trimmedQuestion,
      citations: [],
      created_at: new Date().toISOString(),
    };

    setQuestion("");
    setEvidence(null);
    setSelectedCitation(null);
    setEvidenceError("");
    setMessages((current) => [...current, tempUserMessage]);
    const chat = await run("chat", () =>
      apiRequest(`/api/notebooks/${selectedNotebook.id}/chat`, {
        method: "POST",
        json: { question: trimmedQuestion },
      }),
    );
    if (chat) {
      setMessages((current) => [
        ...current.map((message) =>
          message.id === tempUserMessage.id ? chat.user_message : message,
        ),
        chat.assistant_message,
      ]);
    } else {
      setMessages((current) =>
        current.filter((message) => message.id !== tempUserMessage.id),
      );
    }
  }

  async function openCitation(citation) {
    setSelectedCitation(citation);
    setEvidence(null);
    const chunk = await run(
      "evidence",
      () => apiRequest(`/api/chunks/${citation.chunk_id}`),
      setEvidenceError,
    );
    if (chunk) {
      setEvidence(chunk);
    }
  }

  function toggleMessageExpanded(messageId) {
    setExpandedMessageIds((current) => {
      const next = new Set(current);
      if (next.has(messageId)) {
        next.delete(messageId);
      } else {
        next.add(messageId);
      }
      return next;
    });
  }

  const hasNotebook = Boolean(selectedNotebook);

  return (
    <main className="app-shell">
      <section className="workspace">
        <aside className="panel sources-panel" aria-label="Nguồn">
          <header className="brand-block">
            <p className="eyebrow">Mini NotebookLM</p>
            <h1>Hỏi đáp tài liệu</h1>
          </header>

          <form className="inline-form" onSubmit={createNotebook}>
            <input
              aria-label="Tên notebook mới"
              onChange={(event) => setNewNotebookTitle(event.target.value)}
              placeholder="Notebook mới"
              value={newNotebookTitle}
            />
            <button
              className="primary"
              disabled={loading.createNotebook}
              type="submit"
            >
              Tạo
            </button>
          </form>

          <div className="notebook-list" aria-label="Danh sách notebook">
            {notebooks.map((notebook) => (
              <button
                aria-current={
                  notebook.id === selectedNotebookId ? "true" : undefined
                }
                className={
                  notebook.id === selectedNotebookId
                    ? "notebook-item active"
                    : "notebook-item"
                }
                key={notebook.id}
                onClick={() => setSelectedNotebookId(notebook.id)}
                type="button"
              >
                {notebook.title}
              </button>
            ))}
            {!notebooks.length && (
              <p className="muted compact">Tạo notebook để bắt đầu.</p>
            )}
          </div>

          {hasNotebook && (
            <>
              <details className="notebook-settings">
                <summary>Thiết lập notebook</summary>
                <form className="stack-form" onSubmit={renameNotebook}>
                  <label htmlFor="rename-title">Tên notebook</label>
                  <div className="inline-form">
                    <input
                      id="rename-title"
                      onChange={(event) => setRenameTitle(event.target.value)}
                      value={renameTitle}
                    />
                    <button disabled={loading.renameNotebook} type="submit">
                      Lưu
                    </button>
                  </div>
                  <button
                    className="secondary danger"
                    disabled={loading.deleteNotebook}
                    onClick={deleteNotebook}
                    type="button"
                  >
                    Xóa notebook
                  </button>
                </form>
              </details>

              <section className="source-tools" aria-label="Công cụ nguồn">
                <h2>Nguồn</h2>

                <button
                  className="file-button primary"
                  disabled={loading.sourceAction}
                  onClick={() => fileInputRef.current?.click()}
                  type="button"
                >
                  Tải tệp lên
                </button>
                <input
                  accept={ACCEPTED_SOURCE_TYPES}
                  aria-label="Tải tệp nguồn lên"
                  className="file-input"
                  disabled={loading.sourceAction}
                  onChange={uploadSource}
                  ref={fileInputRef}
                  type="file"
                />

                <details className="paste-source-details">
                  <summary>Dán văn bản thay thế</summary>
                  <form className="stack-form" onSubmit={addPastedSource}>
                    <input
                      aria-label="Tên nguồn"
                      onChange={(event) =>
                        setPasteForm((current) => ({
                          ...current,
                          title: event.target.value,
                        }))
                      }
                      placeholder="Tên nguồn"
                      value={pasteForm.title}
                    />
                    <textarea
                      aria-label="Nội dung nguồn"
                      onChange={(event) =>
                        setPasteForm((current) => ({
                          ...current,
                          content: event.target.value,
                        }))
                      }
                      placeholder="Dán tài liệu học tập"
                      rows="5"
                      value={pasteForm.content}
                    />
                    <button
                      className="primary"
                      disabled={loading.sourceAction}
                      type="submit"
                    >
                      Thêm nguồn
                    </button>
                  </form>
                </details>

                <div className="source-list">
                  {sources.map((source) => (
                    <article className="source-row" key={source.id}>
                      <div>
                        <strong>{source.title}</strong>
                        <span>
                          #{source.id} · {sourceTypeLabel(source.type)} ·{" "}
                          {sourceStatusLabel(source.status)}
                        </span>
                      </div>
                      <div className="source-actions">
                        <label className="switch-label">
                          <input
                            aria-label={`${source.enabled ? "Tắt" : "Bật"} nguồn ${source.title}`}
                            checked={source.enabled}
                            disabled={
                              loading.sourceAction && sourceActionId === source.id
                            }
                            onChange={() => toggleSource(source)}
                            type="checkbox"
                          />
                          Bật
                        </label>
                        <button
                          aria-label={`Xóa nguồn ${source.title}`}
                          className="icon-text danger"
                          disabled={
                            loading.sourceAction && sourceActionId === source.id
                          }
                          onClick={() => deleteSource(source)}
                          type="button"
                        >
                          Xóa
                        </button>
                      </div>
                    </article>
                  ))}
                  {!sources.length && (
                    <p className="muted compact">Chưa có nguồn nào.</p>
                  )}
                </div>
              </section>
            </>
          )}
        </aside>

        <section className="panel chat-panel" aria-label="Trò chuyện">
          <div className="chat-header">
            <div>
              <p className="eyebrow">Trò chuyện</p>
              <h2>{selectedNotebook?.title || "Chưa chọn notebook"}</h2>
            </div>
            {sources.length > 0 && (
              <span className="source-count">
                {sources.filter((source) => source.enabled).length}/
                {sources.length} bật
              </span>
            )}
          </div>

          <div className="messages" aria-live="polite">
            {error && (
              <div className="error-banner" role="alert">
                {error}
              </div>
            )}
            {loading.workspace && (
              <p className="muted compact">Đang tải workspace...</p>
            )}
            {messages.map((message) => (
              <article className={`message ${message.role}`} key={message.id}>
                <span className="message-label">{roleLabel(message.role)}</span>
                <p
                  className={
                    message.role === "assistant" &&
                    !expandedMessageIds.has(message.id)
                      ? "message-text clamped"
                      : "message-text"
                  }
                >
                  {message.content}
                </p>
                {message.role === "assistant" &&
                  message.content.length > COLLAPSIBLE_MESSAGE_LENGTH && (
                    <button
                      className="text-button"
                      onClick={() => toggleMessageExpanded(message.id)}
                      type="button"
                    >
                      {expandedMessageIds.has(message.id) ? "Thu gọn" : "Xem thêm"}
                    </button>
                  )}
                {(message.citations || []).length > 0 && (
                  <div className="citation-list">
                    {message.citations.map((citation, index) => (
                      <button
                        className={
                          selectedCitation?.chunk_id === citation.chunk_id
                            ? "citation-chip active"
                            : "citation-chip"
                        }
                        key={`${message.id}-${citation.chunk_id}`}
                        onClick={() => openCitation(citation)}
                        title={citationLabel(citation)}
                        type="button"
                      >
                        [{index + 1}]{" "}
                        {citation.page ? `p.${citation.page}` : `đoạn ${citation.chunk_id}`}
                      </button>
                    ))}
                  </div>
                )}
                {message.role === "assistant" &&
                  (message.citations || []).length === 0 && (
                    <p className="message-note">
                      Không tìm thấy trích dẫn. Hãy thử dùng từ xuất hiện trong
                      nguồn đang bật.
                    </p>
                  )}
              </article>
            ))}
            {loading.chat && (
              <article className="message assistant pending">
                <span className="message-label">Trợ lý</span>
                <p className="message-text">Đang tìm trong nguồn...</p>
              </article>
            )}
            {hasNotebook && !messages.length && (
              <p className="muted empty-chat">
                Thêm nguồn rồi đặt câu hỏi.
              </p>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="composer" onSubmit={sendQuestion}>
            <textarea
              aria-label="Câu hỏi"
              disabled={!hasNotebook || loading.chat}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  event.currentTarget.form.requestSubmit();
                }
              }}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder={
                hasNotebook ? "Hỏi về nguồn đang bật" : "Chọn notebook"
              }
              rows="2"
              value={question}
            />
            <button
              className="primary"
              disabled={!hasNotebook || loading.chat}
              type="submit"
            >
              Gửi
            </button>
          </form>
        </section>

        <aside className="panel evidence-panel" aria-label="Bằng chứng">
          <p className="eyebrow">Bằng chứng</p>
          {loading.evidence ? (
            <p className="muted">Đang tải bằng chứng...</p>
          ) : evidenceError ? (
            <p className="error-text" role="alert">
              {evidenceError}
            </p>
          ) : evidence ? (
            <article className="evidence-content">
              <h2>
                {evidence.source_title} · đoạn {evidence.id}
              </h2>
              <dl>
                <div>
                  <dt>Đoạn</dt>
                  <dd>{evidence.id}</dd>
                </div>
                {evidence.page && (
                  <div>
                    <dt>Trang</dt>
                    <dd>{evidence.page}</dd>
                  </div>
                )}
              </dl>
              {!evidence.page && (
                <p className="metadata-note">Không có metadata trang cho nguồn này.</p>
              )}
              <p>{evidence.text}</p>
            </article>
          ) : selectedCitation ? (
            <article className="evidence-content">
              <h2>{citationLabel(selectedCitation)}</h2>
              <p>{selectedCitation.quote}</p>
            </article>
          ) : (
            <p className="muted">Chọn một trích dẫn để xem đoạn nguồn.</p>
          )}
        </aside>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
