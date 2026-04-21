export default function Header() {
  return (
    <div style={styles.header}>
      <h3>Painel Operacional</h3>
    </div>
  );
}

const styles = {
  header: {
    height: "60px",
    background: "#fff",
    borderBottom: "1px solid #ddd",
    display: "flex",
    alignItems: "center",
    paddingLeft: "20px",
    marginLeft: "250px"
  }
};