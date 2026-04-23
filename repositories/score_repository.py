import pandas as pd
import os
from typing import Optional

class ScoreRepository:
    def __init__(self, file_path: str = None):
        if file_path is None:
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'score_limite.csv')
        self.file_path = file_path

    def get_limite_maximo(self, score: int) -> float:
        """Retorna o limite máximo permitido para um dado score."""
        if not os.path.exists(self.file_path):
            return 0.0
        df = pd.read_csv(self.file_path)
        # Filtra a faixa onde o score se encaixa
        faixa = df[(df['score_minimo'] <= score) & (df['score_maximo'] >= score)]
        if faixa.empty:
            return 0.0
        return float(faixa.iloc[0]['limite_maximo_permitido'])
