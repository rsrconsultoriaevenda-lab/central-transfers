import { useEffect, useState } from "react";
import Login from "./Login";
import { apiFetch } from "./api";

function App() {
  const [logado, setLogado] = useState(false);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (token) {
      setLogado(true);
      carregarDashboard();
    }
  }, []);

  const carregarDashboard = async () => {
    try {
      const data = await apiFetch("/dashboard/stats");
      setStats(data);
    } catch (err) {
      console.error("Erro ao carregar dashboard:", err);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    window.location.reload();
  };

  if (!logado) return <Login />;

  return (
    <div className="p-10 bg-slate-100 min-h-screen">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>

        <button
          onClick={logout}
          className="bg-red-500 text-white px-4 py-2 rounded"
        >
          Sair
        </button>
      </div>

      {!stats ? (
        <p>Carregando dados...</p>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white p-6 rounded shadow">
            <h2 className="text-gray-500">Clientes</h2>
            <p className="text-2xl font-bold">{stats.clientes || 0}</p>
          </div>

          <div className="bg-white p-6 rounded shadow">
            <h2 className="text-gray-500">Motoristas</h2>
            <p className="text-2xl font-bold">{stats.motoristas || 0}</p>
          </div>

          <div className="bg-white p-6 rounded shadow">
            <h2 className="text-gray-500">Pedidos</h2>
            <p className="text-2xl font-bold">{stats.pedidos || 0}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;