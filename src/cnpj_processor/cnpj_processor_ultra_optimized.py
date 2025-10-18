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
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import pymysql
from sqlalchemy import create_engine

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
        self.batch_size = 10000  # Lotes pequenos para performance consistente
        self.cache_size = 10000  # Cache maior
        self.max_batch_size = 15000  # Tamanho máximo do lote
        self.min_batch_size = 5000   # Tamanho mínimo do lote
        
        # Caches para lookup tables (sem cache de sócios - tabela muito grande)
        self.cnae_cache = {}
        self.municipio_cache = {}
        self.pais_cache = {}
        
    def connect_database(self):
        """Conecta ao banco de dados MySQL com configurações otimizadas"""
        try:
            # Configurações otimizadas para pymysql
            db_config = DATABASE_CONFIG.copy()
            # Remover parâmetros não suportados pelo pymysql
            for key in ["connection_timeout"]:
                if key in db_config:
                    del db_config[key]
            
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
            
            # Configurações de thread (removido thread_cache_size - é variável global)
            
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
    
    def get_total_count_optimized(self, filters_dict: Dict[str, Any] = None, 
                                apply_limit: bool = True) -> int:
        """Contagem otimizada usando índices"""
        # Usar contagem aproximada para melhor performance
        query = """
        SELECT COUNT(*) 
        FROM cnpj_estabelecimentos est
        WHERE est.cnpj_part1 IS NOT NULL
        """
        
        if filters_dict:
            query = self.apply_filters_minimal(query, filters_dict)
        
        # Adicionar LIMIT para acelerar contagem quando há filtros
        if filters_dict and 'uf' in filters_dict:
            query += " LIMIT 1000000"  # Limitar contagem para acelerar
        
        cursor = self.connection.cursor()
        cursor.execute(query)
        total = cursor.fetchone()[0]
        cursor.close()
        
        # Limitar ao máximo global de 200.000 registros se solicitado
        if apply_limit:
            max_limit = 200000
            return min(total, max_limit)
        else:
            return total
    
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
    
    def build_ultra_optimized_query(self, limit: int = 0, offset: int = 0, filters_query: Dict[str, Any] = None, last_cnpj: str = None) -> str:
        """
        Constrói consulta ULTRA otimizada com mínimos JOINs
        """
        # Query ultra otimizada - apenas JOINs essenciais
        query = """
        SELECT 
            CONCAT(
                LPAD(est.cnpj_part1, 8, '0'), 
                LPAD(est.cnpj_part2, 4, '0'), 
                LPAD(est.cnpj_part3, 2, '0')
            ) as cnpj,
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
        
        # Usar cursor-based pagination para melhor performance
        if last_cnpj:
            # Continuar a partir do último CNPJ processado
            query += f" AND est.cnpj_part1 > '{last_cnpj}'"
        
        # Ordenação por CNPJ para cursor-based pagination
        query += " ORDER BY est.cnpj_part1"
        
        # Limite global máximo de 200.000 registros
        max_limit = 200000
        if limit <= 0:
            actual_limit = max_limit
        else:
            actual_limit = min(limit, max_limit)
        
        if actual_limit > 0:
            query += f" LIMIT {actual_limit}"
        
        return query
    
    def get_optimized_order_by(self, filters_query: Dict[str, Any] = None) -> str:
        """
        Retorna a ordenação otimizada baseada nos filtros aplicados
        para aproveitar índices compostos existentes
        """
        if not filters_query:
            # Sem filtros: usar ordenação por data (índice simples)
            return " ORDER BY est.data_inicio_atividade DESC, est.cnpj_part1"
        
        # Verificar se tem filtro de UF e situação cadastral (índice otimizado)
        has_uf = 'uf' in filters_query
        has_situacao = 'situacao_cadastral' in filters_query
        
        if has_uf and has_situacao:
            # Usar índice: idx_estabelecimentos_uf_situacao_data_ultra
            # Ordem: uf, situacao_cadastral, data_inicio_atividade DESC, cnpj_part1
            return " ORDER BY est.uf, est.situacao_cadastral, est.data_inicio_atividade DESC, est.cnpj_part1"
        
        # Verificar se tem filtro de UF apenas
        if has_uf:
            # Usar índice: idx_estabelecimentos_uf_situacao_data_ultra (primeira parte)
            return " ORDER BY est.uf, est.data_inicio_atividade DESC, est.cnpj_part1"
        
        # Verificar se tem filtro de CNAE
        if 'cnae_codes' in filters_query:
            # Usar índice: idx_estabelecimentos_cnae_data_ultra
            return " ORDER BY est.cnae, est.data_inicio_atividade DESC, est.cnpj_part1"
        
        # Verificar se tem filtro de município
        if 'codigo_municipio' in filters_query:
            # Usar índice: idx_estabelecimentos_municipio_situacao_ultra
            return " ORDER BY est.codigo_municipio, est.data_inicio_atividade DESC, est.cnpj_part1"
        
        # Padrão: ordenação por data (mais recente primeiro)
        return " ORDER BY est.data_inicio_atividade DESC, est.cnpj_part1"
    
    def get_socios_batch_direct(self, cnpj_batch: List[str]) -> Dict[str, str]:
        """Busca sócios em lote de forma direta, sem cache - SEMPRE busca todos os sócios"""
        if not cnpj_batch:
            return {}
        
        logger.debug("Buscando sócios diretamente para %s CNPJs", len(cnpj_batch))
        
        # Batch size otimizado para lotes menores
        if len(cnpj_batch) > 2000:
            batch_size = 500  # Batch menor para lotes grandes
        else:
            batch_size = 1000  # Batch normal
        
        results = {}
        
        for i in range(0, len(cnpj_batch), batch_size):
            batch = cnpj_batch[i:i + batch_size]
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
            
            try:
                cursor = self.connection.cursor()
                cursor.execute(query, batch)
                batch_results = cursor.fetchall()
                cursor.close()
                
                # Adicionar resultados
                for row in batch_results:
                    socios_info = row[1] if row[1] else ""
                    results[row[0]] = socios_info
                    
                logger.debug("Batch %s/%s de sócios processado: %s resultados", 
                           i//batch_size + 1, (len(cnpj_batch) + batch_size - 1)//batch_size, len(batch_results))
                    
            except Exception as e:
                logger.error("Erro na busca de sócios para batch %s: %s", i//batch_size + 1, e)
                # Tentar novamente com batch menor
                if batch_size > 100:
                    logger.warning("Tentando novamente com batch size menor...")
                    batch_size = batch_size // 2
                    i -= batch_size  # Voltar para tentar novamente
                    continue
                else:
                    logger.error("Falha crítica na busca de sócios, continuando sem este batch")
                    continue
        
        logger.debug("Busca de sócios concluída: %s CNPJs processados, %s com sócios encontrados", 
                    len(cnpj_batch), len(results))
        return results
    
    def adjust_batch_size(self, batch_time: float, current_batch_size: int) -> int:
        """
        Ajusta dinamicamente o tamanho do lote baseado na performance
        """
        # Se o lote demorar mais de 15 segundos, reduzir tamanho
        if batch_time > 15:
            new_size = max(self.min_batch_size, current_batch_size // 2)
            logger.warning("Lote muito lento (%.2fs), reduzindo tamanho: %s -> %s", 
                         batch_time, f"{current_batch_size:,}", f"{new_size:,}")
            return new_size
        
        # Se o lote for muito rápido (< 5s) e não estiver no máximo, aumentar
        elif batch_time < 5 and current_batch_size < self.max_batch_size:
            new_size = min(self.max_batch_size, int(current_batch_size * 1.5))
            logger.info("Lote muito rápido (%.2fs), aumentando tamanho: %s -> %s", 
                      batch_time, f"{current_batch_size:,}", f"{new_size:,}")
            return new_size
        
        return current_batch_size
    
    def cleanup_resources_after_batch(self):
        """Libera recursos mínimos após cada lote"""
        import gc
        
        # Apenas garbage collection leve
        gc.collect()
        
        logger.debug("Recursos básicos liberados após lote")
    
    def process_batch_ultra_optimized(self, batch_data: pd.DataFrame) -> pd.DataFrame:
        """Processa lote com máxima otimização usando caches pré-carregados"""
        if batch_data.empty:
            return batch_data
        
        # Processar dados básicos primeiro (incluindo correção do código do país)
        batch_data = self.process_dataframe_ultra(batch_data)
        
        # Aplicar lookups usando caches pré-carregados (após correção do código do país)
        batch_data['cnae_fiscal'] = batch_data['cnae_codes'].astype(str).map(self.cnae_cache)
        batch_data['municipio'] = batch_data['codigo_municipio'].astype(str).map(self.municipio_cache)
        batch_data['pais'] = batch_data['codigo_pais'].astype(str).map(self.pais_cache)
        
        # Reordenar colunas após adicionar todas as colunas necessárias
        batch_data = self.reorder_columns_ultra(batch_data)
        
        # Buscar sócios em lote de forma direta (SEMPRE buscar sócios - dados essenciais)
        # Extrair cnpj_part1 da coluna cnpj para buscar sócios
        cnpj_part1_list = batch_data['cnpj'].str[:8].unique().tolist()
        
        logger.debug("Buscando sócios diretamente para %s CNPJs únicos", len(cnpj_part1_list))
        
        socios_start = time.time()
        socios_data = self.get_socios_batch_direct(cnpj_part1_list)
        socios_time = time.time() - socios_start
        
        logger.debug("Busca de sócios concluída em %.2fs", socios_time)
        
        # Se a busca de sócios demorar muito, reduzir tamanho do lote principal
        if socios_time > 10:  # Mais de 10 segundos
            logger.warning("Busca de sócios muito lenta (%.2fs), reduzindo tamanho do lote principal", socios_time)
            self.batch_size = max(self.min_batch_size, self.batch_size // 2)
        
        batch_data['socios'] = batch_data['cnpj'].str[:8].map(socios_data).fillna("")
        
        return batch_data
    
    def process_dataframe_ultra(self, df: pd.DataFrame) -> pd.DataFrame:
        """Processa DataFrame com otimizações ULTRA"""
        if df.empty:
            return df
        
        # Adicionar ID sequencial
        df['id'] = range(1, len(df) + 1)
        
        # CNPJ já vem formatado da query SQL como string
        
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
    
    def reorder_columns_ultra(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reordena colunas para colocar 'pais' logo depois de 'codigo_pais', 'municipio' logo depois de 'codigo_municipio' e 'cnae_codes' logo antes de 'cnae_fiscal'"""
        if df.empty:
            return df
        
        # Obter lista de colunas
        columns = df.columns.tolist()
        
        # Reordenar 'pais' para ficar logo depois de 'codigo_pais'
        if 'codigo_pais' in columns:
            codigo_pais_idx = columns.index('codigo_pais')
            
            # Remover 'pais' da posição atual se existir
            if 'pais' in columns:
                columns.remove('pais')
            
            # Inserir 'pais' logo depois de 'codigo_pais'
            columns.insert(codigo_pais_idx + 1, 'pais')
        
        # Reordenar 'municipio' para ficar logo depois de 'codigo_municipio'
        if 'codigo_municipio' in columns:
            codigo_municipio_idx = columns.index('codigo_municipio')
            
            # Remover 'municipio' da posição atual se existir
            if 'municipio' in columns:
                columns.remove('municipio')
            
            # Inserir 'municipio' logo depois de 'codigo_municipio'
            columns.insert(codigo_municipio_idx + 1, 'municipio')
        
        # Reordenar 'cnae_codes' para ficar logo antes de 'cnae_fiscal'
        if 'cnae_fiscal' in columns:
            cnae_fiscal_idx = columns.index('cnae_fiscal')
            
            # Remover 'cnae_codes' da posição atual se existir
            if 'cnae_codes' in columns:
                columns.remove('cnae_codes')
            
            # Inserir 'cnae_codes' logo antes de 'cnae_fiscal'
            columns.insert(cnae_fiscal_idx, 'cnae_codes')
        
        # Reordenar DataFrame
        df = df[columns]
        
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

    def run_ultra_optimized_with_offset(self, limit: int = 0, offset: int = 0, 
                                      output_path: str = None, filters_dict: Dict[str, Any] = None):
        """Executa processamento ULTRA otimizado com offset específico"""
        try:
            start_time = time.time()
            
            # Preparar arquivo de saída
            if output_path is None:
                output_path = os.path.join(
                    OUTPUT_CONFIG['output_dir'], 'cnpj_empresas_ultra.csv'
                )
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Processar em lotes ULTRA otimizados com cursor-based pagination
            processed = 0
            batch_num = 1
            last_cnpj = None
            
            while processed < limit:
                batch_start = time.time()
                
                # Calcular limite do lote
                current_batch_size = min(self.batch_size, limit - processed)
                
                logger.info("🔄 Iniciando lote %s: cursor=%s, size=%s", 
                           batch_num, last_cnpj or "início", f"{current_batch_size:,}")
                
                try:
                    # Executar consulta ULTRA otimizada com cursor
                    query = self.build_ultra_optimized_query(
                        limit=current_batch_size,
                        offset=0,  # Não usar offset
                        filters_query=filters_dict,
                        last_cnpj=last_cnpj
                    )
                    
                    logger.debug("Executando consulta SQL...")
                    query_start = time.time()
                    
                    # Executar com SQLAlchemy otimizada
                    df_batch = pd.read_sql(query, self.engine)
                    
                    query_time = time.time() - query_start
                    logger.debug("Consulta SQL concluída em %.2fs, retornou %s registros", 
                               query_time, len(df_batch))
                    
                    if df_batch.empty:
                        logger.warning("Lote vazio retornado, interrompendo processamento")
                        break
                    
                    # Processar lote ULTRA otimizado
                    logger.debug("Processando lote...")
                    process_start = time.time()
                    df_processed = self.process_batch_ultra_optimized(df_batch)
                    process_time = time.time() - process_start
                    logger.debug("Processamento concluído em %.2fs", process_time)
                    
                    # Salvar lote
                    logger.debug("Salvando lote...")
                    save_start = time.time()
                    append_mode = batch_num > 1
                    self.save_to_csv_ultra(df_processed, output_path, append=append_mode)
                    save_time = time.time() - save_start
                    logger.debug("Salvamento concluído em %.2fs", save_time)
                    
                    # Capturar o último CNPJ para cursor-based pagination
                    if not df_processed.empty:
                        last_cnpj = df_processed['cnpj'].iloc[-1]
                        logger.debug("Último CNPJ do lote: %s", last_cnpj)
                    
                except Exception as e:
                    logger.error("❌ Erro no lote %s: %s", batch_num, e)
                    logger.error("Cursor: %s, Size: %s", last_cnpj, current_batch_size)
                    raise
                
                processed += len(df_processed)
                batch_time = time.time() - batch_start
                
                # Ajustar tamanho do lote baseado na performance
                self.batch_size = self.adjust_batch_size(batch_time, self.batch_size)
                
                # Calcular métricas de performance
                records_per_second = len(df_processed) / batch_time if batch_time > 0 else 0
                total_time = time.time() - start_time
                avg_speed = processed / total_time if total_time > 0 else 0
                eta_seconds = (limit - processed) / avg_speed if avg_speed > 0 else 0
                eta_minutes = eta_seconds / 60
                
                logger.info(
                    "Lote %s: %s registros processados (%s/%s) - "
                    "Tempo: %.2fs - Velocidade: %.0f reg/s - "
                    "Média: %.0f reg/s - ETA: %.1f min - "
                    "Próximo lote: %s registros",
                    batch_num,
                    f"{len(df_processed):,}",
                    f"{processed:,}",
                    f"{limit:,}",
                    batch_time,
                    records_per_second,
                    avg_speed,
                    eta_minutes,
                    f"{self.batch_size:,}"
                )
                
                # Liberar recursos mínimos após cada lote (apenas a cada 5 lotes)
                if batch_num % 5 == 0:
                    self.cleanup_resources_after_batch()
                
                batch_num += 1
            
            total_time = time.time() - start_time
            final_speed = processed / total_time if total_time > 0 else 0
            
            logger.info(
                "Arquivo concluído! %s registros salvos em: %s",
                f"{processed:,}",
                output_path
            )
            logger.info(
                "Performance: %.0f registros/segundo em %.1f segundos",
                final_speed,
                total_time
            )
            
        except Exception as e:
            logger.error("Erro durante processamento ULTRA: %s", e)
            raise


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
