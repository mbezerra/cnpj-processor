#!/usr/bin/env python3
"""
Script principal para processamento em streaming
Versão com máxima performance usando processamento linha por linha
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cnpj_processor.cnpj_processor_streaming import CNPJProcessorStreaming

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_filters_from_json(json_file: str) -> dict:
    """Carrega filtros de arquivo JSON"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error("Erro ao carregar arquivo de filtros: %s", e)
        raise


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Processador CNPJ Streaming - Máxima Performance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

1. Processamento básico:
   python scripts/main_streaming.py --limit 1000

2. Processamento com filtros:
   python scripts/main_streaming.py --limit 5000 --filters "{\\"uf\\": \\"SP\\", \\"situacao_cadastral\\": \\"ativos\\"}"

3. Processamento com arquivo de filtros:
   python scripts/main_streaming.py --json examples/exemplos_filtros.json --exemplo exemplo_basico

4. Processamento completo (máximo 200.000 registros):
   python scripts/main_streaming.py --limit 0

5. Teste de conexão:
   python scripts/main_streaming.py --test-connection
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
        help='Caminho do arquivo de saída (padrão: output/cnpj_empresas_streaming.csv)'
    )
    
    parser.add_argument(
        '--filters',
        type=str,
        help='Filtros em formato JSON'
    )
    
    parser.add_argument(
        '--json',
        type=str,
        help='Arquivo JSON com exemplos de filtros'
    )
    
    parser.add_argument(
        '--exemplo',
        type=str,
        help='Nome do exemplo de filtro a usar (ex: exemplo_basico, exemplo_completo)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Tamanho do lote para processamento (padrão: 1000)'
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
        args.output = str(project_root / 'output' / 'cnpj_empresas_streaming.csv')
    
    # Criar diretório de saída se não existir
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    # Carregar filtros
    filters = None
    if args.filters:
        try:
            filters = json.loads(args.filters)
        except json.JSONDecodeError as e:
            logger.error("Erro ao parsear filtros JSON: %s", e)
            return 1
    
    elif args.json and args.exemplo:
        try:
            filters_data = load_filters_from_json(args.json)
            if args.exemplo in filters_data:
                filters = filters_data[args.exemplo]
                logger.info("Filtros carregados do exemplo: %s", args.exemplo)
            else:
                logger.error("Exemplo '%s' não encontrado no arquivo JSON", args.exemplo)
                return 1
        except Exception as e:
            logger.error("Erro ao carregar filtros do JSON: %s", e)
            return 1
    
    # Inicializar processador streaming
    processor = CNPJProcessorStreaming()
    
    # Configurar tamanho do lote personalizado
    if args.batch_size != 1000:
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
        
        # Executar processamento streaming
        if args.limit == 0:
            logger.info("🚀 Iniciando processamento STREAMING com limite máximo de 200.000 registros...")
        else:
            logger.info("🚀 Iniciando processamento STREAMING com limite de %s registros...", f"{args.limit:,}")
        
        logger.info("📁 Arquivo de saída: %s", args.output)
        logger.info("📦 Tamanho do lote: %s registros", f"{processor.batch_size:,}")
        
        if filters:
            logger.info("📋 Filtros aplicados: %s", list(filters.keys()))
        
        # Executar processamento
        processor.run_streaming(
            limit=args.limit,
            output_path=args.output,
            filters_dict=filters
        )
        
        logger.info("✅ Processamento STREAMING concluído com sucesso!")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("⚠️ Processamento interrompido pelo usuário")
        return 1
    except Exception as e:
        logger.error("❌ Erro durante processamento: %s", e)
        return 1


if __name__ == "__main__":
    exit(main())
