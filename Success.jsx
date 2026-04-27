import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import axios from 'axios';

const Success = () => {
    const [searchParams] = useSearchParams();
    const [pedido, setPedido] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // O Mercado Pago anexa o 'external_reference' (que definimos como o ID do pedido) na URL de retorno
    const pedidoId = searchParams.get('external_reference');
    const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

    useEffect(() => {
        if (pedidoId) {
            axios.get(`${apiUrl}/pedidos/${pedidoId}`)
                .then(response => {
                    setPedido(response.data);
                    setLoading(false);
                })
                .catch(err => {
                    console.error("Erro ao buscar pedido:", err);
                    setError("Não foi possível carregar os detalhes do seu pedido.");
                    setLoading(false);
                });
        } else {
            setLoading(false);
            setError("Informações do pedido não encontradas na URL de retorno.");
        }
    }, [pedidoId, apiUrl]);

    if (loading) return (
        <div className="flex flex-col justify-center items-center h-screen bg-gray-50">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-gray-200 border-t-green-500 mb-4"></div>
            <p className="text-gray-600 font-medium animate-pulse">Confirmando seu pagamento...</p>
        </div>
    );
    
    if (error) return (
        <div className="max-w-md mx-auto mt-20 p-6 bg-red-50 text-red-700 rounded-lg text-center shadow">
            <p>{error}</p>
            <Link to="/" className="mt-4 inline-block text-red-900 underline">Voltar para a página inicial</Link>
        </div>
    );

    return (
        <div className="max-w-md mx-auto my-10 p-8 bg-white rounded-xl shadow-2xl border-t-8 border-green-500">
            <div className="text-center mb-8">
                <div className="inline-block p-4 bg-green-100 rounded-full text-green-500 text-5xl mb-4">
                    ✓
                </div>
                <h1 className="text-3xl font-extrabold text-gray-900">Sucesso!</h1>
                <p className="text-gray-500 mt-2">Seu pagamento foi processado e o pedido está confirmado.</p>
            </div>

            {pedido && (
                <div className="bg-gray-50 rounded-lg p-6 space-y-4">
                    <div className="flex justify-between border-b border-gray-200 pb-2">
                        <span className="text-gray-500">Pedido:</span>
                        <span className="font-mono font-bold">#{pedido.id}</span>
                    </div>
                    <div>
                        <p className="text-xs text-gray-400 uppercase font-bold">Trajeto</p>
                        <p className="text-gray-800 font-medium">{pedido.origem} → {pedido.destino}</p>
                    </div>
                    <div>
                        <p className="text-xs text-gray-400 uppercase font-bold">Data e Hora</p>
                        <p className="text-gray-800 font-medium">{new Date(pedido.data_servico).toLocaleString('pt-BR')}</p>
                    </div>
                    <div className="pt-4 text-center">
                        <span className="inline-block px-4 py-1 bg-green-500 text-white text-sm font-bold rounded-full uppercase">
                            Status: {pedido.status}
                        </span>
                    </div>
                </div>
            )}

            <div className="mt-10 text-center">
                <Link to="/" className="text-blue-600 hover:text-blue-800 font-semibold transition">
                    Ir para meus pedidos →
                </Link>
            </div>
        </div>
    );
};

export default Success;