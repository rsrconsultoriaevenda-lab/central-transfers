import { useEffect, useState, useRef } from 'react';

export const useWebSocketNotifications = (motoristaId) => {
  const [novaNotificacao, setNovaNotificacao] = useState(null);
  const ws = useRef(null);
  const audioRef = useRef(new Audio('/assets/sounds/alert.mp3')); // Certifique-se de ter este arquivo

  const connect = () => {
    if (!motoristaId) return;

    // Converte a URL da API (http) para a URL do WebSocket (ws)
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8001';
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${apiBase.replace(/^https?/, wsProtocol)}/ws/notifications/${motoristaId}`;

    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('🔌 Conectado ao servidor de notificações');
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('📩 Nova notificação recebida:', data);

      if (data.type === 'NEW_ORDER') {
        setNovaNotificacao(data);
        // Toca o alerta sonoro (estilo Uber)
        audioRef.current.play().catch(e => console.error("Erro ao tocar áudio:", e));
      }

      if (data.type === 'ORDER_ACCEPTED') {
        setNovaNotificacao(prev => {
          // Se o pedido que foi aceito é o que está na tela, limpamos a notificação
          if (prev && prev.pedido_id === data.pedido_id) return null;
          return prev;
        });
      }
    };

    ws.current.onclose = () => {
      console.log('🔌 Conexão fechada. Tentando reconectar em 5s...');
      setTimeout(connect, 5000);
    };

    ws.current.onerror = (err) => {
      console.error('❌ Erro no WebSocket:', err);
      ws.current.close();
    };
  };

  useEffect(() => {
    connect();
    return () => {
      if (ws.current) ws.current.close();
    };
  }, [motoristaId]);

  const limparNotificacao = () => setNovaNotificacao(null);

  return { novaNotificacao, limparNotificacao };
};