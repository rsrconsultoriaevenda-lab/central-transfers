import logging
import mercadopago
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from backend.config import settings
from backend import models
from backend.services.notifier_service import notifier
from backend.services.whatsapp_service import enviar_whatsapp_meta

logger = logging.getLogger("PaymentService")


class PaymentService:
    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    def get_payment_details(self, payment_id: str):
        """Consulta a API do Mercado Pago para obter detalhes do pagamento."""
        try:
            payment_info = self.sdk.payment().get(payment_id)
            if payment_info.get("status") == 200:
                return payment_info.get("response")
            logger.error(
                f"Erro ao buscar pagamento {payment_id} no MP: {payment_info}")
                return None
        except Exception as e:
            logger.error(f"Exceção ao consultar API do Mercado Pago: {str(e)}")
            return None

    async def process_payment_update(self, payment_id: str, db: Session):
        """Processa a atualização de um pagamento e reflete no banco de dados."""
        data = self.get_payment_details(payment_id)
        if not data:
            return False

        status_mp = data.get("status")
        external_ref = data.get("external_reference")

        if status_mp != "approved":
            logger.info(
                f"Pagamento {payment_id} com status: {status_mp}. Ignorando processamento.")
                return False

        if not external_ref:
            logger.warning(
                f"Pagamento {payment_id} aprovado mas sem external_reference.")
                return False

        # 1. Caso seja MENSALIDADE
        if external_ref.startswith("MENSAL_"):
            return await self._process_mensalidade(external_ref, db)

        # 2. Caso seja PEDIDO
        if external_ref.startswith("PEDIDO_") or external_ref.isdigit():
            return await self._process_pedido(external_ref, db)

        return False

    async def _process_mensalidade(self, external_ref: str, db: Session):
        mensalidade_id = int(external_ref.replace("MENSAL_", ""))

        # CORRIGIDO: Removido o 'models.models' duplicado que causaria erro
        mensalidade = db.query(models.Mensalidade).filter(
            models.Mensalidade.id == mensalidade_id
        ).with_for_update().first()

        if mensalidade and mensalidade.status != "PAGO":
            mensalidade.status = "PAGO"
            mensalidade.data_pagamento = datetime.now(timezone.utc)

            # Reativa motorista se necessário
            motorista = mensalidade.motorista
            if motorista and motorista.status == "TRIAL_EXPIRADO":
                motorista.status = "ATIVO"
                if settings.WHATSAPP_TOKEN:
                    enviar_whatsapp_meta(
                        motorista.telefone, "✅ Sua mensalidade foi confirmada! Conta reativada.")

                        db.commit()
                        logger.info(
                            f"Mensalidade {mensalidade_id} confirmada com sucesso.")
                            return True
                return False

    async def _process_pedido(self, external_ref: str, db: Session):
        pedido_id_raw = external_ref.replace("PEDIDO_", "")
        pedido_id = int(pedido_id_raw)

        pedido = db.query(models.Pedido).filter(
            models.Pedido.id == pedido_id
        ).with_for_update().first()

        if pedido and pedido.status in ["PENDENTE", "AGUARDANDO_PAGAMENTO"]:
            pedido.status = models.StatusPedido.PAGO
            db.commit()

            # Dispara notificações via notifier global
            await notifier.broadcast({"type": "NEW_ORDER", "pedido_id": pedido.id, "msg": "Novo pedido pago!"})
            logger.info(f"Pedido {pedido_id} marcado como PAGO.")
            return True
        return False