#!/usr/bin/env python3
"""
Script para carregar todos os dados CNPJ em sequência
Executa os 4 scripts de carga: empresas, estabelecimentos, sócios e simples
"""

import os
import sys
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('carregamento_dados.log')
    ]
)
logger = logging.getLogger(__name__)

def executar_script(script_path: str, nome_script: str) -> bool:
    """
    Executa um script de carregamento e retorna True se bem-sucedido
    
    Args:
        script_path: Caminho para o script
        nome_script: Nome do script para logs
        
    Returns:
        bool: True se executado com sucesso, False caso contrário
    """
    logger.info(f"🚀 Iniciando carregamento: {nome_script}")
    logger.info(f"📁 Script: {script_path}")
    
    inicio = time.time()
    
    try:
        # Executar script
        resultado = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=3600  # Timeout de 1 hora por script
        )
        
        tempo_decorrido = time.time() - inicio
        tempo_formatado = f"{tempo_decorrido//3600:.0f}h {(tempo_decorrido%3600)//60:.0f}m {tempo_decorrido%60:.0f}s"
        
        if resultado.returncode == 0:
            logger.info(f"✅ {nome_script} concluído com sucesso em {tempo_formatado}")
            
            # Log da saída padrão se houver
            if resultado.stdout:
                logger.info(f"📋 Saída de {nome_script}:")
                for linha in resultado.stdout.strip().split('\n'):
                    if linha.strip():
                        logger.info(f"   {linha}")
            
            return True
        else:
            logger.error(f"❌ {nome_script} falhou com código {resultado.returncode}")
            logger.error(f"📋 Erro de {nome_script}:")
            if resultado.stderr:
                for linha in resultado.stderr.strip().split('\n'):
                    if linha.strip():
                        logger.error(f"   {linha}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"⏰ {nome_script} excedeu o tempo limite de 1 hora")
        return False
    except Exception as e:
        logger.error(f"💥 Erro inesperado ao executar {nome_script}: {e}")
        return False

def verificar_script_existe(script_path: str) -> bool:
    """Verifica se o script existe"""
    if not os.path.exists(script_path):
        logger.error(f"❌ Script não encontrado: {script_path}")
        return False
    return True

def verificar_processo_rodando(script_name: str) -> bool:
    """
    Verifica se algum processo do script está rodando
    
    Args:
        script_name: Nome do script para verificar
        
    Returns:
        bool: True se está rodando, False caso contrário
    """
    try:
        resultado = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )
        
        if script_name in resultado.stdout:
            logger.warning(f"⚠️  Processo {script_name} já está em execução!")
            logger.info("💡 Aguarde o processo atual terminar antes de executar este script")
            return True
        return False
    except Exception:
        return False

