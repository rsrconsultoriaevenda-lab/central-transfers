import { useEffect, useState } from "react";
import api from "./services/api";

function App() {
  const [pedidos, setPedidos] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [servicos, setServicos] = useState([]);
  const [form, setForm] = useState({
    cliente_id: "",
    servico_id: "",
    origem: "",
    destino: "",
    data_servico: "",
    valor: "",
    observacoes: "",
  });
  const [message, setMessage] = useState(null);

  useEffect(() => {
    carregarDados();
  }, []);

  async function carregarDados() {
    try {
      const [pedidosRes, clientesRes, servicosRes] = await Promise.all([
        api.get("/pedidos"),
        api.get("/clientes"),
        api.get("/servicos"),
      ]);

      setPedidos(pedidosRes.data);
      setClientes(clientesRes.data);
      setServicos(servicosRes.data);
    } catch (err) {
      console.error(err);
      setMessage("Erro ao carregar dados. Verifique o backend.");
    }
  }

  async function criarPedido(event) {
    event.preventDefault();
    setMessage(null);

    try {
      await api.post("/pedidos", {
        cliente_id: Number(form.cliente_id),
        servico_id: Number(form.servico_id),
        origem: form.origem,
        destino: form.destino,
        data_servico: new Date(form.data_servico).toISOString(),
        valor: Number(form.valor),
        observacoes: form.observacoes,
      });

      setForm({
        cliente_id: "",
        servico_id: "",
        origem: "",
        destino: "",
        data_servico: "",
        valor: "",
        observacoes: "",
      });
      setMessage("Pedido criado com sucesso.");
      carregarDados();
    } catch (err) {
      console.error(err);
      setMessage(err.response?.data?.detail || "Erro ao criar pedido.");
    }
  }

  return (
    <div style={{ padding: 20, fontFamily: "Arial, sans-serif", maxWidth: 960, margin: "0 auto", background: "#282a36", color: "#f8f8f2" }}>
      <h1>Central Transfers</h1>
      <p>Faça pedidos de transferência diretamente para a central.</p>

      {message && (
        <div style={{ marginBottom: 12, padding: 10, background: "#44475a", borderRadius: 6, color: "#f8f8f2" }}>
          {message}
        </div>
      )}

      <section style={{ marginBottom: 40 }}>
        <h2>Novo pedido</h2>
        <form onSubmit={criarPedido} style={{ display: "grid", gap: 12, maxWidth: 500 }}>
          <label>
            Cliente
            <select
              value={form.cliente_id}
              onChange={(e) => setForm({ ...form, cliente_id: e.target.value })}
              required
              style={{ width: "100%", padding: 8 }}
            >
              <option value="">Selecione um cliente</option>
              {clientes.map((c) => (
                <option key={c.id} value={c.id}>{c.nome}</option>
              ))}
            </select>
          </label>

          <label>
            Serviço
            <select
              value={form.servico_id}
              onChange={(e) => setForm({ ...form, servico_id: e.target.value })}
              required
              style={{ width: "100%", padding: 8 }}
            >
              <option value="">Selecione um serviço</option>
              {servicos.map((s) => (
                <option key={s.id} value={s.id}>{s.nome} - {s.tipo}</option>
              ))}
            </select>
          </label>

          <label>
            Origem
            <input
              type="text"
              value={form.origem}
              onChange={(e) => setForm({ ...form, origem: e.target.value })}
              required
              style={{ width: "100%", padding: 8 }}
            />
          </label>

          <label>
            Destino
            <input
              type="text"
              value={form.destino}
              onChange={(e) => setForm({ ...form, destino: e.target.value })}
              required
              style={{ width: "100%", padding: 8 }}
            />
          </label>

          <label>
            Data do serviço
            <input
              type="datetime-local"
              value={form.data_servico}
              onChange={(e) => setForm({ ...form, data_servico: e.target.value })}
              required
              style={{ width: "100%", padding: 8 }}
            />
          </label>

          <label>
            Valor
            <input
              type="number"
              step="0.01"
              value={form.valor}
              onChange={(e) => setForm({ ...form, valor: e.target.value })}
              required
              style={{ width: "100%", padding: 8 }}
            />
          </label>

          <label>
            Observações
            <textarea
              value={form.observacoes}
              onChange={(e) => setForm({ ...form, observacoes: e.target.value })}
              style={{ width: "100%", padding: 8, minHeight: 80 }}
            />
          </label>

          <button type="submit" style={{ padding: "10px 16px", background: "#bd93f9", color: "#282a36", border: "none", borderRadius: 6, cursor: "pointer" }}>
            Enviar pedido
          </button>
        </form>
      </section>

      <section>
        <h2>Pedidos</h2>
        {pedidos.length === 0 ? (
          <p>Nenhum pedido encontrado.</p>
        ) : (
          pedidos.map((p) => (
            <div key={p.id} style={{ background: "#373a4f", border: "1px solid #6272a4", borderRadius: 8, padding: 16, marginBottom: 14 }}>
              <strong>{p.cliente_nome || `Cliente ${p.cliente_id}`}</strong> — <span>{p.servico_nome || `Serviço ${p.servico_id}`}</span>
              <p><b>Origem:</b> {p.origem}</p>
              <p><b>Destino:</b> {p.destino}</p>
              <p><b>Data:</b> {new Date(p.data_servico).toLocaleString()}</p>
              <p><b>Valor:</b> R$ {p.valor}</p>
              <p><b>Status:</b> {p.status || "PENDENTE"}</p>
              <p><b>Motorista:</b> {p.motorista_nome || "Ainda não atribuído"}</p>
            </div>
          ))
        )}
      </section>
    </div>
  );
}

export default App;
