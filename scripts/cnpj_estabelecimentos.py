"""
Script para carregar dados de estabelecimentos CNPJ no banco de dados MySQL.
Processa arquivos CSV da Receita Federal e insere na tabela
cnpj_estabelecimentos.
"""

import gc
import os

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Determina o diretório raiz do projeto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

TABLE_NAME = 'cnpj_estabelecimentos'
COLUMN_NAMES = [
    'cnpj_part1', 'cnpj_part2', 'cnpj_part3', 'identificador_matriz_filial',
    'nome_fantasia', 'situacao_cadastral', 'data_situacao_cadastral',
    'motivo_situacao_cadastral', 'cidade_estrangeira', 'codigo_pais',
    'data_inicio_atividade', 'cnae', 'cnaes_secundarios', 'tipo_logradouro',
    'logradouro', 'numero', 'complemento', 'bairro', 'cep', 'uf',
    'codigo_municipio', 'ddd1', 'telefone1', 'ddd2', 'telefone2',
    'ddd_fax', 'fax', 'correio_eletronico', 'situacao_especial',
    'data_situacao_especial'
]
FILE_SOURCE = os.path.join(
    PROJECT_ROOT, 'data/csv_source/K3241.K03200Y.D51011.ESTABELE')
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

    num_lines = sum(1 for line in open(csv, encoding='iso-8859-1'))
    part_size = num_lines // 3
    remaining = num_lines % 3

    df = pd.read_csv(
        csv, sep=';', encoding='iso-8859-1', header=None, names=COLUMN_NAMES,
        nrows=part_size + (1 if remaining > 0 else 0),
        low_memory=False
    )

    df = df.fillna('')
    df['cnpj_part1'] = df['cnpj_part1'].astype(str).apply(
        lambda x: x.zfill(8))
    df['cnpj_part2'] = df['cnpj_part2'].astype(str).apply(
        lambda x: x.zfill(4))
    df['cnpj_part3'] = df['cnpj_part3'].astype(str).apply(
        lambda x: x.zfill(2))
    df['cep'] = pd.to_numeric(df['cep'], errors='coerce')
    df['cep'] = df['cep'].fillna(0).astype(int).astype(str)
    df['cep'] = df['cep'].astype(str).apply(lambda x: x.zfill(8))
    df['ddd1'] = pd.to_numeric(df['ddd1'], errors='coerce')
    df['ddd1'] = df['ddd1'].fillna(0).astype(int).astype(str)
    df['ddd2'] = pd.to_numeric(df['ddd2'], errors='coerce')
    df['ddd2'] = df['ddd2'].fillna(0).astype(int).astype(str)
    df['ddd_fax'] = pd.to_numeric(df['ddd_fax'], errors='coerce')
    df['ddd_fax'] = df['ddd_fax'].fillna(0).astype(int).astype(str)
    df['data_situacao_especial'] = pd.to_numeric(
        df['data_situacao_especial'], errors='coerce')
    df['data_situacao_especial'] = (
        df['data_situacao_especial'].fillna(0).astype(int).astype(str))
    df['data_situacao_especial'] = (
        df['data_situacao_especial'].astype(str).apply(lambda x: x.zfill(8)))
    df['codigo_pais'] = df['codigo_pais'].replace('', '0').astype(int)

    insert_in_batches(df, TABLE_NAME, engine, 1, csv, batch_size=100000)

    del df
    gc.collect()

    print("Montando o DataFrame 2 do CSV " + csv)

    # noinspection PyTypeChecker
    df = pd.read_csv(
        csv, sep=';', encoding='iso-8859-1', header=None, names=COLUMN_NAMES,
        skiprows=part_size + (1 if remaining > 0 else 0),
        nrows=part_size + (1 if remaining > 1 else 0),
        low_memory=False
    )

    df = df.fillna('')
    df['cnpj_part1'] = df['cnpj_part1'].astype(str).apply(
        lambda x: x.zfill(8))
    df['cnpj_part2'] = df['cnpj_part2'].astype(str).apply(
        lambda x: x.zfill(4))
    df['cnpj_part3'] = df['cnpj_part3'].astype(str).apply(
        lambda x: x.zfill(2))
    df['cep'] = pd.to_numeric(df['cep'], errors='coerce')
    df['cep'] = df['cep'].fillna(0).astype(int).astype(str)
    df['cep'] = df['cep'].astype(str).apply(lambda x: x.zfill(8))
    df['ddd1'] = pd.to_numeric(df['ddd1'], errors='coerce')
    df['ddd1'] = df['ddd1'].fillna(0).astype(int).astype(str)
    df['ddd2'] = pd.to_numeric(df['ddd2'], errors='coerce')
    df['ddd2'] = df['ddd2'].fillna(0).astype(int).astype(str)
    df['ddd_fax'] = pd.to_numeric(df['ddd_fax'], errors='coerce')
    df['ddd_fax'] = df['ddd_fax'].fillna(0).astype(int).astype(str)
    df['data_situacao_especial'] = pd.to_numeric(
        df['data_situacao_especial'], errors='coerce')
    df['data_situacao_especial'] = (
        df['data_situacao_especial'].fillna(0).astype(int).astype(str))
    df['data_situacao_especial'] = (
        df['data_situacao_especial'].astype(str).apply(lambda x: x.zfill(8)))
    df['codigo_pais'] = df['codigo_pais'].replace('', '0').astype(int)

    insert_in_batches(df, TABLE_NAME, engine, 2, csv, batch_size=100000)

    del df
    gc.collect()

    print("Montando o DataFrame 3 do CSV " + csv)

    # noinspection PyTypeChecker
    df = pd.read_csv(
        csv, sep=';', encoding='iso-8859-1', header=None, names=COLUMN_NAMES,
        skiprows=(part_size * 2 + (1 if remaining > 0 else 0) +
                  (1 if remaining > 1 else 0)),
        low_memory=False
    )

    df = df.fillna('')
    df['cnpj_part1'] = df['cnpj_part1'].astype(str).apply(
        lambda x: x.zfill(8))
    df['cnpj_part2'] = df['cnpj_part2'].astype(str).apply(
        lambda x: x.zfill(4))
    df['cnpj_part3'] = df['cnpj_part3'].astype(str).apply(
        lambda x: x.zfill(2))
    df['cep'] = pd.to_numeric(df['cep'], errors='coerce')
    df['cep'] = df['cep'].fillna(0).astype(int).astype(str)
    df['cep'] = df['cep'].astype(str).apply(lambda x: x.zfill(8))
    df['ddd1'] = pd.to_numeric(df['ddd1'], errors='coerce')
    df['ddd1'] = df['ddd1'].fillna(0).astype(int).astype(str)
    df['ddd2'] = pd.to_numeric(df['ddd2'], errors='coerce')
    df['ddd2'] = df['ddd2'].fillna(0).astype(int).astype(str)
    df['ddd_fax'] = pd.to_numeric(df['ddd_fax'], errors='coerce')
    df['ddd_fax'] = df['ddd_fax'].fillna(0).astype(int).astype(str)
    df['data_situacao_especial'] = pd.to_numeric(
        df['data_situacao_especial'], errors='coerce')
    df['data_situacao_especial'] = (
        df['data_situacao_especial'].fillna(0).astype(int).astype(str))
    df['data_situacao_especial'] = (
        df['data_situacao_especial'].astype(str).apply(lambda x: x.zfill(8)))
    df['codigo_pais'] = df['codigo_pais'].replace('', '0').astype(int)

    insert_in_batches(df, TABLE_NAME, engine, 3, csv, batch_size=100000)

    print("Finalizado o CSV " + csv)
