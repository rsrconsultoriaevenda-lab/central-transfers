from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend import models
from datetime import datetime, timedelta
from backend.auth import get_usuario_atual

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(usuario=Depends(get_usuario_atual)):
    return {
"clientes": 12,
"motoristas": 5,
"pedidos": 23
}

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    # Filtramos apenas pedidos que entraram dinheiro no sistema
    pedidos_pagos = db.query(models.Pedido).filter(
        models.Pedido.status.in_(["PAGO", "CONCLUIDO"])
    ).all()

    total_bruto = sum(p.valor for p in pedidos_pagos)

    # O Lucro Líquido é a parte da central
    lucro_liquido = sum(float(p.valor_comissao or 0) for p in pedidos_pagos)

    # O repasse é o que vai para os motoristas
    repasse_motoristas = float(total_bruto) - float(lucro_liquido)

    # Contagem de pedidos por status para o gráfico
    stats_status = db.query(
        models.Pedido.status,
        func.count(models.Pedido.id)
    ).group_by(models.Pedido.status).all()

    return {
        "faturamento_bruto": total_bruto,
        "lucro_liquido": lucro_liquido,
        "repasse_motoristas": repasse_motoristas,
        "total_pedidos": len(pedidos_pagos),
        "resumo_status": {status: count for status, count in stats_status}
    }
