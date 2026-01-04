// In production on Render, NEXT_PUBLIC_* vars are not reliably available at image build time.
// Default to same-origin so our Next.js `/api/*` proxy can forward to the backend at runtime.
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "";

export class APIError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new APIError(text || res.statusText, res.status);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  register: (email: string, password: string, preferred_language: string) =>
    fetchAPI("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, preferred_language }),
    }),

  login: (email: string, password: string) =>
    fetchAPI("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  logout: () =>
    fetchAPI("/api/auth/logout", {
      method: "POST",
    }),

  getMe: () => fetchAPI("/api/me"),

  updateMe: (preferred_language: string) =>
    fetchAPI("/api/me", {
      method: "PATCH",
      body: JSON.stringify({ preferred_language }),
    }),

  createEntry: (text: string, mood_score: number, energy_score: number) =>
    fetchAPI("/api/journal", {
      method: "POST",
      body: JSON.stringify({ text, mood_score, energy_score }),
    }),

  listEntries: (limit = 20) => fetchAPI(`/api/journal?limit=${limit}`),

  getEntry: (id: string) => fetchAPI(`/api/journal/${id}`),

  getEntryAnalysis: (id: string) => fetchAPI(`/api/journal/${id}/analysis`),

  recomputeEntryAnalysis: (id: string) =>
    fetchAPI(`/api/journal/${id}/analysis/recompute`, {
      method: "POST",
    }),

  getCurrentReport: () => fetchAPI("/api/report/current"),

  recomputeReport: () => fetchAPI("/api/report/recompute", { method: "POST" }),

  exportData: () => fetchAPI("/api/export"),

  deleteAccount: () => fetchAPI("/api/account", { method: "DELETE" }),
};
