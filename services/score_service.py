from repositories.clientes_repository import ClientesRepository
from exceptions.auth_exceptions import ClienteNaoEncontradoError
from utils.formatters import formatar_cpf

class ScoreService:
    def __init__(self, clientes_repo: ClientesRepository = None):
        self.clientes_repo = clientes_repo or ClientesRepository()

    def calcular_score(self, renda_mensal: float, tipo_emprego: str, despesas_fixas: float, num_dependentes: str, tem_dividas: str) -> dict:
        peso_emprego = { "formal": 300, "autônomo": 200, "desempregado": 0 }
        
        if num_dependentes in ["0", "1", "2"]:
            dep_key = int(num_dependentes)
        elif num_dependentes in ["3", "3+"]:
            dep_key = "3+"
        else:
            dep_key = "3+"
            
        peso_dependentes = { 0: 100, 1: 80, 2: 60, "3+": 30 }
        
        # Aceita sim, s, não, nao, n (case insensitive)
        td = str(tem_dividas).lower().strip()
        has_dividas = "sim" if td in ["sim", "s", "true", "1"] else "não"
        peso_dividas = { "sim": -100, "não": 100 }

        if tipo_emprego.lower() not in peso_emprego:
            raise ValueError("Tipo de emprego inválido. Use: formal, autônomo ou desempregado.")

        p_emprego = peso_emprego[tipo_emprego.lower()]
        p_dep = peso_dependentes.get(dep_key, 30)
        p_dividas = peso_dividas[has_dividas]

        score = (
            (renda_mensal / (despesas_fixas + 1)) * 30 +
            p_emprego +
            p_dep +
            p_dividas
        )

        score_final = int(min(max(score, 0), 1000))

        return {
            "score_calculado": score_final,
            "detalhes": {
                "renda": renda_mensal,
                "despesas": despesas_fixas,
                "emprego": tipo_emprego,
                "dependentes": num_dependentes,
                "dividas": has_dividas
            }
        }

    def atualizar_score(self, cpf: str, novo_score: int) -> dict:
        cpf_formatado = formatar_cpf(cpf)
        cliente = self.clientes_repo.get_by_cpf(cpf_formatado)
        if not cliente:
            raise ClienteNaoEncontradoError("Cliente não encontrado. Score não atualizado.")
            
        score_anterior = int(cliente['score_credito'])
        self.clientes_repo.update_score(cpf_formatado, novo_score)
        
        return {
            "cpf": cpf_formatado,
            "score_anterior": score_anterior,
            "score_novo": novo_score
        }
