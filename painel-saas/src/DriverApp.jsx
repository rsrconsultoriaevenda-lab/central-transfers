import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

export default function DriverApp() {
  const [isOnline, setIsOnline] = useState(false);
  const [isBrowserOnline, setIsBrowserOnline] = useState(navigator.onLine);
  const [activeTab, setActiveTab] = useState('agenda'); // agenda, historico, perfil
  const [showNewOrderModal, setShowNewOrderModal] = useState(false);
  const [mockOrder, setMockOrder] = useState(null);
  const [deferredPrompt, setDeferredPrompt] = useState(null);

  const [myOrders, setMyOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filtro do Histórico Financeiro
  const [historyPeriod, setHistoryPeriod] = useState('semanal'); // semanal, mensal, anual

  // Dados do Motorista (Perfil)
  const [driverProfile, setDriverProfile] = useState({
    nome: 'João Silva',
    email: 'joao.silva@centraltransfers.com',
    telefone: '(54) 99999-1234',
    veiculo: 'Renault Master - Preta',
    placa: 'BRA2E19',
    nivel: 'PRATA',
    pontos: 1250,
    foto: null
  });

  // Estado para Troca de Senha
  const [passwordForm, setPasswordForm] = useState({
    senhaAtual: '',
    novaSenha: '',
    confirmarSenha: ''
  });

  // Referência para o áudio de notificação
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
      console.error("Erro ao carregar ordens do motorista", err);
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

  const openInMaps = (origem, destino) => {
    const url = `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(origem)}&destination=${encodeURIComponent(destino)}&travelmode=driving`;
    window.open(url, '_blank');
  };

  const updateStatus = async (pedidoId, newStatus) => {
    try {
      await axios.put(`${API_URL}/pedidos/${pedidoId}/status`, { status: newStatus }, { headers: getAuthHeader() });
      loadMyOrders();
    } catch (err) {
      // Simulação local caso falte rota no back
      setMyOrders(prev => prev.map(o => o.id === pedidoId ? { ...o, status: newStatus } : o));
    }
  };

  const handleCloseModal = () => {
    notificationAudio.pause();
    notificationAudio.currentTime = 0;
    if ("vibrate" in navigator) navigator.vibrate(0);
    setShowNewOrderModal(false);
  };

  // Upload de Imagem simulado por Base64
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

  // Alteração de Senha simulada
  const handlePasswordChange = (e) => {
    e.preventDefault();
    if (passwordForm.novaSenha !== passwordForm.confirmarSenha) {
      alert("A nova senha e a confirmação não batem!");
      return;
    }
    alert("Senha alterada com sucesso na Central!");
    setPasswordForm({ senhaAtual: '', novaSenha: '', confirmarSenha: '' });
  };

  useEffect(() => {
    if (isOnline) {
      const timer = setTimeout(() => {
        setMockOrder({ id: "TRF-9912", origem: "Aeroporto POA", destino: "Wish Serrano, Gramado", valor: 295.00 });
        setShowNewOrderModal(true);
        notificationAudio.play().catch(() => console.log("Interação necessária para o áudio"));
        if ("vibrate" in navigator) navigator.vibrate([500, 200, 500, 200, 500]);
      }, 4000);
      return () => { clearTimeout(timer); handleCloseModal(); };
    } else {
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

  // Dados estáticos baseados no período do histórico selecionado
  const getHistoryData = () => {
    switch(historyPeriod) {
      case 'semanal': return { faturamento: 'R$ 1.940,00', corridas: 7, km: '840 km', lista: [
        { id: '1', data: '25 Mai', rota: 'POA ➔ Gramado', valor: 280.00, status: 'CONCLUÍDO' },
        { id: '2', data: '24 Mai', rota: 'Canela ➔ POA', valor: 290.00, status: 'CONCLUÍDO' },
        { id: '3', data: '22 Mai', rota: 'Gramado ➔ Nova Petrópolis', valor: 150.00, status: 'CONCLUÍDO' },
      ]};
      case 'mensal': return { faturamento: 'R$ 8.420,00', corridas: 32, km: '3.620 km', lista: [
        { id: 'M1', data: 'Mai/26', rota: 'Consolidado Semana 3', valor: 2240.00, status: 'PAGO' },
        { id: 'M2', data: 'Mai/26', rota: 'Consolidado Semana 2', valor: 2100.00, status: 'PAGO' },
        { id: 'M3', data: 'Mai/26', rota: 'Consolidado Semana 1', valor: 2080.00, status: 'PAGO' },
      ]};
      case 'anual': return { faturamento: 'R$ 96.380,00', corridas: 342, km: '41.200 km', lista: [
        { id: 'A1', data: '2026', rota: 'Acumulado Geral Temporada', valor: 96380.00, status: 'DECLARADO' }
      ]};
      default: return { faturamento: 'R$ 0,00', corridas: 0, km: '0 km', lista: [] };
    }
  };

  const activeHistory = getHistoryData();

  return (
    <div style={styles.container}>
      {!isBrowserOnline && (
        <div style={styles.offlineBanner}>
          ⚠️ DISPOSITIVO OFFLINE. EXIBINDO DADOS LOCAIS.
        </div>
      )}
      
      <header style={{...styles.header, backgroundColor: isOnline ? (isBrowserOnline ? '#10b981' : '#f59e0b') : '#1e293b'}}>
        <div style={styles.userInfo}>
          {driverProfile.foto ? (
            <img src={driverProfile.foto} alt="Perfil" style={styles.avatarImg} />
          ) : (
            <div style={styles.miniAvatar}>JS</div>
          )}
          <div>
            <span style={{color: '#fff', fontWeight: 'bold', display: 'block'}}>Olá, {driverProfile.nome}</span>
            <span style={styles.badgeNivel}>🏆 Categoria {driverProfile.nivel}</span>
          </div>
        </div>
        <div style={styles.statusToggle} onClick={() => setIsOnline(!isOnline)}>
          <div style={{...styles.toggleCircle, left: isOnline ? '32px' : '4px'}} />
          <span style={styles.statusText}>{isOnline ? 'ONLINE' : 'OFFLINE'}</span>
        </div>
      </header>

      {/* Navegação Principal por Abas Superior */}
      <nav style={styles.tabs}>
        <button onClick={() => setActiveTab('agenda')} style={activeTab === 'agenda' ? styles.tabActive : styles.tab}>📅 Agenda</button>
        <button onClick={() => setActiveTab('historico')} style={activeTab === 'historico' ? styles.tabActive : styles.tab}>📊 Histórico</button>
        <button onClick={() => setActiveTab('perfil')} style={activeTab === 'perfil' ? styles.tabActive : styles.tab}>👤 Minha Conta</button>
      </nav>

      <div style={styles.content}>
        {/* ABA 1: AGENDA DE CORRIDAS */}
        {activeTab === 'agenda' && (
          <div>
            <div style={styles.mapPlaceholder}>
              <div style={styles.mapGradient} />
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
                    <div style={styles.orderType}>TRANSFER PRIVATIVO</div>
                    <span style={styles.timeTag}>⏰ {new Date(order.data_servico).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                    <span style={styles.priceTag}>R$ {Number(order.valor).toFixed(2)}</span>
                  </div>
                  <div style={styles.route}>
                    <div style={styles.dotLine}><div style={styles.dot} /><div style={styles.line} /><div style={styles.dotSquare} /></div>
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
                      <button onClick={() => updateStatus(order.id, 'CONCLUIDO')} style={styles.btnAction}>CONCLUIR</button>
                    ) : (
                      <button disabled style={{...styles.btnAction, background: '#10b981'}}>✓ FINALIZADO</button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ABA 2: HISTÓRICO FINANCEIRO (SEMANAL, MENSAL, ANUAL) */}
        {activeTab === 'historico' && (
          <div style={{padding: '0 15px'}}>
            {/* Filtros de Período */}
            <div style={styles.periodFilterContainer}>
              <button onClick={() => setHistoryPeriod('semanal')} style={historyPeriod === 'semanal' ? styles.btnFilterActive : styles.btnFilter}>Semanal</button>
              <button onClick={() => setHistoryPeriod('mensal')} style={historyPeriod === 'mensal' ? styles.btnFilterActive : styles.btnFilter}>Mensal</button>
              <button onClick={() => setHistoryPeriod('anual')} style={historyPeriod === 'anual' ? styles.btnFilterActive : styles.btnFilter}>Anual</button>
            </div>

            {/* Quadro de Resumo de Ganhos */}
            <div style={styles.earningsCard}>
              <span style={styles.earningsLabel}>Faturamento Bruto ({historyPeriod})</span>
              <h2 style={styles.earningsValue}>{activeHistory.faturamento}</h2>
              <div style={styles.statsRow}>
                <span>🚗 {activeHistory.corridas} viagens</span>
                <span>🛣️ {activeHistory.km}</span>
              </div>
            </div>

            {/* Lista consolidada do histórico */}
            <h4 style={{color: '#94a3b8', margin: '15px 0 10px'}}>Extrato de Repasses</h4>
            {activeHistory.lista.map(item => (
              <div key={item.id} style={styles.historyItem}>
                <div>
                  <span style={{fontSize: '11px', color: '#7c3aed', fontWeight: 'bold'}}>{item.data}</span>
                  <p style={{margin: '3px 0 0', fontSize: '14px', fontWeight: '500'}}>{item.rota}</p>
                </div>
                <div style={{textAlign: 'right'}}>
                  <span style={{color: '#10b981', fontWeight: 'bold'}}>R$ {item.valor.toFixed(2)}</span>
                  <span style={{display: 'block', fontSize: '10px', color: '#94a3b8'}}>{item.status}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ABA 3: PERFIL, FOTO E SEGURANÇA */}
        {activeTab === 'perfil' && (
          <div style={{padding: '0 15px'}}>
            
            {/* Bloco de Informações do Motorista & Upload da Foto */}
            <div style={styles.profileBox}>
              <div style={styles.photoUploadContainer}>
                <div style={styles.bigAvatarContainer}>
                  {driverProfile.foto ? (
                    <img src={driverProfile.foto} alt="Foto Motorista" style={styles.bigAvatar} />
                  ) : (
                    <div style={styles.bigAvatarPlaceholder}>FOTO</div>
                  )}
                </div>
                <label style={styles.lblUpload}>
                  📷 Carregar Nova Foto
                  <input type="file" accept="image/*" onChange={handleFotoUpload} style={{display: 'none'}} />
                </label>
              </div>

              {/* Detalhes Técnicos e Cadastrais */}
              <div style={styles.detailsGrid}>
                <div style={styles.detailField}><label>NOME COMPLETO</label><p>{driverProfile.nome}</p></div>
                <div style={styles.detailField}><label>EMAIL CORPORATIVO</label><p>{driverProfile.email}</p></div>
                <div style={styles.detailField}><label>WHATSAPP/TELEFONE</label><p>{driverProfile.telefone}</p></div>
                <div style={styles.detailField}><label>VEÍCULO CADASTRADO</label><p>{driverProfile.veiculo}</p></div>
                <div style={styles.detailField}><label>PLACA ANTT / MERCOSUL</label><p style={{color: '#fbbf24'}}>{driverProfile.placa}</p></div>
              </div>
            </div>

            {/* Formulário de Troca de Senha */}
            <div style={styles.profileBox}>
              <h4 style={{margin: '0 0 15px 0', color: '#7c3aed'}}>🔐 Alteração de Segurança</h4>
              <form onSubmit={handlePasswordChange} style={styles.passwordForm}>
                <div style={styles.inputWrapper}>
                  <label>Senha Atual</label>
                  <input type="password" required value={passwordForm.senhaAtual} onChange={e => setPasswordForm({...passwordForm, senhaAtual: e.target.value})} style={styles.inputStyle} placeholder="••••••••" />
                </div>
                <div style={styles.inputWrapper}>
                  <label>Nova Senha</label>
                  <input type="password" required value={passwordForm.novaSenha} onChange={e => setPasswordForm({...passwordForm, novaSenha: e.target.value})} style={styles.inputStyle} placeholder="Mínimo 6 dígitos" />
                </div>
                <div style={styles.inputWrapper}>
                  <label>Confirmar Nova Senha</label>
                  <input type="password" required value={passwordForm.confirmarSenha} onChange={e => setPasswordForm({...passwordForm, confirmarSenha: e.target.value})} style={styles.inputStyle} placeholder="Repita a nova senha" />
                </div>
                <button type="submit" style={styles.btnSavePassword}>ATUALIZAR CREDENCIAIS</button>
              </form>
            </div>

          </div>
        )}
      </div>

      {/* MODAL DE ENTRADA DE NOVA SOLICITAÇÃO */}
      {showNewOrderModal && (
        <div style={styles.modalOverlay}>
          <div style={styles.requestCard}>
            <h3 style={{margin