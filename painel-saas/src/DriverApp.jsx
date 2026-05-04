import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

export default function DriverApp() {
  const [isOnline, setIsOnline] = useState(false);
  const [activeTab, setActiveTab] = useState('agenda'); // agenda, ganhos, perfil
  const [showNewOrderModal, setShowNewOrderModal] = useState(false);
  const [mockOrder, setMockOrder] = useState(null);

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

  useEffect(() => { loadMyOrders(); }, []);

  return (
    <div style={styles.container}>
      <header style={{...styles.header, backgroundColor: isOnline ? '#10b981' : '#64748b'}}>
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
                  <div style={{...styles.orderType, background: order.valor > 500 ? 'linear-gradient(90deg, #D4AF37, #C5A059)' : 'rgba(124,58,237,0.1)', color: order.valor > 500 ? '#fff' : '#7c3aed'}}>{order.valor > 500 ? '💎 PREMIUM' : 'TRANSFER PRIVATIVO'}</div>
                  <span style={styles.timeTag}>⏰ {new Date(order.data_servico).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                  <span style={styles.priceTag}>R$ {order.valor.toFixed(2)}</span>
                </div>
                <div style={styles.route}>
                  <div style={styles.dotLine}><div style={styles.dot} /><div style={styles.line} /><div style={styles.dotSquare} /></div>
                  <div style={styles.routeDetails}>
                    <p style={styles.address}><strong>Origem:</strong> {order.origem}</p>
                    <p style={styles.address}><strong>Destino:</strong> {order.destino}</p>
                  </div>
                </div>
                {order.observacoes && (
                  <div style={styles.obsCard}>
                    <span style={{fontSize: '10px', fontWeight: '800', color: '#94a3b8'}}>OBSERVAÇÕES DO CLIENTE</span>
                    <p style={{fontSize: '13px', margin: '5px 0 0', color: '#cbd5e1', lineHeight: '1.4'}}>{order.observacoes}</p>
                  </div>
                )}
                {/* Alerta de Adicionais para o Motorista */}
                {order.valor > 500 && (
                  <div style={styles.addonAlert}>
                    <span style={{fontSize: '12px'}}>🎁 <strong>ITENS EXTRAS:</strong></span>
                    <ul style={{margin: '5px 0 0 15px', padding: 0, fontSize: '12px', color: '#fbbf24'}}>
                      <li>Kit Boas-vindas (Vinho + Taças)</li>
                    </ul>
                  </div>
                )}
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button onClick={() => openInMaps(order.origem, order.destino)} style={styles.btnSecondary}>📍 VER ROTA</button>
                  <button onClick={() => updateStatus(order.id, 'CONCLUIDO')} style={styles.btnAction}>CONCLUIR</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal de Nova Chamada (Estilo Uber) */}
      {showNewOrderModal && (
        <div style={styles.modalOverlay}>
          <div style={styles.requestCard}>
            <div style={styles.pulseRing} />
            <h3>Nova Solicitação!</h3>
            <p><strong>{mockOrder.origem}</strong></p>
            <p>⬇️</p>
            <p><strong>{mockOrder.destino}</strong></p>
            <div style={styles.modalPrice}>R$ {mockOrder.valor.toFixed(2)}</div>
            <div style={styles.modalButtons}>
              <button onClick={handleCloseModal} style={styles.btnReject}>Recusar</button>
              <button onClick={() => {handleCloseModal(); setIsOnline(true)}} style={styles.btnAccept}>ACEITAR</button>
            </div>
          </div>
        </div>
      )}

      <footer style={styles.footerNav}>
        <div style={styles.navItem}>🏠</div>
        <div style={styles.navItem}>📊</div>
        <div style={styles.navItem}>👤</div>
      </footer>
    </div>
  );
}

