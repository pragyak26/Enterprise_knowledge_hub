import { useEffect, useState } from "react";
import { getToken, me, setToken } from "./api.js";
import Login from "./components/Login.jsx";
import Documents from "./components/Documents.jsx";
import Chat from "./components/Chat.jsx";
import Compare from "./components/Compare.jsx";

export default function App() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);
  const [tab, setTab] = useState("chat");
  const [docsVersion, setDocsVersion] = useState(0); // bump to refresh doc lists

  // On load, if we have a stored token, confirm it still works.
  useEffect(() => {
    if (!getToken()) {
      setChecking(false);
      return;
    }
    me()
      .then(setUser)
      .catch(() => setToken(null))
      .finally(() => setChecking(false));
  }, []);

  function handleLoggedIn(u) {
    setUser(u);
  }

  function handleLogout() {
    setToken(null);
    setUser(null);
  }

  if (checking) return <div className="centered">Loading…</div>;

  if (!user) return <Login onLoggedIn={handleLoggedIn} />;

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">📚 Enterprise Knowledge Hub</div>
        <nav className="tabs">
          <button className={tab === "chat" ? "active" : ""} onClick={() => setTab("chat")}>
            Ask
          </button>
          <button className={tab === "docs" ? "active" : ""} onClick={() => setTab("docs")}>
            Documents
          </button>
          <button className={tab === "compare" ? "active" : ""} onClick={() => setTab("compare")}>
            Compare
          </button>
        </nav>
        <div className="user">
          <span>{user.email}</span>
          <button className="ghost" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>

      <main className="content">
        {tab === "chat" && <Chat docsVersion={docsVersion} />}
        {tab === "docs" && (
          <Documents docsVersion={docsVersion} onChange={() => setDocsVersion((v) => v + 1)} />
        )}
        {tab === "compare" && <Compare docsVersion={docsVersion} />}
      </main>
    </div>
  );
}
