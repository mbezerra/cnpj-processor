# CNPJ Processor

Sistema Python para leitura e processamento de dados das tabelas CNPJ, gerando arquivos CSV no formato especificado com detecção inteligente de celulares e processamento otimizado.

## Estrutura do Projeto

```
cnpj-processor/
├── src/                          # Código fonte principal
│   ├── cnpj_processor/          # Módulo de processamento
│   ├── filters/                 # Módulo de filtros
│   └── config/                  # Módulo de configuração
├── scripts/                     # Scripts executáveis
│   ├── main.py                 # Script principal
│   └── test_connection.py      # Teste de conexão
├── docs/                       # Documentação
├── examples/                   # Exemplos e templates
├── .vscode/                    # Configurações do VS Code
├── data/                       # Dados de entrada
├── output/                     # Dados de saída (gerado automaticamente)
├── requirements.txt           # Dependências Python
├── pyproject.toml            # Configuração do projeto
├── Makefile                  # Comandos de desenvolvimento
├── CHANGELOG.md             # Histórico de mudanças
├── cnpj-processor.code-workspace  # Workspace do VS Code
└── README.md                # Este arquivo
```

> 📋 **Nova Estrutura Moderna**: O projeto foi reorganizado seguindo as melhores práticas de desenvolvimento Python. Veja [docs/ESTRUTURA.md](docs/ESTRUTURA.md) para detalhes completos.

## 🚀 CNPJ Processor

**Sistema profissional de processamento de dados CNPJ** com detecção inteligente de celulares, validação de emails e filtros avançados.

## Instalação

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

2. **Testar conexão:**
```bash
python scripts/test_connection.py
```

3. **Usar comandos Make (recomendado):**
```bash
make help              # Mostra todos os comandos
make setup             # Configura o ambiente
make test-connection    # Testa a conexão
make run-dev           # Executa em desenvolvimento
```

4. **Configurar banco de dados:**
   - As tabelas já existem no MySQL
   - Configurações de conexão em `src/config/config.py`

5. **Abrir no VS Code:**
   ```bash
   # Opção 1: Abrir pasta diretamente
   code .
   
   # Opção 2: Abrir workspace
   code cnpj-processor.code-workspace
   ```

## Uso

### Uso Básico (Recomendado)
```bash
# Processamento com limite padrão (50 registros)
python scripts/main.py

# Processamento com limite específico
python scripts/main.py --limit 100 --output output/meu_arquivo.csv

# Processamento sem limite (TODOS os registros)
python scripts/main.py --no-limit --output output/cnpj_completo.csv

# Testar conexão
python scripts/main.py --test-connection
```

### Opções de Linha de Comando
```bash
# Ajuda
python scripts/main.py --help

# Limite específico
python scripts/main.py --limit 1000

# Sem limite (equivale a --limit 0)
python scripts/main.py --no-limit

# Arquivo de saída personalizado
python scripts/main.py --output output/meu_resultado.csv

# Teste de conectividade
python scripts/main.py --test-connection

# Filtros interativos
python scripts/main.py --filters

# Filtros via JSON
python scripts/main.py --json
```

### Uso Programático
```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.cnpj_processor import CNPJProcessor

# Criar processador
processor = CNPJProcessor()

# Processar dados (limite de 50 registros para desenvolvimento)
processor.run(limit=50, output_path="output/cnpj_data.csv")

# Processamento sem limite
processor.run(limit=0, output_path="output/cnpj_completo.csv")
```

## Funcionalidades

### 🔄 Processamento de Dados
- **Leitura de múltiplas tabelas**: Une dados de empresas, estabelecimentos, sócios, etc.
- **Consulta otimizada**: JOINs eficientes entre todas as tabelas relacionadas
- **Processamento de sócios**: Agrega dados dos sócios por empresa
- **Saída formatada**: Gera CSV com separador ';' conforme especificação

### 📱 Detecção Inteligente de Celulares
- **Algoritmo avançado**: Baseado no terceiro dígito do telefone
- **Suporte a 10 e 11 dígitos**: Compatível com diferentes formatos
- **Colunas específicas**: `telefone1_celular` e `telefone2_celular` (0 ou 1)
- **Concatenação automática**: DDD + telefone em campos únicos
- **Fax incluído**: DDD + fax concatenados na coluna `ddd_fax`

### 📧 Validação de Email
- **Regex robusta**: Validação completa de formato de email
- **Coluna booleana**: `email` com valor 0 (inválido) ou 1 (válido)
- **Tratamento de erros**: Suporte a diferentes tipos de dados
- **Padrão internacional**: Suporte a emails com subdomínios e caracteres especiais

