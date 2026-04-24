import re
from datetime import datetime

def validar_cpf(cpf: str) -> bool:
    """Valida formato básico e tamanho de CPF."""
    numeros = re.sub(r'\D', '', cpf)
    return len(numeros) == 11

def validar_data_nascimento(data: str) -> bool:
    """Valida se a data está no formato DD/MM/YYYY e é uma data válida."""
    try:
        datetime.strptime(data, "%d/%m/%Y")
        return True
    except ValueError:
        return False
