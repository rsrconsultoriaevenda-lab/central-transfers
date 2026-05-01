import React, { useState } from "react";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [animando, setAnimando] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    try {
      const response = await fetch(
        "https://central-transfers-production.up.railway.app/auth/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Erro no login");
      }

      // 👉 animação antes de entrar
      setAnimando(true);

      setTimeout(() => {
        localStorage.setItem("token", data.access_token);
        window.location.href = "/";
      }, 1200);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">

      {/* CARD */}
      <div className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md relative overflow-hidden">

        {/* VAN ANIMADA */}
<div
  className={`absolute top-4 left-0 text-4xl transition-all duration-1000
  ${animando ? "translate-x-[400px] opacity-0" : "translate-x-[120px]"}`}
>
  🚐
</div>
        <div className="text-center mb-6 mt-6">
          <h1 className="text-2xl font-bold text-slate-800">
            Central Transfers
          </h1>
          <p className="text-sm text-slate-500">
            Painel de Logística Gramado
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">

          {error && (
            <p className="text-red-500 text-sm text-center">{error}</p>
          )}

          <input
            type="text"
            placeholder="E-mail"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />

          <input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-lg transition-all"
          >
            {loading ? "Entrando..." : "Acessar Painel"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;