### ⚙️ Controle de Processamento
- **Limitação flexível**: Controle de registros processados
- **Processamento sem limite**: Opção para processar todos os registros
- **Logging completo**: Acompanhamento detalhado do processamento
- **Tratamento de erros**: Recuperação automática de falhas

### 🔧 Correções de Dados
- **Código do país**: Substitui 0 por 105 (Brasil) automaticamente
- **Concatenação de contatos**: DDD + telefone/fax em campos únicos
- **Validação de email**: Detecção automática de emails válidos
- **Detecção de celular**: Algoritmo baseado no terceiro dígito

## Configurações

O arquivo `config.py` contém todas as configurações do sistema:

- **DATABASE_CONFIG**: Configurações do banco de dados
- **OUTPUT_CONFIG**: Configurações de saída
- **DEV_CONFIG**: Configurações de desenvolvimento
- **CSV_COLUMNS**: Mapeamento das colunas de saída

## Estrutura de Saída

O CSV gerado contém as seguintes colunas principais:

### 📊 Colunas Principais
- **ID**: Identificador único (inteiro)
- **CNPJ**: Número completo do CNPJ
- **Dados da Empresa**: Razão social, natureza jurídica, capital social
- **Dados do Estabelecimento**: Endereço, telefones, CNAE, situação cadastral
- **Dados dos Sócios**: Nome, qualificação, data de entrada (agregados)
- **Regime Tributário**: Simples Nacional, MEI, datas de opção/exclusão

### 📱 Colunas de Telefone
- **ddd_telefone_1**: DDD + telefone concatenados
- **telefone1_celular**: 1 se for celular, 0 se for fixo
- **ddd_telefone_2**: Segundo telefone (DDD + número)
- **telefone2_celular**: 1 se for celular, 0 se for fixo
- **ddd_fax**: DDD + fax concatenados

### 📧 Colunas de Email
- **correio_eletronico**: Email original (string)
- **email**: Validação booleana (0 = inválido, 1 = válido)

### 🌍 Dados Geográficos
- **Município, UF, País**: Localização completa
- **CEP, Endereço**: Dados de localização detalhados

## Configurações Avançadas

### 🔧 Configurações do Banco
```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'prospectar',
    'password': 'Mova1520#',
    'database': 'cnpj',
    'charset': 'utf8mb4'
}
```

### 📈 Controle de Performance
- **Desenvolvimento**: Limite padrão de 50 registros
- **Produção**: Use `--no-limit` para processar todos os dados
- **Monitoramento**: Logs detalhados no console
- **Filtros**: Reduzem significativamente o volume de dados processados
- **Otimização**: Consultas SQL otimizadas com índices apropriados

## Validações Implementadas

### 📱 Detecção de Celular
```python
# Lógica: Terceiro dígito determina se é celular
# Dígitos 6, 7, 8, 9 = Celular (1)
# Outros dígitos = Fixo (0)
```

**Exemplos:**
- `11999887766` → Terceiro dígito: 9 → **Celular (1)**
- `1133334444` → Terceiro dígito: 3 → **Fixo (0)**

### 📧 Validação de Email
```python
# Regex: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
# Suporte a: subdomínios, caracteres especiais, extensões internacionais
```

**Exemplos:**
- `usuario@empresa.com.br` → **Válido (1)**
- `email_invalido` → **Inválido (0)**
- `user+tag@domain.org` → **Válido (1)**

### 📞 Concatenação de Contatos
```python
# DDD + Telefone/Fax concatenados automaticamente
# ddd_telefone_1: DDD + telefone1
# ddd_telefone_2: DDD + telefone2  
# ddd_fax: DDD + fax
```

**Exemplos:**
- DDD: 11, Telefone: 999887766 → **11999887766**
- DDD: 21, Fax: 33334444 → **2133334444**

### 📊 Situação Cadastral
```python
# Interpretação correta das situações:
# Ativos: situação = 2
# Inaptos: situação = 4  
# Inativos: situações = 1, 3, 8
```

**Opções de Filtro:**
- **1 - Ativos**: Apenas empresas ativas (situação = 2)
- **2 - Inaptos**: Apenas empresas inaptas (situação = 4)
- **3 - Inativos**: Apenas empresas inativas (situações = 1, 3, 8)

### 🌍 Correção de Dados
```python
# Código do país: substitui 0 por 105 (Brasil)
df['codigo_pais'] = df['codigo_pais'].replace(0, 105)
```

**Correção SQL Implementada:**
```sql
-- JOIN corrigido para países
LEFT JOIN cnpj_paises p ON (CASE WHEN est.codigo_pais = 0 THEN 105 ELSE est.codigo_pais END) = p.codigo
```

