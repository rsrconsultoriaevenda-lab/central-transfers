from decimal import Decimal
from backend.models import Pedido, Motorista


def test_calculo_financeiro_plano_master():
    """Valida se a comissão de 15% é aplicada corretamente para motoristas MASTER."""
    motorista = Motorista(plano="MASTER", comissao_master=Decimal("15.0"))
    pedido = Pedido(valor=Decimal("100.00"), motorista=motorista)

    pedido.calcular_financeiro()

    assert pedido.valor_comissao == Decimal("15.00")
    assert pedido.valor_liquido_motorista == Decimal("85.00")
    assert pedido.tipo_comissao_motorista == "PERCENTUAL_CENTRAL"


def test_calculo_financeiro_plano_mensal():
    """Valida se o motorista MENSAL recebe 100% do valor (comissão zero)."""
    motorista = Motorista(plano="MENSAL")
    pedido = Pedido(valor=Decimal("200.00"), motorista=motorista)

    pedido.calcular_financeiro()

    assert pedido.valor_comissao == Decimal("0.00")
    assert pedido.valor_liquido_motorista == Decimal("200.00")
    assert pedido.tipo_comissao_motorista == "PLANO_MENSAL"


def test_calculo_financeiro_sem_motorista():
    """Valida a comissão padrão da central quando o pedido ainda não foi aceito."""
    pedido = Pedido(valor=Decimal("100.00"), comissao=Decimal("20.0"))
    pedido.calcular_financeiro()

    assert pedido.valor_comissao == Decimal("20.00")
    assert pedido.valor_liquido_motorista == Decimal("80.00")
