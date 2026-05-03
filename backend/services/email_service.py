import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

def enviar_email_transacional(destinatario, assunto, html_body):
    """
    Envia e-mails transacionais via SMTP.
    Configurar variáveis de ambiente: SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_user or not smtp_pass:
        logger.warning("⚠️ SMTP não configurado. E-mail não enviado.")
        return

    msg = MIMEMultipart()
    msg['From'] = f"Central Transfers <{smtp_user}>"
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, destinatario, msg.as_string())
        server.quit()
        logger.info(f"📧 E-mail enviado com sucesso para {destinatario}")
    except Exception as e:
        logger.error(f"💥 Erro ao enviar e-mail: {e}")

def notificar_cliente_motorista_atribuido(pedido):
    if not pedido.cliente.email:
        return

    assunto = f"🚗 Motorista Confirmado! Pedido #{pedido.id}"
    html = f"""
    <div style="font-family: sans-serif; color: #1e1b4b;">
        <h2 style="color: #4c1d95;">Olá, {pedido.cliente.nome}!</h2>
        <p>Seu motorista já foi designado para o serviço de <strong>{pedido.servico.nome}</strong>.</p>
        <div style="background: #f5f3ff; padding: 20px; border-radius: 15px; border: 1px solid #ddd;">
            <p><strong>Motorista:</strong> {pedido.motorista.nome}</p>
            <p><strong>Veículo:</strong> {pedido.motorista.carro} ({pedido.motorista.placa})</p>
            <p><strong>WhatsApp:</strong> {pedido.motorista.telefone}</p>
        </div>
        <p style="margin-top: 20px;">O motorista entrará em contato em breve.</p>
    </div>
    """
    enviar_email_transacional(pedido.cliente.email, assunto, html)