const API_BASE = localStorage.getItem("api_base") || "/api";

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = localStorage.getItem("token");
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  });

  let data = {};
  try { data = await response.json(); } catch (_) {}

  if (!response.ok) {
    const message = data.error || data.message || `Request failed (${response.status})`;
    throw new Error(message);
  }

  return data;
}

function setApiBase(url) {
  localStorage.setItem("api_base", url.replace(/\/$/, ""));
}
