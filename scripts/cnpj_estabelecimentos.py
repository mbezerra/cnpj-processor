import pandas as pd
from sqlalchemy import create_engine
import gc

tableName = 'cnpj_estabelecimentos'
columnNames = [
    'cnpj_part1', 'cnpj_part2', 'cnpj_part3', 'identificador_matriz_filial', 'nome_fantasia', 'situacao_cadastral',
    'data_situacao_cadastral', 'motivo_situacao_cadastral', 'cidade_estrangeira', 'codigo_pais', 'data_inicio_atividade', 'cnae',
    'cnaes_secundarios', 'tipo_logradouro', 'logradouro', 'numero', 'complemento', 'bairro', 'cep', 'uf',
    'codigo_municipio', 'ddd1', 'telefone1', 'ddd2', 'telefone2', 'ddd_fax', 'fax', 'correio_eletronico',
    'situacao_especial', 'data_situacao_especial'
]
fileSource = 'K3241.K03200Y.D50913.ESTABELE'
trecho_base = 'K03200Y'
resultados = []
engine = create_engine('mysql+pymysql://prospectar:Mova1520#@127.0.0.1/cnpj')
connection = engine.raw_connection()

try:
    cursor = connection.cursor()
    truncate_query = f"TRUNCATE TABLE {tableName};"
    cursor.execute(truncate_query)
    connection.commit()

    print(f"Tabela {tableName} truncada com sucesso.")

except Exception as e:
    print(f"Erro ao truncar tabela: {e}")

finally:
    if connection:
        connection.close()
        print('Conexão fechada.')

for i in range(10):
    trecho_modificado = trecho_base + str(i)
    file_modificado = fileSource.replace(trecho_base, trecho_modificado)
    resultados.append(file_modificado)


def insert_in_batches(df, tableName, engine, df_part=1, csv_name='', batchSize=1000):
    for i in range(0, len(df), batchSize):
        dfBatch = df.iloc[i:i + batchSize]
        dfBatch.to_sql(tableName, con=engine, if_exists='append', index=False)
        print(f"Inserido lote {i} a {i + batchSize} do DF{df_part} para o CSV {csv_name}")


