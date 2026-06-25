import { useState } from "react";
import { login, me, register } from "../api.js";
import { Spinner } from "./ui.jsx";

export default function Login({ onLoggedIn }) {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "register") {
        await register(email, password);
      }
      await login(email, password);
      const user = await me();
      onLoggedIn(user);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-landing">
      <aside className="auth-hero">
        <h1>Ask your company's documents anything.</h1>
        <p>
          Upload PDFs, Word files, and reports, then get instant answers in plain
          language — with citations you can trust and version-by-version diffs.
        </p>
        <ul className="hero-points">
          <li>
            <span className="dot">🔍</span> Semantic search across every document
          </li>
          <li>
            <span className="dot">📌</span> Answers grounded with source citations
          </li>
          <li>
            <span className="dot">🕑</span> Compare what changed between versions
          </li>
        </ul>
      </aside>

      <div className="auth-pane">
        <form className="card auth" onSubmit={submit}>
        <h1>📚 Knowledge Hub</h1>
        <p className="muted">
          {mode === "login" ? "Sign in to your workspace" : "Create an account"}
        </p>

        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@company.com"
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            minLength={6}
          />
        </label>

        {error && <div className="error">{error}</div>}

        <button type="submit" disabled={busy}>
          {busy ? <Spinner label="Please wait…" /> : mode === "login" ? "Log in" : "Register & log in"}
        </button>

        <div className="switch">
          {mode === "login" ? "No account?" : "Already registered?"}{" "}
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              setError("");
              setMode(mode === "login" ? "register" : "login");
            }}
          >
            {mode === "login" ? "Create one" : "Log in"}
          </a>
        </div>
        </form>
      </div>
    </div>
  );
}
