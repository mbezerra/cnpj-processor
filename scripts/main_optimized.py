#!/usr/bin/env python3
"""
CNPJ Processor Otimizado - Script principal para grandes volumes
Versão otimizada com paginação, cache e melhor performance
"""

import sys
import argparse
import json
import os
from pathlib import Path

# Adicionar o diretório pai ao path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.cnpj_processor.cnpj_processor_optimized import CNPJProcessorOptimized
from src.filters import CNPJFilters
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def coletar_filtros_json():
    """
    Coleta filtros via JSON de forma interativa
    """
    print("\n" + "="*60)
    print("🔧 MODO FILTROS JSON (OTIMIZADO)")
    print("="*60)
    print("Cole o JSON com os filtros desejados abaixo.")
    print("Exemplo de formato:")
    print('{"uf": "SP", "codigo_municipio": 7107, "situacao_cadastral": "ativos"}')
    print("\nFiltros disponíveis:")
    print("- uf: Sigla do estado (ex: 'SP', 'RJ')")
    print("- codigo_municipio: Código do município (ex: 7107)")
    print("- situacao_cadastral: 'ativos', 'inaptos', 'inativos'")
    print("- cnae_codes: Lista de códigos CNAE (ex: ['1234567', '7654321'])")
    print("- data_inicio_atividade: {'inicio': '20200101', 'fim': '20231231'}")
    print("- com_email: true/false")
    print("- com_telefone: true/false")
    print("- tipo_telefone: 'fixo', 'celular', 'ambos'")
    print("- opcao_tributaria: 'mei', 'sem_mei', 'todas'")
    print("- capital_social: '10k', '50k', '100k', 'qualquer'")
    print("\nPressione Enter duas vezes para finalizar a entrada:")
    print("-"*60)
    
    lines = []
    empty_lines = 0
    
    while True:
        try:
            line = input()
            if line.strip() == "":
                empty_lines += 1
                if empty_lines >= 2:
                    break
            else:
                empty_lines = 0
            lines.append(line)
        except EOFError:
            break
    
    json_text = "\n".join(lines).strip()
    
    if not json_text:
        print("❌ Nenhum JSON fornecido.")
        print("❌ Operação cancelada. É necessário fornecer um JSON válido para usar filtros.")
        return "CANCELADO"
    
    try:
        filters = json.loads(json_text)
        print(f"✅ JSON processado com sucesso!")
        print(f"📋 Filtros aplicados: {list(filters.keys())}")
        return filters
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao processar JSON: {e}")
        print("❌ JSON inválido. Processando sem filtros.")
        return None

def main():
    """Função principal do sistema otimizado"""
    # Obter diretório raiz do projeto (pasta pai de scripts/)
    project_root = Path(__file__).parent.parent
    
    parser = argparse.ArgumentParser(
        description='CNPJ Processor Otimizado - Sistema de Processamento de Dados CNPJ para Grandes Volumes'
    )
    parser.add_argument(
        '--limit', 
        type=int, 
        default=0, 
        help='Limite de registros para processamento (padrão: 0 = sem limite)'
    )
    parser.add_argument(
        '--batch-size', 
        type=int, 
        default=10000, 
        help='Tamanho do lote para processamento (padrão: 10000)'
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default=str(project_root / 'output' / 'cnpj_optimized_data.csv'),
        help='Caminho do arquivo de saída (padrão: output/cnpj_optimized_data.csv)'
    )
    parser.add_argument(
        '--test-connection', 
        action='store_true',
        help='Apenas testa a conexão com o banco de dados'
    )
    parser.add_argument(
        '--filters', 
        action='store_true',
        help='Ativa modo interativo para configuração de filtros'
    )
    parser.add_argument(
        '--json', 
        action='store_true',
        help='Permite inserir filtros via JSON interativamente'
    )
    parser.add_argument(
        '--count-only',
        action='store_true',
        help='Apenas conta registros que atendem aos filtros (não processa)'
    )
    
    args = parser.parse_args()
    
    try:
        # Converter caminho relativo para absoluto se necessário
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = project_root / args.output
        
        # Criar diretório de saída se não existir
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar processador otimizado
        processor = CNPJProcessorOptimized()
        
        # Configurar tamanho do lote se especificado
        if args.batch_size != 10000:
            processor.batch_size = args.batch_size
        
        # Coletar filtros se solicitado
        filters = None
        if args.filters:
            filter_manager = CNPJFilters()
            filters = filter_manager.coletar_filtros()
        elif args.json:
            filters = coletar_filtros_json()
            if filters == "CANCELADO":
                logger.info("❌ Operação cancelada pelo usuário.")
                return
        
        if args.test_connection:
            logger.info("🔍 Testando conexão com o banco de dados...")
            processor.connect_database()
            
            # Teste rápido
            cursor = processor.connection.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM cnpj_empresas")
            empresas = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) as total FROM cnpj_estabelecimentos")
            estabelecimentos = cursor.fetchone()[0]
            
            logger.info(f"✅ Conexão OK! Empresas: {empresas:,} | Estabelecimentos: {estabelecimentos:,}")
            processor.close_database()
            return
        
        if args.count_only:
            logger.info("🔢 Contando registros que atendem aos filtros...")
            processor.connect_database()
            processor.setup_optimization_settings()
            
            total = processor.get_total_count(filters)
            logger.info(f"📊 Total de registros: {total:,}")
            
            if filters:
                logger.info(f"📋 Filtros aplicados: {list(filters.keys())}")
            
            processor.close_database()
            return
        
        # Executar processamento otimizado
        if args.limit == 0:
            logger.info("🚀 Iniciando processamento OTIMIZADO com limite máximo de 200.000 registros...")
        else:
            logger.info(f"🚀 Iniciando processamento OTIMIZADO com limite de {args.limit:,} registros...")
        
        logger.info(f"📁 Arquivo de saída: {output_path}")
        logger.info(f"📦 Tamanho do lote: {processor.batch_size:,} registros")
        
        if filters:
            logger.info(f"📋 Filtros aplicados: {list(filters.keys())}")
        
        # Executar processamento
        processor.run_optimized(limit=args.limit, output_path=str(output_path), filters=filters)
        
        logger.info("✅ Processamento OTIMIZADO concluído com sucesso!")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Processamento interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro durante processamento: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
