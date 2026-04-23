from repositories.clientes_repository import ClientesRepository
from exceptions.auth_exceptions import ClienteNaoEncontradoError
from utils.formatters import formatar_cpf

class ScoreService:
    def __init__(self, clientes_repo: ClientesRepository = None):
        self.clientes_repo = clientes_repo or ClientesRepository()

    def calcular_score(self, renda_mensal: float, tipo_emprego: str, despesas_fixas: float, num_dependentes: str, tem_dividas: str) -> dict:
        # Definição de Pesos para escala 0-1000
        # 1. Renda vs Despesas (Max 400 pontos)
        # Se a sobra for > 50% da renda, ganha pontuação máxima
        sobra = renda_mensal - despesas_fixas
        percentual_sobra = (sobra / (renda_mensal + 1)) * 100
        pontos_renda = min(max(percentual_sobra * 4, 0), 400)

        # 2. Tipo de Emprego (Max 300 pontos)
        pesos_emprego = { 
            "formal": 300, "clt": 300, "concursado": 300,
            "autônomo": 200, "autonomo": 200, "empresário": 200, "empresario": 200, "pj": 200,
            "desempregado": 0, "estudante": 50, "aposentado": 250
        }
        tp = str(tipo_emprego).lower().strip()
        p_emprego = pesos_emprego.get(tp, 0)

        # 3. Dependentes (Max 150 pontos)
        try:
            n_dep = int(str(num_dependentes).replace("+", ""))
        except:
            n_dep = 3
        
        if n_dep == 0: p_dep = 150
        elif n_dep == 1: p_dep = 100
        elif n_dep == 2: p_dep = 70
        else: p_dep = 30

        # 4. Dívidas (Max 150 pontos)
        td = str(tem_dividas).lower().strip()
        has_dividas = td in ["sim", "s", "true", "1", "tenho"]
        p_dividas = 0 if has_dividas else 150

        # Cálculo Final
        score_final = int(min(max(pontos_renda + p_emprego + p_dep + p_dividas, 0), 1000))
        
        # Sugestão de novo limite baseado no score
        if score_final >= 800: novo_limite = 15000.0
        elif score_final >= 600: novo_limite = 8000.0
        elif score_final >= 400: novo_limite = 3000.0
        else: novo_limite = 1000.0

        return {
            "score_calculado": score_final,
            "limite_sugerido": novo_limite,
            "detalhes": {
                "renda": renda_mensal,
                "despesas": despesas_fixas,
                "emprego": tp,
                "dependentes": num_dependentes,
                "dividas": "sim" if has_dividas else "não"
            }
        }

    def atualizar_score(self, cpf: str, novo_score: int) -> dict:
        cpf_formatado = formatar_cpf(cpf)
        cliente = self.clientes_repo.get_by_cpf(cpf_formatado)
        if not cliente:
            raise ClienteNaoEncontradoError("Cliente não encontrado. Score não atualizado.")
            
        score_anterior = int(cliente['score_credito'])
        limite_anterior = float(cliente['limite_credito'])
        
        # Define o novo limite com base no novo score
        if novo_score >= 800: novo_limite = 15000.0
        elif novo_score >= 600: novo_limite = 8000.0
        elif novo_score >= 400: novo_limite = 3000.0
        else: novo_limite = 1000.0
        
        # Se o score aumentou, o limite aumenta. Se o score diminuiu drasticamente, mantemos ou reduzimos levemente?
        # Para fins de teste técnico, vamos seguir a sugestão do score.
        self.clientes_repo.update_score_e_limite(cpf_formatado, novo_score, novo_limite)
        
        return {
            "cpf": cpf_formatado,
            "score_anterior": score_anterior,
            "score_novo": novo_score,
            "limite_anterior": limite_anterior,
            "limite_novo": novo_limite
        }
