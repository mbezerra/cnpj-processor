#!/usr/bin/env python3
"""
Script para baixar automaticamente os CSVs da RFB.

Este script:
1. Detecta a pasta com a data mais recente no repositório da RFB
2. Baixa apenas os arquivos necessários (empresas, estabelecimentos, sócios e
   simples)
3. Descompacta automaticamente todos os arquivos zip baixados
4. Remove os arquivos zip após a descompactação
5. Salva os arquivos CSV na pasta data/csv_source
"""

import logging
import os
import re
import zipfile
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Determina o diretório raiz do projeto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = Path(os.path.dirname(SCRIPT_DIR))


class RFBCSVDownloader:
    """
    Classe para baixar e processar CSVs da RFB automaticamente.

    Esta classe gerencia o download, descompactação e limpeza dos arquivos
    CSV da Receita Federal do Brasil.
    """

    def __init__(
        self,
        base_url="https://arquivos.receitafederal.gov.br/dados/cnpj/"
                 "dados_abertos_cnpj/"
    ):
        self.base_url = base_url
        self.download_dir = PROJECT_ROOT / "data" / "csv_source"
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # Padrões dos arquivos que queremos baixar
        self.required_patterns = [
            r'.*Empresas.*\.zip$',  # Empresas
            r'.*Estabelecimentos.*\.zip$',  # Estabelecimentos
            r'.*Socios.*\.zip$',  # Sócios
            r'.*Simples.*\.zip$'    # Simples
        ]

    def get_latest_folder(self):
        """
        Obtém a pasta com a data mais recente do repositório da RFB.
        """
        try:
            response = requests.get(self.base_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Encontra todos os links de pastas (formato YYYY-MM)
            folder_links = []
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and re.match(r'^\d{4}-\d{2}/$', href):
                    folder_links.append(href.rstrip('/'))

            if not folder_links:
                raise ValueError("Nenhuma pasta de dados encontrada")

            # Ordena as pastas por data (mais recente primeiro)
            folder_links.sort(reverse=True)
            latest_folder = folder_links[0]

            logger.info("Pasta mais recente encontrada: %s", latest_folder)
            return latest_folder

        except (requests.RequestException, ValueError) as e:
            logger.error("Erro ao obter pasta mais recente: %s", e)
            raise

    def get_files_in_folder(self, folder_name):
        """
        Obtém a lista de arquivos na pasta especificada.
        """
        folder_url = urljoin(self.base_url, f"{folder_name}/")

        try:
            response = requests.get(folder_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            files = []
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and href.endswith('.zip'):
                    files.append(href)

            logger.info("Encontrados %d arquivos .zip na pasta %s",
                        len(files), folder_name)
            return files

        except (requests.RequestException, ValueError) as e:
            logger.error("Erro ao obter arquivos da pasta %s: %s",
                         folder_name, e)
            raise

    def filter_required_files(self, files):
        """
        Filtra apenas os arquivos necessários baseado nos padrões definidos.
        """
        required_files = []

        for file in files:
            for pattern in self.required_patterns:
                if re.match(pattern, file, re.IGNORECASE):
                    required_files.append(file)
                    break

        logger.info("Arquivos necessários encontrados: %d",
                    len(required_files))
        for file in required_files:
            logger.info("  - %s", file)

        return required_files

    def download_file(self, folder_name, filename):
        """
        Baixa um arquivo específico da pasta.
        """
        file_url = urljoin(self.base_url, f"{folder_name}/{filename}")
        local_path = self.download_dir / filename

        # Verifica se o arquivo já existe
        if local_path.exists():
            logger.info("Arquivo %s já existe, pulando download", filename)
            return True

        try:
            logger.info("Baixando %s...", filename)
            response = requests.get(file_url, stream=True, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r{filename}: {progress:.1f}%",
                                  end='', flush=True)

            print()  # Nova linha após o progresso
            logger.info("Download concluído: %s", filename)
            return True

        except (requests.RequestException, IOError, OSError) as e:
            logger.error("Erro ao baixar %s: %s", filename, e)
            # Remove arquivo parcial se existir
            if local_path.exists():
                local_path.unlink()
            return False

    def download_all_required_files(self):
        """
        Baixa todos os arquivos necessários da pasta mais recente.
        """
        try:
            # Obtém a pasta mais recente
            latest_folder = self.get_latest_folder()

            # Obtém lista de arquivos na pasta
            all_files = self.get_files_in_folder(latest_folder)

            # Filtra apenas os arquivos necessários
            required_files = self.filter_required_files(all_files)

            if not required_files:
                logger.warning("Nenhum arquivo necessário encontrado")
                return False

            # Baixa cada arquivo
            success_count = 0
            for filename in required_files:
                if self.download_file(latest_folder, filename):
                    success_count += 1

            logger.info(
                "Download concluído: %d/%d arquivos baixados com sucesso",
                success_count, len(required_files)
            )
            return success_count == len(required_files)

        except (requests.RequestException, ValueError) as e:
            logger.error("Erro durante o download: %s", e)
            return False

    def cleanup_old_files(self):
        """
        Remove arquivos CSV antigos que não correspondem aos padrões atuais.
        """
        try:
            # Busca por arquivos CSV (não mais zip)
            current_files = list(self.download_dir.glob("*.CSV"))
            removed_count = 0

            for file_path in current_files:
                filename = file_path.name
                is_required = False

                # Adapta os padrões para arquivos CSV
                csv_patterns = [
                    r'.*EMPRECSV.*\.CSV$',  # Empresas
                    r'.*ESTABELE.*\.CSV$',  # Estabelecimentos
                    r'.*SOCIOCSV.*\.CSV$',  # Sócios
                    r'.*SIMPLES.*\.CSV$'    # Simples
                ]

                for pattern in csv_patterns:
                    if re.match(pattern, filename, re.IGNORECASE):
                        is_required = True
                        break

                if not is_required:
                    logger.info("Removendo arquivo CSV antigo: %s", filename)
                    file_path.unlink()
                    removed_count += 1

            if removed_count > 0:
                logger.info("Removidos %d arquivos CSV antigos", removed_count)

        except (OSError, IOError) as e:
            logger.error("Erro durante limpeza: %s", e)

    def extract_zip_files(self):
        """
        Descompacta todos os arquivos zip na pasta de download.
        """
        try:
            zip_files = list(self.download_dir.glob("*.zip"))
            extracted_count = 0

            for zip_path in zip_files:
                try:
                    logger.info("Descompactando %s...", zip_path.name)
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(self.download_dir)
                    extracted_count += 1
                    logger.info(
                        "Arquivo %s descompactado com sucesso", zip_path.name)
                except (zipfile.BadZipFile, OSError, IOError) as e:
                    logger.error("Erro ao descompactar %s: %s",
                                 zip_path.name, e)

            logger.info("Descompactação concluída: %d/%d arquivos processados",
                        extracted_count, len(zip_files))
            return extracted_count == len(zip_files)

        except (OSError, IOError) as e:
            logger.error("Erro durante descompactação: %s", e)
            return False

    def remove_zip_files(self):
        """
        Remove todos os arquivos zip após a descompactação.
        """
        try:
            zip_files = list(self.download_dir.glob("*.zip"))
            removed_count = 0

            for zip_path in zip_files:
                try:
                    logger.info("Removendo arquivo zip: %s", zip_path.name)
                    zip_path.unlink()
                    removed_count += 1
                except (OSError, IOError) as e:
                    logger.error("Erro ao remover %s: %s", zip_path.name, e)

            logger.info(
                "Remoção concluída: %d arquivos zip removidos", removed_count)
            return removed_count == len(zip_files)

        except (OSError, IOError) as e:
            logger.error("Erro durante remoção dos arquivos zip: %s", e)
            return False


def main():
    """
    Função principal do script.
    """
    print("=== Downloader de CSVs da RFB ===")
    dest_path = PROJECT_ROOT / "data" / "csv_source"
    print(f"Diretório de destino: {dest_path}")
    print()

    downloader = RFBCSVDownloader()

    # Limpa arquivos antigos
    downloader.cleanup_old_files()

    # Baixa arquivos necessários
    success = downloader.download_all_required_files()

    if success:
        print("\n✅ Download concluído com sucesso!")

        # Descompacta os arquivos zip
        print("\n📦 Descompactando arquivos...")
        extract_success = downloader.extract_zip_files()

        if extract_success:
            print("✅ Descompactação concluída com sucesso!")

            # Remove os arquivos zip
            print("\n🗑️  Removendo arquivos zip...")
            cleanup_success = downloader.remove_zip_files()

            if cleanup_success:
                print("✅ Limpeza concluída com sucesso!")
                dest_path = downloader.download_dir.absolute()
                print(f"\n📁 Arquivos CSV disponíveis em: {dest_path}")
            else:
                print("⚠️  Aviso: Alguns arquivos zip não foram removidos.")
        else:
            print("❌ Erro durante a descompactação.")
            return 1
    else:
        print("\n❌ Erro durante o download. "
              "Verifique os logs para mais detalhes.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