**Correções Automáticas:**
- **Código do País**: 0 → 105 (Brasil)
- **Nome do País**: "COLIS POSTAUX" → "BRASIL" (quando código era 0)
- **Dados consistentes**: Garante que todos os registros tenham país válido
- **JOIN otimizado**: Consulta SQL corrigida para fazer JOIN correto com países

## Filtros Disponíveis

### 🔍 Filtros Geográficos
- **UF**: Filtro por estado (sigla de 2 letras)
- **Código do Município**: Filtro específico por município (4 dígitos)
- **Código do País**: Filtro por país (padronizado para Brasil)

### 📊 Filtros de Atividade
- **CNAE Codes**: Múltiplos códigos de atividade econômica
- **Situação Cadastral**: Ativos, Inaptos, Inativos
- **Data de Início**: Intervalo de datas (formato YYYYMMDD)

### 📞 Filtros de Contato
- **Com Email**: S/N para registros com/sem email
- **Com Telefone**: S/N para registros com/sem telefone
- **Tipo de Telefone**: Fixo, Celular, Ambos

### 💰 Filtros Tributários
- **Opção Tributária**: Apenas MEI, Sem MEI, Todas
- **Capital Social**: Faixas (>10k, >50k, >100k, qualquer)

## Exemplos de Uso

### 🧪 Desenvolvimento e Testes
```bash
# Teste rápido (3 registros)
python scripts/main.py --limit 3

# Teste médio (100 registros)
python scripts/main.py --limit 100 --output output/teste.csv

# Teste com filtros interativos
python scripts/main.py --filters --limit 50 --output output/filtrado.csv

# Teste com filtros JSON
python scripts/main.py --json --limit 50 --output output/json_filtrado.csv
```

### 🚀 Produção
```bash
# Processamento completo
python scripts/main.py --no-limit --output output/cnpj_completo.csv

# Processamento com filtros interativos
python scripts/main.py --filters --no-limit --output output/cnpj_filtrado.csv

# Processamento com filtros JSON
python scripts/main.py --json --no-limit --output output/cnpj_json.csv

# Processamento por lotes
python scripts/main.py --limit 10000 --output output/lote_1.csv
```

### 🔍 Filtros Específicos
```bash
# Apenas empresas ativas em SP
python scripts/main.py --filters --limit 1000 --output output/ativas_sp.csv

# Empresas com email e telefone celular
python scripts/main.py --filters --limit 500 --output output/contatos_completos.csv

# MEI com capital > R$ 10.000
python scripts/main.py --filters --limit 200 --output output/mei_capital.csv
```

### 📄 Filtros JSON
```bash
# Exemplo: Empresas ativas na Bahia, município 3455
python scripts/main.py --json --limit 100 --output output/ba_cicero_dantas.csv

# Exemplo: Empresas com CNAE específico em SP
python scripts/main.py --json --limit 500 --output output/sp_cnae.csv
```

**Comportamento do Modo JSON:**
- ✅ **JSON válido**: Processa com filtros aplicados
- ❌ **JSON inválido**: Cancela operação com erro
- ❌ **Sem JSON**: Cancela operação (não processa sem filtros)

**Formato JSON de Exemplo:**
```json
{
  "uf": "BA",
  "codigo_municipio": 3455,
  "situacao_cadastral": "ativos",
  "cnae_codes": ["1234567", "7654321"],
  "data_inicio_atividade": {
    "inicio": "20200101",
    "fim": "20231231"
  },
  "com_email": true,
  "com_telefone": true,
  "tipo_telefone": "celular",
  "opcao_tributaria": "mei",
  "capital_social": "10k"
}
```

**Nota sobre Códigos de Município:**
- Os códigos seguem o padrão de **4 dígitos**
- Correspondem à coluna `codigo` da tabela `cnpj_municipios`
- Exemplos: 7107 (São Paulo), 3455 (Cicero Dantas), 6001 (Rio de Janeiro)

## Próximos Passos

- ✅ Sistema base implementado
- ✅ Detecção de celulares funcionando
- ✅ Validação de email implementada
- ✅ Concatenação de DDD + fax corrigida
- ✅ Sistema de filtros interativos implementado
- ✅ Correção da situação cadastral aplicada
- ✅ Correção do código do país implementada
- ✅ Processamento sem limite disponível
- ✅ Sistema de filtros JSON implementado
- 🔄 Adicionar colunas calculadas conforme especificações
- 🔄 Otimizar consultas para grandes volumes de dados
- 🔄 Implementar processamento em lotes
