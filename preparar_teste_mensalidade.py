from backend.database import SessionLocal
from backend import models
from datetime import datetime, timedelta

def preparar():
    db = SessionLocal()
    # Busca o primeiro motorista mensal
    m = db.query(models.Motorista).filter(models.Motorista.plano == "MENSAL").first()
    
    if m:
        # Força o início do trial para 15 dias atrás (para expirar os 14 dias)
        m.data_inicio_trial = datetime.now() - timedelta(days=15)
        m.status = "ATIVO"
        
        # Remove mensalidades deste mês para este motorista (se existirem)
        mes_atual = datetime.now().strftime("%Y-%m")
        db.query(models.Mensalidade).filter(
            models.Mensalidade.motorista_id == m.id,
            models.Mensalidade.mes_referencia == mes_atual
        ).delete()
        
        db.commit()
        print(f"✅ Motorista {m.nome} preparado para teste de mensalidade.")
    db.close()

if __name__ == "__main__":
    preparar()