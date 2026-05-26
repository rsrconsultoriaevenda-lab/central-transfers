import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

export default function DriverApp() {
  const [isOnline, setIsOnline] = useState(false);
  const [isBrowserOnline, setIsBrowserOnline] = useState(navigator.onLine);
  const [activeTab, setActiveTab] = useState('agenda'); // agenda, ganhos, perfil
  const [showNewOrderModal, setShowNewOrderModal] = useState(false);
  const [mockOrder, setMockOrder] = useState(null);
  const [deferredPrompt, setDeferredPrompt] = useState(null);

  const [myOrders, setMyOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  // Benefícios: Simulação de Nível e Fidelidade do Motorista
  const [driverStats] = useState({
    nivel: 'PRATA',
    pontos: 1250,
    viagensParaMeta: 7,
  });

  // Referência para o objeto de áudio para controlar play/pause
  const [notificationAudio] = useState(new Audio('https://assets.mixkit.co/active_storage/sfx/1357/1357-preview.mp3'));

  // Configura o áudio para repetir (loop)
  notificationAudio.loop = true;

  const getAuthHeader = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const loadMyOrders = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/pedidos`, { headers: getAuthHeader() });
      const orders = res.data.filter(p => p.status !== 'CANCELADO');
      
      setMyOrders(orders.length > 0 ? orders : getMockOrders());
    } catch (err) {
      console.error("Erro ao carregar ordens do motorista", err);
      // Fallback para mock caso a API falhe ou não tenha dados
      setMyOrders(getMockOrders());
    } finally {
      setLoading(false);
    }
  };

  const getMockOrders = () => [
    {
      id: "MOCK-001",
      origem: "Aeroporto Salgado Filho (POA)",
      destino: "Rua Coberta, Gramado",
      data_servico: new Date().toISOString(),
      status: "ACEITO",
      valor: 280.00
    },
    {
      id: "MOCK-002",
      origem: "Hotel Master Gramado",
      destino: "Snowland",
      data_servico: new Date(Date.now() + 3600000).toISOString(),
      status: "PENDENTE",
      valor: 65.00
    }
  ];

  const openInMaps = (origem, destino) => {
    const url = `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(origem)}&destination=${encodeURIComponent(destino)}&travelmode=driving`;
    window.open(url, '_blank');
  };

  const updateStatus = async (pedidoId, newStatus) => {
    try {
      await axios.put(`${API_URL}/pedidos/${pedidoId}/status`, { status: newStatus }, { headers: getAuthHeader() });
      loadMyOrders();
    } catch (err) {
      alert("Erro ao atualizar status");
    }
  };

  const handleCloseModal = () => {
    notificationAudio.pause();
    notificationAudio.currentTime = 0;
    // Para a vibração imediatamente
    if ("vibrate" in navigator) navigator.vibrate(0);
    setShowNewOrderModal(false);
  };

  // Simulação de nova chamada para teste de interface
  useEffect(() => {
    if (isOnline) {
      const timer = setTimeout(() => {
        setMockOrder({ id: 999, origem: "Rua Coberta", destino: "Snowland", valor: 45.00 });
        setShowNewOrderModal(true);
        
        // Inicia o som
        notificationAudio.play().catch(e => console.log("Aguardando interação para áudio"));
        
        // Inicia a vibração (Padrão: Vibrar 500ms, Pausa 200ms, repete...)
        if ("vibrate" in navigator) {
          navigator.vibrate([500, 200, 500, 200, 500, 200, 500, 200, 500, 200, 500]);
        }
      }, 5000);
      return () => {
        clearTimeout(timer);
        handleCloseModal();
      };
    } else {
      handleCloseModal();
    }
  }, [isOnline, notificationAudio]);

  // Monitorar a conexão real do dispositivo
  useEffect(() => {
    const handleOnline = () => setIsBrowserOnline(true);
    const handleOffline = () => setIsBrowserOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Função para assinar o Web Push
  const subscribeToPush = async () => {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: import.meta.env.VITE_VAPID_PUBLIC_KEY
      });

      await axios.post(`${API_URL}/notifications/subscribe`, subscription, {
        headers: getAuthHeader()
      });
      console.log("Motorista inscrito para notificações Push!");
    } catch (err) {
      console.error("Falha ao assinar Push:", err);
    }
  };

  useEffect(() => {
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission().then(perm => {
        if (perm === "granted") subscribeToPush();
      });
    }
  }, []);

  useEffect(() => {
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
    });
  }, []);

  const handleInstallApp = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      if (outcome === 'accepted') setDeferredPrompt(null);
    }
  };

  useEffect(() => { loadMyOrders(); }, []);

  return (
    <div style={styles.container}>
      {!isBrowserOnline && (
        <div style={{ background: '#ef4444', color: '#fff', textAlign: 'center', fontSize: '12px', padding: '8px', fontWeight: 'bold' }}>
          ⚠️ VOCÊ ESTÁ SEM INTERNET. EXIBINDO DADOS SALVOS.
        </div>
      )}
      <header style={{...styles.header, backgroundColor: isOnline ? (isBrowserOnline ? '#10b981' : '#f59e0b') : '#64748b'}}>
        <div style={styles.userInfo}>
          <div style={styles.miniAvatar}>JD</div>
          <span style={{color: '#fff', fontWeight: 'bold'}}>Olá, João</span>
        </div>
        <div style={styles.statusToggle} onClick={() => setIsOnline(!isOnline)}>
          <div style={{...styles.toggleCircle, left: isOnline ? '32px' : '4px'}} />
          <span style={styles.statusText}>{isOnline ? 'ONLINE' : 'OFFLINE'}</span>
        </div>
      </header>

      {/* Simulador de Mapa (Uber Experience) */}
      <div style={styles.mapPlaceholder}>
        <div style={styles.mapGradient} />
        <div style={styles.mapOverlay}>
          <div style={styles.locationPulse} />
          <p style={{fontSize: '12px', color: '#fff', fontWeight: 'bold', textShadow: '0 2px 4px rgba(0,0,0,0.5)'}}>Aguardando Chamadas...</p>
        </div>
      </div>

      {deferredPrompt && (
        <div style={{ padding: '10px 20px', background: '#4c1d95', textAlign: 'center' }}>
          <button onClick={handleInstallApp} style={{ background: '#fff', color: '#4c1d95', padding: '5px 15px', borderRadius: '8px', border: 'none', fontWeight: 'bold' }}>
            📥 INSTALAR APLICATIVO CENTRAL
          </button>
        </div>
      )}

      <div style={styles.earningsCard}>
        <span style={styles.earningsLabel}>Ganhos de hoje</span>
        <h2 style={styles.earningsValue}>R$ 482,50</h2>
        <div style={styles.statsRow}>
          <span>⏱️ 5.2h online</span>
          <span>🚗 8 viagens</span>
        </div>
      </div>

      <nav style={styles.tabs}>
        <button onClick={() => setActiveTab('agenda')} style={activeTab === 'agenda' ? styles.tabActive : styles.tab}>Agenda</button>
        <button onClick={() => setActiveTab('ganhos')} style={activeTab === 'ganhos' ? styles.tabActive : styles.tab}>Ganhos</button>
      </nav>

      <div style={styles.content}>
        {activeTab === 'agenda' && (
          <div style={styles.list}>
            {myOrders.map(order => (
              <div key={order.id} style={styles.card}>
                <div style={styles.cardHeader}>
                  <div style={{...styles.orderType, background: order.valor >