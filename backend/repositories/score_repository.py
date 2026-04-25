import pandas as pd
import os
from typing import Optional
from utils.logger import log_erro
from core.db import supabase

class ScoreRepository:
    def __init__(self, use_supabase: bool = True, file_path: str = None):
        self.use_supabase = use_supabase
        if not self.use_supabase:
            if file_path is None:
                file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'score_limite.csv')
            self.file_path = file_path

    def get_limite_maximo(self, score: int) -> float:
        """Retorna o limite máximo permitido para um dado score."""
        try:
            if self.use_supabase:
                response = supabase.table('score_limite').select('limite_maximo_permitido').lte('score_minimo', score).gte('score_maximo', score).execute()
                data = response.data
                if data:
                    return float(data[0]['limite_maximo_permitido'])
                return 0.0
            else:
                if not os.path.exists(self.file_path):
                    return 0.0
                df = pd.read_csv(self.file_path)
                # Filtra a faixa onde o score se encaixa
                faixa = df[(df['score_minimo'] <= score) & (df['score_maximo'] >= score)]
                if faixa.empty:
                    return 0.0
                return float(faixa.iloc[0]['limite_maximo_permitido'])
        except Exception as e:
            log_erro("ScoreRepository.get_limite_maximo", e)
            return 0.0