const styles = {
  container: { background: '#0a0f1e', minHeight: '100vh', paddingBottom: '80px', fontFamily: '"Inter", sans-serif', color: '#fff' },
  header: { padding: '40px 20px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', transition: '0.3s' },
  mapPlaceholder: { height: '220px', background: '#1e293b', margin: '0 15px', borderRadius: '28px', position: 'relative', overflow: 'hidden', border: '1px solid #334155', boxShadow: '0 10px 30px rgba(0,0,0,0.3)' },
  mapGradient: { position: 'absolute', width: '100%', height: '100%', background: 'radial-gradient(circle at center, transparent 0%, rgba(10,15,30,0.4) 100%)' },
  mapOverlay: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' },
  locationPulse: { width: '14px', height: '14px', background: '#3b82f6', borderRadius: '50%', boxShadow: '0 0 0 15px rgba(59, 130, 246, 0.2)', marginBottom: '15px' },
  statusToggle: { width: '70px', height: '32px', background: 'rgba(255,255,255,0.2)', borderRadius: '20px', position: 'relative', cursor: 'pointer' },
  toggleCircle: { width: '24px', height: '24px', background: '#fff', borderRadius: '50%', position: 'absolute', top: '4px', transition: '0.3s' },
  statusText: { position: 'absolute', fontSize: '9px', fontWeight: 'bold', top: '10px', right: '8px', color: '#fff' },
  earningsCard: { margin: '20px', padding: '25px', background: 'linear-gradient(135deg, #4c1d95 0%, #1e1b4b 100%)', borderRadius: '24px', textAlign: 'center' },
  earningsValue: { fontSize: '36px', margin: '10px 0' },
  earningsLabel: { opacity: 0.7, fontSize: '14px' },
  statsRow: { display: 'flex', justifyContent: 'center', gap: '20px', fontSize: '12px', opacity: 0.8 },
  loyaltyBarContainer: { marginBottom: '15px', padding: '0 10px' },
  loyaltyHeader: { display: 'flex', justifyContent: 'space-between', fontSize: '11px', fontWeight: 'bold', marginBottom: '5px' },
  progressBg: { height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '10px', marginBottom: '5px' },
  progressFill: { height: '100%', background: '#10b981', borderRadius: '10px' },
  tabs: { display: 'flex', gap: '10px', padding: '0 20px', marginBottom: '20px' },
  tab: { flex: 1, padding: '10px', borderRadius: '12px', border: 'none', background: 'rgba(255,255,255,0.05)', color: '#fff' },
  tabActive: { flex: 1, padding: '10px', borderRadius: '12px', border: 'none', background: '#fff', color: '#0a0f1e', fontWeight: 'bold' },
  card: { background: '#161e31', margin: '0 15px 15px', padding: '20px', borderRadius: '24px', border: '1px solid rgba(255,255,255,0.05)', boxShadow: '0 4px 20px rgba(0,0,0,0.2)' },
  cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' },
  orderType: { fontSize: '10px', fontWeight: '800', color: '#7c3aed', background: 'rgba(124,58,237,0.1)', padding: '4px 8px', borderRadius: '6px' },
  timeTag: { background: '#334155', padding: '4px 10px', borderRadius: '8px', fontSize: '12px' },
  priceTag: { color: '#10b981', fontWeight: '900', fontSize: '18px' },
  route: { display: 'flex', gap: '15px', marginBottom: '20px' },
  dotLine: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', paddingTop: '5px' },
  dot: { width: '8px', height: '8px', background: '#10b981', borderRadius: '50%' },
  line: { width: '2px', height: '30px', background: '#334155' },
  dotSquare: { width: '8px', height: '8px', background: '#7c3aed' },
  address: { fontSize: '13px', margin: '0 0 10px 0', opacity: 0.9 },
  btnAction: { width: '100%', padding: '15px', borderRadius: '12px', border: 'none', background: '#7c3aed', color: '#fff', fontWeight: 'bold' },
  btnSecondary: { width: '100%', padding: '15px', borderRadius: '12px', border: '1px solid #7c3aed', background: 'transparent', color: '#7c3aed', fontWeight: 'bold' },
  obsCard: { background: 'rgba(255,255,255,0.05)', padding: '12px', borderRadius: '12px', marginBottom: '15px', border: '1px dashed rgba(255,255,255,0.1)' },
  addonAlert: { background: 'rgba(251, 191, 36, 0.1)', padding: '10px', borderRadius: '10px', marginBottom: '15px', borderLeft: '4px solid #fbbf24' },
  footerNav: { position: 'fixed', bottom: 0, width: '100%', height: '70px', background: '#1e293b', display: 'flex', justifyContent: 'space-around', alignItems: 'center', borderTop: '1px solid rgba(255,255,255,0.1)' },
  navItem: { fontSize: '24px', cursor: 'pointer' },
  modalOverlay: { position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.9)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 100, padding: '20px' },
  requestCard: { width: '100%', background: '#fff', color: '#000', borderRadius: '30px', padding: '30px', textAlign: 'center', position: 'relative' },
  modalPrice: { fontSize: '42px', fontWeight: '900', color: '#7c3aed', margin: '20px 0' },
  modalButtons: { display: 'flex', gap: '10px' },
  btnAccept: { flex: 2, padding: '20px', borderRadius: '15px', border: 'none', background: '#10b981', color: '#fff', fontWeight: 'bold', fontSize: '18px' },
  btnReject: { flex: 1, padding: '20px', borderRadius: '15px', border: 'none', background: '#f1f5f9', color: '#64748b', fontWeight: 'bold' },
  miniAvatar: { width: '32px', height: '32px', background: '#7c3aed', borderRadius: '50%', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '12px' },
  userInfo: { display: 'flex', alignItems: 'center', gap: '10px' }
};