const API_URL = "https://central-transfers-production.up.railway.app";

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