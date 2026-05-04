import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

const THEME = {
  primary: '#4c1d95',   // Roxo Profundo
  secondary: '#7c3aed', // Roxo Vibrante
  bg: '#F8FAFC',        // Branco Acinzentado (Clean)
  surface: '#FFFFFF',   // Branco Puro
  text: '#1e293b',      // Azul Escuro/Cinza para texto
  muted: '#64748b'      // Texto secundário
};

export default function Storefront() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('ALL');
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const [cart, setCart] = useState([]);
  const [bookingDetails, setBookingDetails] = useState({
    origem: '',
    destino: '',
    data: '',
    observacoes: ''
  });
  const currentTime = new Date(); // Declaração movida para o escopo correto
  const [weather, setWeather] = useState({ temp: 25, condition: 'Ensolarado' }); // Adicionado estado mock para 'weather'

  // Lógica de Indicação (Parceiros)
  const [referralCode, setReferralCode] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const ref = params.get('ref');
    if (ref) {
      setReferralCode(ref);
      localStorage.setItem('referral_code', ref);
    } else {
      setReferralCode(localStorage.getItem('referral_code'));
    }
  }, []);
  
  // Mock de Combos e Adicionais (Experiência)
  const addOns = [
    { id: 101, nome: 'Kit Vinho & Taças Personalizadas', preco: 180.00, img: '🍷' },
    { id: 102, nome: 'Lembranças de Gramado (Cesta)', preco: 95.00, img: '🎁' },
    { id: 103, nome: 'Ingresso Antecipado: Snowland', preco: 220.00, img: '❄️' }
  ];

  // Configurações da Empresa (SaaS White Label)
  const [tenantConfig, setTenantConfig] = useState({
    name: 'LUXE SERRA',
    primaryColor: '#4c1d95',
    secondaryColor: '#7c3aed',
    heroImage: 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&q=80&w=2000',
    welcomeMessage: 'Sua Jornada de Luxo Começa Aqui'
  });

  const THEME = {
    primary: tenantConfig.primaryColor,
    secondary: tenantConfig.secondaryColor,
    bg: '#F8FAFC',
    surface: '#FFFFFF',
    text: '#1e293b',
    muted: '#64748b'
  };

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const res = await axios.get(`${API_URL}/servicos`);
        setServices(res.data);
      } catch (err) {
        console.error("Erro ao carregar catálogo", err);
        // Mock de luxo caso a API falhe
        setServices([
          { id: 1, nome: 'Premium Transfer: Aero POA', categoria: 'TRANSFERS', valor: 350.00, descricao: 'Transporte privativo em Sedan de Luxo com concierge bilíngue.', imagem_url: 'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&q=80&w=1000' },
          { id: 2, nome: 'Tour Privativo: Vale dos Vinhedos', categoria: 'EXPERIENCIAS', valor: 1200.00, descricao: 'Experiência exclusiva pelas melhores vinícolas com degustação premium.', imagem_url: 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&q=80&w=1000' },
          { id: 3, nome: 'Chauffeur à Disposição (8h)', categoria: 'TRANSFERS', valor: 950.00, descricao: 'Motorista executivo trajado à sua total disposição para roteiros urbanos.', imagem_url: 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&q=80&w=1000' }
        ]);
      } finally {
        setLoading(false);
      }
    };

    const fetchTenantSettings = async () => {
      try {
        // Em um SaaS real, identificaríamos o tenant pelo subdomínio
        // const domain = window.location.hostname;
        // const res = await axios.get(`${API_URL}/tenant/settings?domain=${domain}`);
        // setTenantConfig(res.data);
        console.log("Identificando configurações do cliente SaaS...");
      } catch (err) {
        console.log("Usando branding padrão");
      }
    };

    fetchServices();
    fetchTenantSettings();
  }, []);

  const filteredServices = category === 'ALL' ? services : services.filter(s => s.categoria === category);

  const addToCart = (service) => {
    setCart([...cart, service]);
    setIsCartOpen(true);
  };

  const handleCheckout = async () => {
    if (cart.length === 0) return;
    
    setIsCheckingOut(true);
    try {
      // Exemplo de como enviar o carrinho completo para gerar uma preferência de pagamento única
      const res = await axios.post(`${API_URL}/checkout`, {
        itens: cart.map(item => ({
          id: item.id,
          titulo: item.nome,
          preco: item.valor
        })),
        metadata: {
          ...bookingDetails,
          parceiro_cod: referralCode // Envia o código de quem indicou
        }
      });

      if (res.data.init_point) {
        // Redireciona para o checkout do Mercado Pago (SandBox ou Produção)
        window.location.href = res.data.init_point;
      } else {
        alert("Erro ao gerar link de pagamento.");
      }
    } catch (err) {
      console.error("Erro ao finalizar checkout:", err);
      alert("Ocorreu um erro ao processar sua reserva. Verifique o console.");
    } finally {
      setIsCheckingOut(false);
    }
  };

  return (
    <div style={styles.container}>
      {/* Injeção de Fonte Serifada para Luxo */}
      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600&display=swap');
          .cart-icon:hover { color: ${THEME.secondary} !important; transform: scale(1.1); }
          .card-luxury:hover { transform: translateY(-8px) !important; box-shadow: 0 18px 40px rgba(0,0,0,0.15) !important; }
          @keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
          @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
          .drawer-anim { animation: slideIn 0.3s ease-out; }
          .overlay-anim { animation: fadeIn 0.2s ease-out; }
        `}
      </style>

      {/* Navbar Minimalista */}
      <nav style={styles.nav}>
        <div style={styles.logoContainer}>
          <div style={styles.logo}>{tenantConfig.name.split(' ')[0]} <span style={{color: THEME.primary}}>{tenantConfig.name.split(' ')[1] || ''}</span></div>
          <div style={styles.weatherWidget}>
            <span style={styles.weatherText}>
              {currentTime.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })} • {weather.temp}°C
            </span>
            <span style={styles.weatherCity}>{weather.condition}</span>
          </div>
        </div>
        <div style={styles.navLinks}>
          <span style={styles.navLink}>FROTAS</span>
          <span style={styles.navLink}>DESTINOS</span>
          <div style={styles.cartContainer} className="cart-icon" onClick={() => setIsCartOpen(true)}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>
            <span style={styles.cartBadge}>{cart.length}</span>
          </div>
          <button style={styles.contactBtn}>CONTATO EXCLUSIVO</button>
        </div>
      </nav>

      {/* Hero Section */}
      <header style={{...styles.hero, backgroundImage: `url(${tenantConfig.heroImage})`}}>
        <div style={styles.heroOverlay} />
        <div style={styles.heroContent}>
          <h1 style={styles.heroTitle}>{tenantConfig.welcomeMessage}</h1>
          <p style={styles.heroSubtitle}>A sua experiência de férias começa no momento em que você desembarca. Elegância e pontualidade na Serra Gaúcha.</p>
          <div style={styles.heroDivider} />
          <div style={styles.categoryBar}>
            {['ALL', 'TRANSFERS', 'EXPERIENCIAS', 'INGRESSOS'].map(cat => (
              <button 
                key={cat} 
                onClick={() => setCategory(cat)}
                style={category === cat ? styles.catBtnActive : styles.catBtn}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Listagem de Serviços */}
      <main style={styles.main}>
        <div style={styles.grid}>
          {filteredServices.map(service => (
            <div key={service.id} style={{...styles.card, border: service.valor > 500 ? '2px solid #C5A059' : styles.card.border}} className="card-luxury">
              <div style={styles.imageContainer}>
                <img src={service.imagem_url || 'https://via.placeholder.com/400x300'} alt={service.nome} style={styles.cardImage} />
                <div style={{...styles.priceBadge, background: service.valor > 500 ? 'linear-gradient(135deg, #000, #C5A059)' : THEME.secondary}}>
                  R$ {service.valor.toFixed(2)}
                </div>
              </div>
              <div style={styles.cardContent}>
                <span style={{...styles.cardCategory, color: service.valor > 500 ? '#C5A059' : THEME.secondary}}>
                  {service.valor > 500 ? '💎 PREMIUM BLACK' : service.categoria}
                </span>
                <h3 style={styles.cardTitle}>{service.nome}</h3>
                <p style={styles.cardDesc}>{service.descricao}</p>
                <button style={styles.bookBtn} onClick={() => addToCart(service)}>RESERVAR AGORA</button>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* Drawer do Carrinho */}
      {isCartOpen && (
        <div style={styles.drawerOverlay} onClick={() => setIsCartOpen(false)} className="overlay-anim">
          <div style={styles.drawer} onClick={e => e.stopPropagation()} className="drawer-anim">
            <div style={styles.drawerHeader}>
              <h2 style={styles.drawerTitle}>Sua Reserva</h2>
              <button style={styles.closeBtn} onClick={() => setIsCartOpen(false)}>✕</button>
            </div>
            
            <div style={styles.drawerContent}>
              {cart.length === 0 ? (
                <p style={styles.emptyCart}>Seu carrinho está vazio.</p>
              ) : (
                <>
                  <div style={styles.upsellSection}>
                    <h4 style={styles.sectionTitle}>💎 Complete sua Experiência</h4>
                    <div style={styles.upsellScroll}>
                      {addOns.map(item => (
                        <div key={item.id} style={styles.upsellCard} onClick={() => addToCart({ ...item, valor: item.preco })}>
                          <span style={{fontSize: '24px'}}>{item.img}</span>
                          <div style={{fontSize: '11px', fontWeight: 'bold', margin: '5px 0'}}>{item.nome}</div>
                          <div style={{color: THEME.primary, fontSize: '11px'}}>+ R$ {item.preco}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div style={styles.formSection}>
                    <h4 style={styles.sectionTitle}>Detalhes do Trajeto</h4>
                    <input 
                      style={styles.drawerInput} 
                      placeholder="Local de Origem (Ex: Aeroporto)" 
                      value={bookingDetails.origem}
                      onChange={e => setBookingDetails({...bookingDetails, origem: e.target.value})}
                    />
                    <input 
                      style={styles.drawerInput} 
                      placeholder="Local de Destino (Ex: Hotel)" 
                      value={bookingDetails.destino}
                      onChange={e => setBookingDetails({...bookingDetails, destino: e.target.value})}
                    />
                    <input 
                      type="datetime-local"
                      style={styles.drawerInput} 
                      value={bookingDetails.data}
                      onChange={e => setBookingDetails({...bookingDetails, data: e.target.value})}
                    />
                    <textarea 
                      style={{...styles.drawerInput, height: '80px', resize: 'none'}} 
                      placeholder="Observações ou Mensagem de Boas-vindas (Ex: Placa de recepção com nome)" 
                      value={bookingDetails.observacoes}
                      onChange={e => setBookingDetails({...bookingDetails, observacoes: e.target.value})}
                    />
                  </div>
                  <div style={{marginTop: '20px'}}>
                    <h4 style={styles.sectionTitle}>Itens Selecionados</h4>
                    {cart.map((item, index) => (
                      <div key={index} style={styles.cartItem}>
                        <div style={{flex: 1}}>
                          <h4 style={{margin: 0, fontSize: '14px', color: THEME.text}}>{item.nome}</h4>
                          <small style={{color: THEME.muted}}>{item.categoria}</small>
                        </div>
                        <div style={{fontWeight: '700', color: THEME.primary}}>R$ {item.valor.toFixed(2)}</div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>

            {cart.length > 0 && (
              <div style={styles.drawerFooter}>
                <div style={styles.totalRow}>
                  <span>Total</span>
                  <span>R$ {cart.reduce((acc, curr) => acc + curr.valor, 0).toFixed(2)}</span>
                </div>
                <button 
                  style={{...styles.checkoutBtn, opacity: isCheckingOut ? 0.7 : 1}} 
                  onClick={handleCheckout}
                  disabled={isCheckingOut}
                >
                  {isCheckingOut ? "PROCESSANDO..." : "FINALIZAR CHECKOUT"}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Footer Elegante */}
      <footer style={styles.footer}>
        <p style={{color: THEME.text}}>© 2024 {tenantConfig.name}. Todos os direitos reservados.</p>
        <p style={{fontSize: '12px', color: THEME.muted, marginTop: '10px', letterSpacing: '2px'}}>EXCLUSIVIDADE • SEGURANÇA • PONTUALIDADE</p>
      </footer>
    </div>
  );
}

const styles = {
  container: {
    backgroundColor: THEME.bg,
    minHeight: '100vh',
    color: THEME.text,
    fontFamily: '"Inter", sans-serif',
  },
  nav: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 8%',
    position: 'fixed',
    width: '100%',
    zIndex: 10,
    boxSizing: 'border-box',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(10px)',
    boxShadow: '0 2px 20px rgba(0,0,0,0.05)'
  },
  pointsBadge: { padding: '5px 12px', background: 'rgba(124,58,237,0.1)', color: '#4c1d95', borderRadius: '20px', border: '1px solid rgba(124,58,237,0.2)' },
  logo: {
    fontSize: '22px',
    fontWeight: '700',
    letterSpacing: '3px',
    fontFamily: '"Playfair Display", serif'
  },
  navLinks: { display: 'flex', alignItems: 'center', gap: '40px' },
  navLink: { fontSize: '12px', fontWeight: '600', letterSpacing: '1px', cursor: 'pointer', color: THEME.text },
  cartContainer: { 
    position: 'relative', 
    cursor: 'pointer', 
    display: 'flex', 
    alignItems: 'center', 
    color: THEME.text,
    transition: '0.3s'
  },
  cartBadge: {
    position: 'absolute',
    top: '-8px',
    right: '-12px',
    backgroundColor: THEME.secondary,
    color: '#fff',
    fontSize: '9px',
    fontWeight: '800',
    width: '16px',
    height: '16px',
    borderRadius: '50%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)'
  },
  contactBtn: {
    backgroundColor: THEME.primary,
    border: 'none',
    color: '#fff',
    padding: '10px 25px',
    borderRadius: '50px',
    fontSize: '11px',
    fontWeight: '700',
    cursor: 'pointer',
    transition: '0.3s',
    boxShadow: '0 4px 15px rgba(76, 29, 149, 0.3)'
  },
  hero: {
    height: '80vh',
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    textAlign: 'center',
    backgroundImage: 'url("https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&q=80&w=2000")',
    backgroundSize: 'cover',
    backgroundPosition: 'center'
  },
  heroOverlay: {
    position: 'absolute',
    top: 0, left: 0, right: 0, bottom: 0,
    background: 'linear-gradient(135deg, rgba(76, 29, 149, 0.8) 0%, rgba(10, 10, 11, 0.6) 100%)'
  },
  heroContent: { position: 'relative', zIndex: 1, maxWidth: '800px', padding: '0 20px', color: '#fff' },
  heroTitle: {
    fontFamily: '"Playfair Display", serif',
    fontSize: '56px',
    marginBottom: '10px',
    lineHeight: 1.1
  },
  heroDivider: { width: '60px', height: '3px', background: '#fff', margin: '0 auto 30px auto' },
  heroSubtitle: {
    fontSize: '18px',
    opacity: 0.9,
    marginBottom: '40px',
    fontWeight: '300',
    lineHeight: 1.6
  },
  categoryBar: { display: 'flex', justifyContent: 'center', gap: '15px' },
  catBtn: {
    background: 'rgba(255,255,255,0.1)',
    border: '1px solid rgba(255,255,255,0.1)',
    color: '#fff',
    padding: '8px 20px',
    fontSize: '11px',
    fontWeight: '600',
    borderRadius: '50px',
    cursor: 'pointer'
  },
  catBtnActive: {
    background: '#fff',
    border: '1px solid #fff',
    color: THEME.primary,
    padding: '8px 20px',
    fontSize: '11px',
    fontWeight: '700',
    borderRadius: '30px',
    cursor: 'pointer'
  },
  main: { padding: '80px 8%' },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '40px'
  },
  card: {
    backgroundColor: THEME.surface,
    borderRadius: '20px',
    overflow: 'hidden',
    transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out', // Transição suave
    boxShadow: '0 10px 30px rgba(0,0,0,0.05)', // Sombra padrão
    border: '1px solid #f1f5f9',
  },
  imageContainer: { position: 'relative', height: '240px' },
  cardImage: { width: '100%', height: '100%', objectFit: 'cover' },
  priceBadge: {
    position: 'absolute',
    bottom: '20px',
    right: '20px',
    backgroundColor: THEME.secondary,
    color: '#fff',
    padding: '5px 15px',
    fontWeight: '700',
    fontSize: '13px',
    borderRadius: '50px',
  },
  cardContent: { padding: '30px' },
  cardCategory: {
    color: THEME.secondary,
    fontSize: '10px',
    fontWeight: '800',
    letterSpacing: '2px',
    marginBottom: '10px',
    display: 'block'
  },
  cardTitle: {
    fontFamily: '"Playfair Display", serif',
    fontSize: '22px',
    marginBottom: '15px'
  },
  cardDesc: {
    fontSize: '14px',
    color: THEME.muted,
    lineHeight: 1.6,
    marginBottom: '25px'
  },
  bookBtn: {
    width: '100%',
    padding: '15px',
    background: THEME.primary,
    border: 'none',
    color: '#fff',
    fontWeight: '700',
    fontSize: '12px',
    letterSpacing: '2px',
    cursor: 'pointer',
    transition: '0.3s',
    borderRadius: '12px'
  },
  footer: {
    padding: '100px 8% 50px',
    textAlign: 'center',
    borderTop: '1px solid #e2e8f0',
    backgroundColor: '#fff',
    fontSize: '14px'
  },
  drawerOverlay: {
    position: 'fixed',
    top: 0, left: 0, right: 0, bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    zIndex: 1000,
    display: 'flex',
    justifyContent: 'flex-end',
    backdropFilter: 'blur(4px)'
  },
  drawer: {
    width: '100%',
    maxWidth: '400px',
    height: '100%',
    backgroundColor: '#fff',
    boxShadow: '-10px 0 30px rgba(0,0,0,0.1)',
    display: 'flex',
    flexDirection: 'column',
    padding: '40px',
    boxSizing: 'border-box'
  },
  drawerHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' },
  drawerTitle: { fontFamily: '"Playfair Display", serif', fontSize: '28px', margin: 0 },
  closeBtn: { background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: THEME.muted },
  drawerContent: { flex: 1, overflowY: 'auto' },
  emptyCart: { textAlign: 'center', color: THEME.muted, marginTop: '100px' },
  cartItem: { 
    display: 'flex', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    padding: '20px 0', 
    borderBottom: '1px solid #f1f5f9' 
  },
  drawerFooter: { paddingTop: '30px', borderTop: '2px solid #f1f5f9' },
  totalRow: { display: 'flex', justifyContent: 'space-between', fontSize: '18px', fontWeight: '700', marginBottom: '30px' },
  checkoutBtn: {
    width: '100%',
    padding: '18px',
    backgroundColor: THEME.secondary,
    color: '#fff',
    border: 'none',
    borderRadius: '12px',
    fontWeight: '700',
    cursor: 'pointer',
    fontSize: '14px',
    letterSpacing: '1px'
  },
  formSection: { marginBottom: '30px' },
  sectionTitle: { fontSize: '12px', fontWeight: '800', color: THEME.primary, textTransform: 'uppercase', marginBottom: '15px', letterSpacing: '1px' },
  drawerInput: {
    width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '10px', fontSize: '14px', outline: 'none'
  }
};