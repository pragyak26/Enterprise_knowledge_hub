import { useEffect, useRef, useState } from "react";
import {
  deleteDocument,
  listDocuments,
  uploadDocument,
  uploadVersion,
} from "../api.js";
import { EmptyState, Loading, Spinner } from "./ui.jsx";

const ACCEPT = ".pdf,.docx,.doc,.txt,.md";

export default function Documents({ onChange }) {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [title, setTitle] = useState("");
  const newFileRef = useRef(null);

  async function refresh() {
    setLoading(true);
    try {
      setDocs(await listDocuments());
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleNewUpload(e) {
    e.preventDefault();
    const file = newFileRef.current?.files?.[0];
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      await uploadDocument(file, title.trim() || undefined);
      setTitle("");
      newFileRef.current.value = "";
      await refresh();
      onChange?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleAddVersion(docId, file) {
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      await uploadVersion(docId, file);
      await refresh();
      onChange?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(docId) {
    if (!confirm("Delete this document and all its versions?")) return;
    setBusy(true);
    try {
      await deleteDocument(docId);
      await refresh();
      onChange?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel">
      <div className="card">
        <h2>Upload a document</h2>
        <form className="upload-form" onSubmit={handleNewUpload}>
          <input
            type="text"
            placeholder="Title (optional)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <input type="file" ref={newFileRef} accept={ACCEPT} required />
          <button type="submit" disabled={busy}>
            {busy ? <Spinner label="Working…" /> : "Upload"}
          </button>
        </form>
        <p className="muted small">Supported: PDF, DOCX, TXT, MD. Indexing runs on upload.</p>
        {error && <div className="error">{error}</div>}
      </div>

      <div className="card">
        <div className="card-head">
          <h2>Your documents</h2>
          <button className="ghost" onClick={refresh} disabled={loading}>
            Refresh
          </button>
        </div>

        {loading ? (
          <Loading label="Loading your documents…" />
        ) : docs.length === 0 ? (
          <EmptyState icon="📄" title="No documents yet">
            Upload your first file above. Once indexed, you can ask questions about it
            and compare versions.
          </EmptyState>
        ) : (
          <ul className="doc-list">
            {docs.map((d) => (
              <li key={d.id} className="doc">
                <div className="doc-head">
                  <div>
                    <span className="doc-title">{d.title}</span>
                    <span className="badge">#{d.id}</span>
                  </div>
                  <button className="ghost danger" onClick={() => handleDelete(d.id)}>
                    Delete
                  </button>
                </div>
                <div className="versions">
                  {d.versions.map((v) => (
                    <span key={v.id} className="version-chip" title={`${v.num_chunks} chunks`}>
                      v{v.version_number} · {v.original_filename}
                    </span>
                  ))}
                </div>
                <label className="add-version">
                  + Add new version
                  <input
                    type="file"
                    accept={ACCEPT}
                    onChange={(e) => handleAddVersion(d.id, e.target.files[0])}
                  />
                </label>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
