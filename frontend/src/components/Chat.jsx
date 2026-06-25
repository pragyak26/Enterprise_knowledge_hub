import { useEffect, useState } from "react";
import { ask, listDocuments } from "../api.js";
import { EmptyState, Spinner } from "./ui.jsx";

export default function Chat() {
  const [docs, setDocs] = useState([]);
  const [scope, setScope] = useState(""); // "" = all documents
  const [latestOnly, setLatestOnly] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]); // {question, answer, citations}
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    listDocuments().then(setDocs).catch(() => {});
  }, []);

  async function submit(e) {
    e.preventDefault();
    const q = question.trim();
    if (!q) return;
    setBusy(true);
    setError("");
    try {
      const res = await ask(q, {
        documentId: scope ? Number(scope) : undefined,
        latestOnly,
      });
      setMessages((m) => [{ question: q, ...res }, ...m]);
      setQuestion("");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const noDocs = docs.length === 0;

  return (
    <div className="panel">
      <div className="card">
        <h2>Ask your documents</h2>
        <form className="ask-form" onSubmit={submit}>
          <select value={scope} onChange={(e) => setScope(e.target.value)}>
            <option value="">All documents</option>
            {docs.map((d) => (
              <option key={d.id} value={d.id}>
                {d.title} (#{d.id})
              </option>
            ))}
          </select>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. How many maternity leave days are allowed?"
            disabled={noDocs}
          />
          <button type="submit" disabled={busy || noDocs}>
            {busy ? <Spinner label="Thinking…" /> : "Ask"}
          </button>
        </form>
        <label className="toggle">
          <input
            type="checkbox"
            checked={latestOnly}
            onChange={(e) => setLatestOnly(e.target.checked)}
          />
          <span>
            Latest version only
            <span className="muted small"> — ignore older versions when answering</span>
          </span>
        </label>
        {error && <div className="error">{error}</div>}
      </div>

      {messages.length === 0 ? (
        noDocs ? (
          <EmptyState icon="📂" title="No documents yet">
            Upload a file in the <strong>Documents</strong> tab, then come back to ask questions about it.
          </EmptyState>
        ) : (
          <EmptyState icon="💬" title="Ask anything about your documents">
            Answers come only from your uploaded files, each with citations you can verify.
            Try “How many maternity leave days are allowed?”
          </EmptyState>
        )
      ) : (
        <div className="thread">
          {messages.map((m, i) => (
            <div key={i} className="card qa">
              <div className="q">🧑 {m.question}</div>
              <div className="a">🤖 {m.answer}</div>
              {m.citations?.length > 0 && (
                <div className="citations">
                  <div className="citations-title">Sources</div>
                  {m.citations.map((c, j) => (
                    <div key={j} className="citation">
                      <div className="cite-meta">
                        {c.document_title} · v{c.version_number}
                        {c.page != null ? ` · page ${c.page}` : ""}
                      </div>
                      <div className="cite-snippet">{c.snippet}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
