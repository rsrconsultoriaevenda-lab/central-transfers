export default function PedidoCard({ pedido }) {
  const statusColor = {
    PENDENTE: "#f59e0b",
    ACEITO: "#3b82f6",
    FINALIZADO: "#10b981"
  };

  return (
    <div style={styles.card}>
      <h3>Pedido #{pedido.id}</h3>

      <p><b>Serviço:</b> {pedido.servico}</p>
      <p><b>Origem:</b> {pedido.origem}</p>
      <p><b>Destino:</b> {pedido.destino}</p>

      <span style={{
        background: statusColor[pedido.status] || "#999",
        color: "#fff",
        padding: "5px 10px",
        borderRadius: "8px",
        fontSize: "12px"
      }}>
        {pedido.status}
      </span>
    </div>
  );
}

const styles = {
  card: {
    background: "#fff",
    padding: "15px",
    borderRadius: "12px",
    boxShadow: "0 2px 10px rgba(0,0,0,0.1)"
  }
};