#!/usr/bin/env python3
"""
Script principal para processamento ULTRA otimizado
Versão com máxima performance para grandes volumes
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cnpj_processor.cnpj_processor_ultra_optimized import (
    CNPJProcessorUltraOptimized
)
from src.filters import CNPJFilters

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_output_filename(base_path: str, filters: dict = None, 
                           file_part: int = 1, total_parts: int = 1) -> str:
    """
    Gera nome do arquivo de saída com sufixo baseado nos filtros de UF
    
    Args:
        base_path: Caminho base do arquivo
        filters: Dicionário com filtros aplicados
        file_part: Número da parte atual (1, 2, 3...)
        total_parts: Total de partes que serão geradas
        
    Returns:
        Caminho do arquivo com sufixo apropriado
    """
    path_obj = Path(base_path)
    
    # Verificar se há filtro de UF
    if filters and 'uf' in filters:
        uf = filters['uf'].upper()
        # Adicionar sufixo _UF ao nome do arquivo
        base_name = f"{path_obj.stem}_{uf}"
    else:
        # Se não há filtro de UF ou são todas as UFs, usar sufixo _BR
        base_name = f"{path_obj.stem}_BR"
    
    # Adicionar numeração de partes
    new_name = f"{base_name}_{file_part}_de_{total_parts}{path_obj.suffix}"
    return str(path_obj.parent / new_name)


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
        help='Caminho do arquivo de saída (padrão: output/cnpj_empresas.csv)'
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

    # Carregar filtros primeiro para determinar o nome do arquivo
    filters = None
    if args.filters:
        filter_manager = CNPJFilters()
        filters = filter_manager.coletar_filtros()

    # Configurar caminho de saída padrão
    if args.output is None:
        base_output = str(project_root / 'output' / 'cnpj_empresas.csv')
    else:
        base_output = args.output

    # Criar diretório de saída se não existir
    Path(base_output).parent.mkdir(parents=True, exist_ok=True)

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

        # Obter contagem total de registros (sem limite para divisão de arquivos)
        logger.info("📊 Contando registros...")
        processor.connect_database()
        total_records = processor.get_total_count_optimized(filters, apply_limit=False)
        processor.close_database()
        
        # Aplicar limite se especificado
        if args.limit > 0:
            total_records = min(total_records, args.limit)
        
        logger.info("Total de registros a processar: %s", f"{total_records:,}")
        
        # Determinar se precisa dividir arquivos
        max_records_per_file = 500000
        if total_records > max_records_per_file:
            total_files = (total_records + max_records_per_file - 1) // max_records_per_file
            logger.info("📁 Arquivos serão divididos em %s partes (máximo %s registros por arquivo)", 
                       total_files, f"{max_records_per_file:,}")
        else:
            total_files = 1
            logger.info("📁 Arquivo único será gerado")
        
        logger.info("📦 Tamanho do lote: %s registros", f"{processor.batch_size:,}")
        if filters:
            logger.info("📋 Filtros aplicados: %s", list(filters.keys()))

        # Executar processamento com divisão de arquivos
        processor.connect_database()
        processor.setup_ultra_optimization_settings()
        processor.preload_lookup_caches()
        
        processed_total = 0
        for file_part in range(1, total_files + 1):
            # Calcular limites para este arquivo
            start_offset = (file_part - 1) * max_records_per_file
            file_limit = min(max_records_per_file, total_records - start_offset)
            
            # Gerar nome do arquivo para esta parte
            output_file = generate_output_filename(base_output, filters, file_part, total_files)
            
            logger.info("🚀 Processando arquivo %s de %s: %s", 
                       file_part, total_files, Path(output_file).name)
            logger.info("📊 Registros neste arquivo: %s (offset: %s)", 
                       f"{file_limit:,}", f"{start_offset:,}")
            
            # Executar processamento para este arquivo
            processor.run_ultra_optimized_with_offset(
                limit=file_limit,
                offset=start_offset,
                output_path=output_file,
                filters_dict=filters
            )
            
            processed_total += file_limit
            logger.info("✅ Arquivo %s de %s concluído! (%s/%s registros processados)", 
                       file_part, total_files, f"{processed_total:,}", f"{total_records:,}")
        
        processor.close_database()
        logger.info("✅ Processamento ULTRA concluído com sucesso! %s arquivos gerados", total_files)
        return 0

    except KeyboardInterrupt:
        logger.warning("⚠️ Processamento interrompido pelo usuário")
        return 1
    except (ConnectionError, OSError, ValueError) as e:
        logger.error("❌ Erro durante processamento: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())