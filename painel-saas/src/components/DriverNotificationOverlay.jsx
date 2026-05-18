import React from 'react';
import { useWebSocketNotifications } from '../hooks/useWebSocketNotifications';
import axios from 'axios'; // Assumindo o uso de axios para chamadas API

const DriverNotificationOverlay = ({ motoristaId }) => {
  const { novaNotificacao, limparNotificacao } = useWebSocketNotifications(motoristaId);

  if (!novaNotificacao) return null;

  // Efeito sonoro para garantir que o motorista ouça o pedido
  const tocarAlerta = () => {
    const audio = new Audio('/notification-alert.mp3'); // Certifique-se que o arquivo existe em /public
    audio.play().catch(e => console.log("Áudio bloqueado pelo navegador"));
  };

  // Tocar alerta quando uma nova notificação chegar
  React.useEffect(() => {
    if (novaNotificacao) {
      tocarAlerta();
      
      // Notificação nativa via Service Worker (mesmo com aba em segundo plano)
      navigator.serviceWorker.ready.then((registration) => {
        registration.showNotification('🚖 Novo Pedido Recebido', {
          body: novaNotificacao.mensagem,
          icon: '/icon-192x192.png',
        });
      });
    }
  }, [novaNotificacao]);

  const aceitarPedido = async () => {
    try {
      const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8001';
      // Chamada para o endpoint de aceite
      await axios.put(`${apiBase}/pedidos/${novaNotificacao.pedido_id}/aceitar`, {
        motorista_id: motoristaId
      });
      
      alert("Sucesso! O pedido agora é seu. Dirija com cuidado!");
      limparNotificacao();
    } catch (error) {
      // Tratamento de erro de concorrência (Status 400 ou 409)
      if (error.response && error.response.status === 400) {
        alert("Tarde demais! Outro motorista aceitou este pedido alguns milissegundos antes.");
      } else {
        alert("Ocorreu um erro ao aceitar o pedido. Verifique sua conexão.");
      }
      limparNotificacao();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl animate-bounce">
        <div className="text-center">
          <div className="bg-green-100 text-green-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">🚖</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Novo Pedido!</h2>
          <p className="text-gray-600 mb-4">{novaNotificacao.mensagem}</p>
          <div className="text-3xl font-black text-indigo-600 mb-6">
            R$ {novaNotificacao.valor}
          </div>
          
          <div className="flex flex-col gap-3">
            <button 
              onClick={aceitarPedido}
              className="bg-indigo-600 text-white font-bold py-4 rounded-xl hover:bg-indigo-700 transition"
            >
              ACEITAR AGORA
            </button>
            <button 
              onClick={limparNotificacao}
              className="text-gray-400 font-medium py-2"
            >
              Recusar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DriverNotificationOverlay;