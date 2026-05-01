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
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">
            Central Transfers
          </h1>
          <p className="text-slate-500">Visão geral da operação</p>
        </div>

        <button
          onClick={logout}
          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
        >
          Sair
        </button>
      </div>

      {!stats ? (
        <p>Carregando dados...</p>
      ) : (
        <>
          <div className="grid grid-cols-3 gap-6 mb-8">
            <div className="bg-white p-6 rounded-2xl shadow">
              <h2 className="text-slate-500">Clientes</h2>
              <p className="text-3xl font-bold text-indigo-600">
                {stats.clientes || 0}
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow">
              <h2 className="text-slate-500">Motoristas ativos</h2>
              <p className="text-3xl font-bold text-green-600">
                {stats.motoristas || 0}
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow">
              <h2 className="text-slate-500">Pedidos hoje</h2>
              <p className="text-3xl font-bold text-blue-600">
                {stats.pedidos || 0}
              </p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow">
            <h2 className="text-lg font-semibold mb-4">
              📊 Status da operação
            </h2>

            <div className="grid grid-cols-3 gap-4">
              <div className="bg-green-100 p-4 rounded">
                <p className="text-sm text-green-700">Concluídos</p>
                <p className="text-xl font-bold">
                  {stats.finalizados || 0}
                </p>
              </div>

              <div className="bg-yellow-100 p-4 rounded">
                <p className="text-sm text-yellow-700">Em andamento</p>
                <p className="text-xl font-bold">
                  {stats.em_execucao || 0}
                </p>
              </div>

              <div className="bg-red-100 p-4 rounded">
                <p className="text-sm text-red-700">Pendentes</p>
                <p className="text-xl font-bold">
                  {stats.pendentes || 0}
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default App;