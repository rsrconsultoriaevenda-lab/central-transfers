// Em produção, o VITE_API_URL será algo como https://sua-api.railway.app
// Em desenvolvimento local, ele cairá automaticamente para o localhost:8001
const API_URL = (import.meta.env.VITE_API_URL && import.meta.env.VITE_API_URL !== "undefined")
  ? import.meta.env.VITE_API_URL.replace(/\/$/, "")
  : "http://localhost:8001";

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