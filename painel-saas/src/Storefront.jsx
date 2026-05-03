import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

export default function Storefront() {
  const [services, setServices] = useState([]);
  const [cart, setCart] = useState([]);
  const [category, setCategory] = useState('TRANSFERS'); 
  const [bookingData, setBookingData] = useState({
    nome: '',
    email: '',
    telefone: '',
    origem: '',
    destino: '',
    data: '',
    hora: '',
    passageiros: 1
  });
  const [step, setStep] = useState('catalog'); // catalog, details, success
  const [isProcessing, setIsProcessing] = useState(false);
  const [blockedDates, setBlockedDates] = useState([]);
  const [dateError, setDateError] = useState('');

  // Dicas dinâmicas para atrair o cliente
  const gramadoTips = [
    { id: 1, icon: '🌲', title: 'Lago Negro', desc: 'Perfeito para um passeio de pedalinho ao entardecer.' },
    { id: 2, icon: '🍫', title: 'Rua Coberta', desc: 'O melhor lugar para um chocolate quente artesanal.' },
    { id: 3, icon: '❄️', title: 'Snowland', desc: 'Diversão na neve o ano todo em Gramado.' },
    { id: 4, icon: '🍷', title: 'Vale dos Vinhedos', desc: 'Uma experiência gastronômica inesquecível.' }
  ];

  const testimonials = [
    { id: 1, name: "Mariana Silva", text: "Atendimento impecável! O transfer chegou antes do horário e o carro era extremamente confortável.", stars: 5 },
    { id: 2, name: "Ricardo Oliveira", text: "Melhor experiência em Gramado. O tour Uva e Vinho foi sensacional e muito bem organizado.", stars: 5 }
  ];

  const features = [
    { icon: '🛡️', title: 'Seguro Viagem', desc: 'Proteção total em todos os trajetos.' },
    { icon: '🕒', title: 'Pontualidade', desc: 'Respeito rigoroso aos seus horários.' },
    { icon: '💎', title: 'Frota Premium', desc: 'Veículos novos e higienizados.' }
  ];

  useEffect(() => {
    // Busca serviços cadastrados no seu backend
    axios.get(`${API_URL}/servicos`).then(res => {
      // Ordena ou filtra se necessário
      setServices(res.data);
    });

    // Busca datas bloqueadas
    axios.get(`${API_URL}/servicos/disponibilidade/datas-bloqueadas`).then(res => {
      setBlockedDates(res.data.bloqueadas || []);
    });
  }, []);

  const addToCart = (service) => {
    setCart([service]); // Para o MVP, focamos em um serviço por vez
    setStep('details');
  };

  const handleDateChange = (dateValue) => {
    setDateError('');
    if (blockedDates.includes(dateValue)) {
      setDateError('⚠️ Desculpe, estamos com a frota completa para esta data.');
    }
    setBookingData({...bookingData, data: dateValue});
  };

  const handleCheckout = async () => {
    if (!bookingData.nome || !bookingData.telefone) {
      alert("Por favor, preencha seu nome e telefone.");
      return;
    }

    if (!bookingData.data || dateError) {
      alert("Por favor, selecione uma data disponível.");
      return;
    }

    setIsProcessing(true);
    try {
      // Criamos o pedido no backend (endpoint público para clientes)
      const response = await axios.post(`${API_URL}/pedidos/publico`, {
        ...bookingData,
        servico_id: cart[0].id,
        valor: cart[0].valor
      });

      const { checkout_url } = response.data;
      
      // Redireciona o usuário para o Checkout do Mercado Pago
      window.location.href = checkout_url;
    } catch (err) {
      console.error("Erro ao processar reserva:", err);
      alert("Ocorreu um erro ao gerar o pagamento. Tente novamente.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div style={styles.container}>
      {/* Hero Section Cromático */}
      <div style={styles.hero}>
        <div style={styles.heroOverlay}>
          <h1 style={styles.heroTitle}>Viva a Magia da Serra</h1>
          <p style={styles.heroSubtitle}>Transfers exclusivos e experiências inesquecíveis em Gramado e Canela</p>
        </div>
      </div>

      {step === 'catalog' ? (
        <>
      {/* Dicas de Gramado (Diferencial) */}
      <section style={styles.tipsSection}>
        <h2 style={styles.sectionTitle}>Dicas da Serra 🏔️</h2>
        <div style={styles.tipsGrid}>
          {gramadoTips.map(tip => (
            <div key={tip.id} style={styles.tipCard}>
              <span style={styles.tipIcon}>{tip.icon}</span>
              <h4 style={styles.tipTitle}>{tip.title}</h4>
              <p style={styles.tipDesc}>{tip.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <h2 style={styles.sectionTitle}>Nossos Serviços</h2>
      <nav style={styles.nav}>
        {['TRANSFERS', 'INGRESSOS', 'PACOTES', 'EXPERIENCIAS'].map(cat => (
          <button 
            key={cat} 
            onClick={() => setCategory(cat)}
            style={category === cat ? styles.navBtnActive : styles.navBtn}
          >
            {cat}
          </button>
        ))}
      </nav>

      <div style={styles.grid}>
        {services.filter(s => (s.categoria || s.tipo) === category).map(service => (
          <div key={service.id} style={styles.card}>
            {service.imagem_url ? (
              <img src={service.imagem_url} alt={service.nome} style={styles.image} />
            ) : (
              <div style={styles.imagePlaceholder}>📸</div>
            )}
            <div style={styles.cardContent}>
              <div style={styles.categoryBadge}>{service.categoria || 'PREMIUM'}</div>
              <h3 style={styles.cardTitle}>{service.nome}</h3>
              <p style={styles.cardDesc}>{service.descricao}</p>
              
              {/* Atributos do Veículo/Serviço */}
              <div style={styles.attributes}>
                <span title="Passageiros">👤 {service.capacidade_passageiros || 4}</span>
                <span title="Malas">🧳 {service.capacidade_malas || 2}</span>
                <span title="Conforto">✨ Premium</span>
              </div>
            </div>
            <div style={styles.priceRow}>
              <div style={styles.priceContainer}>
                <span style={styles.priceLabel}>Investimento</span>
                <span style={styles.priceValue}>R$ {parseFloat(service.valor || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</span>
              </div>
              <button onClick={() => addToCart(service)} style={styles.addBtn}>Selecionar</button>
            </div>
          </div>
        ))}
      </div>

      {/* Seção de Diferenciais */}
      <section style={styles.featuresSection}>
        <div style={styles.featuresGrid}>
          {features.map((f, i) => (
            <div key={i} style={styles.featureItem}>
              <span style={styles.featureIcon}>{f.icon}</span>
              <h5 style={styles.featureTitle}>{f.title}</h5>
              <p style={styles.featureDesc}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Depoimentos */}
      <section style={styles.testimonialSection}>
        <h2 style={styles.sectionTitle}>O que dizem nossos clientes</h2>
        <div style={styles.testimonialGrid}>
          {testimonials.map(t => (
            <div key={t.id} style={styles.testimonialCard}>
              <div style={styles.stars}>{'⭐'.repeat(t.stars)}</div>
              <p style={styles.testimonialText}>"{t.text}"</p>
              <h6 style={styles.testimonialAuthor}>{t.name}</h6>
            </div>
          ))}
        </div>
      </section>
        </>
      ) : (
        <div style={styles.formCard}>
          <h2 style={styles.formTitle}>Quase lá! 🚖</h2>
          <p style={styles.formSubtitle}>Confirme os detalhes para sua reserva premium</p>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Seu Nome Completo</label>
            <input type="text" placeholder="Como podemos te chamar?" style={styles.input} onChange={e => setBookingData({...bookingData, nome: e.target.value})}/>

            <label style={styles.label}>Seu Melhor E-mail</label>
            <input type="email" placeholder="Para receber o comprovante e dados do motorista" style={styles.input} onChange={e => setBookingData({...bookingData, email: e.target.value})}/>

            <label style={styles.label}>Seu WhatsApp</label>
            <input type="tel" placeholder="Ex: 54999999999" style={styles.input} onChange={e => setBookingData({...bookingData, telefone: e.target.value})}/>

            <label style={styles.label}>Ponto de Partida</label>
            <input type="text" placeholder="Ex: Aeroporto Salgado Filho" style={styles.input} onChange={e => setBookingData({...bookingData, origem: e.target.value})}/>

            <label style={styles.label}>Destino</label>
            <input type="text" placeholder="Ex: Hotel em Gramado" style={styles.input} onChange={e => setBookingData({...bookingData, destino: e.target.value})}/>
            
            <div style={{display: 'flex', gap: '10px'}}>
              <div style={{flex: 1}}>
                <label>Data</label>
                <input 
                  type="date" 
                  min={new Date().toISOString().split('T')[0]}
                  onChange={e => handleDateChange(e.target.value)} 
                  style={{...styles.input, borderColor: dateError ? '#ef4444' : '#f1f5f9'}}
                />
              </div>
              <div style={{flex: 1}}>
                <label>Hora</label>
                <input type="time" onChange={e => setBookingData({...bookingData, hora: e.target.value})} style={styles.input}/>
              </div>
            </div>
            {dateError && <p style={styles.errorText}>{dateError}</p>}
          </div>
          <button onClick={handleCheckout} style={styles.finishBtnFull} disabled={isProcessing}>
            {isProcessing ? "Processando..." : "Pagar e Confirmar Agora"}
          </button>
          <button onClick={() => setStep('catalog')} style={styles.backBtn}>Voltar ao catálogo</button>
        </div>
      )}

    </div>
  );
}

const styles = {
  container: { fontFamily: '"Inter", sans-serif', padding: '0 0 40px 0', maxWidth: '900px', margin: '0 auto', background: '#f5f3ff', minHeight: '100vh' },
  hero: { 
    height: '400px', 
    backgroundImage: 'url("https://images.unsplash.com/photo-1626014903708-3607062400f0?q=80&w=1200")', 
    backgroundSize: 'cover', 
    backgroundPosition: 'center',
    borderRadius: '0 0 60px 60px',
    position: 'relative',
    overflow: 'hidden',
    marginBottom: '30px'
  },
  heroOverlay: {
    position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
    background: 'linear-gradient(to bottom, rgba(30, 27, 75, 0.2), rgba(76, 29, 149, 0.85))',
    display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: '20px', textAlign: 'center'
  },
  heroTitle: { color: '#fff', fontSize: '42px', fontWeight: '900', margin: 0, textShadow: '0 4px 15px rgba(0,0,0,0.4)', letterSpacing: '-1px' },
  heroSubtitle: { color: 'rgba(255,255,255,0.95)', fontSize: '18px', marginTop: '15px', maxWidth: '600px', fontWeight: '400' },
  
  sectionTitle: { fontSize: '26px', color: '#1e1b4b', fontWeight: '800', margin: '40px 20px 25px 20px', letterSpacing: '-0.5px' },
  
  tipsSection: { padding: '0 20px' },
  tipsGrid: { display: 'flex', gap: '15px', overflowX: 'auto', paddingBottom: '10px', scrollbarWidth: 'none' },
  tipCard: { minWidth: '180px', background: '#fff', padding: '20px', borderRadius: '25px', boxShadow: '0 10px 15px rgba(76, 29, 149, 0.05)', border: '1px solid #ede9fe' },
  tipIcon: { fontSize: '30px', display: 'block', marginBottom: '10px' },
  tipTitle: { fontSize: '14px', fontWeight: '700', color: '#4c1d95', margin: '0 0 5px 0' },
  tipDesc: { fontSize: '12px', color: '#64748b', margin: 0, lineHeight: '1.4' },

  nav: { display: 'flex', gap: '10px', marginBottom: '25px', padding: '0 20px', overflowX: 'auto', scrollbarWidth: 'none' },
  navBtn: { padding: '12px 24px', borderRadius: '25px', border: '1px solid #ddd', cursor: 'pointer', background: '#fff', color: '#64748b', fontWeight: '600', whiteSpace: 'nowrap', transition: '0.3s' },
  navBtnActive: { padding: '12px 24px', borderRadius: '25px', border: 'none', background: '#7c3aed', color: '#fff', cursor: 'pointer', fontWeight: '700', boxShadow: '0 10px 20px rgba(124, 58, 237, 0.3)', whiteSpace: 'nowrap' },
  
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '25px', padding: '0 20px' },
  card: { background: '#fff', padding: '0', borderRadius: '35px', overflow: 'hidden', boxShadow: '0 25px 40px -10px rgba(76, 29, 149, 0.12)', border: '1px solid rgba(255,255,255,0.7)', transition: 'transform 0.3s' },
  image: { width: '100%', height: '200px', objectFit: 'cover' },
  imagePlaceholder: { width: '100%', height: '200px', background: '#e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  cardContent: { padding: '20px 20px 10px 20px' },
  categoryBadge: { fontSize: '10px', fontWeight: '800', color: '#7c3aed', background: '#f5f3ff', padding: '4px 10px', borderRadius: '8px', display: 'inline-block', marginBottom: '10px' },
  cardTitle: { fontSize: '18px', fontWeight: '800', color: '#1e1b4b', margin: '0 0 8px 0' },
  cardDesc: { fontSize: '13px', color: '#64748b', margin: '0 0 15px 0', lineHeight: '1.5' },
  attributes: { display: 'flex', gap: '15px', fontSize: '12px', color: '#94a3b8', fontWeight: '600', marginBottom: '10px' },
  priceRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', padding: '0 20px 20px 20px' },
  priceContainer: { display: 'flex', flexDirection: 'column' },
  priceLabel: { fontSize: '10px', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase' },
  priceValue: { fontSize: '18px', fontWeight: '900', color: '#4c1d95' },
  addBtn: { background: '#7c3aed', color: '#fff', border: 'none', padding: '12px 18px', borderRadius: '18px', fontWeight: '700', cursor: 'pointer', boxShadow: '0 8px 15px rgba(124, 58, 237, 0.2)' },

  featuresSection: { padding: '40px 20px' },
  featuresGrid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' },
  featureItem: { textAlign: 'center', padding: '20px', background: 'rgba(255,255,255,0.5)', borderRadius: '25px', border: '1px solid #ede9fe' },
  featureIcon: { fontSize: '24px', display: 'block', marginBottom: '10px' },
  featureTitle: { fontSize: '14px', fontWeight: '800', color: '#1e1b4b', margin: '0 0 5px 0' },
  featureDesc: { fontSize: '11px', color: '#64748b', margin: 0 },

  testimonialSection: { padding: '20px 20px 40px 20px' },
  testimonialGrid: { display: 'flex', gap: '20px', overflowX: 'auto', scrollbarWidth: 'none', padding: '10px 0' },
  testimonialCard: { minWidth: '260px', background: '#fff', padding: '25px', borderRadius: '30px', boxShadow: '0 15px 30px rgba(0,0,0,0.03)' },
  stars: { fontSize: '12px', marginBottom: '10px' },
  testimonialText: { fontSize: '14px', color: '#475569', fontStyle: 'italic', lineHeight: '1.6', marginBottom: '15px' },
  testimonialAuthor: { fontSize: '13px', fontWeight: '800', color: '#1e1b4b', margin: 0 },
  
  formCard: { background: '#fff', padding: '40px', borderRadius: '40px', margin: '0 20px', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)' },
  formTitle: { fontSize: '28px', color: '#1e1b4b', textAlign: 'center', margin: 0 },
  formSubtitle: { textAlign: 'center', color: '#64748b', marginBottom: '30px' },
  label: { fontSize: '12px', fontWeight: '800', color: '#4c1d95', marginLeft: '5px', textTransform: 'uppercase' },
  inputGroup: { display: 'flex', flexDirection: 'column', gap: '15px', margin: '20px 0' },
  input: { padding: '15px', borderRadius: '18px', border: '2px solid #f1f5f9', fontSize: '16px', outline: 'none', transition: '0.3s' },
  errorText: { color: '#ef4444', fontSize: '12px', fontWeight: 'bold', margin: '-5px 0 10px 5px' },
  mapContainer: { height: '250px', borderRadius: '25px', overflow: 'hidden', border: '2px solid #f1f5f9', marginBottom: '10px' },
  finishBtnFull: { width: '100%', background: '#22c55e', color: '#fff', border: 'none', padding: '18px', borderRadius: '20px', fontWeight: '800', fontSize: '18px', cursor: 'pointer', boxShadow: '0 15px 30px rgba(34, 197, 94, 0.4)' },
  backBtn: { width: '100%', background: 'transparent', color: '#94a3b8', border: 'none', marginTop: '15px', cursor: 'pointer', fontWeight: '600' }
};