import phonenumbers
from phonenumbers import NumberParseException


def formatar_telefone_e164(numero: str, region: str = "BR") -> str:
    """
    Converte qualquer telefone para formato E.164 (+55...)
    """

    try:
        # tenta interpretar o número
        parsed = phonenumbers.parse(numero, region)

        # valida se é um número possível/real
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Número de telefone inválido")

        # retorna no formato internacional E.164
        return phonenumbers.format_number(
        parsed,
        phonenumbers.PhoneNumberFormat.E164
    )

    except NumberParseException:
        raise ValueError("Formato de telefone inválido")