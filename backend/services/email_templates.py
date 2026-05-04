from backend.models import Motorista


def get_welcome_email_html(motorista: Motorista):
    """Retorna o template HTML de boas-vindas para o motorista."""
    primary_color = "#4c1d95"
    # Ajuste para sua URL de produção
    login_url = "https://centraltransfers.com/driver"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ background-color: {primary_color}; padding: 40px 20px; text-align: center; color: #ffffff; }}
            .content {{ padding: 30px; color: #1e293b; line-height: 1.6; }}
            .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; color: #64748b; font-size: 12px; }}
            .button {{ display: inline-block; padding: 14px 28px; background-color: {primary_color}; color: #ffffff !important; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 20px; }}
            .info-box {{ background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; margin-top: 20px; }}
            .highlight {{ color: {primary_color}; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin:0; font-size: 24px;">Bem-vindo(a) à Frota!</h1>
            </div>
            <div class="content">
                <p>Olá, <span class="highlight">{motorista.nome}</span>,</p>
                <p>É um prazer ter você conosco! Seu cadastro na <strong>Central Transfers</strong> foi analisado e <strong>APROVADO</strong>.</p>
                
                <p>A partir de agora, você já pode acessar nossa plataforma e começar a receber solicitações de viagens diretamente no seu celular.</p>
                
                <div class="info-box">
                    <strong>Dados de Acesso:</strong><br>
                    📍 Login: {motorista.telefone}@motorista.com<br>
                    🔑 Senha: (A senha que você cadastrou)
                </div>

                <center>
                    <a href="{login_url}" class="button">Acessar Painel do Motorista</a>
                </center>

                <p style="margin-top: 30px;"><strong>O que fazer agora?</strong></p>
                <ul>
                    <li>Mantenha seu status como "Disponível".</li>
                    <li>Verifique se sua localização está ativa no App.</li>
                    <li>Prepare seu veículo para oferecer a melhor experiência.</li>
                </ul>
            </div>
            <div class="footer">
                <p>© 2024 Central Transfers - Excelência em Mobilidade</p>
                <p>Este é um e-mail automático, por favor não responda.</p>
            </div>
        </div>
    </body>
    </html>
    """


async def enviar_email_boas_vindas(motorista: Motorista):
    """
    Lógica simulada para envio de e-mail. 
    Aqui você integraria com SendGrid, AWS SES ou SMTP.
    """
    html = get_welcome_email_html(motorista)
    destinatario = f"{motorista.telefone}@motorista.com"

    # Exemplo de Log para debug
    print(f"📧 Enviando e-mail de boas-vindas para: {destinatario}")

    # Se você tiver um serviço de SMTP configurado:
    # await send_email(subject="Cadastro Aprovado! Bem-vindo à Central Transfers", html=html, to=destinatario)
    return True
