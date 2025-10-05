"""
Configurações do Sistema CNPJ
"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Banco de Dados
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'cnpj'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4'),
    'connection_timeout': int(os.getenv('DB_CONNECTION_TIMEOUT', '30'))
}

# Configurações de Saída
# Obter diretório raiz do projeto (pasta pai de src/)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
OUTPUT_CONFIG = {
    'output_dir': os.path.join(project_root, 'output'),
    'csv_separator': ';',
    'csv_encoding': 'utf-8',
    'csv_quoting': 'all'
}

# Configurações de Desenvolvimento
DEV_CONFIG = {
    'default_limit': 50,
    'enable_logging': True,
    'log_level': 'INFO'
}

# Mapeamento de Colunas para CSV de Saída
CSV_COLUMNS = [
    'id', 'cnpj', 'identificador_m_f', 'razao_social', 'nome_fantasia',
    'situacao_cadastral', 'data_situacao_cadastral',
    'motivo_situacao_cadastral',
    'nome_cidade_exterior', 'codigo_pais', 'nome_pais',
    'codigo_natureza_juridica', 'data_inicio_atividade', 'cnae_fiscal',
    'cnae_codes', 'descricao_tipo_logradouro', 'logradouro', 'numero',
    'complemento', 'bairro', 'cep', 'uf', 'codigo_municipio', 'municipio',
    'ddd_telefone_1', 'telefone1_celular', 'ddd_telefone_2',
    'telefone2_celular', 'ddd_fax', 'correio_eletronico', 'email',
    'qualificacao_responsavel', 'capital_social_empresa', 'porte_empresa',
    'opcao_simples', 'data_opcao_simples', 'data_exclusao_simples',
    'opcao_mei', 'situacao_especial', 'data_situacao_especial', 'socios',
    'cnaes_secundarios', 'data_opcao_mei', 'data_exclusao_opcao_mei'
]
