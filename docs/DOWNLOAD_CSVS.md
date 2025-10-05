# Download Automático de CSVs da RFB

Este documento explica como usar os scripts para baixar automaticamente os CSVs da Receita Federal do Brasil (RFB).

## Scripts Disponíveis

### 1. `download_rfb_csvs.py`
Script principal que baixa os CSVs da RFB. Este script:
- Detecta automaticamente a pasta com a data mais recente
- Baixa apenas os arquivos necessários (empresas, estabelecimentos, sócios e simples)
- Descompacta automaticamente todos os arquivos zip baixados
- Remove os arquivos zip após a descompactação
- Remove arquivos antigos que não correspondem aos padrões atuais

### 2. `update_csvs.py`
Script simplificado que é um wrapper do script principal, com interface mais amigável.

## Como Usar

### Opção 1: Usando o Makefile (Recomendado)

```bash
# Baixar CSVs usando o script completo
make download-csvs

# Ou usar a versão simplificada
make update-csvs
```

### Opção 2: Executando diretamente

```bash
# Script completo
python scripts/download_rfb_csvs.py

# Script simplificado
python scripts/update_csvs.py
```

## Arquivos Baixados

O script baixa automaticamente apenas os arquivos necessários:

- **Empresas**: Arquivos com padrão `*EMPRECSV*.zip`
- **Estabelecimentos**: Arquivos com padrão `*ESTABELE*.zip`
- **Sócios**: Arquivos com padrão `*SOCIOCSV*.zip`
- **Simples**: Arquivos com padrão `*SIMPLES*.zip`

## Localização dos Arquivos

Todos os arquivos são baixados como zip na pasta `data/csv_source/`, descompactados automaticamente na mesma pasta, e os arquivos zip são removidos após a extração. Os arquivos CSV ficam disponíveis diretamente na pasta `data/csv_source/`.

## Funcionalidades

### Detecção Automática da Pasta Mais Recente
O script acessa o repositório da RFB e identifica automaticamente a pasta com a data mais recente (formato YYYY-MM).

### Download Inteligente
- Verifica se o arquivo já existe antes de baixar
- Mostra progresso durante o download
- Remove arquivos parciais em caso de erro

### Descompactação Automática
- Descompacta todos os arquivos zip baixados na mesma pasta
- Remove os arquivos zip após a extração bem-sucedida
- Mantém apenas os arquivos CSV descompactados

### Limpeza Automática
Remove automaticamente arquivos antigos que não correspondem aos padrões atuais dos arquivos necessários.

## Dependências

Certifique-se de que as seguintes dependências estão instaladas:

```bash
pip install -r requirements.txt
```

As dependências necessárias são:
- `requests>=2.28.0`
- `beautifulsoup4>=4.11.0`

## Logs

O script gera logs detalhados mostrando:
- Pasta mais recente encontrada
- Arquivos necessários identificados
- Progresso dos downloads
- Erros encontrados

## Exemplo de Uso

```bash
$ make update-csvs
🔄 Atualizando CSVs da RFB...

🧹 Limpando arquivos antigos...
2024-01-15 10:30:00 - INFO - Removidos 0 arquivos antigos

⬇️  Baixando arquivos mais recentes...
2024-01-15 10:30:01 - INFO - Pasta mais recente encontrada: 2025-01
2024-01-15 10:30:02 - INFO - Encontrados 31 arquivos .zip na pasta 2025-01
2024-01-15 10:30:02 - INFO - Arquivos necessários encontrados: 31
2024-01-15 10:30:02 - INFO -   - F.K03200$W.SIMPLES.CSV.D50913.zip
2024-01-15 10:30:02 - INFO -   - K3241.K03200Y0.D50913.EMPRECSV.zip
...

✅ Download concluído com sucesso!
📦 Descompactando arquivos...
2024-01-15 10:35:00 - INFO - Descompactando F.K03200$W.SIMPLES.CSV.D50913.zip...
2024-01-15 10:35:01 - INFO - Arquivo F.K03200$W.SIMPLES.CSV.D50913.zip descompactado com sucesso
...
✅ Descompactação concluída!
🗑️  Removendo arquivos zip...
2024-01-15 10:35:30 - INFO - Removendo arquivo zip: F.K03200$W.SIMPLES.CSV.D50913.zip
...
✅ Atualização concluída com sucesso!
📁 Arquivos CSV disponíveis em: /home/user/cnpj-processor/data/csv_source
```

## Troubleshooting

### Erro de Conexão
Se houver problemas de conexão, verifique:
- Conexão com a internet
- Acessibilidade do site da RFB
- Configurações de proxy (se aplicável)

### Erro de Permissão
Certifique-se de que o usuário tem permissão para:
- Criar a pasta `data/csv_source`
- Escrever arquivos nesta pasta

### Arquivos Corrompidos
Se um arquivo for baixado corrompido, o script irá:
- Remover o arquivo parcial
- Tentar baixar novamente na próxima execução
