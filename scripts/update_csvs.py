#!/usr/bin/env python3
"""
Script simplificado para atualizar os CSVs da RFB.
Este é um wrapper do download_rfb_csvs.py para facilitar o uso.
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.download_rfb_csvs import RFBCSVDownloader


def main():
    """
    Função principal simplificada.
    """
    print("🔄 Atualizando CSVs da RFB...")
    print()

    downloader = RFBCSVDownloader()

    # Limpa arquivos antigos
    print("🧹 Limpando arquivos antigos...")
    downloader.cleanup_old_files()

    # Baixa arquivos necessários
    print("⬇️  Baixando arquivos mais recentes...")
    success = downloader.download_all_required_files()

    if success:
        print("\n✅ Download concluído com sucesso!")
        
        # Descompacta os arquivos zip
        print("📦 Descompactando arquivos...")
        extract_success = downloader.extract_zip_files()
        
        if extract_success:
            print("✅ Descompactação concluída!")
            
            # Remove os arquivos zip
            print("🗑️  Removendo arquivos zip...")
            cleanup_success = downloader.remove_zip_files()
            
            if cleanup_success:
                print("✅ Atualização concluída com sucesso!")
                dest_path = downloader.download_dir.absolute()
                print(f"📁 Arquivos CSV disponíveis em: {dest_path}")
            else:
                print("⚠️  Aviso: Alguns arquivos zip não foram removidos.")
        else:
            print("❌ Erro durante a descompactação.")
            return 1
    else:
        print("\n❌ Erro durante a atualização.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
