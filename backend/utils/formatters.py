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

def formatar_data(data: str) -> str:
    """Tenta converter formatos variados (DD MM AAAA, DD-MM-AAAA) para DD/MM/YYYY"""
    # Remove qualquer caractere que não seja número, barra, espaço ou hífen
    limpo = re.sub(r'[^0-9/ -]', '', data)
    # Substitui espaços ou hifens por barras
    limpo = re.sub(r'[ -]', '/', limpo)
    # Remove barras duplicadas
    limpo = re.sub(r'/+', '/', limpo)
    
    # Se tiver apenas números (ex: 20122005)
    nums = re.sub(r'\D', '', limpo)
    if len(nums) == 8:
        return f"{nums[:2]}/{nums[2:4]}/{nums[4:]}"
    
    return limpo
