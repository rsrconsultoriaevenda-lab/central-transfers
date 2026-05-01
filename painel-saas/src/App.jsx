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
      console.error(err);
    }
  };

  if (!logado) return <Login />;

  return (
    <div className="p-10">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>

      {!stats ? (
        <p>Carregando dados...</p>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded shadow">
            <h2>Clientes</h2>
            <p className="text-xl">{stats.clientes || 0}</p>
          </div>

          <div className="bg-white p-4 rounded shadow">
            <h2>Motoristas</h2>
            <p className="text-xl">{stats.motoristas || 0}</p>
          </div>

          <div className="bg-white p-4 rounded shadow">
            <h2>Pedidos</h2>
            <p className="text-xl">{stats.pedidos || 0}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;