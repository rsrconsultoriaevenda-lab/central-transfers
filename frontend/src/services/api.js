import axios from "axios";

const api = axios.create({
  // Ele vai tentar ler a variável de ambiente, se não existir, usa localhost
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8001",
});

export default api;