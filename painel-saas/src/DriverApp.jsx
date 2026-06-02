import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import { API_URL } from './App';

export default function DriverApp() {
  const [isOnline, setIsOnline] = useState(false);
  const [isBrowserOnline, setIsBrowserOnline] = useState(navigator.onLine);
  const [activeTab, setActiveTab] = useState('agenda');
  const [showNewOrderModal, setShowNewOrderModal] = useState(false);
  const [mockOrder, setMockOrder] = useState(null);
  const ws = useRef(null);

  const [myOrders, setMyOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  const [activeHistory, setActiveHistory] = useState({ faturamento: 'R$ 0,00', corridas: 0, km: '0 km', lista: [] });
  const [historyPeriod, setHistoryPeriod] = useState('semanal');

  const [driverProfile, setDriverProfile] = useState({
    id: 1, // ID para identificação no WebSocket
    nome: 'João Silva',
    email: 'joao.silva@centraltransfers.com',
    telefone: '(54) 99999-1234',
    veiculo: 'Renault Master - Preta',
    placa: 'BRA2E19',
    nivel: 'PRATA',
    pontos: 1250,
    foto: null
  });

  const [passwordForm, setPasswordForm] = useState({
    senhaAtual: '',
    novaSenha: '',
    confirmarSenha: ''
  });

  const [notificationAudio] = useState(new Audio('https://assets.mixkit.co/active_storage/sfx/1357/1357-preview.mp3'));
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
      console.error("Erro ao carregar ordens", err);
      setMyOrders(getMockOrders());
    } finally {
      setLoading(false);
    }
  };

  const getMockOrders = () => [
    {
      id: "TRF-7812",
      origem: "Aeroporto Salgado Filho (POA)",
      destino: "Hotel Master, Gramado",
      data_servico: new Date().toISOString(),
      status: "ACEITO",
      valor: 280.00,
      observacoes: "Passageiros com 3 malas grandes. Aguardar no desembarque."
    },
    {
      id: "TRF-7901",
      origem: "Rua Coberta, Gramado",
      destino: "Snowland, Gramado",
      data_servico: new Date(Date.now() + 3600000).toISOString(),
      status: "PENDENTE",
      valor: 65.00
    }
  ];

  const loadHistory = async () => {
    try {
      const res = await axios.get(`${API_URL}/pagamentos/stats?period=${historyPeriod}`, { 
        headers: getAuthHeader() 
      });
      setActiveHistory(res.data);
    } catch (err) {
      console.error("Erro ao carregar histórico real", err);
    }
  };

  const openInMaps = (origem, destino) => {
    const url = `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(origem)}&destination=${encodeURIComponent(destino)}&travelmode=driving`;
    window.open(url, '_blank');
  };

  const updateStatus = async (pedidoId, newStatus) => {
    try {
      await axios.put(`${API_URL}/pedidos/${pedidoId}/status`, { status: newStatus }, { headers: getAuthHeader() });
      loadMyOrders();
    } catch (err) {
      setMyOrders(prev => prev.map(o => o.id === pedidoId ? { ...o, status: newStatus } : o));
    }
  };

  const handleCloseModal = () => {
    notificationAudio.pause();
    notificationAudio.currentTime = 0;
    if ("vibrate" in navigator) navigator.vibrate(0);
    setShowNewOrderModal(false);
  };

  const handleFotoUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setDriverProfile(prev => ({ ...prev, foto: reader.result }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handlePasswordChange = (e) => {
    e.preventDefault();
    if (passwordForm.novaSenha !== passwordForm.confirmarSenha) {
      alert("A nova senha e a confirmação não batem!");
      return;
    }
    alert("Senha alterada com sucesso!");
    setPasswordForm({ senhaAtual: '', novaSenha: '', confirmarSenha: '' });
  };

  useEffect(() => {
    if (isOnline) {
      // Conectar ao WebSocket quando o motorista ficar ONLINE
      // Converte http/https para ws/wss e troca o prefixo /api por /ws
      const socketUrl = API_URL.replace(/^http/, 'ws').replace('/api', '/ws') + `/${driverProfile.id}`;
      console.log(`📡 Tentando conectar ao WebSocket: ${socketUrl}`);
      
      ws.current = new WebSocket(socketUrl);

      ws.current.onopen = () => {
        console.log("%c✅ WebSocket Conectado! O motorista está pronto para receber viagens.", "color: #10b981; font-weight: bold;");
      };

      ws.current.onclose = (e) => {
        console.log(`%c🛑 WebSocket Desconectado (Código: ${e.code}). Razão: ${e.reason || 'Desconexão manual'}`, "color: #ef4444;");
      };

      ws.current.onerror = (err) => {
        console.error("❌ Erro no WebSocket:", err);
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("📩 Nova mensagem recebida via WS:", data);
          if (data.type === 'NEW_ORDER') {
            setMockOrder({ 
              id: data.pedido_id, 
              origem: data.origem || "Novo Pedido", 
              destino: data.destino || "Ver Detalhes", 
              valor: data.valor 
            });
            setShowNewOrderModal(true);
            notificationAudio.play().catch(e => console.log("Interação de áudio pendente:", e));
            if ("vibrate" in navigator) navigator.vibrate([500, 200, 500, 200, 500]);
          }
        } catch (err) {
          console.error("Erro ao processar mensagem do servidor:", err);
        }
      };

      return () => { if (ws.current) ws.current.close(); handleCloseModal(); };
    } else {
      if (ws.current) ws.current.close();
      handleCloseModal();
    }
  }, [isOnline]);

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

  useEffect(() => { loadMyOrders(); }, []);
  useEffect(() => { loadHistory(); }, [historyPeriod]);

  return (
    <div style={styles.container}>
      <style>{`
        body { 
          background-color: #0B0F19;
          overscroll-behavior-y: contain; /* Impede pull-to-refresh acidental */
          user-select: none; /* Deixa com cara de app nativo */
          -webkit-tap-highlight-color: transparent;
        }
        input, textarea { user-select: auto !important; } /* Permite digitar */
      `}</style>

      {!isBrowserOnline && (
        <div style={styles.offlineBanner}>
          ⚠️ DISPOSITIVO OFFLINE. EXIBINDO DADOS LOCAIS.
        </div>
      )}
      
      <header style={{...styles.header, backgroundColor: isOnline ? (isBrowserOnline ? '#2563EB' : '#f59e0b') : '#1E293B'}}>
        <div style={styles.userInfo}>
          {driverProfile.foto ? (
            <img src={driverProfile.foto} alt="Perfil" style={styles.avatarImg} />
          ) : (
            <div style={styles.miniAvatar}>JS</div>
          )}
          <div>
            <span style={{color: '#fff', fontWeight: 'bold', display: 'block'}}>Olá, {driverProfile.nome}</span>
            <span style={styles.badgeNivel}>Categoria {driverProfile.nivel}</span>
          </div>
        </div>
        <div style={styles.statusToggle} onClick={() => setIsOnline(!isOnline)}>
          <div style={{...styles.toggleCircle, left: isOnline ? '40px' : '4px', background: isOnline ? '#fff' : '#94A3B8'}} />
          <span style={styles.statusText}>{isOnline ? 'ONLINE' : 'OFFLINE'}</span>
        </div>
      </header>

      <nav style={styles.tabs}>
        <button onClick={() => setActiveTab('agenda')} style={activeTab === 'agenda' ? styles.tabActive : styles.tab}>📅 Agenda</button>
        <button onClick={() => setActiveTab('historico')} style={activeTab === 'historico' ? styles.tabActive : styles.tab}>📈 Ganhos</button>
        <button onClick={() => setActiveTab('perfil')} style={activeTab === 'perfil' ? styles.tabActive : styles.tab}>👤 Perfil</button>
      </nav>

      <div style={styles.content}>
        {activeTab === 'agenda' && (
          <div>
            <div style={styles.mapPlaceholder}>
              <div style={{...styles.mapGradient, background: 'radial-gradient(circle, transparent 30%, #0B0F19 100%)'}} />
              <div style={styles.mapOverlay}>
                <div style={styles.locationPulse} />
                <p style={{fontSize: '13px', color: '#fff', fontWeight: 'bold'}}>{isOnline ? 'Rastreando localização ativa...' : 'Fique online para receber chamadas'}</p>
              </div>
            </div>

            <div style={styles.list}>
              <h3 style={styles.sectionTitle}>Suas Atividades Programadas</h3>
              {myOrders.map(order => (
                <div key={order.id} style={styles.card}>
                  <div style={styles.cardHeader}>
                    <div style={styles.orderType}>PREMIUM TRANSFER</div>
                    <span style={styles.timeTag}>⏰ {new Date(order.data_servico).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                    <span style={styles.priceTag}>R$ {Number(order.valor).toFixed(2)}</span>
                  </div>
                  <div style={styles.route}>
                    <div style={styles.dotLine}>
                      <div style={styles.dot} />
                      <div style={styles.line} />
                      <div style={styles.dotSquare} />
                    </div>
                    <div style={styles.routeDetails}>
                      <p style={styles.address}><strong>Origem:</strong> {order.origem}</p>
                      <p style={styles.address}><strong>Destino:</strong> {order.destino}</p>
                    </div>
                  </div>
                  {order.observacoes && (
                    <div style={styles.obsCard}>{order.observacoes}</div>
                  )}
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={() => openInMaps(order.origem, order.destino)} style={styles.btnSecondary}>📍 NAVEGAR</button>
                    {order.status !== 'CONCLUIDO' ? (
                      <button onClick={() => updateStatus(order.id, 'CONCLUIDO')} style={styles.btnAction}>CONCLUIR VIAGEM</button>
                    ) : (
                      <button disabled style={{...styles.btnAction, background: '#10b981'}}>✓ FINALIZADO</button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'historico' && (
          <div style={{padding: '0 15px'}}>
            <div style={styles.periodFilterContainer}>
              <button onClick={() => setHistoryPeriod('semanal')} style={historyPeriod === 'semanal' ? styles.btnFilterActive : styles.btnFilter}>Semanal</button>
              <button onClick={() => setHistoryPeriod('mensal')} style={historyPeriod === 'mensal' ? styles.btnFilterActive : styles.btnFilter}>Mensal</button>
              <button onClick={() => setHistoryPeriod('anual')} style={historyPeriod === 'anual' ? styles.btnFilterActive : styles.btnFilter}>Anual</button>
            </div>

            <div style={styles.earningsCard}>
              <span style={styles.earningsLabel}>Faturamento Bruto ({historyPeriod})</span>
              <h2 style={styles.earningsValue}>{activeHistory.faturamento}</h2>
              <div style={{...styles.statsRow, color: '#F1F5F9'}}>
                <span>🚗 {activeHistory.corridas} viagens</span>
                <span>🛣️ {activeHistory.km}</span>
              </div>
            </div>

            {/* Gráfico de Evolução Financeira */}
            <div style={styles.chartBox}>
              <h4 style={{color: '#94a3b8', margin: '0 0 15px 0', fontSize: '11px', fontWeight: '700', letterSpacing: '1px'}}>DESEMPENHO FINANCEIRO</h4>
              <div style={{height: '180px', width: '100%'}}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={[...activeHistory.lista].reverse()}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                    <XAxis 
                      dataKey="data" 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{fill: '#64748b', fontSize: 10}} 
                    />
                    <YAxis hide />
                    <Tooltip 
                      contentStyle={{ background: '#111827', border: '1px solid #1e293b', borderRadius: '12px', fontSize: '12px' }}
                      itemStyle={{ color: '#10b981' }}
                      labelStyle={{ color: '#7c3aed', fontWeight: 'bold' }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="valor" 
                      stroke="#2563EB" 
                      strokeWidth={3} 
                      dot={{ r: 4, fill: '#2563EB', strokeWidth: 2, stroke: '#0B0F19' }} 
                      activeDot={{ r: 6, strokeWidth: 0 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <h4 style={{color: '#94a3b8', margin: '15px 0 10px'}}>Extrato de Repasses</h4>
            {activeHistory.lista.map(item => (
              <div key={item.id} style={styles.historyItem}>
                <div>
                  <span style={{fontSize: '11px', color: '#2563EB', fontWeight: 'bold'}}>{item.data}</span>
                  <p style={{margin: '3px 0 0', fontSize: '14px', fontWeight: '500'}}>{item.rota}</p>
                </div>
                <div style={{textAlign: 'right'}}>
                  <span style={{color: '#fff', fontWeight: 'bold'}}>R$ {item.valor.toFixed(2)}</span>
                  <span style={{display: 'block', fontSize: '10px', color: '#94a3b8'}}>{item.status}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'perfil' && (
          <div style={{padding: '0 15px'}}>
            <div style={styles.profileBox}>
              <div style={styles.photoUploadContainer}>
                <div style={styles.bigAvatarContainer}>
                  {driverProfile.foto ? (
                    <img src={driverProfile.foto} alt="Foto Motorista" style={styles.bigAvatar} />
                  ) : (
                    <div style={styles.bigAvatarPlaceholder}>SEM FOTO</div>
                  )}
                </div>
                <label style={styles.lblUpload}>
                  📷 Carregar Nova Foto
                  <input type="file" accept="image/*" onChange={handleFotoUpload} style={{display: 'none'}} />
                </label>
              </div>

              <div style={styles.detailsGrid}>
                <div style={styles.detailField}>
                  <span style={styles.detailFieldLabel}>NOME COMPLETO</span>
                  <p style={{margin: '2px 0 0', fontSize: '14px'}}>{driverProfile.nome}</p>
                </div>
                <div style={styles.detailField}>
                  <span style={styles.detailFieldLabel}>EMAIL CORPORATIVO</span>
                  <p style={{margin: '2px 0 0', fontSize: '14px'}}>{driverProfile.email}</p>
                </div>
                <div style={styles.detailField}>
                  <span style={styles.detailFieldLabel}>WHATSAPP / TELEFONE</span>
                  <p style={{margin: '2px 0 0', fontSize: '14px'}}>{driverProfile.telefone}</p>
                </div>
                <div style={styles.detailField}>
                  <span style={styles.detailFieldLabel}>VEÍCULO CADASTRADO</span>
                  <p style={{margin: '2px 0 0', fontSize: '14px'}}>{driverProfile.veiculo}</p>
                </div>
                <div style={styles.detailField}>
                  <span style={styles.detailFieldLabel}>PLACA MERCOSUL</span>
                  <p style={{margin: '2px 0 0', fontSize: '14px', color: '#fbbf24', fontWeight: 'bold'}}>{driverProfile.placa}</p>
                </div>
              </div>
            </div>

            <div style={styles.profileBox}>
              <h4 style={{margin: '0 0 15px 0', color: '#2563EB'}}>🔐 Segurança</h4>
              <form onSubmit={handlePasswordChange} style={styles.passwordForm}>
                <div style={styles.inputWrapper}>
                  <label style={{fontSize: '11px', color: '#64748b'}}>Senha Atual</label>
                  <input type="password" required value={passwordForm.senhaAtual} onChange={e => setPasswordForm({...passwordForm, senhaAtual: e.target.value})} style={styles.inputStyle} placeholder="••••••••" />
                </div>
                <div style={styles.inputWrapper}>
                  <label style={{fontSize: '11px', color: '#64748b'}}>Nova Senha</label>
                  <input type="password" required value={passwordForm.novaSenha} onChange={e => setPasswordForm({...passwordForm, novaSenha: e.target.value})} style={styles.inputStyle} placeholder="Mínimo 6 dígitos" />
                </div>
                <div style={styles.inputWrapper}>
                  <label style={{fontSize: '11px', color: '#64748b'}}>Confirmar Nova Senha</label>
                  <input type="password" required value={passwordForm.confirmarSenha} onChange={e => setPasswordForm({...passwordForm, confirmarSenha: e.target.value})} style={styles.inputStyle} placeholder="Repita a nova senha" />
                </div>
                <button type="submit" style={styles.btnSavePassword}>ATUALIZAR CREDENCIAIS</button>
              </form>
            </div>
          </div>
        )}
      </div>

      {showNewOrderModal && (
        <div style={styles.modalOverlay}>
          <div style={styles.requestCard}>
            <h3 style={{margin: '0 0 10px 0', color: '#000'}}>⚠️ Viagem Disponível!</h3>
            <p style={{margin: '5px 0', color: '#334155'}}><strong>De:</strong> {mockOrder?.origem}</p>
            <p style={{margin: '5px 0', color: '#334155'}}><strong>Para:</strong> {mockOrder?.destino}</p>
            <div style={styles.modalPrice}>R$ {mockOrder?.valor.toFixed(2)}</div>
            <div style={styles.modalButtons}>
              <button onClick={handleCloseModal} style={styles.btnReject}>Ignorar</button>
              <button onClick={() => { handleCloseModal(); updateStatus(mockOrder.id, 'ACEITO'); }} style={styles.btnAccept}>ACEITAR</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { 
    background: '#0B0F19', 
    minHeight: '100vh', 
    paddingBottom: 'calc(40px + env(safe-area-inset-bottom))', 
    fontFamily: '"Inter", sans-serif', 
    color: '#fff' 
  },
  offlineBanner: { background: '#ef4444', color: '#fff', textAlign: 'center', fontSize: '12px', padding: '8px', fontWeight: 'bold' },
  header: { 
    padding: 'calc(env(safe-area-inset-top) + 20px) 20px 20px', 
    display: 'flex', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    transition: '0.3s' 
  },
  userInfo: { display: 'flex', alignItems: 'center', gap: '12px' },
  miniAvatar: { width: '38px', height: '38px', background: '#2563EB', borderRadius: '50%', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '14px', fontWeight: 'bold' },
  avatarImg: { width: '38px', height: '38px', borderRadius: '50%', objectFit: 'cover', border: '2px solid #2563EB' },
  badgeNivel: { fontSize: '10px', background: 'rgba(255,255,255,0.15)', padding: '2px 6px', borderRadius: '4px', marginTop: '3px', display: 'inline-block', fontWeight: 'bold' },
  statusToggle: { width: '70px', height: '32px', background: 'rgba(0,0,0,0.3)', borderRadius: '20px', position: 'relative', cursor: 'pointer', border: '1px solid rgba(255,255,255,0.1)' },
  toggleCircle: { width: '24px', height: '24px', background: '#fff', borderRadius: '50%', position: 'absolute', top: '4px', transition: '0.3s' },
  statusText: { position: 'absolute', fontSize: '9px', fontWeight: 'bold', top: '10px', right: '8px', color: '#fff' },
  tabs: { display: 'flex', gap: '5px', padding: '15px 15px 5px', background: '#0B0F19' },
  tab: { flex: 1, padding: '12px 5px', borderRadius: '10px', border: 'none', background: 'transparent', color: '#94a3b8', fontSize: '13px', cursor: 'pointer' },
  tabActive: { flex: 1, padding: '12px 5px', borderRadius: '10px', border: 'none', background: '#1E293B', color: '#2563EB', fontWeight: 'bold', fontSize: '13px' },
  content: { paddingTop: '15px' },
  sectionTitle: { fontSize: '15px', color: '#94a3b8', margin: '0 0 15px 20px', fontWeight: '600' },
  mapPlaceholder: { height: '140px', background: '#1E293B', margin: '0 15px 20px', borderRadius: '20px', position: 'relative', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.05)' },
  mapGradient: { position: 'absolute', width: '100%', height: '100%', background: 'radial-gradient(circle, transparent 30%, #0a0f1e 100%)' },
  mapOverlay: { position: 'absolute', width: '100%', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' },
  locationPulse: { width: '12px', height: '12px', background: '#2563EB', borderRadius: '50%', boxShadow: '0 0 0 10px rgba(37, 99, 235, 0.3)', marginBottom: '10px' },
  card: { background: '#1E293B', margin: '0 15px 15px', padding: '18px', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.05)' },
  cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' },
  orderType: { fontSize: '10px', fontWeight: 'bold', color: '#2563EB', background: 'rgba(37, 99, 235, 0.1)', padding: '4px 8px', borderRadius: '5px' },
  timeTag: { background: '#0B0F19', padding: '4px 8px', borderRadius: '6px', fontSize: '11px', color: '#94A3B8' },
  priceTag: { color: '#fff', fontWeight: '900', fontSize: '18px' },
  route: { display: 'flex', gap: '12px', marginBottom: '15px' },
  dotLine: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '3px', paddingTop: '4px' },
  dot: { width: '7px', height: '7px', background: '#F1F5F9', borderRadius: '50%' },
  line: { width: '1px', height: '25px', background: '#334155' },
  dotSquare: { width: '7px', height: '7px', background: '#2563EB' },
  address: { fontSize: '12px', margin: '0 0 6px 0', color: '#cbd5e1' },
  obsCard: { background: '#0B0F19', padding: '10px', borderRadius: '8px', fontSize: '12px', marginBottom: '15px', color: '#94a3b8', borderLeft: '3px solid #2563EB' },
  btnAction: { flex: 1, padding: '12px', borderRadius: '10px', border: 'none', background: '#2563EB', color: '#fff', fontWeight: 'bold', fontSize: '13px', cursor: 'pointer' },
  btnSecondary: { padding: '12px 20px', borderRadius: '10px', border: '1px solid #334155', background: 'transparent', color: '#cbd5e1', fontWeight: '500', fontSize: '13px', cursor: 'pointer' },
  periodFilterContainer: { display: 'flex', background: '#111827', padding: '5px', borderRadius: '12px', marginBottom: '15px', border: '1px solid #1e293b' },
  btnFilter: { flex: 1, background: 'transparent', border: 'none', color: '#64748b', padding: '8px', borderRadius: '8px', cursor: 'pointer', fontSize: '12px' },
  btnFilterActive: { flex: 1, background: '#7c3aed', border: 'none', color: '#fff', padding: '8px', borderRadius: '8px', fontWeight: 'bold', fontSize: '12px' },
  earningsCard: { padding: '20px', background: 'linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%)', borderRadius: '20px', textAlign: 'center', marginBottom: '20px', border: '1px solid #1e293b' },
  earningsValue: { fontSize: '32px', margin: '8px 0', color: '#10b981', fontWeight: 'bold' },
  earningsLabel: { color: '#64748b', fontSize: '13px' },
  statsRow: { display: 'flex', justifyContent: 'center', gap: '20px', fontSize: '12px', color: '#94a3b8' },
  historyItem: { background: '#111827', padding: '15px', borderRadius: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', border: '1px solid #1e293b' },
  chartBox: { background: '#111827', padding: '20px', borderRadius: '20px', marginBottom: '20px', border: '1px solid #1e293b' },
  profileBox: { background: '#111827', padding: '20px', borderRadius: '20px', marginBottom: '20px', border: '1px solid #1e293b' },
  photoUploadContainer: { display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '20px' },
  bigAvatarContainer: { width: '80px', height: '80px', borderRadius: '50%', background: '#1e293b', overflow: 'hidden', display: 'flex', justifyContent: 'center', alignItems: 'center', border: '3px solid #7c3aed', marginBottom: '10px' },
  bigAvatar: { width: '100%', height: '100%', objectFit: 'cover' },
  bigAvatarPlaceholder: { fontSize: '11px', color: '#64748b', fontWeight: 'bold' },
  lblUpload: { fontSize: '12px', color: '#a78bfa', cursor: 'pointer', fontWeight: '500' },
  detailsGrid: { display: 'flex', flexDirection: 'column', gap: '12px' },
  detailField: { borderBottom: '1px solid #1e293b', paddingBottom: '8px' },
  detailFieldLabel: { display: 'block', fontSize: '10px', color: '#64748b', fontWeight: 'bold', marginBottom: '2px' },
  passwordForm: { display: 'flex', flexDirection: 'column', gap: '12px' },
  inputWrapper: { display: 'flex', flexDirection: 'column', gap: '4px' },
  inputStyle: { background: '#0a0f1e', border: '1px solid #1e293b', padding: '10px', borderRadius: '8px', color: '#fff', fontSize: '13px' },
  btnSavePassword: { background: 'transparent', border: '1px dashed #7c3aed', color: '#a78bfa', padding: '12px', borderRadius: '8px', fontWeight: 'bold', fontSize: '12px', cursor: 'pointer', marginTop: '5px' },
  modalOverlay: { position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.85)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 100, padding: '25px' },
  requestCard: { width: '100%', background: '#fff', borderRadius: '24px', padding: '25px', textAlign: 'center' },
  modalPrice: { fontSize: '36px', fontWeight: 'bold', color: '#7c3aed', margin: '15px 0' },
  modalButtons: { display: 'flex', gap: '10px' },
  btnAccept: { flex: 2, padding: '15px', borderRadius: '12px', border: 'none', background: '#10b981', color: '#fff', fontWeight: 'bold', fontSize: '15px' },
  btnReject: { flex: 1, padding: '15px', borderRadius: '12px', border: 'none', background: '#e2e8f0', color: '#475569', fontWeight: 'bold' }
};