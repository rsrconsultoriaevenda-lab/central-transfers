function Dashboard() {
  const navigate = useNavigate();
  
  // ESTADOS PARA CONTROLE DE TELA E DADOS
  const [tab, setTab] = useState('Home');
  const [loading, setLoading] = useState(false);
  const [faturamento, setFaturamento] = useState(74503);
  const [atividades, setAtividades] = useState([
    { id: 1, label: 'Transfer Gramado', user: 'Spotify', price: 20, icon: '🚐' },
    { id: 2, label: 'Tour Vinhedos', user: 'YouTube', price: 12, icon: '🍷' },
  ]);

  // FUNÇÃO PARA "DAR VIDA": Simula atualização de dados ao clicar
  const atualizarDados = () => {
    setLoading(true);
    setTimeout(() => {
      setFaturamento(prev => prev + Math.floor(Math.random() * 100)); // Simula venda nova
      setLoading(false);
    }, 800);
  };

  const adminInfo = { name: "Alex Turner", email: "aturner@gmail.com" };

  return (
    <div style={ds.wrapper}>
      <aside style={ds.sidebar}>
        <div style={{fontSize: '24px', marginBottom: '30px'}}>🚐</div>
        
        {/* BOTÕES COM LÓGICA DE TROCA DE ABA */}
        <div onClick={() => setTab('Home')} style={tab === 'Home' ? ds.sideIconActive : ds.sideIcon}>
          <Icons.Home /><span style={ds.sideLabel}>HOME</span>
        </div>
        <div onClick={() => setTab('Stats')} style={tab === 'Stats' ? ds.sideIconActive : ds.sideIcon}>
          <Icons.Stats /><span style={ds.sideLabel}>STAT</span>
        </div>
        <div onClick={() => setTab('User')} style={tab === 'User' ? ds.sideIconActive : ds.sideIcon}>
          <Icons.User /><span style={ds.sideLabel}>USER</span>
        </div>
        
        <div onClick={() => { if(window.confirm("Sair do sistema?")) navigate('/login') }} style={ds.sideIcon}>
          <Icons.Settings /><span style={ds.sideLabel}>SAIR</span>
        </div>
      </aside>

      <main style={ds.main}>
        <header style={ds.header}>
          <div>
            <h1 style={ds.welcomeText}>Bom dia, <span style={{fontWeight:800}}>{adminInfo.name}</span></h1>
            <p style={ds.subWelcome}>Status: {loading ? 'Atualizando...' : 'Sistema Online'}</p>
          </div>
          <div style={ds.adminProfile}>
            <div style={ds.adminTextGroup}>
              <p style={ds.adminName}>{adminInfo.name}</p>
              <p style={ds.adminEmail}>{adminInfo.email}</p>
            </div>
            <div style={ds.avatar}>AT</div>
          </div>
        </header>

        {/* CONTEÚDO DINÂMICO BASEADO NA ABA SELECIONADA */}
        {tab === 'Home' ? (
          <div style={ds.grid}>
            <section style={ds.cardMain} onClick={atualizarDados}>
              <div style={{display:'flex', justifyContent:'space-between'}}>
                <h3 style={{margin:0}}>Faturamento Dinâmico</h3>
                <small>(Clique para atualizar)</small>
              </div>
              <h2 style={{fontSize: '34px', margin: '20px 0'}}>
                R$ {faturamento.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </h2>
              <div style={ds.chartContainer}>
                {[30, 60, 40, 85, 50, 70, 45].map((h, i) => (
                  <div key={i} style={{...ds.bar, height: `${h}%`, background: h === 85 ? '#fff' : 'rgba(255,255,255,0.3)'}}></div>
                ))}
              </div>
            </section>

            <section style={ds.cardBlack}>
              <p style={{fontSize: '11px', opacity: 0.6}}>Ação Rápida</p>
              <h4 style={{margin: '5px 0 20px 0'}}>Gestão de Frota</h4>
              <button style={ds.btnSmall} onClick={() => alert("Abrindo check-in da Van...")}>Check-in Veículo</button>
            </section>

            <section style={ds.cardWhite}>
              <h4>Atividades Recentes</h4>
              {atividades.map((item) => (
                <div key={item.id} style={ds.row} onClick={() => alert(`Detalhes de: ${item.label}`)}>
                  <div style={ds.rowIcon}>{item.icon}</div>
                  <div style={{flex: 1}}><strong>{item.label}</strong></div>
                  <div style={{fontWeight:'bold', color:'#10b981'}}>R$ {item.price}</div>
                </div>
              ))}
            </section>
          </div>
        ) : (
          <div style={{padding: '50px', textAlign: 'center', background: '#fff', borderRadius: '30px'}}>
            <h2>Tela de {tab} em desenvolvimento...</h2>
            <p>Em breve você verá os gráficos detalhados aqui.</p>
          </div>
        )}
      </main>
    </div>
  );
}