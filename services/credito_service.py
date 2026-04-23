from utils.formatters import formatar_cpf
from repositories.clientes_repository import ClientesRepository
from repositories.score_repository import ScoreRepository
from repositories.solicitacoes_repository import SolicitacoesRepository
from exceptions.credito_exceptions import ScoreInsuficienteError, ErroAoGravarSolicitacaoError
from exceptions.auth_exceptions import ClienteNaoEncontradoError
from datetime import datetime

class CreditoService:
    def __init__(
        self, 
        clientes_repo: ClientesRepository = None,
        score_repo: ScoreRepository = None,
        solicitacoes_repo: SolicitacoesRepository = None
    ):
        self.clientes_repo = clientes_repo or ClientesRepository()
        self.score_repo = score_repo or ScoreRepository()
        self.solicitacoes_repo = solicitacoes_repo or SolicitacoesRepository()

    def consultar_limite(self, cpf: str) -> dict:
        cpf_formatado = formatar_cpf(cpf)
        cliente = self.clientes_repo.get_by_cpf(cpf_formatado)
        if not cliente:
            raise ClienteNaoEncontradoError("Cliente não encontrado.")
        return cliente

    def solicitar_aumento(self, cpf: str, novo_limite: float) -> dict:
        cpf_formatado = formatar_cpf(cpf)
        cliente = self.clientes_repo.get_by_cpf(cpf_formatado)
        if not cliente:
            raise ClienteNaoEncontradoError("Cliente não encontrado.")

        # Verifica o score antes de salvar para definir o status final
        score_atual = int(cliente['score_credito'])
        limite_maximo = self.score_repo.get_limite_maximo(score_atual)
        status = "aprovado" if float(novo_limite) <= limite_maximo else "rejeitado"

        solicitacao = {
            'cpf_cliente': cpf_formatado,
            'data_hora_solicitacao': datetime.now().isoformat(),
            'limite_atual': float(cliente['limite_credito']),
            'novo_limite_solicitado': float(novo_limite),
            'status_pedido': status
        }
        
        sucesso = self.solicitacoes_repo.save(solicitacao)
        if not sucesso:
            raise ErroAoGravarSolicitacaoError("Erro ao salvar solicitação.")
            
        return solicitacao

    def verificar_score(self, score_atual: int, novo_limite: float) -> dict:
        limite_maximo = self.score_repo.get_limite_maximo(score_atual)
        aprovado = novo_limite <= limite_maximo
        
        # A atualização do status_pedido no CSV e de limite não está totalmente definida no spec 
        # (se ele aprova, devíamos atualizar). O spec foca em verificar o score vs score_limite.csv
        # Retorna o dict conforme spec
        status = "aprovado" if aprovado else "rejeitado"
        
        if not aprovado:
            raise ScoreInsuficienteError("Score insuficiente para o limite solicitado.")
            
        return {
            "status_pedido": status,
            "score_atual": score_atual,
            "limite_maximo_permitido": limite_maximo,
            "novo_limite_solicitado": novo_limite
        }
