import React, { useEffect, useState } from 'react';

interface DriverStats {
  id: number;
  nome: string;
  plano: string;
  total_bruto: number;
  total_repasse: number;
  comissao_central: number;
  corridas: number;
}

const FinancialSummary: React.FC = () => {
  const [data, setData] = useState<DriverStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';
        
        const response = await fetch(`${apiUrl}/dashboard/admin/drivers-summary`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          if (response.status === 403) throw new Error('Acesso negado. Apenas administradores podem ver este relatório.');
          throw new Error('Falha ao carregar dados financeiros.');
        }

        const result = await response.json();
        setData(result);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
  };

  if (loading) return <div className="p-8 text-center text-gray-600">Carregando relatório financeiro...</div>;
  if (error) return <div className="p-8 text-red-500 text-center font-medium bg-red-50 rounded-lg m-6 border border-red-200">{error}</div>;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Fechamento de Caixa - Motoristas</h1>
        <button 
          onClick={() => window.print()} 
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors print:hidden"
        >
          Imprimir Relatório
        </button>
      </div>
      
      <div className="overflow-hidden bg-white rounded-xl shadow-sm border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Motorista</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Plano</th>
              <th className="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Corridas</th>
              <th className="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Total Bruto</th>
              <th className="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Repasse (Motorista)</th>
              <th className="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Comissão (Central)</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {data.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-10 text-center text-gray-500 italic">Nenhum dado financeiro disponível para o período.</td>
              </tr>
            ) : (
              data.map((driver) => (
                <tr key={driver.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">{driver.nome}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${driver.plano === 'MENSAL' ? 'bg-indigo-100 text-indigo-700' : 'bg-emerald-100 text-emerald-700'}`}>
                      {driver.plano}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-600">{driver.corridas}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">{formatCurrency(driver.total_bruto)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-emerald-600 font-bold">{formatCurrency(driver.total_repasse)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-blue-600 font-bold">{formatCurrency(driver.comissao_central)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      
      <div className="mt-4 text-xs text-gray-400 text-right">
        * Dados baseados apenas em pedidos com status 'CONCLUIDO'.
      </div>
    </div>
  );
};

export default FinancialSummary;