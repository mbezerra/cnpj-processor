#!/usr/bin/env python3
"""
CNPJ Processor - Módulo de Processamento
Lê dados das tabelas CNPJ e gera CSV no formato especificado
"""

import pymysql
import pandas as pd
import csv
import re
from typing import List, Dict, Any
import logging
from pathlib import Path
from sqlalchemy import create_engine
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.config import DATABASE_CONFIG
from src.filters import CNPJFilters

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CNPJProcessor:
    """Classe principal para processamento dos dados CNPJ"""
    
    def __init__(self, db_config: Dict[str, Any] = None):
        """
        Inicializa o processador CNPJ
        
        Args:
            db_config: Configurações do banco de dados MySQL
        """
        self.db_config = db_config or DATABASE_CONFIG
        self.connection = None
        self.engine = None
        
    def connect_database(self):
        """Conecta ao banco de dados MySQL"""
        try:
            # Conexão direta para consultas SQL
            self.connection = pymysql.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                charset=self.db_config['charset'],
                connect_timeout=self.db_config['connection_timeout']
            )
            
            # Engine SQLAlchemy para pandas
            connection_string = f"mysql+pymysql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}?charset={self.db_config['charset']}"
            self.engine = create_engine(connection_string)
            
            logger.info(f"Conectado ao banco MySQL: {self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}")
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco de dados: {e}")
            raise
    
    def close_database(self):
        """Fecha a conexão com o banco de dados"""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        logger.info("Conexão com banco de dados fechada")
    
    def get_columns_mapping(self) -> Dict[str, str]:
        """
        Mapeia as colunas do CSV de saída para os campos das tabelas
        
        Returns:
            Dicionário com mapeamento de colunas
        """
        return {
            'id': 'ROWID',  # Será gerado automaticamente
            'cnpj': 'CONCAT(cnpj_part1, cnpj_part2, cnpj_part3)',
            'identificador_m_f': 'identificador_matriz_filial',
            'razao_social': 'e.razao_social',
            'nome_fantasia': 'est.nome_fantasia',
            'situacao_cadastral': 'est.situacao_cadastral',
            'data_situacao_cadastral': 'est.data_situacao_cadastral',
            'motivo_situacao_cadastral': 'est.motivo_situacao_cadastral',
            'nome_cidade_exterior': 'est.cidade_estrangeira',
            'codigo_pais': 'est.codigo_pais',
            'nome_pais': 'p.pais',
            'codigo_natureza_juridica': 'e.natureza_juridica',
            'data_inicio_atividade': 'est.data_inicio_atividade',
            'cnae_fiscal': 'cnae.descricao',
            'cnae_codes': 'est.cnae',
            'descricao_tipo_logradouro': 'est.tipo_logradouro',
            'logradouro': 'est.logradouro',
            'numero': 'est.numero',
            'complemento': 'est.complemento',
            'bairro': 'est.bairro',
            'cep': 'est.cep',
            'uf': 'est.uf',
            'codigo_municipio': 'est.codigo_municipio',
            'municipio': 'm.municipio',
            'ddd_telefone_1': 'est.ddd1',
            'telefone1_celular': 'est.telefone1',
            'ddd_telefone_2': 'est.ddd2',
            'telefone2_celular': 'est.telefone2',
            'ddd_fax': 'est.ddd_fax',
            'correio_eletronico': 'est.correio_eletronico',
            'email': 'est.correio_eletronico',  # Mesmo campo
            'qualificacao_responsavel': 'e.qualificacao_socio',
            'capital_social_empresa': 'e.capital_social',
            'porte_empresa': 'e.porte_empresa',
            'opcao_simples': 's.opcao_simples',
            'data_opcao_simples': 's.data_opcao_simples',
            'data_exclusao_simples': 's.data_exclusao_simples',
            'opcao_mei': 's.opcao_mei',
            'situacao_especial': 'est.situacao_especial',
            'data_situacao_especial': 'est.data_situacao_especial',
            'socios': 'GROUP_CONCAT(soc.nome_socio, " | ")',  # Será tratado separadamente
            'cnaes_secundarios': 'est.cnaes_secundarios',
            'data_opcao_mei': 's.data_opcao_mei',
            'data_exclusao_opcao_mei': 's.data_exclusao_opcao_mei'
        }
    
    def build_query(self, limit: int = 100, filters: Dict[str, Any] = None) -> str:
        """
        Constrói a consulta SQL principal
        
        Args:
            limit: Limite de registros para desenvolvimento/testes
            filters: Dicionário com filtros aplicados
            
        Returns:
            String com a consulta SQL
        """
        # Construir query base
        query = """
        SELECT 
            (@row_number := @row_number + 1) as id,
            est.cnpj_part1,
            CONCAT(est.cnpj_part1, est.cnpj_part2, est.cnpj_part3) as cnpj,
            est.identificador_matriz_filial,
            e.razao_social,
            est.nome_fantasia,
            est.situacao_cadastral,
            est.data_situacao_cadastral,
            est.motivo_situacao_cadastral,
            est.cidade_estrangeira,
            est.codigo_pais,
            p.pais,
            e.natureza_juridica,
            est.data_inicio_atividade,
            cnae.descricao as cnae_fiscal,
            est.cnae as cnae_codes,
            est.tipo_logradouro,
            est.logradouro,
            est.numero,
            est.complemento,
            est.bairro,
            est.cep,
            est.uf,
            est.codigo_municipio,
            m.municipio,
            est.ddd1,
            est.telefone1,
            est.ddd2,
            est.telefone2,
            est.ddd_fax,
            est.fax,
            est.correio_eletronico,
            est.correio_eletronico as email,
            e.qualificacao_socio,
            e.capital_social,
            e.porte_empresa,
            s.opcao_simples,
            s.data_opcao_simples,
            s.data_exclusao_simples,
            s.opcao_mei,
            est.situacao_especial,
            est.data_situacao_especial,
            est.cnaes_secundarios,
            s.data_opcao_mei,
            s.data_exclusao_opcao_mei
        FROM cnpj_estabelecimentos est
        LEFT JOIN cnpj_empresas e ON est.cnpj_part1 = e.cnpj_part1
        LEFT JOIN cnpj_cnaes cnae ON est.cnae = cnae.cnae
        LEFT JOIN cnpj_municipios m ON est.codigo_municipio = m.codigo
        LEFT JOIN cnpj_paises p ON (CASE WHEN est.codigo_pais = 0 THEN 105 ELSE est.codigo_pais END) = p.codigo
        LEFT JOIN cnpj_simples s ON e.cnpj_part1 = s.cnpj_part1
        CROSS JOIN (SELECT @row_number := 0) r
        WHERE est.cnpj_part1 IS NOT NULL
        """
        
        # Aplicar filtros se fornecidos
        if filters:
            query = self.apply_filters(query, filters)
        
        # Adicionar LIMIT apenas se especificado
        if limit > 0:
            query += f" LIMIT {limit}"
        return query
    
    def apply_filters(self, query: str, filters: Dict[str, Any]) -> str:
        """
        Aplica filtros à consulta SQL
        
        Args:
            query: Consulta SQL base
            filters: Dicionário com filtros aplicados
            
        Returns:
            Consulta SQL com filtros aplicados
        """
        where_conditions = []
        
        # Filtro CNAE Codes
        if 'cnae_codes' in filters:
            cnae_list = "','".join(filters['cnae_codes'])
            where_conditions.append(f"est.cnae IN ('{cnae_list}')")
        
        # Filtro UF
        if 'uf' in filters:
            where_conditions.append(f"est.uf = '{filters['uf']}'")
        
        # Filtro Código do Município
        if 'codigo_municipio' in filters:
            where_conditions.append(f"est.codigo_municipio = {filters['codigo_municipio']}")
        
        # Filtro Situação Cadastral
        if 'situacao_cadastral' in filters:
            situacao = filters['situacao_cadastral']
            if situacao == 'ativos':
                where_conditions.append("est.situacao_cadastral = 2")
            elif situacao == 'inaptos':
                where_conditions.append("est.situacao_cadastral = 4")
            elif situacao == 'inativos':
                where_conditions.append("est.situacao_cadastral IN (1, 3, 8)")
        
        # Filtro Data de Início de Atividade
        if 'data_inicio_atividade' in filters:
            data_filtro = filters['data_inicio_atividade']
            if 'inicio' in data_filtro:
                where_conditions.append(f"est.data_inicio_atividade >= '{data_filtro['inicio']}'")
            if 'fim' in data_filtro:
                where_conditions.append(f"est.data_inicio_atividade <= '{data_filtro['fim']}'")
        
        # Filtro Com Email
        if 'com_email' in filters:
            if filters['com_email']:
                where_conditions.append("est.correio_eletronico IS NOT NULL AND est.correio_eletronico != ''")
            else:
                where_conditions.append("(est.correio_eletronico IS NULL OR est.correio_eletronico = '')")
        
        # Filtro Com Telefone
        if 'com_telefone' in filters:
            if filters['com_telefone']:
                where_conditions.append("(est.telefone1 IS NOT NULL AND est.telefone1 != '')")
            else:
                where_conditions.append("(est.telefone1 IS NULL OR est.telefone1 = '')")
        
        # Filtro Tipo de Telefone (aplicado após processamento)
        if 'tipo_telefone' in filters:
            # Este filtro será aplicado no processamento, não na consulta SQL
            pass
        
        # Filtro Opção Tributária
        if 'opcao_tributaria' in filters:
            if filters['opcao_tributaria'] == 'mei':
                where_conditions.append("s.opcao_mei = 'S'")
            elif filters['opcao_tributaria'] == 'sem_mei':
                where_conditions.append("(s.opcao_mei IS NULL OR s.opcao_mei != 'S')")
        
        # Filtro Capital Social
        if 'capital_social' in filters:
            if filters['capital_social'] == '10k':
                where_conditions.append("e.capital_social > 10000")
            elif filters['capital_social'] == '50k':
                where_conditions.append("e.capital_social > 50000")
            elif filters['capital_social'] == '100k':
                where_conditions.append("e.capital_social > 100000")
        
        # Aplicar condições WHERE
        if where_conditions:
            where_clause = " AND ".join(where_conditions)
            if "WHERE" in query:
                query = query.replace("WHERE est.cnpj_part1 IS NOT NULL", f"WHERE est.cnpj_part1 IS NOT NULL AND {where_clause}")
            else:
                query += f" WHERE {where_clause}"
        
        return query
    
    def get_socios_data(self, cnpj_list: List[str]) -> Dict[str, str]:
        """
        Busca dados dos sócios para uma lista de CNPJs
        
        Args:
            cnpj_list: Lista de CNPJs para buscar sócios
            
        Returns:
            Dicionário com CNPJ como chave e dados dos sócios como valor
        """
        if not cnpj_list:
            return {}
        
        placeholders = ','.join(['%s' for _ in cnpj_list])
        query = f"""
        SELECT 
            soc.cnpj_part1,
            GROUP_CONCAT(
                CONCAT(
                    'ID: ', IFNULL(soc.identificador_socio, ''), 
                    ' | Nome: ', IFNULL(soc.nome_socio, ''), 
                    ' | Qualificação: ', IFNULL(qs.qualificacao, ''), 
                    ' | Data Entrada Sociedade: ', IFNULL(soc.data_entrada_sociedade, '')
                ) 
                SEPARATOR ' | '
            ) as socios_info
        FROM cnpj_socios soc
        LEFT JOIN cnpj_qualificacao_socios qs ON soc.codigo_qualificacao_socio = qs.codigo
        WHERE soc.cnpj_part1 IN ({placeholders})
        GROUP BY soc.cnpj_part1
        """
        
        cursor = self.connection.cursor()
        cursor.execute(query, cnpj_list)
        results = cursor.fetchall()
        
        return {row[0]: row[1] for row in results}
    
    def is_celular(self, telefone: str) -> int:
        """
        Verifica se um telefone é celular baseado no terceiro dígito
        
        Args:
            telefone: Número de telefone completo (DDD + número)
            
        Returns:
            1 se for celular, 0 se não for
        """
        if not telefone or telefone == '':
            return 0
        
        # Remove caracteres não numéricos
        telefone_limpo = ''.join(filter(str.isdigit, str(telefone)))
        
        # Verifica se o número tem pelo menos 10 dígitos
        if len(telefone_limpo) >= 10:
            # Obtém o terceiro dígito do número
            terceiro_digito = telefone_limpo[2]
            # Compara o terceiro dígito com os dígitos que determinam celular (6, 7, 8, 9)
            if terceiro_digito in ['6', '7', '8', '9']:
                return 1
        
        return 0

    def is_valid_email(self, email: str) -> int:
        """
        Verifica se um email é válido
        
        Args:
            email: Endereço de email para validar
            
        Returns:
            1 se for email válido, 0 se não for
        """
        try:
            if isinstance(email, str) and email.strip() != '':
                # Expressão regular para validar email
                regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                
                # Verifica se o email corresponde à expressão regular
                if re.match(regex, email):
                    return 1
                
                return 0
            
            return 0
        except TypeError:
            return 0

    def process_data(self, limit: int = 100, filters: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Processa os dados das tabelas CNPJ
        
        Args:
            limit: Limite de registros para processamento
            filters: Dicionário com filtros aplicados
            
        Returns:
            DataFrame com os dados processados
        """
        logger.info(f"Iniciando processamento com limite de {limit} registros")
        if filters:
            logger.info(f"Filtros aplicados: {list(filters.keys())}")
        
        # Executa consulta principal
        query = self.build_query(limit, filters)
        df = pd.read_sql_query(query, self.engine)
        
        logger.info(f"Consultados {len(df)} registros")
        
        # Busca dados dos sócios
        cnpj_list = df['cnpj_part1'].unique().tolist()
        socios_data = self.get_socios_data(cnpj_list)
        
        # Adiciona dados dos sócios ao DataFrame
        df['socios'] = df['cnpj_part1'].map(socios_data).fillna('')
        
        # Processa colunas de telefone
        df['ddd_telefone_1'] = df.apply(lambda row: 
            f"{row['ddd1']}{row['telefone1']}" if pd.notna(row['ddd1']) and pd.notna(row['telefone1']) 
            else '', axis=1)
        
        df['telefone1_celular'] = df['ddd_telefone_1'].apply(self.is_celular)
        
        df['ddd_telefone_2'] = df.apply(lambda row: 
            f"{row['ddd2']}{row['telefone2']}" if pd.notna(row['ddd2']) and pd.notna(row['telefone2']) 
            else '', axis=1)
        
        df['telefone2_celular'] = df['ddd_telefone_2'].apply(self.is_celular)
        
        # Processa validação de email
        df['email'] = df['correio_eletronico'].apply(self.is_valid_email)
        
        # Processa concatenação de DDD + fax
        df['ddd_fax'] = df.apply(lambda row: 
            f"{row['ddd_fax']}{row['fax']}" if pd.notna(row['ddd_fax']) and pd.notna(row['fax']) 
            else '', axis=1)
        
        # Aplica filtro de tipo de telefone se especificado
        if filters and 'tipo_telefone' in filters:
            tipo = filters['tipo_telefone']
            if tipo == 'fixo':
                df = df[df['telefone1_celular'] == 0]
            elif tipo == 'celular':
                df = df[df['telefone1_celular'] == 1]
            # 'ambos' não filtra nada
        
        # Corrige código do país: substitui 0 por 105 (Brasil)
        df['codigo_pais'] = df['codigo_pais'].replace(0, 105)
        
        # Converte ID para inteiro
        df['id'] = df['id'].astype(int)
        
        # Remove colunas auxiliares
        columns_to_drop = ['cnpj_part1', 'ddd1', 'telefone1', 'ddd2', 'telefone2', 'fax']
        for col in columns_to_drop:
            if col in df.columns:
                df = df.drop(col, axis=1)
        
        logger.info("Processamento concluído")
        return df
    
    def save_to_csv(self, df: pd.DataFrame, output_path: str = None):
        """
        Salva o DataFrame em arquivo CSV
        
        Args:
            df: DataFrame com os dados
            output_path: Caminho do arquivo de saída
        """
        if output_path is None:
            # Usar configuração padrão
            from src.config.config import OUTPUT_CONFIG
            output_path = os.path.join(OUTPUT_CONFIG['output_dir'], 'cnpj_data.csv')
        
        # Cria diretório de saída se não existir
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Salva CSV com separador ';' conforme exemplo
        df.to_csv(output_path, sep=';', index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')
        logger.info(f"Dados salvos em: {output_path}")
    
    def run(self, limit: int = 100, output_path: str = None, filters: Dict[str, Any] = None):
        """
        Executa o processamento completo
        
        Args:
            limit: Limite de registros para processamento
            output_path: Caminho do arquivo de saída
            filters: Dicionário com filtros aplicados
        """
        try:
            self.connect_database()
            df = self.process_data(limit, filters)
            self.save_to_csv(df, output_path)
            logger.info("Processamento concluído com sucesso!")
        except Exception as e:
            logger.error(f"Erro durante processamento: {e}")
            raise
        finally:
            self.close_database()


def main():
    """Função principal"""
    processor = CNPJProcessor()
    
    # Para desenvolvimento/testes, limitar a 50 registros
    processor.run(limit=50, output_path="output/cnpj_vestuario_calcados.csv")


if __name__ == "__main__":
    main()
