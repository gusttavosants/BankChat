import re

# Regex que cobre blocos unicode de emojis (símbolos, pictogramas, dingbats, etc.)
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # símbolos & pictogramas
    "\U0001F680-\U0001F6FF"  # transporte & mapas
    "\U0001F1E0-\U0001F1FF"  # bandeiras
    "\U00002500-\U00002BEF"  # CJK e símbolos
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"
    "\U0001f926-\U0001f937"
    "\U00010000-\U0010ffff"
    "\u2640-\u2642"
    "\u2600-\u2B55"
    "\u200d"
    "\u23cf"
    "\u23e9"
    "\u231a"
    "\ufe0f"
    "\u3030"
    "]+",
    flags=re.UNICODE,
)

def clean_llm_response(text: str) -> str:
    """Remove emojis e marcadores markdown (negrito/italico) de respostas da LLM."""
    if not text:
        return text
    # Remove emojis
    text = _EMOJI_PATTERN.sub("", text)
    # Remove marcadores de negrito/italico (**texto**, *texto*, __texto__, _texto_)
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,2}(.*?)_{1,2}', r'\1', text)
    # Limpa espaços extras que podem sobrar
    text = re.sub(r'  +', ' ', text).strip()
    return text

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
