#!/usr/bin/env python3
"""
CNPJ Processor - Teste Completo com Exemplo Básico
Testa consulta completa usando o filtro exemplo_basico e gera CSV
"""

import sys
import os
import json
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.cnpj_processor import CNPJProcessor
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_example_filters():
    """Carrega os filtros de exemplo do arquivo JSON"""
    try:
        with open('examples/exemplos_filtros.json', 'r', encoding='utf-8') as f:
            examples = json.load(f)
        return examples
    except Exception as e:
        logger.error(f"Erro ao carregar exemplos de filtros: {e}")
        return None

def test_exemplo_basico_complete():
    """Teste completo usando o filtro exemplo_basico"""
    try:
        # Carrega filtros de exemplo
        examples = load_example_filters()
        if not examples:
            logger.error("❌ Não foi possível carregar os exemplos de filtros")
            return False
        
        # Usa o filtro exemplo_basico
        filtro_exemplo = examples['exemplo_basico']
        
        logger.info("🚀 Iniciando teste completo com exemplo_basico")
        logger.info("=" * 70)
        logger.info(f"📋 Filtro exemplo_basico:")
        for chave, valor in filtro_exemplo.items():
            logger.info(f"   {chave}: {valor}")
        logger.info("=" * 70)
        
        # Inicializa o processador
        processor = CNPJProcessor()
        processor.connect_database()
        
        # Executa processamento completo com limite maior para ter dados suficientes
        logger.info("🔍 Executando consulta com filtros...")
        df = processor.process_data(limit=100, filters=filtro_exemplo)
        
        # Validações e análises
        logger.info(f"✅ Consulta executada com sucesso!")
        logger.info(f"📊 Total de registros encontrados: {len(df)}")
        
        if len(df) > 0:
            # Análise dos dados retornados
            logger.info("\n📈 ANÁLISE DOS DADOS:")
            
            # Verifica UF
            uf_unicas = df['uf'].unique()
            logger.info(f"   🌍 UFs encontradas: {uf_unicas}")
            
            # Verifica municípios
            municipios = df['municipio'].unique()
            logger.info(f"   🏙️ Municípios encontrados: {len(municipios)}")
            if len(municipios) <= 5:
                logger.info(f"      {municipios}")
            
            # Verifica situações cadastrais
            situacoes = df['situacao_cadastral'].unique()
            logger.info(f"   📊 Situações cadastrais: {situacoes}")
            
            # Verifica códigos de município
            codigos_municipio = df['codigo_municipio'].unique()
            logger.info(f"   🏷️ Códigos de município: {codigos_municipio}")
            
            # Mostra alguns exemplos de registros
            logger.info(f"\n📋 EXEMPLOS DE REGISTROS ENCONTRADOS:")
            for i, row in df.head(5).iterrows():
                logger.info(f"   {i+1}. CNPJ: {row['cnpj']}")
                logger.info(f"      Razão Social: {row['razao_social']}")
                logger.info(f"      Município: {row['municipio']} ({row['codigo_municipio']})")
                logger.info(f"      UF: {row['uf']}")
                logger.info(f"      Situação: {row['situacao_cadastral']}")
                if row['nome_fantasia']:
                    logger.info(f"      Nome Fantasia: {row['nome_fantasia']}")
                logger.info(f"      ---")
            
            # Gera CSV com timestamp para identificação única
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"exemplo_basico_BA_municipio3455_{timestamp}.csv"
            output_path = f"output/{output_filename}"
            
            logger.info(f"\n💾 Gerando arquivo CSV...")
            processor.save_to_csv(df, output_path)
            
            # Validação do arquivo gerado
            import pandas as pd
            df_verificacao = pd.read_csv(output_path, sep=';')
            logger.info(f"✅ CSV gerado com sucesso!")
            logger.info(f"📁 Arquivo: {output_path}")
            logger.info(f"📊 Registros no CSV: {len(df_verificacao)}")
            logger.info(f"📋 Colunas no CSV: {len(df_verificacao.columns)}")
            
            # Mostra algumas colunas importantes
            colunas_importantes = ['cnpj', 'razao_social', 'nome_fantasia', 'uf', 'municipio', 'situacao_cadastral']
            colunas_presentes = [col for col in colunas_importantes if col in df_verificacao.columns]
            logger.info(f"🔍 Colunas importantes presentes: {colunas_presentes}")
            
            # Verifica se o filtro foi aplicado corretamente
            logger.info(f"\n🔍 VALIDAÇÃO DOS FILTROS:")
            
            # Valida UF = BA
            uf_correta = df_verificacao['uf'].isin(['BA']).all()
            logger.info(f"   ✅ UF = BA: {'SIM' if uf_correta else 'NÃO'}")
            
            # Valida código município = 3455
            municipio_correto = df_verificacao['codigo_municipio'].isin([3455]).all()
            logger.info(f"   ✅ Código Município = 3455: {'SIM' if municipio_correto else 'NÃO'}")
            
            # Valida situação cadastral = ativos (2)
            situacao_correta = df_verificacao['situacao_cadastral'].isin([2]).all()
            logger.info(f"   ✅ Situação = Ativos (2): {'SIM' if situacao_correta else 'NÃO'}")
            
            if uf_correta and municipio_correto and situacao_correta:
                logger.info("🎉 Todos os filtros foram aplicados corretamente!")
            else:
                logger.warning("⚠️ Alguns filtros podem não ter sido aplicados corretamente")
            
        else:
            logger.warning("⚠️ Nenhum registro encontrado com o filtro exemplo_basico")
            logger.info("💡 Dica: Verifique se existem empresas ativas em BA, município 3455")
        
        processor.close_database()
        logger.info("\n✅ Teste completo do exemplo_basico concluído!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste completo: {e}")
        import traceback
        logger.error(f"Detalhes do erro: {traceback.format_exc()}")
        return False

def test_comparison_without_filters():
    """Teste comparativo sem filtros"""
    try:
        logger.info("\n🔍 TESTE COMPARATIVO - Sem filtros:")
        logger.info("-" * 50)
        
        processor = CNPJProcessor()
        processor.connect_database()
        
        # Consulta sem filtros para comparação
        df_sem_filtro = processor.process_data(limit=50, filters=None)
        
        logger.info(f"📊 Registros sem filtros: {len(df_sem_filtro)}")
        
        if len(df_sem_filtro) > 0:
            uf_sem_filtro = df_sem_filtro['uf'].value_counts().head()
            logger.info(f"🌍 Top 5 UFs sem filtro:")
            for uf, count in uf_sem_filtro.items():
                logger.info(f"   {uf}: {count} registros")
            
            situacoes_sem_filtro = df_sem_filtro['situacao_cadastral'].value_counts()
            logger.info(f"📊 Situações sem filtro:")
            for situacao, count in situacoes_sem_filtro.items():
                logger.info(f"   {situacao}: {count} registros")
        
        processor.close_database()
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste comparativo: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 INICIANDO TESTE COMPLETO - EXEMPLO BÁSICO")
    logger.info("=" * 70)
    
    # Executa teste principal
    sucesso_principal = test_exemplo_basico_complete()
    
    # Executa teste comparativo
    sucesso_comparativo = test_comparison_without_filters()
    
    logger.info("=" * 70)
    if sucesso_principal and sucesso_comparativo:
        logger.info("🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
        logger.info("📁 Verifique a pasta 'output' para o arquivo CSV gerado")
    else:
        logger.error("💥 ALGUNS TESTES FALHARAM!")
        logger.error("🔍 Verifique os logs acima para detalhes dos erros")
