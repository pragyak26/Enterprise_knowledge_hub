import { useEffect, useMemo, useState } from "react";
import { compare, listDocuments } from "../api.js";
import { Spinner } from "./ui.jsx";

export default function Compare() {
  const [docs, setDocs] = useState([]);
  const [docId, setDocId] = useState("");
  const [va, setVa] = useState("");
  const [vb, setVb] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    listDocuments().then(setDocs).catch(() => {});
  }, []);

  const selectedDoc = useMemo(
    () => docs.find((d) => String(d.id) === String(docId)),
    [docs, docId]
  );
  const versions = selectedDoc?.versions ?? [];

  async function submit(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    if (va === vb) {
      setError("Pick two different versions.");
      return;
    }
    setBusy(true);
    try {
      setResult(await compare(Number(docId), Number(va), Number(vb)));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel">
      <div className="card">
        <h2>Compare versions</h2>
        <p className="muted small">
          The AI summarizes what changed between two versions of the same document.
        </p>
        <form className="compare-form" onSubmit={submit}>
          <select
            value={docId}
            onChange={(e) => {
              setDocId(e.target.value);
              setVa("");
              setVb("");
              setResult(null);
            }}
            required
          >
            <option value="">Select a document…</option>
            {docs
              .filter((d) => d.versions.length >= 2)
              .map((d) => (
                <option key={d.id} value={d.id}>
                  {d.title} (#{d.id})
                </option>
              ))}
          </select>

          <select value={va} onChange={(e) => setVa(e.target.value)} required disabled={!docId}>
            <option value="">From…</option>
            {versions.map((v) => (
              <option key={v.id} value={v.version_number}>
                v{v.version_number}
              </option>
            ))}
          </select>

          <select value={vb} onChange={(e) => setVb(e.target.value)} required disabled={!docId}>
            <option value="">To…</option>
            {versions.map((v) => (
              <option key={v.id} value={v.version_number}>
                v{v.version_number}
              </option>
            ))}
          </select>

          <button type="submit" disabled={busy || !docId}>
            {busy ? <Spinner label="Comparing…" /> : "Compare"}
          </button>
        </form>
        {docs.filter((d) => d.versions.length >= 2).length === 0 && (
          <p className="muted small">
            You need a document with at least two versions. Add one in the Documents tab.
          </p>
        )}
        {error && <div className="error">{error}</div>}
      </div>

      {result && (
        <div className="card">
          <h3>
            {result.document_title}: v{result.version_a} → v{result.version_b}
          </h3>
          <pre className="compare-result">{result.summary}</pre>
        </div>
      )}
    </div>
  );
}
