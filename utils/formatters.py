import re

def formatar_cpf(cpf: str) -> str:
    """Garante que o CPF está no formato XXX.XXX.XXX-XX"""
    numeros = re.sub(r'\D', '', cpf)
    if len(numeros) == 11:
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    return cpf

def formatar_moeda(valor: float) -> str:
    """Formata valor float para R$ XX.XX"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
