from .auth_exceptions import ClienteNaoEncontradoError, CredenciaisInvalidasError, MaxTentativasAtingidasError
from .credito_exceptions import ScoreInsuficienteError, ErroAoGravarSolicitacaoError
from .cambio_exceptions import APIIndisponivelError, MoedaNaoSuportadaError

__all__ = [
    "ClienteNaoEncontradoError", "CredenciaisInvalidasError", "MaxTentativasAtingidasError",
    "ScoreInsuficienteError", "ErroAoGravarSolicitacaoError",
    "APIIndisponivelError", "MoedaNaoSuportadaError"
]
