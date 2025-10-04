#!/usr/bin/env python3
"""
CNPJ Processor - Script principal
Executa o processamento de dados CNPJ
"""

import sys
import argparse
import json
import os
from pathlib import Path

# Adicionar o diretório pai ao path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.cnpj_processor import CNPJProcessor
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
    
    Returns:
        dict: Dicionário com filtros processados
    """
    print("\n" + "="*60)
    print("🔧 MODO FILTROS JSON")
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
    """Função principal do sistema"""
    parser = argparse.ArgumentParser(description='CNPJ Processor - Sistema de Processamento de Dados CNPJ')
    parser.add_argument(
        '--limit', 
        type=int, 
        default=50, 
        help='Limite de registros para processamento (padrão: 50). Use 0 para sem limite'
    )
    parser.add_argument(
        '--no-limit', 
        action='store_true',
        help='Processa todos os registros sem limite (equivale a --limit 0)'
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default='output/cnpj_empresas.csv',
        help='Caminho do arquivo de saída (padrão: output/cnpj_empresas.csv)'
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
    
    args = parser.parse_args()
    
    # Processar argumentos de limite
    if args.no_limit:
        limit = 0
    else:
        limit = args.limit
    
    try:
        # Criar diretório de saída se não existir
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar processador
        processor = CNPJProcessor()
        
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
        
        # Executar processamento
        if limit == 0:
            logger.info("🚀 Iniciando processamento SEM LIMITE (todos os registros)...")
        else:
            logger.info(f"🚀 Iniciando processamento com limite de {limit} registros...")
        logger.info(f"📁 Arquivo de saída: {args.output}")
        
        processor.run(limit=limit, output_path=args.output, filters=filters)
        
        logger.info("✅ Processamento concluído com sucesso!")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Processamento interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro durante processamento: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
