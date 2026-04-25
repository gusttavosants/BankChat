import os
import pandas as pd
from typing import Dict, Any
from utils.logger import log_erro
from core.db import supabase

class SolicitacoesRepository:
    def __init__(self, use_supabase: bool = True, file_path: str = None):
        self.use_supabase = use_supabase
        if not self.use_supabase:
            if file_path is None:
                file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'solicitacoes_aumento_limite.csv')
            self.file_path = file_path
            
            # Cria o arquivo se não existir, com os cabeçalhos
            if not os.path.exists(self.file_path):
                os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
                df = pd.DataFrame(columns=[
                    'cpf_cliente', 'data_hora_solicitacao', 'limite_atual', 
                    'novo_limite_solicitado', 'status_pedido'
                ])
                df.to_csv(self.file_path, index=False)

    def save(self, solicitacao: Dict[str, Any]) -> bool:
        """Salva uma nova solicitação no banco."""
        try:
            if self.use_supabase:
                response = supabase.table('solicitacoes_aumento_limite').insert(solicitacao).execute()
                return True
            else:
                df = pd.DataFrame([solicitacao])
                df.to_csv(self.file_path, mode='a', header=not os.path.exists(self.file_path), index=False)
                return True
        except Exception as e:
            log_erro("SolicitacoesRepository.save", e)
            return False
