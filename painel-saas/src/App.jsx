import React from "react";
import Login from "./Login";

const App = () => {
  const token = localStorage.getItem("token");

  // 🔒 Se não estiver logado → mostra login
  if (!token) {
    return <Login />;
  }

  // ✅ Se estiver logado → mostra painel
  return (
    <div className="min-h-screen bg-slate-100">
      
      {/* Header */}
      <header className="bg-white shadow p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-slate-800">
          Central Transfers
        </h1>

        <button
          onClick={() => {
            localStorage.removeItem("token");
            window.location.reload();
          }}
          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
        >
          Sair
        </button>
      </header>

      {/* Conteúdo do painel */}
      <main className="p-6">
        <h2 className="text-2xl font-semibold text-slate-700 mb-4">
          Dashboard
        </h2>

        <div className="bg-white p-6 rounded shadow">
          <p className="text-slate-600">
            ✅ Login realizado com sucesso!
          </p>
          <p className="text-slate-500 mt-2">
            Agora vamos evoluir esse painel com dados reais.
          </p>
        </div>
      </main>
    </div>
  );
};

export default App;