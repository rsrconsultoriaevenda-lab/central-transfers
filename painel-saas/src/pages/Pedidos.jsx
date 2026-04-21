import React, { useEffect, useState } from 'react';
import api from '../services/api';

const Pedidos = () => {
  const [pedidos, setPedidos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtro, setFiltro] = useState('TODOS');

  const carregarPedidos = async () => {
    try {
      const response = await api.get('/pedidos');
      const data = await response.json();
      setPedidos(data);
    } catch (error) {
      console.error("Erro ao carregar pedidos:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarPedidos();
  }, []);

  const pedidosFiltrados = filtro === 'TODOS' 
    ? pedidos 
    : pedidos.filter(p => p.status === filtro);

  const getStatusStyle = (status) => {
    switch (status) {
      case 'PENDENTE': return 'bg-slate-100 text-slate-600 border-slate-200';
      case 'AGUARDANDO_PAGAMENTO': return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'PAGO': return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'ACEITO': return 'bg-indigo-50 text-indigo-700 border-indigo-200';
      case 'CONCLUIDO': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="p-8 bg-slate-50 min-h-screen font-sans">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Gerenciamento de Pedidos</h1>
          
          <div className="flex bg-white p-1 rounded-xl shadow-sm border border-slate-200 overflow-x-auto max-w-full">
            {['TODOS', 'PENDENTE', 'AGUARDANDO_PAGAMENTO', 'PAGO', 'ACEITO', 'CONCLUIDO'].map((s) => (
              <button
                key={s}
                onClick={() => setFiltro(s)}
                className={`px-4 py-2 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
                  filtro === s ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-500 hover:bg-slate-50'
                }`}
              >
                {s.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase">ID / Cliente</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase">Serviço</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase">Rota</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase">Data</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase text-right">Valor</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr><td colSpan="6" className="px-6 py-12 text-center text-slate-400">Carregando viagens...</td></tr>
              ) : pedidosFiltrados.length === 0 ? (
                <tr><td colSpan="6" className="px-6 py-12 text-center text-slate-400">Nenhum pedido encontrado neste status.</td></tr>
              ) : pedidosFiltrados.map((pedido) => (
                <tr key={pedido.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="text-sm font-bold text-slate-900">#{pedido.id}</div>
                    <div className="text-xs text-slate-500">{pedido.cliente?.nome}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm font-medium text-slate-700">{pedido.servico?.nome}</span>
                  </td>
                  <td className="px-6 py-4 text-xs text-slate-600">
                    <div className="font-semibold">De: <span className="font-normal">{pedido.origem}</span></div>
                    <div className="font-semibold">Para: <span className="font-normal">{pedido.destino}</span></div>
                  </td>
                  <td className="px-6 py-4 text-xs text-slate-600">
                    {new Date(pedido.data_servico).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })}
                  </td>
                  <td className="px-6 py-4 text-sm font-bold text-slate-900 text-right">R$ {pedido.valor}</td>
                  <td className="px-6 py-4 text-center">
                    <span className={`px-3 py-1 rounded-full text-[10px] font-bold border ${getStatusStyle(pedido.status)}`}>
                      {pedido.status.replace('_', ' ')}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Pedidos;