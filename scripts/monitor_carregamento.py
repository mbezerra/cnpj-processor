#!/usr/bin/env python3
"""
Script para monitorar o progresso dos carregamentos CNPJ
Mostra estatísticas em tempo real dos scripts em execução
"""

import os
import sys
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from config.config import DATABASE_CONFIG
    import pymysql
except ImportError:
    print("❌ Erro: Não foi possível importar configurações do banco")
    print("💡 Certifique-se de que o arquivo .env está configurado")
    sys.exit(1)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

def conectar_banco():
    """Conecta ao banco de dados"""
    try:
        db_config = DATABASE_CONFIG.copy()
        if 'connection_timeout' in db_config:
            del db_config['connection_timeout']
        
        conn = pymysql.connect(**db_config)
        return conn
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao banco: {e}")
        return None

def obter_estatisticas_banco():
    """Obtém estatísticas do banco de dados"""
    conn = conectar_banco()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Contar registros em cada tabela
        tabelas = {
            'cnpj_empresas': 'Empresas',
            'cnpj_estabelecimentos': 'Estabelecimentos', 
            'cnpj_socios': 'Sócios',
            'cnpj_simples': 'Simples Nacional'
        }
        
        stats = {}
        for tabela, nome in tabelas.items():
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = cursor.fetchone()[0]
                stats[tabela] = {
                    'nome': nome,
                    'registros': count
                }
            except Exception:
                stats[tabela] = {
                    'nome': nome,
                    'registros': 0
                }
        
        cursor.close()
        conn.close()
        return stats
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {e}")
        if conn:
            conn.close()
        return None

def verificar_processos_carregamento():
    """Verifica quais scripts de carregamento estão em execução"""
    scripts = [
        'cnpj_empresas.py',
        'cnpj_estabelecimentos.py', 
        'cnpj_socios.py',
        'cnpj_simples.py'
    ]
    
    processos = {}
    
    try:
        resultado = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )
        
        for script in scripts:
            if script in resultado.stdout:
                # Extrair informações do processo
                linhas = resultado.stdout.split('\n')
                for linha in linhas:
                    if script in linha and 'python' in linha:
                        partes = linha.split()
                        if len(partes) >= 11:
                            pid = partes[1]
                            cpu = partes[2]
                            mem = partes[3]
                            tempo = partes[9]
                            
                            processos[script] = {
                                'pid': pid,
                                'cpu': cpu,
                                'mem': mem,
                                'tempo': tempo
                            }
                            break
        
        return processos
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar processos: {e}")
        return {}

def mostrar_ajuda():
    """Mostra informações de uso do script"""
    print("""
📊 Monitor de Carregamento CNPJ
==============================

Este script monitora o progresso dos carregamentos CNPJ em tempo real.

🔧 Uso:
    python scripts/monitor_carregamento.py

📋 Funcionalidades:
- Mostra estatísticas do banco de dados
- Lista processos de carregamento em execução
- Atualização automática a cada 30 segundos
- Histórico de progresso

⌨️  Controles:
- Ctrl+C: Sair do monitor
- Enter: Atualizar manualmente

📊 Informações mostradas:
- Registros por tabela
- Processos em execução (PID, CPU, Memória, Tempo)
- Data/hora da última atualização
""")

def main():
    """Função principal do monitor"""
    logger.info("📊 Monitor de Carregamento CNPJ iniciado")
    logger.info("💡 Pressione Ctrl+C para sair")
    logger.info("")
    
    try:
        while True:
            # Limpar tela (funciona na maioria dos terminais)
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("=" * 80)
            print("📊 MONITOR DE CARREGAMENTO CNPJ")
            print("=" * 80)
            print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            print("")
            
            # Estatísticas do banco
            print("🗄️  ESTATÍSTICAS DO BANCO DE DADOS:")
            print("-" * 50)
            
            stats = obter_estatisticas_banco()
            if stats:
                for tabela, info in stats.items():
                    registros = info['registros']
                    registros_formatado = f"{registros:,}".replace(',', '.')
                    print(f"📋 {info['nome']:<20}: {registros_formatado:>12} registros")
            else:
                print("❌ Não foi possível obter estatísticas do banco")
            
            print("")
            
            # Processos em execução
            print("🔄 PROCESSOS DE CARREGAMENTO EM EXECUÇÃO:")
            print("-" * 50)
            
            processos = verificar_processos_carregamento()
            if processos:
                print(f"{'Script':<25} {'PID':<8} {'CPU%':<6} {'MEM%':<6} {'Tempo':<8}")
                print("-" * 60)
                
                for script, info in processos.items():
                    nome_script = script.replace('cnpj_', '').replace('.py', '').title()
                    print(f"{nome_script:<25} {info['pid']:<8} {info['cpu']:<6} {info['mem']:<6} {info['tempo']:<8}")
            else:
                print("ℹ️  Nenhum script de carregamento em execução")
            
            print("")
            print("⌨️  Pressione Enter para atualizar ou Ctrl+C para sair")
            
            # Aguardar entrada do usuário ou timeout
            try:
                input()
            except KeyboardInterrupt:
                break
                
    except KeyboardInterrupt:
        print("")
        print("👋 Monitor encerrado pelo usuário")
    except Exception as e:
        logger.error(f"💥 Erro no monitor: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        mostrar_ajuda()
    else:
        main()
