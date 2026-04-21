export default function Sidebar() {
  return (
    <div style={styles.sidebar}>
      <h2>🚗 SaaS Transfers</h2>

      <nav style={styles.nav}>
        <p>📊 Dashboard</p>
        <p>🚕 Corridas</p>
        <p>👨‍✈️ Motoristas</p>
        <p>🧾 Serviços</p>
      </nav>
    </div>
  );
}

const styles = {
  sidebar: {
    width: "250px",
    height: "100vh",
    background: "#111827",
    color: "#fff",
    padding: "20px",
    position: "fixed"
  },
  nav: {
    marginTop: "30px",
    display: "flex",
    flexDirection: "column",
    gap: "15px",
    cursor: "pointer"
  }
};