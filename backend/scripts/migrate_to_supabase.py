import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Add parent directory to path so we can import core.db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import supabase

load_dotenv()

def migrate_clientes():
    print("Iniciando migração de clientes...")
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'clientes.csv')
    if not os.path.exists(file_path):
        print("clientes.csv não encontrado.")
        return
        
    df = pd.read_csv(file_path, dtype={'cpf': str, 'data_nascimento': str})
    registros = df.to_dict(orient='records')
    
    sucesso = 0
    for row in registros:
        try:
            # check if exists
            res = supabase.table('clientes').select('cpf').eq('cpf', row['cpf']).execute()
            if res.data:
                # Update
                supabase.table('clientes').update(row).eq('cpf', row['cpf']).execute()
            else:
                # Insert
                supabase.table('clientes').insert(row).execute()
            sucesso += 1
        except Exception as e:
            print(f"Erro ao migrar cliente {row['cpf']}: {e}")
            
    print(f"Migrados {sucesso}/{len(registros)} clientes com sucesso.")

def migrate_solicitacoes():
    print("Iniciando migração de solicitações...")
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'solicitacoes_aumento_limite.csv')
    if not os.path.exists(file_path):
        print("solicitacoes_aumento_limite.csv não encontrado.")
        return
        
    df = pd.read_csv(file_path)
    registros = df.to_dict(orient='records')
    
    sucesso = 0
    for row in registros:
        try:
            supabase.table('solicitacoes_aumento_limite').insert(row).execute()
            sucesso += 1
        except Exception as e:
            print(f"Erro ao migrar solicitação: {e}")
            
    print(f"Migradas {sucesso}/{len(registros)} solicitações com sucesso.")

def migrate_score_limite():
    print("Iniciando migração de faixas de score...")
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'score_limite.csv')
    if not os.path.exists(file_path):
        print("score_limite.csv não encontrado.")
        return
        
    df = pd.read_csv(file_path)
    registros = df.to_dict(orient='records')
    
    sucesso = 0
    for row in registros:
        try:
            # check if exists
            res = supabase.table('score_limite').select('*').eq('score_minimo', row['score_minimo']).eq('score_maximo', row['score_maximo']).execute()
            if res.data:
                supabase.table('score_limite').update(row).eq('score_minimo', row['score_minimo']).eq('score_maximo', row['score_maximo']).execute()
            else:
                supabase.table('score_limite').insert(row).execute()
            sucesso += 1
        except Exception as e:
            print(f"Erro ao migrar faixa de score: {e}")
            
    print(f"Migradas {sucesso}/{len(registros)} faixas de score com sucesso.")

if __name__ == "__main__":
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_URL") == "SUA_URL_AQUI":
        print("ERRO: SUPABASE_URL e SUPABASE_KEY não estão configuradas no .env!")
        sys.exit(1)
        
    print("--- MUDANÇA PARA SUPABASE ---")
    print("Certifique-se de que as tabelas 'clientes' e 'solicitacoes_aumento_limite' foram criadas no Supabase.")
    print("Tabela clientes: cpf (PK), nome, data_nascimento, profissao, renda_mensal, score_credito, limite_credito, data_cadastro")
    print("Tabela solicitacoes_aumento_limite: id (PK, serial), cpf_cliente, data_hora_solicitacao, limite_atual, novo_limite_solicitado, status_pedido")
    print("Tabela score_limite: score_minimo, score_maximo, limite_maximo_permitido")
    
    migrate_clientes()
    migrate_solicitacoes()
    migrate_score_limite()
    print("Migração finalizada.")
