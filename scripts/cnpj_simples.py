import pandas as pd
from sqlalchemy import create_engine

tableName = 'cnpj_simples'
columnNames = [
    'cnpj_part1', 'opcao_simples', 'data_opcao_simples', 'data_exclusao_simples',
    'opcao_mei', 'data_opcao_mei', 'data_exclusao_opcao_mei'
]
fileSource = 'F.K03200$W.SIMPLES.CSV.D50913'
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

def insert_in_batches(df, tableName, engine, df_part=1, csv_name='',batchSize=1000):
    # Usa context manager para gerenciar transações automaticamente
    with engine.begin() as conn:
        for i in range(0, len(df), batchSize):
            try:
                dfBatch = df.iloc[i:i + batchSize]
                dfBatch.to_sql(tableName, con=conn, if_exists='append', index=False)
                print(f"Inserido lote {i} a {i + batchSize} do DF{df_part} para o CSV {csv_name}")
            except Exception as e:
                print(f"Erro ao inserir lote {i} a {i + batchSize}: {e}")
                # O context manager fará rollback automaticamente
                raise

print("Montando o DataFrame 1 do CSV " + fileSource)

df = pd.read_csv(fileSource, sep=';', encoding='iso-8859-1', header=None, names=columnNames)
df = df.drop_duplicates(subset=['cnpj_part1'])
df['cnpj_part1'] = df['cnpj_part1'].astype(str).apply(lambda x: x.zfill(8))

insert_in_batches(df, tableName, engine, 1, fileSource, batchSize=50000)

print("Finalizado o CSV " + fileSource)
