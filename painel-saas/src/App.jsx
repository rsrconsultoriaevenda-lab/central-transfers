import React, { useState, useEffect } from 'react';

function Dashboard() {
  const [activeTab, setActiveTab] = useState('Geral');
  const [lastUpdate, setLastUpdate] = useState(new Date().toLocaleTimeString());

  // Simulação de tempo real (atualiza a cada 10 segundos)
  useEffect(() => {
    const timer = setInterval(() => {
      setLastUpdate(new Date().toLocaleTimeString());
    }, 10000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div style={styles.appContainer}>
      {/* SIDEBAR DISRUPTIVA */}
      <aside style={styles.sidebar}>
        <div style={styles.logoBadge}>🚐</div>
        <nav style={styles.iconMenu}>
          <button onClick={() => setActiveTab('Geral')} style={activeTab === 'Geral' ? styles.iconActive : styles.iconWrapper}>📊</button>
          <button onClick={() => setActiveTab('Frota')} style={activeTab === 'Frota' ? styles.iconActive : styles.iconWrapper}>🚍</button>
          <button onClick={() => setActiveTab('Preços')} style={activeTab === 'Preços' ? styles.iconActive : styles.iconWrapper}>💰</button>
          <button onClick={() => setActiveTab('Relatórios')} style={activeTab === 'Relatórios' ? styles.iconActive : styles.iconWrapper}>📄</button>
        </nav>
      </aside>

      <main style={styles.mainContent}>
        {/* HEADER COM STATUS TEMPO REAL */}
        <header style={styles.header}>
          <div>
            <h1 style={styles.greetingTitle}>Central Transfers <span style={styles.livePulse}>● LIVE</span></h1>
            <p style={styles.greetingSubtitle}>Última atualização: {lastUpdate}</p>
          </div>
          <div style={styles.headerControls}>
            <div style={styles.profileArea}>
              <div style={styles.avatar}>AD</div>
              <div>
                <p style={styles.adminName}>Admin Logística</p>
                <p style={styles.adminEmail}>Gramado, RS</p>
              </div>
            </div>
          </div>
        </header>

        {/* CONTEÚDO DINÂMICO BASEADO NA ABA */}
        {activeTab === 'Geral' && <OverviewView />}
        {activeTab === 'Frota' && <FleetView />}
        {activeTab === 'Preços' && <PricingView />}
        {activeTab === 'Relatórios' && <ReportsView />}
      </main>
    </div>
  );
}

// --- SUB-COMPONENTE: VISÃO GERAL ---
function OverviewView() {
  return (
    <div style={styles.grid}>
      <div style={styles.cardChromatic}>
        <p>Faturamento Diário</p>
        <h2>R$ 4.250,00</h2>
        <small>+18% que ontem</small>
      </div>
      <div style={styles.cardWhite}>
        <p style={{color: '#666'}}>Serviços Hoje</p>
        <h2 style={{color: '#333'}}>24</h2>
        <div style={styles.progressBar}><div style={{...styles.progressFill, width: '70%'}}></div></div>
      </div>
      <div style={styles.cardWhite}>
        <p style={{color: '#666'}}>Pagamentos Pendentes</p>
        <h2 style={{color: '#ef4444'}}>R$ 890,00</h2>
      </div>
      
      <div style={{gridColumn: 'span 3', ...styles.cardWhite}}>
        <h3 style={styles.cardTitle}>Próximos Transfers - Gramado/PoA</h3>
        <table style={styles.table}>
          <thead>
            <tr><th>Hora</th><th>Passageiro</th><th>Voo</th><th>Motorista</th><th>Status</th></tr>
          </thead>
          <tbody>
            <tr><td>14:30</td><td>Família Silva (4pax)</td><td>G3 1234</td><td>Ricardo</td><td><span style={styles.badge}>A Caminho</span></td></tr>
            <tr><td>15:00</td><td>Ana Souza (1pax)</td><td>AD 4567</td><td>Marcos</td><td><span style={styles.badgeWait}>Aguardando</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

// --- SUB-COMPONENTE: GESTÃO DE PREÇOS ---
function PricingView() {
  const [servicos, setServicos] = useState([
    { id: 1, nome: 'PoA x Gramado (Van)', valor: 250 },
    { id: 2, nome: 'PoA x Gramado (Sedan)', valor: 180 },
    { id: 3, nome: 'Tour Uva e Vinho', valor: 350 },
  ]);

  const updatePrice = (id, novoValor) => {
    setServicos(servicos.map(s => s.id === id ? {...s, valor: novoValor} : s));
  };

  return (
    <div style={styles.cardWhite}>
      <h3 style={styles.cardTitle}>Banco de Serviços e Valores</h3>
      <table style={styles.table}>
        <thead><tr><th>Serviço</th><th>Valor Base</th><th>Ação</th></tr></thead>
        <tbody>
          {servicos.map(s => (
            <tr key={s.id}>
              <td>{s.nome}</td>
              <td><strong>R$ {s.valor}</strong></td>
              <td>
                <button style={styles.btnSmall} onClick={() => updatePrice(s.id, s.valor + 10)}>+ R$10</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// --- ESTILOS (SaaS DISRUPTIVO) ---
const styles = {
  appContainer: { display: 'flex', minHeight: '100vh', backgroundColor: '#f4f7fe', fontFamily: '"Inter", sans-serif' },
  sidebar: { width: '90px', backgroundColor: '#fff', borderRight: '1px solid #eef2f8', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '30px 0' },
  logoBadge: { fontSize: '32px', marginBottom: '40px', filter: 'drop-shadow(0 4px 10px rgba(0,0,0,0.1))' },
  iconMenu: { display: 'flex', flexDirection: 'column', gap: '25px' },
  iconWrapper: { background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', padding: '15px', borderRadius: '15px', transition: '0.3s' },
  iconActive: { background: '#f3e8ff', border: 'none', fontSize: '24px', cursor: 'pointer', padding: '15px', borderRadius: '15px', color: '#7c3aed', boxShadow: '0 4px 12px rgba(124, 58, 237, 0.15)' },
  
  mainContent: { flex: 1, padding: '40px', overflowY: 'auto' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' },
  greetingTitle: { fontSize: '28px', fontWeight: '800', color: '#1e293b', margin: 0 },
  livePulse: { fontSize: '12px', color: '#10b981', verticalAlign: 'middle', marginLeft: '10px', animation: 'pulse 2s infinite' },
  greetingSubtitle: { color: '#64748b', fontSize: '14px' },
  
  grid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '25px' },
  cardChromatic: { background: 'linear-gradient(135deg, #7c3aed, #db2777)', padding: '25px', borderRadius: '24px', color: '#fff', boxShadow: '0 20px 40px rgba(124, 58, 237, 0.2)' },
  cardWhite: { backgroundColor: '#fff', padding: '25px', borderRadius: '24px', boxShadow: '0 10px 30px rgba(0,0,0,0.02)' },
  
  table: { width: '100%', borderCollapse: 'collapse', marginTop: '20px' },
  badge: { backgroundColor: '#dcfce7', color: '#166534', padding: '5px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold' },
  badgeWait: { backgroundColor: '#fef9c3', color: '#854d0e', padding: '5px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold' },
  btnSmall: { padding: '6px 12px', backgroundColor: '#f3e8ff', color: '#7c3aed', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' },
  
  progressBar: { height: '8px', backgroundColor: '#f1f5f9', borderRadius: '10px', marginTop: '15px' },
  progressFill: { height: '100%', backgroundColor: '#7c3aed', borderRadius: '10px' },
  
  profileArea: { display: 'flex', alignItems: 'center', gap: '12px', backgroundColor: '#fff', padding: '10px 20px', borderRadius: '16px' },
  avatar: { width: '40px', height: '40px', background: '#7c3aed', color: '#fff', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' },
  adminName: { margin: 0, fontSize: '14px', fontWeight: 'bold' },
  adminEmail: { margin: 0, fontSize: '12px', color: '#64748b' }
};

// Aba FleetView e ReportsView seguem a mesma lógica (podemos expandir se desejar)
function FleetView() { return <div style={styles.cardWhite}><h3>Monitoramento de Motoristas</h3><p>Lista de motoristas e status dos veículos...</p></div>; }
function ReportsView() { return <div style={styles.cardWhite}><h3>Relatórios Financeiros</h3><p>Gráficos de desempenho Mensal/Semanal...</p></div>; }

export default Dashboard;