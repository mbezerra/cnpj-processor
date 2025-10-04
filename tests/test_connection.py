#!/usr/bin/env python3
"""
CNPJ Processor - Teste de Conexão
Verifica conexão com MySQL
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.cnpj_processor import CNPJProcessor
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_connection():
    """Testa a conexão com o banco MySQL"""
    try:
        processor = CNPJProcessor()
        processor.connect_database()
        
        # Testa uma consulta simples
        cursor = processor.connection.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM cnpj_empresas")
        result = cursor.fetchone()
        logger.info(f"Total de empresas no banco: {result[0]}")
        
        # Testa consulta em estabelecimentos
        cursor.execute("SELECT COUNT(*) as total FROM cnpj_estabelecimentos")
        result = cursor.fetchone()
        logger.info(f"Total de estabelecimentos no banco: {result[0]}")
        
        # Testa JOIN básico
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM cnpj_estabelecimentos est
            LEFT JOIN cnpj_empresas e ON est.cnpj_part1 = e.cnpj_part1
            LIMIT 1
        """)
        result = cursor.fetchone()
        logger.info(f"Teste de JOIN executado com sucesso: {result[0]} registros")
        
        processor.close_database()
        logger.info("✅ Conexão com MySQL funcionando perfeitamente!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na conexão: {e}")
        return False

if __name__ == "__main__":
    test_connection()
