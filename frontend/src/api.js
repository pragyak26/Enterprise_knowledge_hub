// Thin API client around the FastAPI backend. Dev requests go through the Vite
// proxy at /api -> http://127.0.0.1:8000.

const BASE = "/api";

let token = localStorage.getItem("ekh_token") || null;

export function getToken() {
  return token;
}

export function setToken(value) {
  token = value;
  if (value) localStorage.setItem("ekh_token", value);
  else localStorage.removeItem("ekh_token");
}

function authHeaders(extra = {}) {
  return token ? { ...extra, Authorization: `Bearer ${token}` } : extra;
}

async function handle(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* ignore */
    }
    throw new Error(detail || `Request failed (${res.status})`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export async function register(email, password) {
  return handle(
    await fetch(`${BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    })
  );
}

export async function login(email, password) {
  // OAuth2 password form: fields are username + password.
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);
  const data = await handle(
    await fetch(`${BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    })
  );
  setToken(data.access_token);
  return data;
}

export async function me() {
  return handle(await fetch(`${BASE}/auth/me`, { headers: authHeaders() }));
}

export async function listDocuments() {
  return handle(await fetch(`${BASE}/documents`, { headers: authHeaders() }));
}

export async function uploadDocument(file, title) {
  const form = new FormData();
  form.append("file", file);
  if (title) form.append("title", title);
  return handle(
    await fetch(`${BASE}/documents`, {
      method: "POST",
      headers: authHeaders(),
      body: form,
    })
  );
}

export async function uploadVersion(documentId, file) {
  const form = new FormData();
  form.append("file", file);
  return handle(
    await fetch(`${BASE}/documents/${documentId}/versions`, {
      method: "POST",
      headers: authHeaders(),
      body: form,
    })
  );
}

export async function deleteDocument(documentId) {
  return handle(
    await fetch(`${BASE}/documents/${documentId}`, {
      method: "DELETE",
      headers: authHeaders(),
    })
  );
}

export async function ask(question, { documentId, latestOnly } = {}) {
  const body = { question };
  if (documentId) body.document_id = documentId;
  if (latestOnly) body.latest_only = true;
  return handle(
    await fetch(`${BASE}/ask`, {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(body),
    })
  );
}

export async function compare(documentId, versionA, versionB) {
  return handle(
    await fetch(`${BASE}/compare`, {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({
        document_id: documentId,
        version_a: versionA,
        version_b: versionB,
      }),
    })
  );
}
