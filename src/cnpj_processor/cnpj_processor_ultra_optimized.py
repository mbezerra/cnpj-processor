#!/usr/bin/env python3
"""
CNPJ Processor ULTRA Otimizado - Versão para Máxima Performance
Versão com consultas mínimas, cache agressivo e processamento em streaming
"""

import csv
import logging
import os
import re
import sys
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import pymysql
from sqlalchemy import create_engine, text

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.config import DATABASE_CONFIG
from src.config.config import OUTPUT_CONFIG

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CNPJProcessorUltraOptimized:
    """
    Processador CNPJ ULTRA otimizado para máxima performance
    - Consultas mínimas com JOINs essenciais apenas
    - Cache agressivo para lookup tables
    - Processamento em streaming
    - Uso de views pré-compiladas quando disponíveis
    """

    def __init__(self):
        self.connection = None
        self.engine = None
        self.batch_size = 50000  # Lotes maiores para reduzir overhead
        self.cache_size = 10000  # Cache maior
        
        # Caches para lookup tables
        self.cnae_cache = {}
        self.municipio_cache = {}
        self.pais_cache = {}
        self.socios_cache = {}
        
    def connect_database(self):
        """Conecta ao banco de dados MySQL com configurações otimizadas"""
        try:
            # Configurações otimizadas para pymysql
            db_config = DATABASE_CONFIG.copy()
            if "connection_timeout" in db_config:
                del db_config["connection_timeout"]
            
            # Configurações adicionais para performance
            db_config.update({
                'autocommit': True,
                'charset': 'utf8mb4',
                'use_unicode': True,
                'connect_timeout': 60,
                'read_timeout': 300,
                'write_timeout': 300
            })
            
            self.connection = pymysql.connect(**db_config)
            
            # Engine SQLAlchemy otimizada
            connection_string = (
                f"mysql+pymysql://{DATABASE_CONFIG['user']}:"
                f"{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:"
                f"{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
                f"?charset=utf8mb4&autocommit=true"
            )
            self.engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            
            logger.info(
                "Conectado ao banco MySQL: %s:%s/%s",
                DATABASE_CONFIG['host'],
                DATABASE_CONFIG['port'],
                DATABASE_CONFIG['database']
            )
        except Exception as e:
            logger.error("Erro ao conectar ao banco: %s", e)
            raise
    
    def close_database(self):
        """Fecha conexão com banco de dados"""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        logger.info("Conexão com banco de dados fechada")
    
    def setup_ultra_optimization_settings(self):
        """Configura otimizações ULTRA para consultas grandes"""
        cursor = self.connection.cursor()
        
        optimization_queries = [
            # Configurações de buffer otimizadas
            "SET SESSION sort_buffer_size = 512*1024*1024",  # 512MB
            "SET SESSION join_buffer_size = 256*1024*1024",  # 256MB
            "SET SESSION read_buffer_size = 128*1024*1024",  # 128MB
            "SET SESSION read_rnd_buffer_size = 64*1024*1024",  # 64MB
            
            # Otimizações de consulta
            "SET SESSION tmp_table_size = 256*1024*1024",  # 256MB
            "SET SESSION max_heap_table_size = 256*1024*1024",  # 256MB
            
            # Configurações de thread
            "SET SESSION thread_cache_size = 100",
            
            # Otimizações de índice
            "SET SESSION optimizer_switch = 'index_merge=on,index_merge_union=on,index_merge_sort_union=on'",
        ]
        
        for query in optimization_queries:
            try:
                cursor.execute(query)
            except Exception as e:
                logger.warning("Erro ao aplicar otimização: %s - %s", query, e)
        
        cursor.close()
        logger.info("Configurações ULTRA de otimização aplicadas")
    
    def preload_lookup_caches(self):
        """Pré-carrega todos os caches de lookup para evitar consultas repetidas"""
        logger.info("Pré-carregando caches de lookup...")
        
        # Carregar CNAEs
        cursor = self.connection.cursor()
        cursor.execute("SELECT cnae, descricao FROM cnpj_cnaes")
        self.cnae_cache = {str(row[0]): row[1] for row in cursor.fetchall()}
        logger.info("Cache CNAEs carregado: %s registros", len(self.cnae_cache))
        
        # Carregar Municípios
        cursor.execute("SELECT codigo, municipio FROM cnpj_municipios")
        self.municipio_cache = {str(row[0]): row[1] for row in cursor.fetchall()}
        logger.info("Cache Municípios carregado: %s registros", len(self.municipio_cache))
        
        # Carregar Países
        cursor.execute("SELECT codigo, pais FROM cnpj_paises")
        self.pais_cache = {str(row[0]): row[1] for row in cursor.fetchall()}
        logger.info("Cache Países carregado: %s registros", len(self.pais_cache))
        
        cursor.close()
        logger.info("Todos os caches pré-carregados com sucesso!")
    
    def get_total_count_optimized(self, filters_dict: Dict[str, Any] = None) -> int:
        """Contagem otimizada usando índices"""
        # Usar contagem aproximada para melhor performance
        query = """
        SELECT COUNT(*) 
        FROM cnpj_estabelecimentos est
        WHERE est.cnpj_part1 IS NOT NULL
        """
        
        if filters_dict:
            query = self.apply_filters_minimal(query, filters_dict)
        
        cursor = self.connection.cursor()
        cursor.execute(query)
        total = cursor.fetchone()[0]
        cursor.close()
        
        # Limitar ao máximo global de 200.000 registros
        max_limit = 200000
        return min(total, max_limit)
    
    def apply_filters_minimal(self, query: str, filters_dict: Dict[str, Any]) -> str:
        """Aplica apenas filtros essenciais para máxima performance"""
        where_conditions = []
        
        # Filtros mais comuns e com índices
        if "uf" in filters_dict:
            where_conditions.append(f"est.uf = '{filters_dict['uf']}'")
        
        if "situacao_cadastral" in filters_dict:
            situacao = filters_dict["situacao_cadastral"]
            if situacao == "ativos":
                where_conditions.append("est.situacao_cadastral = 2")
            elif situacao == "inaptos":
                where_conditions.append("est.situacao_cadastral = 4")
            elif situacao == "inativos":
                where_conditions.append("est.situacao_cadastral IN (1, 3, 8)")
        
        if "codigo_municipio" in filters_dict:
            where_conditions.append(f"est.codigo_municipio = {filters_dict['codigo_municipio']}")
        
        if "cnae_codes" in filters_dict:
            cnae_list = "','".join(filters_dict["cnae_codes"])
            where_conditions.append(f"est.cnae IN ('{cnae_list}')")
        
        # Aplicar condições WHERE
        if where_conditions:
            where_clause = " AND ".join(where_conditions)
            query += f" AND {where_clause}"
        
        return query
    
    def build_ultra_optimized_query(self, limit: int = 0, offset: int = 0, filters_query: Dict[str, Any] = None) -> str:
        """
        Constrói consulta ULTRA otimizada com mínimos JOINs
        """
        # Query ultra otimizada - apenas JOINs essenciais
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
        if filters_query:
            query = self.apply_filters_minimal(query, filters_query)
        
        # Ordenação otimizada - usar índice se disponível
        query += " ORDER BY est.cnpj_part1, est.data_inicio_atividade DESC"
        
        # Limite global máximo de 200.000 registros
        max_limit = 200000
        if limit <= 0:
            actual_limit = max_limit
        else:
            actual_limit = min(limit, max_limit)
        
        # Paginação respeitando o limite máximo
        if offset + actual_limit > max_limit:
            actual_limit = max_limit - offset
            if actual_limit <= 0:
                actual_limit = 0
        
        if actual_limit > 0:
            query += f" LIMIT {actual_limit} OFFSET {offset}"
        
        return query
    
    def get_socios_batch_optimized(self, cnpj_batch: List[str]) -> Dict[str, str]:
        """Busca sócios em lote com cache otimizado"""
        if not cnpj_batch:
            return {}
        
        # Verificar cache primeiro
        cached_results = {}
        uncached_cnpjs = []
        
        for cnpj in cnpj_batch:
            if cnpj in self.socios_cache:
                cached_results[cnpj] = self.socios_cache[cnpj]
            else:
                uncached_cnpjs.append(cnpj)
        
        # Buscar apenas CNPJs não em cache
        if uncached_cnpjs:
            # Limitar tamanho do batch para evitar queries muito grandes
            batch_size = 1000
            for i in range(0, len(uncached_cnpjs), batch_size):
                batch = uncached_cnpjs[i:i + batch_size]
                placeholders = ','.join(['%s' for _ in batch])
                
                query = f"""
                SELECT 
                    soc.cnpj_part1,
                    GROUP_CONCAT(
                        CONCAT(
                            'ID: ', IFNULL(soc.identificador_socio, ''), 
                            ' | Nome: ', IFNULL(soc.nome_socio, ''), 
                            ' | Qualificação: ', IFNULL(qs.qualificacao, ''), 
                            ' | Data Entrada: ', IFNULL(soc.data_entrada_sociedade, '')
                        ) 
                        SEPARATOR ' | '
                    ) as socios_info
                FROM cnpj_socios soc
                LEFT JOIN cnpj_qualificacao_socios qs ON soc.codigo_qualificacao_socio = qs.codigo
                WHERE soc.cnpj_part1 IN ({placeholders})
                GROUP BY soc.cnpj_part1
                """
                
                cursor = self.connection.cursor()
                cursor.execute(query, batch)
                results = cursor.fetchall()
                cursor.close()
                
                # Atualizar caches
                for row in results:
                    socios_info = row[1] if row[1] else ""
                    self.socios_cache[row[0]] = socios_info
                    cached_results[row[0]] = socios_info
        
        return cached_results
    
    def process_batch_ultra_optimized(self, batch_data: pd.DataFrame) -> pd.DataFrame:
        """Processa lote com máxima otimização usando caches pré-carregados"""
        if batch_data.empty:
            return batch_data
        
        # Aplicar lookups usando caches pré-carregados
        batch_data['cnae_fiscal'] = batch_data['cnae'].astype(str).map(self.cnae_cache)
        batch_data['municipio'] = batch_data['codigo_municipio'].astype(str).map(self.municipio_cache)
        batch_data['pais'] = batch_data['codigo_pais'].astype(str).map(self.pais_cache)
        
        # Processar dados básicos
        batch_data = self.process_dataframe_ultra(batch_data)
        
        # Buscar sócios em lote otimizado
        cnpj_list = batch_data['cnpj_part1'].unique().tolist()
        socios_data = self.get_socios_batch_optimized(cnpj_list)
        batch_data['socios'] = batch_data['cnpj_part1'].map(socios_data).fillna("")
        
        return batch_data
    
    def process_dataframe_ultra(self, df: pd.DataFrame) -> pd.DataFrame:
        """Processa DataFrame com otimizações ULTRA"""
        if df.empty:
            return df
        
        # Adicionar ID sequencial
        df['id'] = range(1, len(df) + 1)
        
        # Criar CNPJ completo
        df['cnpj'] = df['cnpj_part1'].astype(str) + df['cnpj_part2'].astype(str) + df['cnpj_part3'].astype(str)
        
        # Renomear colunas
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
        df = self.apply_data_processing_ultra(df)
        
        return df
    
    def apply_data_processing_ultra(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica processamentos específicos com otimizações"""
        # Detectar celulares
        df['telefone1_celular'] = df.apply(self.detect_celular_ultra, axis=1, args=('telefone1_celular', 'ddd_telefone_1'))
        df['telefone2_celular'] = df.apply(self.detect_celular_ultra, axis=1, args=('telefone2_celular', 'ddd_telefone_2'))
        
        # Validar emails
        df['email'] = df['email'].apply(self.validate_email_ultra)
        
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
    
    def detect_celular_ultra(self, row, telefone_col: str, ddd_col: str) -> str:
        """Detecta se telefone é celular com otimização"""
        telefone = str(row[telefone_col])
        ddd = str(row[ddd_col])
        
        if len(telefone) == 9 and telefone[0] in ['9']:
            return f"({ddd}) {telefone}"
        return ""
    
    def validate_email_ultra(self, email: str) -> str:
        """Valida formato de email com otimização"""
        if pd.isna(email) or email == '':
            return ""
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email):
            return email
        return ""
    
    def save_to_csv_ultra(self, df: pd.DataFrame, output_path: str, append: bool = False):
        """Salva DataFrame em CSV com otimizações ULTRA"""
        mode = 'a' if append else 'w'
        header = not append
        
        # Otimizações para CSV
        df.to_csv(
            output_path, 
            sep=';', 
            index=False, 
            quoting=csv.QUOTE_ALL, 
            encoding='utf-8',
            mode=mode,
            header=header,
            chunksize=10000  # Processar em chunks para economizar memória
        )
    
    def run_ultra_optimized(self, limit: int = 0, output_path: str = None, filters_dict: Dict[str, Any] = None):
        """Executa processamento ULTRA otimizado para máxima performance"""
        try:
            start_time = time.time()
            
            self.connect_database()
            self.setup_ultra_optimization_settings()
            self.preload_lookup_caches()
            
            # Obter total de registros (limitado a 200.000)
            total_records = self.get_total_count_optimized(filters_dict)
            max_limit = 200000
            
            logger.info("Total de registros a processar: %s", f"{total_records:,}")
            logger.info(
                "📊 Limite global máximo: %s registros (ordenação otimizada)",
                f"{max_limit:,}"
            )
            
            if limit > 0:
                total_records = min(total_records, limit)
            
            # Preparar arquivo de saída
            if output_path is None:
                output_path = os.path.join(
                    OUTPUT_CONFIG['output_dir'], 'cnpj_empresas_ultra.csv'
                )
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Processar em lotes ULTRA otimizados
            processed = 0
            batch_num = 1
            
            logger.info("Iniciando processamento ULTRA em lotes de %s registros...", f"{self.batch_size:,}")
            
            while processed < total_records:
                batch_start = time.time()
                
                # Calcular offset e limite do lote
                current_batch_size = min(self.batch_size, total_records - processed)
                
                # Executar consulta ULTRA otimizada
                query = self.build_ultra_optimized_query(
                    limit=current_batch_size,
                    offset=processed,
                    filters_query=filters_dict
                )
                
                # Executar com SQLAlchemy otimizada
                df_batch = pd.read_sql(query, self.engine)
                
                if df_batch.empty:
                    logger.warning("Lote vazio retornado, interrompendo processamento")
                    break
                
                # Processar lote ULTRA otimizado
                df_processed = self.process_batch_ultra_optimized(df_batch)
                
                # Salvar lote
                append_mode = batch_num > 1
                self.save_to_csv_ultra(df_processed, output_path, append=append_mode)
                
                processed += len(df_processed)
                batch_time = time.time() - batch_start
                
                # Calcular métricas de performance
                records_per_second = len(df_processed) / batch_time if batch_time > 0 else 0
                total_time = time.time() - start_time
                avg_speed = processed / total_time if total_time > 0 else 0
                eta_seconds = (total_records - processed) / avg_speed if avg_speed > 0 else 0
                eta_minutes = eta_seconds / 60
                
                logger.info(
                    "Lote %s: %s registros processados (%s/%s) - "
                    "Tempo: %.2fs - Velocidade: %.0f reg/s - "
                    "Média: %.0f reg/s - ETA: %.1f min",
                    batch_num,
                    f"{len(df_processed):,}",
                    f"{processed:,}",
                    f"{total_records:,}",
                    batch_time,
                    records_per_second,
                    avg_speed,
                    eta_minutes
                )
                
                batch_num += 1
            
            total_time = time.time() - start_time
            final_speed = processed / total_time if total_time > 0 else 0
            
            logger.info(
                "Processamento ULTRA concluído! %s registros salvos em: %s",
                f"{processed:,}",
                output_path
            )
            logger.info(
                "Performance final: %.0f registros/segundo em %.1f segundos",
                final_speed,
                total_time
            )
            
        except Exception as e:
            logger.error("Erro durante processamento ULTRA: %s", e)
            raise
        finally:
            self.close_database()


# Função de conveniência para uso direto
def run_ultra_optimized_processing(
    limit: int = 0, output_path: str = None, filters_proc: Dict[str, Any] = None
):
    """
    Função de conveniência para executar processamento ULTRA otimizado
    """
    processor = CNPJProcessorUltraOptimized()
    processor.run_ultra_optimized(limit=limit, output_path=output_path, filters_dict=filters_proc)


if __name__ == "__main__":
    # Exemplo de uso ULTRA otimizado
    processor_example = CNPJProcessorUltraOptimized()
    
    # Filtros de exemplo
    filters_run = {"uf": "SP", "situacao_cadastral": "ativos", "com_email": True}
    
    processor_example.run_ultra_optimized(
        limit=100000, 
        output_path="output/sp_ativos_com_email_ultra.csv", 
        filters_dict=filters_run
    )
