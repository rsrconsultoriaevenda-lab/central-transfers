import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from './App';

// Configuração de Branding
const tenantConfig = {
  name: 'LUXE SERRA',
  primaryColor: '#2563EB',
  secondaryColor: '#1E293B',
  heroImage: 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&q=80&w=2000',
  welcomeMessage: 'Sua Jornada de Luxo Começa Aqui'
};

const THEME = {
  primary: tenantConfig.primaryColor,
  secondary: tenantConfig.secondaryColor,
  bg: '#0B0F19',
  surface: '#1E293B',
  text: '#FFFFFF',
  muted: '#64748b'
};

export default function Storefront() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('ALL');
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const [cart, setCart] = useState(() => {
    const saved = localStorage.getItem('cart');
    return saved ? JSON.parse(saved) : [];
  });
  const [bookingDetails, setBookingDetails] = useState({
    nome: '', email: '', telefone: '', cpf: '', origem: '', destino: '', data: '', observacoes: ''
  });
  const [weather] = useState({ temp: 25, condition: 'Ensolarado' });
  const [referralCode, setReferralCode] = useState(localStorage.getItem('referral_code') || null);

  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart));
  }, [cart]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const ref = params.get('ref');
    if (ref) {
      setReferralCode(ref);
      localStorage.setItem('referral_code', ref);
    }
  }, []);

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const res = await axios.get(`${API_URL}/servicos/`);
        setServices(res.data);
      } catch (err) {
        setServices([
          { id: 1, nome: 'Premium Transfer: Aero POA', categoria: 'TRANSFERS', valor: 350.00, descricao: 'Transporte privativo em Sedan de Luxo.', imagem_url: '' },
          { id: 2, nome: 'Tour Privativo: Vale dos Vinhedos', categoria: 'EXPERIENCIAS', valor: 1200.00, descricao: 'Experiência exclusiva.', imagem_url: '' }
        ]);
      } finally {
        setLoading(false);
      }
    };
    fetchServices();
  }, []);

  const updateQuantity = (index, delta) => {
    setCart(prev => prev.map((item, i) => i === index ? {...item, quantidade: Math.max(1, (item.quantidade || 1) + delta)} : item));
  };

  const removeFromCart = (index) => setCart(prev => prev.filter((_, i) => i !== index));

  const addToCart = (service) => {
    setCart(prev => {
      const existing = prev.find(i => i.id === service.id);
      if (existing) {
        return prev.map(i => i.id === service.id ? { ...i, quantidade: (i.quantidade || 1) + 1 } : i);
      }
      return [...prev, { ...service, quantidade: 1 }];
    });
    setIsCartOpen(true);
  };

  const handleCPFChange = (e) => {
    let value = e.target.value.replace(/\D/g, ''); // Remove tudo que não é dígito
    if (value.length > 11) value = value.slice(0, 11);
    
    value = value.replace(/(\d{3})(\d)/, '$1.$2');
    value = value.replace(/(\d{3})(\d)/, '$1.$2');
    value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    setBookingDetails({ ...bookingDetails, cpf: value });
  };

  const renderFormFields = () => (
    <>
      <input 
        style={styles.drawerInput} 
        placeholder="Seu Nome Completo" 
        value={bookingDetails.nome}
        onChange={e => setBookingDetails({...bookingDetails, nome: e.target.value})}
      />
      <input 
        style={styles.drawerInput} 
        placeholder="Seu E-mail (Obrigatório para Pix)" 
        value={bookingDetails.email}
        onChange={e => setBookingDetails({...bookingDetails, email: e.target.value})}
      />
      <input 
        style={styles.drawerInput} 
        placeholder="Seu WhatsApp/Telefone" 
        value={bookingDetails.telefone}
        onChange={e => setBookingDetails({...bookingDetails, telefone: e.target.value})}
      />
      <input 
        style={styles.drawerInput} 
        placeholder="CPF (Opcional - Melhora aprovação do cartão)" 
        value={bookingDetails.cpf}
        onChange={handleCPFChange}
      />
      <input 
        style={styles.drawerInput} 
        placeholder="Local de Origem" 
        value={bookingDetails.origem}
        onChange={e => setBookingDetails({...bookingDetails, origem: e.target.value})}
      />
      <input 
        style={styles.drawerInput} 
        placeholder="Local de Destino" 
        value={bookingDetails.destino}
        onChange={e => setBookingDetails({...bookingDetails, destino: e.target.value})}
      />
    </>
  );

  const handleCheckout = async () => {
    if (!bookingDetails.nome || !bookingDetails.email || !bookingDetails.telefone || !bookingDetails.origem || !bookingDetails.destino) {
      alert("Por favor, preencha todos os campos obrigatórios: Nome, E-mail, Telefone, Origem e Destino.");
      return;
    }
    setIsCheckingOut(true);
    try {
      const res = await axios.post(`${API_URL}/pagamentos/checkout/`, {
        itens: cart,
        metadata: { ...bookingDetails, parceiro_cod: referralCode }
      });
      if (res.data.init_point) window.location.href = res.data.init_point;
    } catch (err) {
      alert("Erro ao processar reserva.");
    } finally {
      setIsCheckingOut(false);
    }
  };

  const filteredServices = category === 'ALL' ? services : services.filter(s => s.categoria === category);

  return (
    <div style={styles.container}>
      <style>{`
        @media (max-width: 768px) {
          .hero-section { height: 320px !important; }
          .hero-title { font-size: 32px !important; }
          .service-grid { 
            grid-template-columns: 1fr !important; 
            padding: 20px 15px 120px !important;
            gap: 20px !important;
          }
          .drawer-full-mobile { 
            width: 100% !important; 
            max-width: 100% !important; 
          }
          .footer-social-links {
            flex-direction: column !important;
            align-items: center !important;
            gap: 15px !important;
          }
        }
        body { background-color: #0B0F19; }
        input::placeholder { color: #94A3B8; }
      `}</style>
      {/* Navbar */}
      <nav style={styles.navbar}>
        <div style={styles.logo}>{tenantConfig.name}</div>
        <div style={styles.cartBtn} onClick={() => setIsCartOpen(true)}>
          <span style={{fontSize: '24px'}}>💼</span> 
          <span style={styles.cartBadge}>{cart.reduce((acc, i) => acc + (i.quantidade || 1), 0)}</span>
        </div>
      </nav>

      {/* Hero */}
      <header className="hero-section" style={{...styles.hero, backgroundImage: `linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url(${tenantConfig.heroImage})`}}>
        <h1 className="hero-title" style={styles.heroTitle}>{tenantConfig.welcomeMessage}</h1>
        <p>Conforto e Segurança na Serra Gaúcha</p>
      </header>

      {/* Filters */}
      <div style={styles.filters}>
        {['ALL', 'TRANSFERS', 'EXPERIENCIAS', 'PACOTES'].map(cat => (
          <button 
            key={cat} 
            onClick={() => setCategory(cat)}
            style={{...styles.filterBtn, background: category === cat ? THEME.primary : THEME.surface, color: '#fff', borderColor: category === cat ? THEME.primary : 'rgba(255,255,255,0.1)'}}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Services Grid */}
      <main className="service-grid" style={styles.serviceGrid}>
        {loading ? (
          <p>Carregando experiências...</p>
        ) : (
          filteredServices.map(service => (
            <div key={service.id} style={styles.card}>
              <div style={styles.imageContainer}>
                <img 
                  src={service.imagem_url ? (service.imagem_url.startsWith('http') ? service.imagem_url : `${API_URL.replace('/api', '')}${service.imagem_url}`) : 'https://placehold.co/600x400?text=Premium+Transfer'} 
                  alt={service.nome} 
                  style={styles.cardImage} 
                />
                <div style={styles.priceBadge}>R$ {service.valor.toFixed(2)}</div>
              </div>
              <div style={styles.cardContent}>
                <h3 style={styles.cardTitle}>{service.nome}</h3>
                <p style={styles.cardDesc}>{service.descricao || 'Transporte privativo com foco em conforto e segurança.'}</p>
                <button style={styles.bookBtn} onClick={() => addToCart(service)}>RESERVAR AGORA</button>
              </div>
            </div>
          ))
        )}
      </main>

      {/* Rodapé Personalizado */}
      <footer style={styles.footer}>
        <div style={styles.footerBrand}>
          <h3 style={{ color: THEME.primary, marginBottom: '5px' }}>{tenantConfig.name}</h3>
          <p style={{ fontSize: '14px', color: THEME.muted }}>Excelência em transporte e experiências na Serra Gaúcha.</p>
        </div>
        <div style={styles.socialLinks} className="footer-social-links">
          <a href="https://instagram.com" target="_blank" rel="noreferrer" style={styles.socialLink}>📸 Instagram</a>
          <a href="https://wa.me/5554999990000" target="_blank" rel="noreferrer" style={styles.socialLink}>💬 WhatsApp</a>
          <a href="https://facebook.com" target="_blank" rel="noreferrer" style={styles.socialLink}>👥 Facebook</a>
        </div>
        <div style={styles.footerCopyright}>
          © {new Date().getFullYear()} {tenantConfig.name}. Todos os direitos reservados.
        </div>
      </footer>

      {/* Cart Drawer Overlay */}
      {isCartOpen && (
        <div style={styles.drawerOverlay} onClick={() => setIsCartOpen(false)}>
          <div className="drawer-full-mobile" style={{...styles.drawer, background: '#0B0F19', color: '#fff'}} onClick={e => e.stopPropagation()}>
            <div style={{...styles.drawerHeader, borderBottom: '1px solid rgba(255,255,255,0.1)'}}>
              <h2 style={styles.drawerTitle}>Sua Reserva</h2>
              <button style={styles.closeBtn} onClick={() => setIsCartOpen(false)}>✕</button>
            </div>

            <div style={styles.drawerContent}>
              {cart.length === 0 ? (
                <p style={{textAlign: 'center', marginTop: '50px'}}>Seu carrinho está vazio.</p>
              ) : (
                <>
                  <div style={styles.cartList}>
                    {cart.map((item, index) => (
                      <div key={index} style={styles.cartItem}>
                        <div style={{flex: 1}}>
                          <h4 style={{margin: 0, color: '#fff'}}>{item.nome}</h4>
                          <div style={styles.qtyContainer}>
                            <button style={styles.qtyBtn} onClick={() => updateQuantity(index, -1)}>-</button>
                            <span style={styles.qtyValue}>{item.quantidade || 1}</span>
                            <button style={styles.qtyBtn} onClick={() => updateQuantity(index, 1)}>+</button>
                          </div>
                        </div>
                        <div style={{textAlign: 'right'}}>
                          <div style={{fontWeight: 'bold', color: THEME.primary}}>R$ {(item.valor * (item.quantidade || 1)).toFixed(2)}</div>
                          <button style={styles.removeItemBtn} onClick={() => removeFromCart(index)}>Remover</button>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div style={styles.formSection}>
                    <h3 style={styles.sectionTitle}>Dados do Passageiro</h3>
                    {renderFormFields()}
                  </div>
                </>
              )}
            </div>

            {cart.length > 0 && (
              <div style={{...styles.drawerFooter, background: '#1E293B', borderTop: 'none'}}>
                <div style={styles.totalRow}>
                  <span>Total</span>
                  <span>R$ {cart.reduce((acc, curr) => acc + (curr.valor * (curr.quantidade || 1)), 0).toFixed(2)}</span>
                </div>
                <button 
                  style={{...styles.checkoutBtn, background: THEME.primary, opacity: isCheckingOut ? 0.7 : 1}} 
                  disabled={isCheckingOut}
                  onClick={handleCheckout}
                >
                  {isCheckingOut ? 'PROCESSANDO...' : 'FINALIZAR RESERVA'}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { background: '#0B0F19', color: '#fff', minHeight: '100vh', fontFamily: '"Inter", sans-serif' },
  navbar: { display: 'flex', justifyContent: 'space-between', padding: '20px 5%', background: '#0B0F19', borderBottom: '1px solid rgba(255,255,255,0.05)', position: 'sticky', top: 0, zIndex: 100 },
  logo: { fontSize: '20px', fontWeight: '900', color: THEME.primary, letterSpacing: '1px' },
  cartBtn: { cursor: 'pointer', position: 'relative' },
  cartBadge: { position: 'absolute', top: '-8px', right: '-8px', background: THEME.primary, color: '#fff', fontSize: '10px', width: '18px', height: '18px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  hero: { height: '400px', backgroundSize: 'cover', backgroundPosition: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', color: '#fff', textAlign: 'center', padding: '0 20px' },
  heroTitle: { fontSize: '48px', fontWeight: '900', marginBottom: '10px' },
  filters: { display: 'flex', justifyContent: 'center', gap: '10px', padding: '40px 20px', overflowX: 'auto' },
  filterBtn: { padding: '10px 20px', borderRadius: '30px', border: '1px solid #e2e8f0', cursor: 'pointer', fontWeight: '600', transition: '0.2s' },
  serviceGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '30px', padding: '0 5% 80px' },
  card: { background: '#1E293B', borderRadius: '20px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.05)' },
  imageContainer: { height: '200px', position: 'relative' },
  cardImage: { width: '100%', height: '100%', objectFit: 'cover' },
  priceBadge: { position: 'absolute', bottom: '15px', right: '15px', background: THEME.primary, color: '#fff', padding: '5px 15px', borderRadius: '30px', fontWeight: '900' },
  cardContent: { padding: '20px' },
  cardTitle: { fontSize: '18px', margin: '0 0 10px 0', color: '#fff' },
  cardDesc: { fontSize: '14px', color: THEME.muted, marginBottom: '20px', lineHeight: '1.5' },
  bookBtn: { width: '100%', padding: '12px', background: THEME.primary, color: '#fff', border: 'none', borderRadius: '12px', fontWeight: 'bold', cursor: 'pointer' },
  drawerOverlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', zIndex: 1000, backdropFilter: 'blur(4px)' },
  drawer: { position: 'absolute', top: 0, right: 0, width: '100%', maxWidth: '400px', height: '100%', background: '#fff', display: 'flex', flexDirection: 'column' },
  drawerHeader: { padding: '20px', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  drawerTitle: { margin: 0, fontSize: '20px' },
  closeBtn: { background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: '#fff' },
  drawerContent: { flex: 1, overflowY: 'auto', padding: '20px' },
  cartList: { marginBottom: '30px' },
  cartItem: { display: 'flex', justifyContent: 'space-between', padding: '15px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' },
  qtyContainer: { display: 'flex', alignItems: 'center', gap: '10px', marginTop: '10px' },
  qtyBtn: { width: '28px', height: '28px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', background: '#1E293B', cursor: 'pointer', color: '#fff' },
  qtyValue: { fontSize: '14px', fontWeight: 'bold' },
  removeItemBtn: { background: 'none', border: 'none', color: '#ef4444', fontSize: '12px', cursor: 'pointer', marginTop: '5px' },
  formSection: { marginTop: '20px' },
  sectionTitle: { fontSize: '16px', marginBottom: '15px', color: THEME.primary },
  drawerInput: {
    width: '100%',
    padding: '12px',
    marginBottom: '15px',
    borderRadius: '8px',
    border: '1px solid rgba(255,255,255,0.1)',
    background: '#1E293B',
    color: '#fff',
    fontSize: '14px',
    boxSizing: 'border-box',
    outline: 'none'
  },
  drawerFooter: { padding: '25px 20px calc(20px + env(safe-area-inset-bottom))' },
  totalRow: { display: 'flex', justifyContent: 'space-between', fontSize: '22px', fontWeight: '900', marginBottom: '20px' },
  checkoutBtn: { width: '100%', padding: '20px', color: '#fff', border: 'none', borderRadius: '16px', fontWeight: '900', fontSize: '16px', cursor: 'pointer', boxShadow: '0 10px 20px rgba(37, 99, 235, 0.3)' },
  footer: { backgroundColor: '#0B0F19', padding: '60px 5% 40px', borderTop: '1px solid rgba(255,255,255,0.05)', textAlign: 'center' },
  footerBrand: { marginBottom: '30px' },
  socialLinks: { display: 'flex', justifyContent: 'center', gap: '25px', marginBottom: '30px' },
  socialLink: { color: '#fff', textDecoration: 'none', fontWeight: '600', fontSize: '14px', transition: '0.2s' },
  footerCopyright: { fontSize: '12px', color: THEME.muted, borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '20px' }
};