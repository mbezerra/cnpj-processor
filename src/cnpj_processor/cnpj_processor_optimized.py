#!/usr/bin/env python3
"""
CNPJ Processor Otimizado - Versão para Grandes Volumes
Versão otimizada com paginação, cache e consultas melhoradas
"""

import pymysql
import pandas as pd
import csv
import re
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
import sys
import os
import time
from functools import lru_cache
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.config import DATABASE_CONFIG
from src.filters import CNPJFilters

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CNPJProcessorOptimized:
    """
    Processador CNPJ otimizado para grandes volumes de dados
    """
    
    def __init__(self):
        self.connection = None
        self.engine = None
        self.batch_size = 10000  # Tamanho do lote para processamento
        self.socios_cache = {}   # Cache para dados de sócios
        
    def connect_database(self):
        """Conecta ao banco de dados MySQL"""
        try:
            # Remover connection_timeout se existir (não suportado pelo pymysql)
            db_config = DATABASE_CONFIG.copy()
            if 'connection_timeout' in db_config:
                del db_config['connection_timeout']
            
            self.connection = pymysql.connect(**db_config)
            self.engine = create_engine(
                f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}"
                f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
            )
            logger.info(f"Conectado ao banco MySQL: {DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}")
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco: {e}")
            raise
    
    def close_database(self):
        """Fecha conexão com banco de dados"""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        logger.info("Conexão com banco de dados fechada")
    
    def setup_optimization_settings(self):
        """Configura otimizações de sessão para consultas grandes"""
        cursor = self.connection.cursor()
        
        optimization_queries = [
            "SET SESSION sort_buffer_size = 256*1024*1024",  # 256MB
            "SET SESSION join_buffer_size = 128*1024*1024",  # 128MB
            "SET SESSION read_buffer_size = 64*1024*1024",   # 64MB
            # query_cache_type removido - não existe no MySQL 8.0+
        ]
        
        for query in optimization_queries:
            try:
                cursor.execute(query)
            except Exception as e:
                logger.warning(f"Erro ao aplicar otimização: {query} - {e}")
        
        cursor.close()
        logger.info("Configurações de otimização aplicadas")
    
    def get_total_count(self, filters: Dict[str, Any] = None) -> int:
        """
        Obtém o número total de registros que atendem aos filtros
        """
        query = """
        SELECT COUNT(*)
        FROM cnpj_estabelecimentos est
        LEFT JOIN cnpj_empresas e ON est.cnpj_part1 = e.cnpj_part1
        LEFT JOIN cnpj_simples s ON e.cnpj_part1 = s.cnpj_part1
        WHERE est.cnpj_part1 IS NOT NULL
        """
        
        if filters:
            query = self.apply_filters_optimized(query, filters, count_only=True)
        
        cursor = self.connection.cursor()
        cursor.execute(query)
        total = cursor.fetchone()[0]
        cursor.close()
        
        return total
    
    def apply_filters_optimized(self, query: str, filters: Dict[str, Any], count_only: bool = False) -> str:
        """
        Aplica filtros otimizados à consulta SQL
        """
        where_conditions = []
        
        # Filtro UF (muito comum)
        if 'uf' in filters:
            where_conditions.append(f"est.uf = '{filters['uf']}'")
        
        # Filtro Situação Cadastral (muito comum)
        if 'situacao_cadastral' in filters:
            situacao = filters['situacao_cadastral']
            if situacao == 'ativos':
                where_conditions.append("est.situacao_cadastral = 2")
            elif situacao == 'inaptos':
                where_conditions.append("est.situacao_cadastral = 4")
            elif situacao == 'inativos':
                where_conditions.append("est.situacao_cadastral IN (1, 3, 8)")
        
        # Filtro Código do Município
        if 'codigo_municipio' in filters:
            where_conditions.append(f"est.codigo_municipio = {filters['codigo_municipio']}")
        
        # Filtro CNAE Codes (usar IN para melhor performance)
        if 'cnae_codes' in filters:
            cnae_list = "','".join(filters['cnae_codes'])
            where_conditions.append(f"est.cnae IN ('{cnae_list}')")
        
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
    
    def build_optimized_query(self, limit: int = 0, offset: int = 0, filters: Dict[str, Any] = None) -> str:
        """
        Constrói consulta SQL otimizada para grandes volumes
        """
        # Query otimizada com menos JOINs desnecessários
        query = """
        SELECT 
            est.cnpj_part1,
            est.cnpj_part2,
            est.cnpj_part3,
            est.identificador_matriz_filial,
            e.razao_social,
            est.nome_fantasia,
            est.situacao_cadastral,
            est.data_situacao_cadastral,
            est.motivo_situacao_cadastral,
            est.cidade_estrangeira,
            est.codigo_pais,
            est.data_inicio_atividade,
            est.cnae,
            est.tipo_logradouro,
            est.logradouro,
            est.numero,
            est.complemento,
            est.bairro,
            est.cep,
            est.uf,
            est.codigo_municipio,
            est.ddd1,
            est.telefone1,
            est.ddd2,
            est.telefone2,
            est.ddd_fax,
            est.fax,
            est.correio_eletronico,
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
        INNER JOIN cnpj_empresas e ON est.cnpj_part1 = e.cnpj_part1
        LEFT JOIN cnpj_simples s ON e.cnpj_part1 = s.cnpj_part1
        WHERE est.cnpj_part1 IS NOT NULL
        """
        
        # Aplicar filtros
        if filters:
            query = self.apply_filters_optimized(query, filters)
        
        # Ordenação para paginação consistente
        query += " ORDER BY est.cnpj_part1, est.cnpj_part2, est.cnpj_part3"
        
        # Paginação
        if limit > 0:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        return query
    
    @lru_cache(maxsize=1000)
    def get_lookup_data(self, table: str, key_field: str, value_field: str, keys: tuple) -> Dict[str, str]:
        """
        Busca dados de lookup com cache para melhorar performance
        """
        if not keys:
            return {}
        
        placeholders = ','.join(['%s' for _ in keys])
        query = f"SELECT {key_field}, {value_field} FROM {table} WHERE {key_field} IN ({placeholders})"
        
        cursor = self.connection.cursor()
        cursor.execute(query, keys)
        results = cursor.fetchall()
        cursor.close()
        
        return {str(row[0]): row[1] for row in results}
    
    def process_batch(self, batch_data: pd.DataFrame) -> pd.DataFrame:
        """
        Processa um lote de dados com otimizações
        """
        if batch_data.empty:
            return batch_data
        
        # Obter CNPJs únicos do lote
        cnpj_list = batch_data['cnpj_part1'].unique().tolist()
        
        # Buscar dados de lookup em lote (com cache)
        cnae_lookup = self.get_lookup_data('cnpj_cnaes', 'cnae', 'descricao', tuple(cnpj_list))
        municipio_lookup = self.get_lookup_data('cnpj_municipios', 'codigo', 'municipio', tuple(batch_data['codigo_municipio'].unique()))
        pais_lookup = self.get_lookup_data('cnpj_paises', 'codigo', 'pais', tuple(batch_data['codigo_pais'].unique()))
        
        # Aplicar lookups
        batch_data['cnae_fiscal'] = batch_data['cnae'].map(cnae_lookup)
        batch_data['municipio'] = batch_data['codigo_municipio'].map(municipio_lookup)
        batch_data['pais'] = batch_data['codigo_pais'].map(pais_lookup)
        
        # Processar dados (mesmo processamento da versão original)
        batch_data = self.process_dataframe(batch_data)
        
        # Buscar sócios apenas para CNPJs únicos
        socios_data = self.get_socios_data_optimized(cnpj_list)
        batch_data['socios'] = batch_data['cnpj_part1'].map(socios_data)
        
        return batch_data
    
    def get_socios_data_optimized(self, cnpj_list: List[str]) -> Dict[str, str]:
        """
        Busca dados dos sócios otimizada
        """
        if not cnpj_list:
            return {}
        
        # Verificar cache primeiro
        cached_socios = {}
        uncached_cnpjs = []
        
        for cnpj in cnpj_list:
            if cnpj in self.socios_cache:
                cached_socios[cnpj] = self.socios_cache[cnpj]
            else:
                uncached_cnpjs.append(cnpj)
        
        # Buscar apenas CNPJs não em cache
        if uncached_cnpjs:
            placeholders = ','.join(['%s' for _ in uncached_cnpjs])
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
            cursor.execute(query, uncached_cnpjs)
            results = cursor.fetchall()
            cursor.close()
            
            # Atualizar cache
            for row in results:
                socios_info = row[1] if row[1] else ""
                self.socios_cache[row[0]] = socios_info
                cached_socios[row[0]] = socios_info
        
        return cached_socios
    
    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processa DataFrame com as mesmas otimizações da versão original
        """
        if df.empty:
            return df
        
        # Adicionar ID sequencial
        df['id'] = range(1, len(df) + 1)
        
        # Criar CNPJ completo
        df['cnpj'] = df['cnpj_part1'].astype(str) + df['cnpj_part2'].astype(str) + df['cnpj_part3'].astype(str)
        
        # Renomear colunas conforme esperado
        df = df.rename(columns={
            'identificador_matriz_filial': 'identificador_m_f',
            'motivo_situacao_cadastral': 'motivo_situacao_cadastral',
            'cidade_estrangeira': 'nome_cidade_exterior',
            'natureza_juridica': 'codigo_natureza_juridica',
            'cnae': 'cnae_codes',
            'ddd1': 'ddd_telefone_1',
            'telefone1': 'telefone1_celular',
            'ddd2': 'ddd_telefone_2',
            'telefone2': 'telefone2_celular',
            'correio_eletronico': 'email',
            'qualificacao_socio': 'qualificacao_responsavel',
            'capital_social': 'capital_social_empresa',
            'porte_empresa': 'porte_empresa'
        })
        
        # Aplicar processamentos específicos
        df = self.apply_data_processing(df)
        
        return df
    
    def apply_data_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica processamentos específicos aos dados
        """
        # Detectar celulares
        df['telefone1_celular'] = df.apply(self.detect_celular, axis=1, args=('telefone1_celular', 'ddd_telefone_1'))
        df['telefone2_celular'] = df.apply(self.detect_celular, axis=1, args=('telefone2_celular', 'ddd_telefone_2'))
        
        # Validar emails
        df['email'] = df['email'].apply(self.validate_email)
        
        # Corrigir situação cadastral
        df['situacao_cadastral'] = df['situacao_cadastral'].replace({
            2: 'ATIVA',
            4: 'INAPTA',
            8: 'SUSPENSA'
        })
        
        # Corrigir código do país
        df['codigo_pais'] = df['codigo_pais'].replace(0, 105)
        
        # Concatenação DDD + Fax
        df['ddd_fax'] = df['ddd_fax'].astype(str) + df['fax'].astype(str)
        
        return df
    
    def detect_celular(self, row, telefone_col: str, ddd_col: str) -> str:
        """Detecta se telefone é celular"""
        telefone = str(row[telefone_col])
        ddd = str(row[ddd_col])
        
        if len(telefone) == 9:
            if telefone[0] in ['9']:
                return f"({ddd}) {telefone}"
        return ""
    
    def validate_email(self, email: str) -> str:
        """Valida formato de email"""
        if pd.isna(email) or email == '':
            return ""
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email):
            return email
        return ""
    
    def save_to_csv_batch(self, df: pd.DataFrame, output_path: str, append: bool = False):
        """
        Salva DataFrame em CSV com otimizações para grandes volumes
        """
        mode = 'a' if append else 'w'
        header = not append
        
        df.to_csv(
            output_path, 
            sep=';', 
            index=False, 
            quoting=csv.QUOTE_ALL, 
            encoding='utf-8',
            mode=mode,
            header=header
        )
    
    def run_optimized(self, limit: int = 0, output_path: str = None, filters: Dict[str, Any] = None):
        """
        Executa processamento otimizado para grandes volumes
        """
        try:
            self.connect_database()
            self.setup_optimization_settings()
            
            # Obter total de registros
            total_records = self.get_total_count(filters)
            logger.info(f"Total de registros a processar: {total_records:,}")
            
            if limit > 0:
                total_records = min(total_records, limit)
            
            # Preparar arquivo de saída
            if output_path is None:
                from src.config.config import OUTPUT_CONFIG
                output_path = os.path.join(OUTPUT_CONFIG['output_dir'], 'cnpj_optimized_data.csv')
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Processar em lotes
            processed = 0
            batch_num = 1
            
            logger.info(f"Iniciando processamento em lotes de {self.batch_size:,} registros...")
            
            while processed < total_records:
                batch_start = time.time()
                
                # Calcular offset e limite do lote
                current_batch_size = min(self.batch_size, total_records - processed)
                
                # Executar consulta otimizada
                query = self.build_optimized_query(
                    limit=current_batch_size,
                    offset=processed,
                    filters=filters
                )
                
                # Executar com SQLAlchemy para melhor performance
                df_batch = pd.read_sql(query, self.engine)
                
                if df_batch.empty:
                    logger.warning("Lote vazio retornado, interrompendo processamento")
                    break
                
                # Processar lote
                df_processed = self.process_batch(df_batch)
                
                # Salvar lote
                append_mode = batch_num > 1
                self.save_to_csv_batch(df_processed, output_path, append=append_mode)
                
                processed += len(df_processed)
                batch_time = time.time() - batch_start
                
                logger.info(f"Lote {batch_num}: {len(df_processed):,} registros processados "
                          f"({processed:,}/{total_records:,}) - "
                          f"Tempo: {batch_time:.2f}s - "
                          f"Velocidade: {len(df_processed)/batch_time:.0f} reg/s")
                
                batch_num += 1
            
            logger.info(f"Processamento concluído! {processed:,} registros salvos em: {output_path}")
            
        except Exception as e:
            logger.error(f"Erro durante processamento: {e}")
            raise
        finally:
            self.close_database()

# Função de conveniência para uso direto
def run_optimized_processing(limit: int = 0, output_path: str = None, filters: Dict[str, Any] = None):
    """
    Função de conveniência para executar processamento otimizado
    """
    processor = CNPJProcessorOptimized()
    processor.run_optimized(limit=limit, output_path=output_path, filters=filters)

if __name__ == "__main__":
    # Exemplo de uso
    processor = CNPJProcessorOptimized()
    
    # Filtros de exemplo
    filters = {
        'uf': 'SP',
        'situacao_cadastral': 'ativos',
        'com_email': True
    }
    
    processor.run_optimized(limit=100000, output_path='output/sp_ativos_com_email.csv', filters=filters)
