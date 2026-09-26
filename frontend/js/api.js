const API_BASE = localStorage.getItem("api_base") || "/api";

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) headers["Content-Type"] = "application/json";
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

async function downloadFile(path, filename) {
  const headers = {};
  const token = localStorage.getItem("token");
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}${path}`, { headers });
  if (!response.ok) {
    let data = {};
    try { data = await response.json(); } catch (_) {}
    throw new Error(data.error || data.message || `Download failed (${response.status})`);
  }

  const url = URL.createObjectURL(await response.blob());
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function setApiBase(url) {
  localStorage.setItem("api_base", url.replace(/\/$/, ""));
}
