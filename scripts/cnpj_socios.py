"""
Script para carregar dados de sócios CNPJ no banco de dados MySQL.
Processa arquivos CSV da Receita Federal e insere na tabela cnpj_socios.
"""

import gc
import os

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

TABLE_NAME = 'cnpj_socios'
COLUMN_NAMES = [
    'cnpj_part1', 'identificador_socio', 'nome_socio', 'cpf_cnpj_socio',
    'codigo_qualificacao_socio', 'data_entrada_sociedade',
    'nome_representante_legal', 'cpf_representante_legal', 'x1', 'x2', 'x3'
]
FILE_SOURCE = 'data/csv_source/K3241.K03200Y.D50913.SOCIOCSV'
TRECHO_BASE = 'K03200Y'
resultados = []

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

for file_idx in range(10):
    resultados.append(
        FILE_SOURCE.replace(TRECHO_BASE, TRECHO_BASE + str(file_idx)))


def insert_in_batches(dataframe, table_name, db_engine, df_part=1,
                      csv_name='', batch_size=1000):
    """Insere DataFrame no banco em lotes para otimizar performance."""
    for batch_idx in range(0, len(dataframe), batch_size):
        df_batch = dataframe.iloc[batch_idx:batch_idx + batch_size]
        df_batch.to_sql(table_name, con=db_engine, if_exists='append',
                        index=False)
        print(f"Inserido lote {batch_idx} a {batch_idx + batch_size} "
              f"do DF{df_part} para o CSV {csv_name}")


for csv in resultados:

    print("Montando o DataFrame 1 do CSV " + csv)

    total_linhas = sum(1 for line in open(csv, encoding='iso-8859-1'))
    metade = total_linhas // 2

    df = pd.read_csv(
        csv, sep=';', encoding='iso-8859-1', header=None,
        names=COLUMN_NAMES, nrows=metade
    )

    df = df.fillna('')
    df['cnpj_part1'] = df['cnpj_part1'].astype(str).apply(
        lambda x: x.zfill(8))
    df = df.drop(columns=['cpf_cnpj_socio', 'cpf_representante_legal',
                          'x1', 'x2', 'x3'])

    insert_in_batches(df, TABLE_NAME, engine, 1, csv, batch_size=50000)

    del df
    gc.collect()

    print("Montando o DataFrame 2 do CSV " + csv)

    # noinspection PyTypeChecker
    df = pd.read_csv(
        csv, sep=';', encoding='iso-8859-1', header=None,
        names=COLUMN_NAMES, skiprows=metade
    )

    df = df.fillna('')
    df['cnpj_part1'] = df['cnpj_part1'].astype(str).apply(
        lambda x: x.zfill(8))
    df = df.drop(columns=['cpf_cnpj_socio', 'cpf_representante_legal',
                          'x1', 'x2', 'x3'])

    insert_in_batches(df, TABLE_NAME, engine, 2, csv, batch_size=50000)

    print("Finalizado o CSV " + csv)
