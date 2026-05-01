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

  const logout = () => {
    localStorage.removeItem("token");
    window.location.reload();
  };

  if (!logado) return <Login />;

  return (
    <div className="flex min-h-screen bg-slate-100">

      {/* SIDEBAR */}
      <aside className="w-64 bg-slate-900 text-white p-6 flex flex-col justify-between">
        <div>
          <h1 className="text-xl font-bold mb-8">🚐 Central</h1>

          <nav className="space-y-4">
            <button className="block w-full text-left hover:text-blue-400">
              Dashboard
            </button>
            <button className="block w-full text-left hover:text-blue-400">
              Clientes
            </button>
            <button className="block w-full text-left hover:text-blue-400">
              Motoristas
            </button>
            <button className="block w-full text-left hover:text-blue-400">
              Pedidos
            </button>
          </nav>
        </div>

        <button
          onClick={logout}
          className="bg-red-500 hover:bg-red-600 p-2 rounded"
        >
          Sair
        </button>
      </aside>

      {/* CONTEÚDO */}
      <main className="flex-1 p-10">

        <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

        {!stats ? (
          <p>Carregando dados...</p>
        ) : (
          <div className="grid grid-cols-3 gap-6">

            <Card titulo="Clientes" valor={stats.clientes} />
            <Card titulo="Motoristas" valor={stats.motoristas} />
            <Card titulo="Pedidos" valor={stats.pedidos} />

          </div>
        )}
      </main>
    </div>
  );
}

function Card({ titulo, valor }) {
  return (
    <div className="bg-white p-6 rounded-2xl shadow hover:shadow-lg transition">
      <h2 className="text-slate-500 text-sm">{titulo}</h2>
      <p className="text-3xl font-bold mt-2">{valor || 0}</p>
    </div>
  );
}

export default App;