#!/usr/bin/env python3
"""
CNPJ Processor Streaming - Versão para Máxima Performance
Versão com consultas diretas, sem JOINs desnecessários e processamento em streaming
"""

import csv
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import pymysql

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.config import DATABASE_CONFIG
from src.config.config import OUTPUT_CONFIG

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CNPJProcessorStreaming:
    """
    Processador CNPJ com processamento em streaming para máxima performance
    - Consultas diretas sem JOINs complexos
    - Processamento linha por linha
    - Cache mínimo e eficiente
    """

    def __init__(self):
        self.connection = None
        self.batch_size = 1000  # Lotes menores para streaming
        
        # Caches mínimos
        self.cnae_cache = {}
        self.municipio_cache = {}
        self.pais_cache = {}
        
    def connect_database(self):
        """Conecta ao banco de dados MySQL"""
        try:
            db_config = DATABASE_CONFIG.copy()
            if "connection_timeout" in db_config:
                del db_config["connection_timeout"]
            
            self.connection = pymysql.connect(**db_config)
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
        logger.info("Conexão com banco de dados fechada")
    
    def load_minimal_cache(self):
        """Carrega apenas caches essenciais"""
        logger.info("Carregando caches essenciais...")
        
        cursor = self.connection.cursor()
        
        # Carregar apenas CNAEs mais comuns
        cursor.execute("SELECT cnae, descricao FROM cnpj_cnaes LIMIT 1000")
        self.cnae_cache = {str(row[0]): row[1] for row in cursor.fetchall()}
        
        # Carregar apenas municípios mais comuns
        cursor.execute("SELECT codigo, municipio FROM cnpj_municipios LIMIT 1000")
        self.municipio_cache = {str(row[0]): row[1] for row in cursor.fetchall()}
        
        # Carregar países
        cursor.execute("SELECT codigo, pais FROM cnpj_paises")
        self.pais_cache = {str(row[0]): row[1] for row in cursor.fetchall()}
        
        cursor.close()
        logger.info("Caches essenciais carregados")
    
    def build_simple_query(self, limit: int = 1000, filters_dict: Dict[str, Any] = None) -> str:
        """
        Constrói consulta SIMPLES sem JOINs complexos
        """
        # Query ultra simples - apenas tabela principal
        query = """
        SELECT 
            cnpj_part1,
            cnpj_part2,
            cnpj_part3,
            identificador_matriz_filial,
            nome_fantasia,
            situacao_cadastral,
            data_situacao_cadastral,
            motivo_situacao_cadastral,
            cidade_estrangeira,
            codigo_pais,
            data_inicio_atividade,
            cnae,
            tipo_logradouro,
            logradouro,
            numero,
            complemento,
            bairro,
            cep,
            uf,
            codigo_municipio,
            ddd1,
            telefone1,
            ddd2,
            telefone2,
            ddd_fax,
            fax,
            correio_eletronico,
            situacao_especial,
            data_situacao_especial,
            cnaes_secundarios
        FROM cnpj_estabelecimentos
        WHERE cnpj_part1 IS NOT NULL
        """
        
        # Aplicar filtros simples
        if filters_dict:
            if "uf" in filters_dict:
                query += f" AND uf = '{filters_dict['uf']}'"
            
            if "situacao_cadastral" in filters_dict:
                situacao = filters_dict["situacao_cadastral"]
                if situacao == "ativos":
                    query += " AND situacao_cadastral = 2"
                elif situacao == "inaptos":
                    query += " AND situacao_cadastral = 4"
                elif situacao == "inativos":
                    query += " AND situacao_cadastral IN (1, 3, 8)"
            
            if "codigo_municipio" in filters_dict:
                query += f" AND codigo_municipio = {filters_dict['codigo_municipio']}"
            
            if "cnae_codes" in filters_dict:
                cnae_list = "','".join(filters_dict["cnae_codes"])
                query += f" AND cnae IN ('{cnae_list}')"
        
        # Ordenação simples
        query += " ORDER BY cnpj_part1, data_inicio_atividade DESC"
        
        # Limite
        max_limit = min(limit, 200000) if limit > 0 else 200000
        query += f" LIMIT {max_limit}"
        
        return query
    
    def get_empresa_data(self, cnpj_part1: str) -> Dict[str, Any]:
        """Busca dados da empresa individualmente"""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT razao_social, natureza_juridica, qualificacao_socio, capital_social, porte_empresa "
            "FROM cnpj_empresas WHERE cnpj_part1 = %s",
            (cnpj_part1,)
        )
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                'razao_social': result[0],
                'natureza_juridica': result[1],
                'qualificacao_socio': result[2],
                'capital_social': result[3],
                'porte_empresa': result[4]
            }
        return {
            'razao_social': None,
            'natureza_juridica': None,
            'qualificacao_socio': None,
            'capital_social': None,
            'porte_empresa': None
        }
    
    def get_simples_data(self, cnpj_part1: str) -> Dict[str, Any]:
        """Busca dados do simples nacional individualmente"""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT opcao_simples, data_opcao_simples, data_exclusao_simples, opcao_mei, data_opcao_mei, data_exclusao_opcao_mei "
            "FROM cnpj_simples WHERE cnpj_part1 = %s",
            (cnpj_part1,)
        )
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                'opcao_simples': result[0],
                'data_opcao_simples': result[1],
                'data_exclusao_simples': result[2],
                'opcao_mei': result[3],
                'data_opcao_mei': result[4],
                'data_exclusao_opcao_mei': result[5]
            }
        return {
            'opcao_simples': None,
            'data_opcao_simples': None,
            'data_exclusao_simples': None,
            'opcao_mei': None,
            'data_opcao_mei': None,
            'data_exclusao_opcao_mei': None
        }
    
    def get_socios_data(self, cnpj_part1: str) -> str:
        """Busca dados dos sócios individualmente"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT 
                identificador_socio,
                nome_socio,
                codigo_qualificacao_socio,
                data_entrada_sociedade
            FROM cnpj_socios 
            WHERE cnpj_part1 = %s
            LIMIT 5
        """, (cnpj_part1,))
        
        results = cursor.fetchall()
        cursor.close()
        
        if results:
            socios_info = []
            for row in results:
                socios_info.append(
                    f"ID: {row[0] or ''} | Nome: {row[1] or ''} | Qualificação: {row[2] or ''} | Data: {row[3] or ''}"
                )
            return " | ".join(socios_info)
        return ""
    
    def process_row_streaming(self, row: tuple, row_id: int) -> Dict[str, Any]:
        """Processa uma linha individualmente"""
        # Dados básicos
        processed = {
            'id': row_id,
            'cnpj_part1': row[0],
            'cnpj_part2': row[1],
            'cnpj_part3': row[2],
            'cnpj': f"{row[0]}{row[1]}{row[2]}",
            'identificador_m_f': row[3],
            'nome_fantasia': row[4],
            'situacao_cadastral': row[5],
            'data_situacao_cadastral': row[6],
            'motivo_situacao_cadastral': row[7],
            'nome_cidade_exterior': row[8],
            'codigo_pais': row[9],
            'data_inicio_atividade': row[10],
            'cnae_codes': row[11],
            'tipo_logradouro': row[12],
            'logradouro': row[13],
            'numero': row[14],
            'complemento': row[15],
            'bairro': row[16],
            'cep': row[17],
            'uf': row[18],
            'codigo_municipio': row[19],
            'ddd_telefone_1': f"{row[20] or ''}{row[21] or ''}",
            'telefone1_celular': 1 if row[21] and len(str(row[21])) == 9 and str(row[21])[0] == '9' else 0,
            'ddd_telefone_2': f"{row[22] or ''}{row[23] or ''}",
            'telefone2_celular': 1 if row[23] and len(str(row[23])) == 9 and str(row[23])[0] == '9' else 0,
            'ddd_fax': f"{row[24] or ''}{row[25] or ''}",
            'correio_eletronico': row[26],
            'email': 1 if row[26] and '@' in str(row[26]) else 0,
            'situacao_especial': row[27],
            'data_situacao_especial': row[28],
            'cnaes_secundarios': row[29]
        }
        
        # Lookups básicos
        processed['cnae_fiscal'] = self.cnae_cache.get(str(row[11]), '')
        processed['municipio'] = self.municipio_cache.get(str(row[19]), '')
        processed['pais'] = self.pais_cache.get(str(row[9]), '')
        
        # Corrigir código do país
        if processed['codigo_pais'] == 0:
            processed['codigo_pais'] = 105
        
        # Dados da empresa
        empresa_data = self.get_empresa_data(row[0])
        processed.update({
            'razao_social': empresa_data['razao_social'],
            'codigo_natureza_juridica': empresa_data['natureza_juridica'],
            'qualificacao_responsavel': empresa_data['qualificacao_socio'],
            'capital_social_empresa': empresa_data['capital_social'],
            'porte_empresa': empresa_data['porte_empresa']
        })
        
        # Dados do simples
        simples_data = self.get_simples_data(row[0])
        processed.update(simples_data)
        
        # Dados dos sócios
        processed['socios'] = self.get_socios_data(row[0])
        
        return processed
    
    def run_streaming(self, limit: int = 1000, output_path: str = None, filters_dict: Dict[str, Any] = None):
        """Executa processamento em streaming"""
        try:
            start_time = time.time()
            
            self.connect_database()
            self.load_minimal_cache()
            
            # Preparar arquivo de saída
            if output_path is None:
                output_path = os.path.join(
                    OUTPUT_CONFIG['output_dir'], 'cnpj_empresas_streaming.csv'
                )
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Construir consulta
            query = self.build_simple_query(limit, filters_dict)
            
            logger.info("Iniciando processamento em streaming...")
            logger.info("Consulta: %s", query[:200] + "..." if len(query) > 200 else query)
            
            # Executar consulta
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            # Processar em streaming
            processed = 0
            batch_data = []
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = None
                
                while True:
                    row = cursor.fetchone()
                    if not row:
                        break
                    
                    # Processar linha
                    processed_row = self.process_row_streaming(row, processed + 1)
                    batch_data.append(processed_row)
                    
                    # Escrever em lotes
                    if len(batch_data) >= self.batch_size:
                        if writer is None:
                            writer = csv.DictWriter(
                                csvfile, 
                                fieldnames=batch_data[0].keys(),
                                delimiter=';',
                                quoting=csv.QUOTE_ALL
                            )
                            writer.writeheader()
                        
                        for row_data in batch_data:
                            writer.writerow(row_data)
                        
                        processed += len(batch_data)
                        current_time = time.time()
                        speed = processed / (current_time - start_time) if current_time > start_time else 0
                        
                        logger.info(
                            "Processados %s registros - Velocidade: %.0f reg/s",
                            f"{processed:,}",
                            speed
                        )
                        
                        batch_data = []
                
                # Escrever último lote
                if batch_data:
                    if writer is None:
                        writer = csv.DictWriter(
                            csvfile, 
                            fieldnames=batch_data[0].keys(),
                            delimiter=';',
                            quoting=csv.QUOTE_ALL
                        )
                        writer.writeheader()
                    
                    for row_data in batch_data:
                        writer.writerow(row_data)
                    
                    processed += len(batch_data)
            
            cursor.close()
            
            total_time = time.time() - start_time
            final_speed = processed / total_time if total_time > 0 else 0
            
            logger.info(
                "Processamento em streaming concluído! %s registros salvos em: %s",
                f"{processed:,}",
                output_path
            )
            logger.info(
                "Performance final: %.0f registros/segundo em %.1f segundos",
                final_speed,
                total_time
            )
            
        except Exception as e:
            logger.error("Erro durante processamento em streaming: %s", e)
            raise
        finally:
            self.close_database()


# Função de conveniência
def run_streaming_processing(
    limit: int = 1000, output_path: str = None, filters_dict: Dict[str, Any] = None
):
    """Função de conveniência para executar processamento em streaming"""
    processor = CNPJProcessorStreaming()
    processor.run_streaming(limit=limit, output_path=output_path, filters_dict=filters_dict)


if __name__ == "__main__":
    # Exemplo de uso
    processor_example = CNPJProcessorStreaming()
    
    filters_run = {"uf": "SP", "situacao_cadastral": "ativos"}
    
    processor_example.run_streaming(
        limit=1000, 
        output_path="output/sp_ativos_streaming.csv", 
        filters_dict=filters_run
    )
