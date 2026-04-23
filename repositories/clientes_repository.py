import pandas as pd
import os
from typing import Optional

class ClientesRepository:
    def __init__(self, file_path: str = None):
        if file_path is None:
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'clientes.csv')
        self.file_path = file_path

    def get_by_cpf(self, cpf: str) -> Optional[dict]:
        if not os.path.exists(self.file_path):
            return None
        df = pd.read_csv(self.file_path, dtype={'cpf': str, 'data_nascimento': str})
        cliente_row = df[df['cpf'] == cpf]
        if cliente_row.empty:
            return None
        return cliente_row.iloc[0].to_dict()

    def update_score(self, cpf: str, novo_score: int) -> bool:
        if not os.path.exists(self.file_path):
            return False
        df = pd.read_csv(self.file_path, dtype={'cpf': str, 'data_nascimento': str})
        if cpf not in df['cpf'].values:
            return False
        df.loc[df['cpf'] == cpf, 'score_credito'] = novo_score
        df.to_csv(self.file_path, index=False)
        return True
