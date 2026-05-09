import React from 'react';
import { useWebSocketNotifications } from '../hooks/useWebSocketNotifications';
# Lógica sugerida para o endpoint PUT /pedidos/{id}/aceitar
@router.put("/{pedido_id}/aceitar")
async def aceitar_pedido(pedido_id: int, data: dict, db: Session = Depends(get_db)):
    motorista_id = data.get("motorista_id")
    
    # .with_for_update() é a chave aqui. Ele bloqueia a linha no PostgreSQL/MySQL
    # até que o db.commit() seja executado.
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id
    ).with_for_update().first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Verificação atômica: se o status não for mais 'PAGO', alguém já aceitou
    if pedido.status != "PAGO" or pedido.motorista_id is not None:
        raise HTTPException(
            status_code=400, 
            detail="Este pedido já foi aceito por outro motorista ou não está mais disponível."
        )

    # Atribui o motorista e muda o status
    pedido.motorista_id = motorista_id
    pedido.status = "ACEITO"
    
    db.commit() # Aqui o lock é liberado e os outros motoristas recebem o erro acima
    return pedido
import axios from 'axios'; // Assumindo o uso de axios para chamadas API

const DriverNotificationOverlay = ({ motoristaId }) => {
  const { novaNotificacao, limparNotificacao } = useWebSocketNotifications(motoristaId);

  if (!novaNotificacao) return null;

  const aceitarPedido = async () => {
    try {
      const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8001';
      // Chamada para o endpoint de aceite
      await axios.put(`${apiBase}/pedidos/${novaNotificacao.pedido_id}/aceitar`, {
        motorista_id: motoristaId
      });
      
      alert("Sucesso! O pedido agora é seu. Dirija com cuidado!");
      limparNotificacao();
    } catch (error) {
      // Tratamento de erro de concorrência (Status 400 ou 409)
      if (error.response && error.response.status === 400) {
        alert("Tarde demais! Outro motorista aceitou este pedido alguns milissegundos antes.");
      } else {
        alert("Ocorreu um erro ao aceitar o pedido. Verifique sua conexão.");
      }
      limparNotificacao();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl animate-bounce">
        <div className="text-center">
          <div className="bg-green-100 text-green-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">🚖</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Novo Pedido!</h2>
          <p className="text-gray-600 mb-4">{novaNotificacao.mensagem}</p>
          <div className="text-3xl font-black text-indigo-600 mb-6">
            R$ {novaNotificacao.valor}
          </div>
          
          <div className="flex flex-col gap-3">
            <button 
              onClick={aceitarPedido}
              className="bg-indigo-600 text-white font-bold py-4 rounded-xl hover:bg-indigo-700 transition"
            >
              ACEITAR AGORA
            </button>
            <button 
              onClick={limparNotificacao}
              className="text-gray-400 font-medium py-2"
            >
              Recusar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DriverNotificationOverlay;