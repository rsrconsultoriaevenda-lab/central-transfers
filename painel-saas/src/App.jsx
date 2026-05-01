import { useState } from 'react';

function Dashboard() {
  const [activeTab, setActiveTab] = useState('Home');

  return (
    <div style={styles.appContainer}>
      {/* Sidebar Lateral (Ícones) */}
      <aside style={styles.sidebar}>
        <div style={styles.logoBadge}>🚐</div>
        <div style={styles.iconMenu}>
          <div style={{...styles.iconWrapper, ...styles.iconActive}}>📊</div>
          <div style={styles.iconWrapper}>🚘</div>
          <div style={styles.iconWrapper}>📅</div>
          <div style={styles.iconWrapper}>⚙️</div>
        </div>
      </aside>

      {/* Área Principal */}
      <main style={styles.mainContent}>
        {/* Top Navigation */}
        <header style={styles.header}>
          <div style={styles.navTabs}>
            {['Visão Geral', 'Reservas', 'Motoristas', 'Relatórios'].map((tab) => (
              <button 
                key={tab} 
                style={tab === 'Visão Geral' ? styles.tabActive : styles.tab}
              >
                {tab}
              </button>
            ))}
          </div>
          <div style={styles.headerControls}>
            <input type="text" placeholder="Buscar passageiro ou rota..." style={styles.searchInput} />
            <div style={styles.profileArea}>
              <div style={styles.notification}>🔔</div>
              <div style={styles.avatar}>A</div>
              <div>
                <p style={styles.adminName}>Admin Logística</p>
                <p style={styles.adminEmail}>admin@centraltransfers.com</p>
              </div>
            </div>
          </div>
        </header>

        {/* Saudação */}
        <section style={styles.greetingSection}>
          <h1 style={styles.greetingTitle}>Bom dia, Admin</h1>
          <p style={styles.greetingSubtitle}>
            <span style={styles.alertIcon}>!</span> Você tem <strong>12 transfers pendentes</strong> hoje para Gramado!
          </p>
        </section>

        {/* Grid Principal */}
        <div style={styles.dashboardGrid}>
          
          {/* Coluna Esquerda (Gráfico e Status) */}
          <div style={styles.leftColumn}>
            
            {/* Gráfico Principal (Cromático Roxo) */}
            <div style={styles.cardLarge}>
              <div style={styles.cardHeader}>
                <h3 style={styles.cardTitle}>Volume de Passageiros</h3>
                <select style={styles.selectBox}>
                  <option>Esta Semana</option>
                </select>
              </div>
              <div style={styles.chartArea}>
                {/* Simulação de Gráfico de Barras */}
                <div style={styles.barGroup}>
                  <div style={{...styles.bar, height: '40%', ...styles.chromaticBar}}></div>
                  <div style={{...styles.bar, height: '70%', ...styles.chromaticBar}}></div>
                  <div style={{...styles.bar, height: '100%', ...styles.chromaticBar}}></div>
                  <div style={{...styles.bar, height: '60%', ...styles.chromaticBar}}></div>
                </div>
              </div>
            </div>

            {/* Atividades Recentes (Tabela) */}
            <div style={styles.cardMedium}>
              <h3 style={styles.cardTitle}>Últimas Reservas</h3>
              <table style={styles.table}>
                <thead>
                  <tr style={styles.tableHead}>
                    <th style={styles.th}>Rota</th>
                    <th style={styles.th}>Valor</th>
                    <th style={styles.th}>Veículo</th>
                    <th style={styles.th}>Data</th>
                    <th style={styles.th}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { rota: 'PoA ✈️ Gramado', valor: 'R$ 250', van: 'Van Executiva', data: '12 Ago', status: 'Confirmado' },
                    { rota: 'Gramado ✈️ PoA', valor: 'R$ 250', van: 'Spin', data: '13 Ago', status: 'Pendente' },
                    { rota: 'Tour Uva e Vinho', valor: 'R$ 320', van: 'Micro-ônibus', data: '15 Ago', status: 'Concluído' }
                  ].map((item, i) => (
                    <tr key={i} style={styles.tableRow}>
                      <td style={styles.td}><strong>{item.rota}</strong></td>
                      <td style={styles.td}>{item.valor}</td>
                      <td style={styles.td}>
                        <span style={styles.badge}>{item.van}</span>
                      </td>
                      <td style={styles.td}>{item.data}</td>
                      <td style={{...styles.td, color: item.status === 'Confirmado' ? '#8b5cf6' : '#666'}}>
                        {item.status}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

          </div>

          {/* Coluna Direita (Cards Rápidos e Cromáticos) */}
          <div style={styles.rightColumn}>
            
            {/* Card Faturamento - Roxo Vibrante */}
            <div style={styles.cardChromatic}>
              <h4 style={styles.chromaticTitle}>Faturamento Previsto</h4>
              <h2 style={styles.chromaticValue}>R$ 14.500,00</h2>
              <p style={styles.chromaticSubtitle}>+12% em relação a semana passada</p>
              
              <div style={styles.chromaticButtons}>
                <button style={styles.btnAction}>Ver Relatório</button>
              </div>
            </div>

            {/* Resumo Diário */}
            <div style={styles.cardSmall}>
              <div style={styles.statRow}>
                <div style={styles.statIconWrapper}>🚐</div>
                <div>
                  <h3 style={styles.statValue}>8</h3>
                  <p style={styles.statLabel}>Veículos em Rota</p>
                </div>
              </div>
            </div>

            <div style={styles.cardSmall}>
              <div style={styles.statRow}>
                <div style={styles.statIconWrapper}>✅</div>
                <div>
                  <h3 style={styles.statValue}>24</h3>
                  <p style={styles.statLabel}>Transfers Concluídos</p>
                </div>
              </div>
            </div>

          </div>
        </div>
      </main>
    </div>
  );
}

// Estilização baseada em tons de Branco, Cinza Claro e Roxo/Cromático
const styles = {
  appContainer: {
    display: 'flex',
    backgroundColor: '#f5f5f7', // Fundo cinza bem claro/off-white
    minHeight: '100vh',
    fontFamily: '"Inter", "Segoe UI", sans-serif',
    color: '#333',
  },
  sidebar: {
    width: '80px',
    backgroundColor: '#ffffff',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '30px 0',
    borderRight: '1px solid #eaeaea',
  },
  logoBadge: {
    fontSize: '28px',
    marginBottom: '40px',
  },
  iconMenu: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  iconWrapper: {
    width: '45px',
    height: '45px',
    borderRadius: '50%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontSize: '20px',
    cursor: 'pointer',
    backgroundColor: 'transparent',
    transition: 'all 0.3s',
  },
  iconActive: {
    backgroundColor: '#f3e8ff', // Roxo super claro
    color: '#a855f7',
    boxShadow: '0 4px 12px rgba(168, 85, 247, 0.2)',
  },
  mainContent: {
    flex: 1,
    padding: '30px 40px',
    overflowY: 'auto',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px',
  },
  navTabs: {
    display: 'flex',
    gap: '10px',
    backgroundColor: '#ffffff',
    padding: '5px',
    borderRadius: '30px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.02)',
  },
  tab: {
    padding: '10px 20px',
    border: 'none',
    backgroundColor: 'transparent',
    borderRadius: '20px',
    cursor: 'pointer',
    color: '#666',
    fontWeight: '500',
  },
  tabActive: {
    padding: '10px 20px',
    border: 'none',
    backgroundColor: '#333',
    color: '#fff',
    borderRadius: '20px',
    cursor: 'pointer',
    fontWeight: 'bold',
  },
  headerControls: {
    display: 'flex',
    alignItems: 'center',
    gap: '20px',
  },
  searchInput: {
    padding: '12px 20px',
    borderRadius: '20px',
    border: '1px solid #eaeaea',
    width: '250px',
    outline: 'none',
    backgroundColor: '#ffffff',
  },
  profileArea: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    backgroundColor: '#ffffff',
    padding: '8px 20px',
    borderRadius: '30px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.02)',
  },
  avatar: {
    width: '35px',
    height: '35px',
    borderRadius: '50%',
    backgroundColor: '#a855f7',
    color: '#fff',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontWeight: 'bold',
  },
  adminName: { margin: 0, fontSize: '14px', fontWeight: 'bold' },
  adminEmail: { margin: 0, fontSize: '12px', color: '#888' },
  notification: { cursor: 'pointer' },
  
  greetingSection: { marginBottom: '30px' },
  greetingTitle: { fontSize: '32px', margin: '0 0 10px 0', fontWeight: '600' },
  greetingSubtitle: { color: '#666', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' },
  alertIcon: { 
    display: 'inline-block', width: '20px', height: '20px', 
    backgroundColor: '#fef08a', color: '#854d0e', borderRadius: '50%', 
    textAlign: 'center', fontWeight: 'bold', lineHeight: '20px', fontSize: '12px'
  },

  dashboardGrid: {
    display: 'grid',
    gridTemplateColumns: '2fr 1fr',
    gap: '30px',
  },
  leftColumn: { display: 'flex', flexDirection: 'column', gap: '30px' },
  rightColumn: { display: 'flex', flexDirection: 'column', gap: '30px' },

  cardLarge: {
    backgroundColor: '#ffffff',
    borderRadius: '24px',
    padding: '30px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.03)',
  },
  cardMedium: {
    backgroundColor: '#ffffff',
    borderRadius: '24px',
    padding: '30px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.03)',
  },
  cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' },
  cardTitle: { margin: 0, fontSize: '18px', fontWeight: '600', color: '#333' },
  selectBox: { padding: '8px 15px', borderRadius: '10px', border: '1px solid #eaeaea', outline: 'none' },
  
  chartArea: {
    height: '250px',
    display: 'flex',
    alignItems: 'flex-end',
    paddingTop: '20px',
    borderBottom: '2px dashed #eaeaea',
  },
  barGroup: {
    display: 'flex',
    justifyContent: 'space-around',
    width: '100%',
    height: '100%',
    alignItems: 'flex-end',
  },
  bar: {
    width: '60px',
    borderRadius: '10px 10px 0 0',
  },
  chromaticBar: {
    // Efeito cromático com tons de roxo, rosa e lilás
    background: 'linear-gradient(180deg, rgba(217,70,239,1) 0%, rgba(168,85,247,1) 50%, rgba(139,92,246,0.5) 100%)',
    boxShadow: '0 0 20px rgba(168, 85, 247, 0.4)',
  },

  cardChromatic: {
    // O grande diferencial do estilo solicitado (roxo cromático)
    background: 'linear-gradient(135deg, #8b5cf6 0%, #d946ef 50%, #f472b6 100%)',
    borderRadius: '24px',
    padding: '35px 30px',
    color: '#ffffff',
    boxShadow: '0 15px 35px rgba(217, 70, 239, 0.3)',
    position: 'relative',
    overflow: 'hidden',
  },
  chromaticTitle: { margin: '0 0 10px 0', fontSize: '16px', fontWeight: '400', opacity: 0.9 },
  chromaticValue: { margin: '0 0 10px 0', fontSize: '42px', fontWeight: 'bold' },
  chromaticSubtitle: { margin: '0 0 25px 0', fontSize: '14px', opacity: 0.8 },
  chromaticButtons: { display: 'flex', gap: '10px' },
  btnAction: {
    padding: '12px 24px',
    borderRadius: '30px',
    border: 'none',
    backgroundColor: '#ffffff',
    color: '#a855f7',
    fontWeight: 'bold',
    cursor: 'pointer',
    boxShadow: '0 4px 15px rgba(0,0,0,0.1)',
  },

  cardSmall: {
    backgroundColor: '#ffffff',
    borderRadius: '20px',
    padding: '25px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.03)',
  },
  statRow: { display: 'flex', alignItems: 'center', gap: '20px' },
  statIconWrapper: {
    width: '50px',
    height: '50px',
    borderRadius: '15px',
    backgroundColor: '#f3e8ff',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontSize: '24px',
  },
  statValue: { margin: '0 0 5px 0', fontSize: '24px', fontWeight: 'bold' },
  statLabel: { margin: 0, color: '#888', fontSize: '14px' },

  table: { width: '100%', borderCollapse: 'collapse', marginTop: '10px' },
  tableHead: { borderBottom: '2px solid #eaeaea' },
  th: { textAlign: 'left', padding: '15px 10px', color: '#888', fontWeight: '500', fontSize: '14px' },
  tableRow: { borderBottom: '1px solid #f5f5f5' },
  td: { padding: '15px 10px', fontSize: '14px', color: '#333' },
  badge: {
    padding: '6px 12px',
    backgroundColor: '#fdf4ff',
    color: '#d946ef',
    borderRadius: '20px',
    fontSize: '12px',
    fontWeight: 'bold',
  }
};

export default Dashboard;