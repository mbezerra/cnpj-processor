#!/usr/bin/env python3
"""
Script de Benchmark de Performance
Compara diferentes versões do processador CNPJ
"""

import time
import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cnpj_processor.cnpj_processor import CNPJProcessor
from src.cnpj_processor.cnpj_processor_optimized import CNPJProcessorOptimized
from src.cnpj_processor.cnpj_processor_ultra_optimized import CNPJProcessorUltraOptimized

import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def benchmark_processor(processor_class, name: str, limit: int = 1000, filters: dict = None):
    """Executa benchmark de um processador"""
    logger.info(f"\n🚀 Iniciando benchmark: {name}")
    logger.info(f"📊 Limite: {limit:,} registros")
    logger.info(f"📋 Filtros: {filters}")
    
    start_time = time.time()
    
    try:
        processor = processor_class()
        
        if name == "ULTRA Otimizado":
            processor.run_ultra_optimized(
                limit=limit,
                output_path=f"output/benchmark_{name.lower().replace(' ', '_')}.csv",
                filters_dict=filters
            )
        elif name == "Otimizado":
            processor.run_optimized(
                limit=limit,
                output_path=f"output/benchmark_{name.lower().replace(' ', '_')}.csv",
                filters_run=filters
            )
        else:
            processor.run(
                limit=limit,
                output_path=f"output/benchmark_{name.lower().replace(' ', '_')}.csv",
                filters=filters
            )
        
        end_time = time.time()
        duration = end_time - start_time
        records_per_second = limit / duration if duration > 0 else 0
        
        logger.info(f"✅ {name} concluído!")
        logger.info(f"⏱️  Tempo total: {duration:.2f} segundos")
        logger.info(f"📈 Velocidade: {records_per_second:.0f} registros/segundo")
        
        return {
            'name': name,
            'duration': duration,
            'records_per_second': records_per_second,
            'success': True
        }
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        logger.error(f"❌ {name} falhou: {e}")
        
        return {
            'name': name,
            'duration': duration,
            'records_per_second': 0,
            'success': False,
            'error': str(e)
        }


def main():
    """Função principal do benchmark"""
    logger.info("🎯 Iniciando Benchmark de Performance dos Processadores CNPJ")
    logger.info("=" * 80)
    
    # Configurar diretório de saída
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Configurações de teste
    test_configs = [
        {
            'name': 'Teste Pequeno',
            'limit': 1000,
            'filters': {'uf': 'SP', 'situacao_cadastral': 'ativos'}
        },
        {
            'name': 'Teste Médio',
            'limit': 10000,
            'filters': {'uf': 'SP', 'situacao_cadastral': 'ativos'}
        },
        {
            'name': 'Teste Grande',
            'limit': 50000,
            'filters': {'uf': 'SP', 'situacao_cadastral': 'ativos'}
        }
    ]
    
    # Processadores para testar
    processors = [
        (CNPJProcessor, "Padrão"),
        (CNPJProcessorOptimized, "Otimizado"),
        (CNPJProcessorUltraOptimized, "ULTRA Otimizado")
    ]
    
    results = []
    
    for test_config in test_configs:
        logger.info(f"\n{'='*20} {test_config['name']} {'='*20}")
        
        for processor_class, processor_name in processors:
            result = benchmark_processor(
                processor_class,
                processor_name,
                test_config['limit'],
                test_config['filters']
            )
            
            result.update(test_config)
            results.append(result)
            
            # Pausa entre testes para não sobrecarregar o banco
            time.sleep(2)
    
    # Relatório final
    logger.info("\n" + "="*80)
    logger.info("📊 RELATÓRIO FINAL DE PERFORMANCE")
    logger.info("="*80)
    
    # Agrupar resultados por teste
    for test_config in test_configs:
        logger.info(f"\n🔍 {test_config['name']} ({test_config['limit']:,} registros):")
        logger.info("-" * 60)
        
        test_results = [r for r in results if r['name'] == test_config['name']]
        
        for result in test_results:
            if result['success']:
                logger.info(
                    f"  {result['name']:15} | "
                    f"{result['duration']:8.2f}s | "
                    f"{result['records_per_second']:8.0f} reg/s"
                )
            else:
                logger.info(
                    f"  {result['name']:15} | "
                    f"FALHOU: {result.get('error', 'Erro desconhecido')}"
                )
    
    # Melhor performance por teste
    logger.info(f"\n🏆 MELHOR PERFORMANCE POR TESTE:")
    logger.info("-" * 40)
    
    for test_config in test_configs:
        test_results = [r for r in results if r['name'] == test_config['name'] and r['success']]
        if test_results:
            best = max(test_results, key=lambda x: x['records_per_second'])
            logger.info(
                f"  {test_config['name']:15} | "
                f"{best['name']:15} | "
                f"{best['records_per_second']:8.0f} reg/s"
            )
    
    # Performance relativa
    logger.info(f"\n📈 MELHORIA DE PERFORMANCE (vs Padrão):")
    logger.info("-" * 50)
    
    for test_config in test_configs:
        test_results = [r for r in results if r['name'] == test_config['name'] and r['success']]
        
        # Encontrar resultado do processador padrão
        standard_result = next((r for r in test_results if r['name'] == 'Padrão'), None)
        
        if standard_result:
            for result in test_results:
                if result['name'] != 'Padrão':
                    improvement = (result['records_per_second'] / standard_result['records_per_second']) * 100
                    logger.info(
                        f"  {test_config['name']:15} | "
                        f"{result['name']:15} | "
                        f"{improvement:6.1f}x mais rápido"
                    )
    
    logger.info("\n✅ Benchmark concluído!")
    logger.info("📁 Arquivos de saída salvos em: output/benchmark_*.csv")


if __name__ == "__main__":
    main()
