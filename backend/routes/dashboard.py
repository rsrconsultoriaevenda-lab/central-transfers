from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend import models
from datetime import datetime, timedelta
from backend.auth import get_usuario_atual
from decimal import Decimal

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db), usuario: dict = Depends(get_usuario_atual)):
    # Use SQL Aggregations for better performance and precision
    stats_query = db.query(
        func.sum(models.Pedido.valor).label("total_bruto"),
        func.sum(models.Pedido.valor_comissao).label("lucro_liquido"),
        func.count(models.Pedido.id).label("total_pedidos")
    ).filter(
        models.Pedido.status.in_(["PAGO", "CONCLUIDO"])
    ).first()

    total_bruto = stats_query.total_bruto or Decimal("0.00")
    lucro_liquido = stats_query.lucro_liquido or Decimal("0.00")
    total_pedidos = stats_query.total_pedidos or 0

    # Repasse é a diferença (Bruto - Comissão da Central)
    repasse_motoristas = total_bruto - lucro_liquido

    # Contagem de pedidos por status para o gráfico
    stats_status = db.query(
        models.Pedido.status,
        func.count(models.Pedido.id)
    ).group_by(models.Pedido.status).all()

    return {
        "faturamento_bruto": float(total_bruto),
        "lucro_liquido": float(lucro_liquido),
        "repasse_motoristas": float(repasse_motoristas),
        "total_pedidos": total_pedidos,
        "resumo_status": {status: count for status, count in stats_status}
    }