def main():
    """Função principal"""
    logger.info("="*80)
    logger.info("🚀 INICIANDO CARREGAMENTO COMPLETO DOS DADOS CNPJ")
    logger.info("="*80)
    logger.info(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Obter diretório do script atual
    script_dir = Path(__file__).parent
    
    # Lista dos scripts a serem executados
    scripts = [
        {
            'nome': 'CNPJ Empresas',
            'arquivo': 'cnpj_empresas.py',
            'descricao': 'Carregamento de dados das empresas'
        },
        {
            'nome': 'CNPJ Estabelecimentos', 
            'arquivo': 'cnpj_estabelecimentos.py',
            'descricao': 'Carregamento de dados dos estabelecimentos'
        },
        {
            'nome': 'CNPJ Sócios',
            'arquivo': 'cnpj_socios.py', 
            'descricao': 'Carregamento de dados dos sócios'
        },
        {
            'nome': 'CNPJ Simples',
            'arquivo': 'cnpj_simples.py',
            'descricao': 'Carregamento de dados do Simples Nacional'
        }
    ]
    
    # Verificar se todos os scripts existem
    logger.info("🔍 Verificando scripts...")
    for script in scripts:
        script_path = script_dir / script['arquivo']
        if not verificar_script_existe(script_path):
            logger.error(f"❌ Script obrigatório não encontrado: {script_path}")
            logger.error("💡 Certifique-se de que todos os scripts estão na pasta scripts/")
            return 1
    
    # Verificar se algum processo está rodando
    logger.info("🔍 Verificando processos em execução...")
    for script in scripts:
        if verificar_processo_rodando(script['arquivo']):
            return 1
    
    logger.info("✅ Todos os scripts encontrados e nenhum processo em execução")
    logger.info("")
    
    # Executar scripts em sequência
    sucessos = 0
    falhas = 0
    inicio_total = time.time()
    
    for i, script in enumerate(scripts, 1):
        logger.info(f"📋 ETAPA {i}/4: {script['nome']}")
        logger.info(f"📝 {script['descricao']}")
        logger.info("-" * 60)
        
        script_path = script_dir / script['arquivo']
        
        if executar_script(str(script_path), script['nome']):
            sucessos += 1
        else:
            falhas += 1
            logger.error(f"💥 Falha em {script['nome']}. Interrompendo sequência.")
            break
        
        logger.info("")
    
    # Resumo final
    tempo_total = time.time() - inicio_total
    tempo_total_formatado = f"{tempo_total//3600:.0f}h {(tempo_total%3600)//60:.0f}m {tempo_total%60:.0f}s"
    
    logger.info("="*80)
    logger.info("📊 RESUMO DO CARREGAMENTO")
    logger.info("="*80)
    logger.info(f"✅ Scripts executados com sucesso: {sucessos}")
    logger.info(f"❌ Scripts com falha: {falhas}")
    logger.info(f"⏱️  Tempo total: {tempo_total_formatado}")
    logger.info(f"📅 Concluído em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    if falhas == 0:
        logger.info("🎉 CARREGAMENTO COMPLETO FINALIZADO COM SUCESSO!")
        logger.info("💡 Todos os dados CNPJ foram carregados no banco de dados")
        return 0
    else:
        logger.error("💥 CARREGAMENTO FINALIZADO COM FALHAS")
        logger.error("💡 Verifique os logs acima para identificar os problemas")
        return 1

def mostrar_ajuda():
    """Mostra informações de uso do script"""
    print("""
🚀 Script de Carregamento Completo dos Dados CNPJ
================================================

Este script executa em sequência os 4 scripts de carregamento:

1. cnpj_empresas.py      - Dados das empresas
2. cnpj_estabelecimentos.py - Dados dos estabelecimentos  
3. cnpj_socios.py        - Dados dos sócios
4. cnpj_simples.py       - Dados do Simples Nacional

📋 Funcionalidades:
- Execução sequencial (um por vez)
- Logs detalhados em arquivo e console
- Verificação de scripts existentes
- Detecção de processos em execução
- Resumo final com estatísticas

🔧 Uso:
    python scripts/carregar_dados_completo.py

⚠️  Pré-requisitos:
- Todos os 4 scripts devem estar na pasta scripts/
- Banco de dados configurado e acessível
- Arquivos CSV originais na pasta data/csv_source/
- Nenhum script de carregamento em execução

📊 Logs:
- Console: Saída em tempo real
- Arquivo: carregamento_dados.log (na raiz do projeto)

⏱️  Tempo estimado:
- Empresas: ~2-4 horas
- Estabelecimentos: ~4-8 horas  
- Sócios: ~3-6 horas
- Simples: ~1-2 horas
- Total: ~10-20 horas (dependendo do hardware)
""")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        mostrar_ajuda()
    else:
        try:
            resultado = main()
            sys.exit(resultado)
        except KeyboardInterrupt:
            logger.info("")
            logger.info("⚠️  Execução interrompida pelo usuário (Ctrl+C)")
            logger.info("💡 Para retomar, execute o script novamente")
            sys.exit(1)
        except Exception as e:
            logger.error(f"💥 Erro inesperado: {e}")
            sys.exit(1)
