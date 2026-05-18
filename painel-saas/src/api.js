// Em produção, o VITE_API_URL será algo como https://sua-api.railway.app
// Em desenvolvimento local, ele cairá automaticamente para o localhost:8001
// Garante o prefixo /api padrão do FastAPI para todas as requisições do ecossistema Central Transfers
const BASE_URL = (import.meta.env.VITE_API_URL && import.meta.env.VITE_API_URL !== "undefined")
  ? import.meta.env.VITE_API_URL.replace(/\/$/, "")
  : "http://localhost:8001";

// Se a URL já não terminar com /api, nós injetamos ela aqui de forma limpa
const API_URL = BASE_URL.endsWith("/api") ? BASE_URL : `${BASE_URL}/api`;

export const getToken = () => {
  return localStorage.getItem("token");
};

export const apiFetch = async (endpoint, options = {}) => {
  const token = getToken();

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...(options.headers || {}),
    },
  });

  if (response.status === 401) {
    localStorage.removeItem("token");
    window.location.href = "/";
    return;
  }

  return response.json();
};