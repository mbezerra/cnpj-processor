import pandas as pd
from sqlalchemy import create_engine
import gc

tableName = 'cnpj_socios'
columnNames = [
    'cnpj_part1', 'identificador_socio', 'nome_socio', 'cpf_cnpj_socio', 'codigo_qualificacao_socio',
    'data_entrada_sociedade', 'nome_representante_legal', 'cpf_representante_legal', 'x1', 'x2', 'x3'
]
fileSource = 'K3241.K03200Y.D50913.SOCIOCSV'
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

    total_linhas = sum(1 for line in open(csv, encoding='iso-8859-1'))
    metade = total_linhas // 2

    df = pd.read_csv(
        csv, sep=';', encoding='iso-8859-1', header=None, names=columnNames, nrows=metade
    )

    df = df.fillna('')
    df['cnpj_part1'] = df['cnpj_part1'].astype(str).apply(lambda x: x.zfill(8))
    df = df.drop(columns=['cpf_cnpj_socio', 'cpf_representante_legal', 'x1', 'x2', 'x3'])

    insert_in_batches(df, tableName, engine, 1, csv, batchSize=50000)

    del df
    gc.collect()

    print("Montando o DataFrame 2 do CSV " + csv)

    # noinspection PyTypeChecker
    df = pd.read_csv(
        csv, sep=';', encoding='iso-8859-1', header=None, names=columnNames, skiprows=metade
    )

    df = df.fillna('')
    df['cnpj_part1'] = df['cnpj_part1'].astype(str).apply(lambda x: x.zfill(8))
    df = df.drop(columns=['cpf_cnpj_socio', 'cpf_representante_legal', 'x1', 'x2', 'x3'])

    insert_in_batches(df, tableName, engine, 2, csv, batchSize=50000)

    print("Finalizado o CSV " + csv)
