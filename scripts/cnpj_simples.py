"""
Script para carregar dados de simples CNPJ no banco de dados MySQL.
Processa arquivos CSV da Receita Federal e insere na tabela cnpj_simples.
"""

import os

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

TABLE_NAME = 'cnpj_simples'
COLUMN_NAMES = [
    'cnpj_part1', 'opcao_simples', 'data_opcao_simples',
    'data_exclusao_simples', 'opcao_mei', 'data_opcao_mei',
    'data_exclusao_opcao_mei'
]
FILE_SOURCE = 'F.K03200$W.SIMPLES.CSV.D50913'

# Configuração do banco via variáveis de ambiente
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'cnpj')

CONNECTION_STRING = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
engine = create_engine(CONNECTION_STRING)
connection = engine.raw_connection()

try:
    cursor = connection.cursor()
    cursor.execute(f"TRUNCATE TABLE {TABLE_NAME};")
    connection.commit()

    print(f"Tabela {TABLE_NAME} truncada com sucesso.")

except (ConnectionError, OSError, ValueError) as e:
    print(f"Erro ao truncar tabela: {e}")

finally:
    if connection:
        connection.close()
        print('Conexão fechada.')


def insert_in_batches(dataframe, table_name, db_engine, df_part=1,
                      csv_name='', batch_size=1000):
    """Insere DataFrame no banco em lotes para otimizar performance."""
    # Usa context manager para gerenciar transações automaticamente
    with db_engine.begin() as conn:
        for batch_idx in range(0, len(dataframe), batch_size):
            try:
                df_batch = dataframe.iloc[batch_idx:batch_idx + batch_size]
                df_batch.to_sql(table_name, con=conn, if_exists='append',
                                index=False)
                print(f"Inserido lote {batch_idx} a {batch_idx + batch_size} "
                      f"do DF{df_part} para o CSV {csv_name}")
            except (ConnectionError, OSError, ValueError) as e:
                print(f"Erro ao inserir lote {batch_idx} a "
                      f"{batch_idx + batch_size}: {e}")
                # O context manager fará rollback automaticamente
                raise


print("Montando o DataFrame 1 do CSV " + FILE_SOURCE)

df = pd.read_csv(
    FILE_SOURCE, sep=';', encoding='iso-8859-1', header=None,
    names=COLUMN_NAMES
)
df = df.drop_duplicates(subset=['cnpj_part1'])
df['cnpj_part1'] = df['cnpj_part1'].astype(str).apply(
    lambda x: x.zfill(8))

insert_in_batches(df, TABLE_NAME, engine, 1, FILE_SOURCE, batch_size=50000)

print("Finalizado o CSV " + FILE_SOURCE)
