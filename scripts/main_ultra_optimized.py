#!/usr/bin/env python3
"""
Script principal para processamento ULTRA otimizado
Versão com máxima performance para grandes volumes
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cnpj_processor.cnpj_processor_ultra_optimized import CNPJProcessorUltraOptimized
from src.filters import CNPJFilters

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)




def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Processador CNPJ ULTRA Otimizado - Máxima Performance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

1. Processamento básico com limite:
   python scripts/main_ultra_optimized.py --limit 50000

2. Processamento com filtros interativos:
   python scripts/main_ultra_optimized.py --limit 100000 --filters

3. Processamento completo (máximo 200.000 registros):
   python scripts/main_ultra_optimized.py --limit 0

4. Teste de conexão:
   python scripts/main_ultra_optimized.py --test-connection
        """
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=1000,
        help='Limite de registros para processamento (0 = máximo de 200.000)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Caminho do arquivo de saída (padrão: output/cnpj_empresas_ultra.csv)'
    )
    
    parser.add_argument(
        '--filters',
        action='store_true',
        help='Ativa modo interativo para configuração de filtros'
    )
    
    parser.add_argument(
        '--count-only',
        action='store_true',
        help='Apenas contar registros sem processar'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50000,
        help='Tamanho do lote para processamento (padrão: 50000)'
    )
    
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='Testar conexão com banco de dados'
    )
    
    args = parser.parse_args()
    
    # Obter diretório raiz do projeto (pasta pai de scripts/)
    project_root = Path(__file__).parent.parent
    
    # Configurar caminho de saída padrão
    if args.output is None:
        args.output = str(project_root / 'output' / 'cnpj_empresas_ultra.csv')
    
    # Criar diretório de saída se não existir
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    # Carregar filtros
    filters = None
    if args.filters:
        filter_manager = CNPJFilters()
        filters = filter_manager.coletar_filtros()
    
    # Inicializar processador ULTRA otimizado
    processor = CNPJProcessorUltraOptimized()
    
    # Configurar tamanho do lote personalizado
    if args.batch_size != 50000:
        processor.batch_size = args.batch_size
        logger.info("Tamanho do lote configurado para: %s registros", f"{args.batch_size:,}")
    
    try:
        # Teste de conexão
        if args.test_connection:
            logger.info("🔍 Testando conexão com banco de dados...")
            processor.connect_database()
            processor.close_database()
            logger.info("✅ Conexão com banco de dados bem-sucedida!")
            return 0
        
        # Apenas contar registros
        if args.count_only:
            logger.info("📊 Contando registros...")
            processor.connect_database()
            total = processor.get_total_count_optimized(filters)
            processor.close_database()
            logger.info("Total de registros encontrados: %s", f"{total:,}")
            return 0
        
        # Executar processamento ULTRA otimizado
        if args.limit == 0:
            logger.info("🚀 Iniciando processamento ULTRA com limite máximo de 200.000 registros...")
        else:
            logger.info("🚀 Iniciando processamento ULTRA com limite de %s registros...", f"{args.limit:,}")
        
        logger.info("📁 Arquivo de saída: %s", args.output)
        logger.info("📦 Tamanho do lote: %s registros", f"{processor.batch_size:,}")
        
        if filters:
            logger.info("📋 Filtros aplicados: %s", list(filters.keys()))
        
        # Executar processamento
        processor.run_ultra_optimized(
            limit=args.limit,
            output_path=args.output,
            filters_dict=filters
        )
        
        logger.info("✅ Processamento ULTRA concluído com sucesso!")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("⚠️ Processamento interrompido pelo usuário")
        return 1
    except Exception as e:
        logger.error("❌ Erro durante processamento: %s", e)
        return 1


if __name__ == "__main__":
    exit(main())