for csv in resultados:

    print("Montando o DataFrame 1 do CSV " + csv)

    num_lines = sum(1 for line in open(csv, encoding='iso-8859-1'))
    part_size = num_lines // 3
    remaining = num_lines % 3

    df = pd.read_csv(
        csv, sep=';', encoding='iso-8859-1', header=None, names=columnNames,
        nrows=part_size + (1 if remaining > 0 else 0),
        low_memory=False
    )

    df = df.fillna('')
    df['cnpj_part1'] = df['cnpj_part1'].astype(str).apply(lambda x: x.zfill(8))
    df['cnpj_part2'] = df['cnpj_part2'].astype(str).apply(lambda x: x.zfill(4))
    df['cnpj_part3'] = df['cnpj_part3'].astype(str).apply(lambda x: x.zfill(2))
    df['cep'] = pd.to_numeric(df['cep'], errors='coerce')
    df['cep'] = df['cep'].fillna(0).astype(int).astype(str)
    df['cep'] = df['cep'].astype(str).apply(lambda x: x.zfill(8))
    df['ddd1'] = pd.to_numeric(df['ddd1'], errors='coerce')
    df['ddd1'] = df['ddd1'].fillna(0).astype(int).astype(str)
    df['ddd2'] = pd.to_numeric(df['ddd2'], errors='coerce')
    df['ddd2'] = df['ddd2'].fillna(0).astype(int).astype(str)
    df['ddd_fax'] = pd.to_numeric(df['ddd_fax'], errors='coerce')
    df['ddd_fax'] = df['ddd_fax'].fillna(0).astype(int).astype(str)
    df['data_situacao_especial'] = pd.to_numeric(df['data_situacao_especial'], errors='coerce')
    df['data_situacao_especial'] = df['data_situacao_especial'].fillna(0).astype(int).astype(str)
    df['data_situacao_especial'] = df['data_situacao_especial'].astype(str).apply(lambda x: x.zfill(8))
    df['codigo_pais'] = df['codigo_pais'].replace('', '0').astype(int)

    insert_in_batches(df, tableName, engine, 1, csv, batchSize=2000)

    del df
    gc.collect()

    print("Montando o DataFrame 2 do CSV " + csv)

    # noinspection PyTypeChecker
    df = pd.read_csv(
        csv, sep=';', encoding='iso-8859-1', header=None, names=columnNames,
        skiprows=part_size + (1 if remaining > 0 else 0), nrows=part_size + (1 if remaining > 1 else 0),
        low_memory=False
    )

    df = df.fillna('')
    df['cnpj_part1'] = df['cnpj_part1'].astype(str).apply(lambda x: x.zfill(8))
    df['cnpj_part2'] = df['cnpj_part2'].astype(str).apply(lambda x: x.zfill(4))
    df['cnpj_part3'] = df['cnpj_part3'].astype(str).apply(lambda x: x.zfill(2))
    df['cep'] = pd.to_numeric(df['cep'], errors='coerce')
    df['cep'] = df['cep'].fillna(0).astype(int).astype(str)
    df['cep'] = df['cep'].astype(str).apply(lambda x: x.zfill(8))
    df['ddd1'] = pd.to_numeric(df['ddd1'], errors='coerce')
    df['ddd1'] = df['ddd1'].fillna(0).astype(int).astype(str)
    df['ddd2'] = pd.to_numeric(df['ddd2'], errors='coerce')
    df['ddd2'] = df['ddd2'].fillna(0).astype(int).astype(str)
    df['ddd_fax'] = pd.to_numeric(df['ddd_fax'], errors='coerce')
    df['ddd_fax'] = df['ddd_fax'].fillna(0).astype(int).astype(str)
    df['data_situacao_especial'] = pd.to_numeric(df['data_situacao_especial'], errors='coerce')
    df['data_situacao_especial'] = df['data_situacao_especial'].fillna(0).astype(int).astype(str)
    df['data_situacao_especial'] = df['data_situacao_especial'].astype(str).apply(lambda x: x.zfill(8))
    df['codigo_pais'] = df['codigo_pais'].replace('', '0').astype(int)

    insert_in_batches(df, tableName, engine, 2, csv, batchSize=2000)

    del df
    gc.collect()

    print("Montando o DataFrame 3 do CSV " + csv)

    # noinspection PyTypeChecker
    df = pd.read_csv(
        csv, sep=';', encoding='iso-8859-1', header=None, names=columnNames,
        skiprows=part_size * 2 + (1 if remaining > 0 else 0) + (1 if remaining > 1 else 0),
        low_memory=False
    )

    df = df.fillna('')
    df['cnpj_part1'] = df['cnpj_part1'].astype(str).apply(lambda x: x.zfill(8))
    df['cnpj_part2'] = df['cnpj_part2'].astype(str).apply(lambda x: x.zfill(4))
    df['cnpj_part3'] = df['cnpj_part3'].astype(str).apply(lambda x: x.zfill(2))
    df['cep'] = pd.to_numeric(df['cep'], errors='coerce')
    df['cep'] = df['cep'].fillna(0).astype(int).astype(str)
    df['cep'] = df['cep'].astype(str).apply(lambda x: x.zfill(8))
    df['ddd1'] = pd.to_numeric(df['ddd1'], errors='coerce')
    df['ddd1'] = df['ddd1'].fillna(0).astype(int).astype(str)
    df['ddd2'] = pd.to_numeric(df['ddd2'], errors='coerce')
    df['ddd2'] = df['ddd2'].fillna(0).astype(int).astype(str)
    df['ddd_fax'] = pd.to_numeric(df['ddd_fax'], errors='coerce')
    df['ddd_fax'] = df['ddd_fax'].fillna(0).astype(int).astype(str)
    df['data_situacao_especial'] = pd.to_numeric(df['data_situacao_especial'], errors='coerce')
    df['data_situacao_especial'] = df['data_situacao_especial'].fillna(0).astype(int).astype(str)
    df['data_situacao_especial'] = df['data_situacao_especial'].astype(str).apply(lambda x: x.zfill(8))
    df['codigo_pais'] = df['codigo_pais'].replace('', '0').astype(int)

    insert_in_batches(df, tableName, engine, 3, csv, batchSize=2000)

    print("Finalizado o CSV " + csv)
