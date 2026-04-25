import os
import pandas as pd
from typing import Optional
from utils.logger import log_erro
from core.db import supabase

class ClientesRepository:
    def __init__(self, use_supabase: bool = True, file_path: str = None):
        self.use_supabase = use_supabase
        if not self.use_supabase:
            if file_path is None:
                file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'clientes.csv')
            self.file_path = file_path

    def get_by_cpf(self, cpf: str) -> Optional[dict]:
        try:
            if self.use_supabase:
                response = supabase.table('clientes').select('*').eq('cpf', cpf).execute()
                data = response.data
                if data and len(data) > 0:
                    return data[0]
                return None
            else:
                if not os.path.exists(self.file_path):
                    return None
                df = pd.read_csv(self.file_path, dtype={'cpf': str, 'data_nascimento': str})
                cliente_row = df[df['cpf'] == cpf]
                return cliente_row.iloc[0].to_dict() if not cliente_row.empty else None
        except Exception as e:
            log_erro("ClientesRepository.get_by_cpf", e)
            return None

    def update_score_e_limite(self, cpf: str, novo_score: int, novo_limite: float) -> bool:
        try:
            if self.use_supabase:
                response = supabase.table('clientes').update({
                    'score_credito': novo_score,
                    'limite_credito': novo_limite
                }).eq('cpf', cpf).execute()
                return True
            else:
                if not os.path.exists(self.file_path):
                    return False
                df = pd.read_csv(self.file_path, dtype={'cpf': str, 'data_nascimento': str})
                if cpf not in df['cpf'].values:
                    return False
                df.loc[df['cpf'] == cpf, ['score_credito', 'limite_credito']] = [novo_score, novo_limite]
                df.to_csv(self.file_path, index=False)
                return True
        except Exception as e:
            log_erro("ClientesRepository.update_score_e_limite", e)
            return False
