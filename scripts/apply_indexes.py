#!/usr/bin/env python3
"""
Script para aplicar índices essenciais ao banco de dados
Versão segura que trata erros de índices duplicados
"""

import logging
import sys
from pathlib import Path

import pymysql

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config.config import DATABASE_CONFIG

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IndexManager:
    """Gerenciador de índices para o banco de dados CNPJ"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect_database(self):
        """Conecta ao banco de dados"""
        try:
            # Remover connection_timeout se existir
            db_config = DATABASE_CONFIG.copy()
            if 'connection_timeout' in db_config:
                del db_config['connection_timeout']
                
            self.connection = pymysql.connect(**db_config)
            self.cursor = self.connection.cursor()
            
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
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Conexão com banco de dados fechada")
        
    def create_index_safe(self, table_name: str, index_name: str, columns: str, description: str = ""):
        """
        Cria um índice de forma segura, ignorando erros de duplicação
        
        Args:
            table_name: Nome da tabela
            index_name: Nome do índice
            columns: Especificação das colunas
            description: Descrição do índice
        """
        try:
            query = f"CREATE INDEX {index_name} ON {table_name} ({columns})"
            self.cursor.execute(query)
            self.connection.commit()
            logger.info("✅ %s - %s", index_name, description or "Criado com sucesso")
            return True
            
        except pymysql.err.OperationalError as e:
            if e.args[0] == 1061:  # Duplicate key name
                logger.info("⚠️  %s - Já existe, ignorando", index_name)
                return True
            else:
                logger.error("❌ %s - Erro: %s", index_name, e)
                return False
        except Exception as e:
            logger.error("❌ %s - Erro inesperado: %s", index_name, e)
            return False
            
    def apply_essential_indexes(self):
        """Aplica todos os índices essenciais"""
        
        logger.info("🚀 Iniciando aplicação de índices essenciais...")
        
        # Lista de índices essenciais
        indexes = [
            # Índices primários (críticos)
            {
                'table': 'cnpj_estabelecimentos',
                'name': 'idx_estabelecimentos_cnpj_data',
                'columns': 'cnpj_part1(8), data_inicio_atividade DESC',
                'description': 'Índice principal para ordenação'
            },
            {
                'table': 'cnpj_estabelecimentos',
                'name': 'idx_estabelecimentos_uf_situacao',
                'columns': 'uf, situacao_cadastral, data_inicio_atividade DESC',
                'description': 'Filtros geográficos mais comuns'
            },
            {
                'table': 'cnpj_estabelecimentos',
                'name': 'idx_estabelecimentos_cnae_data',
                'columns': 'cnae, data_inicio_atividade DESC',
                'description': 'Filtros de CNAE'
            },
            
            # Índices para tabelas de lookup
            {
                'table': 'cnpj_empresas',
                'name': 'idx_empresas_cnpj',
                'columns': 'cnpj_part1(8)',
                'description': 'Tabela de empresas'
            },
            {
                'table': 'cnpj_simples',
                'name': 'idx_simples_cnpj',
                'columns': 'cnpj_part1(8)',
                'description': 'Tabela simples nacional'
            },
            {
                'table': 'cnpj_socios',
                'name': 'idx_socios_cnpj',
                'columns': 'cnpj_part1(8), codigo_qualificacao_socio',
                'description': 'Tabela de sócios'
            },
            
            # Índices para filtros específicos
            {
                'table': 'cnpj_estabelecimentos',
                'name': 'idx_estabelecimentos_email',
                'columns': 'correio_eletronico(50), cnpj_part1(8)',
                'description': 'Empresas com email'
            },
            {
                'table': 'cnpj_estabelecimentos',
                'name': 'idx_estabelecimentos_telefone',
                'columns': 'telefone1, cnpj_part1(8)',
                'description': 'Empresas com telefone'
            }
        ]
        
        # Aplicar índices
        success_count = 0
        for idx in indexes:
            if self.create_index_safe(idx['table'], idx['name'], idx['columns'], idx['description']):
                success_count += 1
                
        logger.info("📊 Resultado: %d/%d índices aplicados com sucesso", success_count, len(indexes))
        
        # Atualizar estatísticas
        self.update_statistics()
        
        # Verificar índices criados
        self.verify_indexes()
        
    def update_statistics(self):
        """Atualiza estatísticas das tabelas"""
        logger.info("📈 Atualizando estatísticas das tabelas...")
        
        tables = ['cnpj_estabelecimentos', 'cnpj_empresas', 'cnpj_simples', 'cnpj_socios']
        
        for table in tables:
            try:
                self.cursor.execute(f"ANALYZE TABLE {table}")
                logger.info("✅ Estatísticas atualizadas para %s", table)
            except Exception as e:
                logger.warning("⚠️  Erro ao atualizar estatísticas para %s: %s", table, e)
                
    def verify_indexes(self):
        """Verifica se os índices foram criados corretamente"""
        logger.info("🔍 Verificando índices criados...")
        
        try:
            query = """
            SELECT 
                TABLE_NAME,
                INDEX_NAME,
                GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX SEPARATOR ', ') as COLUMNS
            FROM information_schema.STATISTICS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME IN ('cnpj_estabelecimentos', 'cnpj_empresas', 'cnpj_simples', 'cnpj_socios')
            AND INDEX_NAME LIKE 'idx_%'
            GROUP BY TABLE_NAME, INDEX_NAME
            ORDER BY TABLE_NAME, INDEX_NAME
            """
            
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            if results:
                logger.info("📋 Índices encontrados:")
                for table, index, columns in results:
                    logger.info("  %s.%s: %s", table, index, columns)
            else:
                logger.warning("⚠️  Nenhum índice encontrado")
                
        except Exception as e:
            logger.error("❌ Erro ao verificar índices: %s", e)
            
    def test_performance(self):
        """Testa uma consulta para verificar se os índices estão sendo usados"""
        logger.info("🧪 Testando performance com EXPLAIN...")
        
        try:
            query = """
            EXPLAIN SELECT 
                est.cnpj_part1,
                est.data_inicio_atividade,
                e.razao_social
            FROM cnpj_estabelecimentos est
            INNER JOIN cnpj_empresas e ON est.cnpj_part1 = e.cnpj_part1
            WHERE est.uf = 'SP'
            AND est.situacao_cadastral = 2
            ORDER BY est.cnpj_part1, est.data_inicio_atividade DESC
            LIMIT 1000
            """
            
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            logger.info("📊 Resultado do EXPLAIN:")
            for row in results:
                logger.info("  %s", row)
                
        except Exception as e:
            logger.error("❌ Erro no teste de performance: %s", e)


def main():
    """Função principal"""
    manager = IndexManager()
    
    try:
        manager.connect_database()
        manager.apply_essential_indexes()
        manager.test_performance()
        
        logger.info("🎉 Processo concluído com sucesso!")
        logger.info("💡 Agora você pode usar os processadores otimizados:")
        logger.info("   python scripts/main_ultra_optimized.py")
        logger.info("   python scripts/main_streaming.py")
        logger.info("   python scripts/benchmark_performance.py")
        
    except Exception as e:
        logger.error("💥 Erro durante o processo: %s", e)
        sys.exit(1)
        
    finally:
        manager.close_database()


if __name__ == "__main__":
    main()
