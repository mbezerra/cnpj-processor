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
│   ├── main.py                 # Script principal de processamento
│   ├── main_optimized.py       # Script otimizado para grandes volumes
│   ├── cnpj_empresas.py       # Carregamento de dados das empresas
│   ├── cnpj_estabelecimentos.py # Carregamento de dados dos estabelecimentos
│   ├── cnpj_socios.py         # Carregamento de dados dos sócios
│   └── cnpj_simples.py        # Carregamento de dados do Simples Nacional
├── tests/                       # Testes automatizados
│   ├── test_connection.py      # Teste de conexão
│   └── test_exemplo_basico.py  # Teste com filtros
├── docs/                       # Documentação
│   ├── ESTRUTURA.md          # Estrutura do projeto
│   ├── INSTALACAO_BANCO.md   # Guia de instalação do banco
│   ├── TROUBLESHOOTING.md    # Solução de problemas
│   ├── OTIMIZACAO_PERFORMANCE.md # Guia de otimização para grandes volumes
│   └── relacionamentos_tabelas.md # Relacionamentos das tabelas
├── examples/                   # Exemplos e templates
├── data/                       # Dados e scripts de banco
│   ├── csv_source/           # Arquivos CSV originais da Receita Federal
│   │   └── K3241.K03200Y*.EMPRECSV # Arquivos grandes (gitignored)
│   └── sql/                  # Scripts de banco de dados
│       ├── ddls.sql          # Estrutura das tabelas (CREATE TABLE)
│       ├── insert-cnpj-cnaes.sql # Dados de CNAEs
│       ├── insert-cnpj-paises.sql # Dados de países
│       ├── insert-cnpj-municipios.sql # Dados de municípios
│       ├── insert-cnpj-naturezas-juridicas.sql # Naturezas jurídicas
│       ├── insert-cnpj-qualificacao-socios.sql # Qualificações de sócios
│       └── insert-cnpj-motivos.sql # Motivos de situação cadastral
├── output/                     # Dados de saída (gerado automaticamente)
├── requirements.txt           # Dependências Python
├── pyproject.toml            # Configuração do projeto
├── config.example.env        # Exemplo de configuração
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

2. **Configurar banco de dados:**
   
   📖 **Guia completo**: [docs/INSTALACAO_BANCO.md](docs/INSTALACAO_BANCO.md)
   
   ```bash
   # 1. Criar o banco de dados MySQL
   mysql -u root -p -e "CREATE DATABASE cnpj CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

   # 2. Criar a estrutura das tabelas
   mysql -u root -p cnpj < data/sql/ddls.sql

   # 3. Popular as tabelas de referência (obrigatório)
   mysql -u root -p cnpj < data/sql/insert-cnpj-cnaes.sql
   mysql -u root -p cnpj < data/sql/insert-cnpj-paises.sql
   mysql -u root -p cnpj < data/sql/insert-cnpj-municipios.sql
   mysql -u root -p cnpj < data/sql/insert-cnpj-naturezas-juridicas.sql
   mysql -u root -p cnpj < data/sql/insert-cnpj-qualificacao-socios.sql
   mysql -u root -p cnpj < data/sql/insert-cnpj-motivos.sql

   # 4. Carregar dados das empresas (opcional)
   Nota: Requer arquivos CSV originais da Receita Federal
   
   python scripts/cnpj_empresas.py      # Empresas
   python scripts/cnpj_estabelecimentos.py  # Estabelecimentos
   python scripts/cnpj_socios.py        # Sócios
   python scripts/cnpj_simples.py       # Simples Nacional
   ```

3. **Configurar variáveis de ambiente:**
```bash
# Copiar arquivo de exemplo
cp config.example.env .env

# Editar com suas configurações
nano .env
```

4. **Testar conexão:**
```bash
python tests/test_connection.py
```

5. **Usar comandos Make (recomendado):**
```bash
make help              # Mostra todos os comandos
make setup             # Configura o ambiente
make test-connection    # Testa a conexão
make run-dev           # Executa em desenvolvimento
```

6. **Abrir no VS Code:**
   ```bash
   # Opção 1: Abrir pasta diretamente
   code .
   
   # Opção 2: Abrir workspace
   code cnpj-processor.code-workspace
   ```

## Uso

### Uso Básico (Recomendado)
```bash
# Processamento com limite padrão (50 registros) - salva em output/cnpj_empresas.csv
python scripts/main.py

# Processamento com limite específico
python scripts/main.py --limit 100 --output output/meu_arquivo.csv

# Processamento sem limite (TODOS os registros)
python scripts/main.py --no-limit --output output/cnpj_completo.csv

# Testar conexão
python scripts/main.py --test-connection
```

> 📁 **Localização dos arquivos**: Os arquivos CSV são salvos automaticamente na pasta `output/` na raiz do projeto. O sistema detecta automaticamente o diretório correto, independentemente de onde o script for executado.

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

## 🗄️ Instalação do Banco de Dados

### **Estrutura do Banco**
O sistema utiliza um banco MySQL com as seguintes tabelas principais:

#### **Tabelas de Dados Principais:**
- `cnpj_empresas` - Dados das empresas (razão social, natureza jurídica, capital social)
- `cnpj_estabelecimentos` - Dados dos estabelecimentos (endereços, telefones, CNAEs)
- `cnpj_socios` - Dados dos sócios (nomes, qualificações, datas de entrada)

#### **Tabelas de Referência:**
- `cnpj_cnaes` - Códigos de atividade econômica (CNAE)
- `cnpj_municipios` - Códigos de municípios brasileiros
- `cnpj_paises` - Códigos de países
- `cnpj_naturezas_juridicas` - Naturezas jurídicas das empresas
- `cnpj_qualificacao_socios` - Qualificações dos sócios
- `cnpj_motivos` - Motivos de situação cadastral
- `cnpj_simples` - Dados do Simples Nacional e MEI

### **📊 Scripts de Instalação Disponíveis**

Na pasta `data/sql/` você encontrará os seguintes scripts SQL:

| 📁 Arquivo | 📝 Descrição | 📏 Tamanho | 📈 Registros |
|------------|--------------|------------|--------------|
| `ddls.sql` | Estrutura das tabelas (CREATE TABLE) | ~5KB | - |
| `insert-cnpj-cnaes.sql` | Códigos de atividade econômica (CNAE) | ~200KB | ~1.500 |
| `insert-cnpj-paises.sql` | Códigos de países | ~15KB | ~280 |
| `insert-cnpj-municipios.sql` | Códigos de municípios brasileiros | ~300KB | ~5.500 |
| `insert-cnpj-naturezas-juridicas.sql` | Naturezas jurídicas das empresas | ~10KB | ~100 |
| `insert-cnpj-qualificacao-socios.sql` | Qualificações dos sócios | ~5KB | ~50 |
| `insert-cnpj-motivos.sql` | Motivos de situação cadastral | ~5KB | ~20 |

### **Processo de Instalação Completo**

#### **1. Criar o Banco de Dados**
```bash
mysql -u root -p -e "CREATE DATABASE cnpj CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

#### **2. Criar a Estrutura das Tabelas**
```bash
mysql -u root -p cnpj < data/ddls.sql
```

#### **3. Popular Tabelas de Referência (Obrigatório)**
```bash
# Essas tabelas são essenciais para o funcionamento do sistema
mysql -u root -p cnpj < data/insert-cnpj-cnaes.sql
mysql -u root -p cnpj < data/insert-cnpj-paises.sql
mysql -u root -p cnpj < data/insert-cnpj-municipios.sql
mysql -u root -p cnpj < data/insert-cnpj-naturezas-juridicas.sql
mysql -u root -p cnpj < data/insert-cnpj-qualificacao-socios.sql
mysql -u root -p cnpj < data/insert-cnpj-motivos.sql
```

#### **4. Carregar Dados das Empresas (Opcional)**

⚠️ **Importante:** Este passo é opcional e requer os arquivos CSV originais da Receita Federal.

```bash
# Carregar dados das empresas
python scripts/cnpj_empresas.py

# Carregar dados dos estabelecimentos  
python scripts/cnpj_estabelecimentos.py

# Carregar dados dos sócios
python scripts/cnpj_socios.py

# Carregar dados do Simples Nacional
python scripts/cnpj_simples.py
```

> 📝 **Nota:** Os scripts esperam arquivos CSV no formato original da Receita Federal (ex: `K3241.K03200Y.D50913.EMPRECSV`) na pasta `data/csv_source/`. Estes arquivos grandes não estão incluídos no repositório (gitignored).

### **✅ Verificação da Instalação**

Após a instalação, você pode verificar se tudo está funcionando:

```bash
# 🔗 Testar conexão com o banco
python tests/test_connection.py

# 🧪 Executar teste completo com filtros
python tests/test_exemplo_basico.py
```

**Resultados esperados:**
- ✅ Conexão estabelecida com sucesso
- ✅ Testes executados sem erros
- ✅ Arquivo CSV gerado na pasta `output/`

### **📋 Notas Importantes**

| Aspecto | Descrição |
|---------|-----------|
| ⚠️ **Dados das empresas** | Arquivos CSV originais da Receita Federal não estão incluídos no repositório |
| ✅ **Tabelas de referência** | Todas as tabelas de referência estão incluídas e são essenciais |
| 🔧 **Scripts de carregamento** | Scripts em `scripts/` processam CSV originais e carregam no banco |
| 🔧 **Encoding** | Banco deve usar `utf8mb4` para suportar caracteres especiais |
| 📊 **Tamanho** | Tabelas de referência ocupam aproximadamente 600KB total |

## Configurações Avançadas

### 🔧 Configurações do Banco
As configurações do banco são carregadas via variáveis de ambiente do arquivo `.env`:

```python
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'cnpj'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4')
}
```

**Arquivo `.env` de exemplo:**
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=cnpj
DB_CHARSET=utf8mb4
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

> 📁 **Nota sobre localização**: Todos os arquivos CSV são salvos na pasta `output/` na raiz do projeto. O sistema detecta automaticamente o diretório correto.

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

### 🚀 Processamento Otimizado para Grandes Volumes

> ⚡ **Versão Otimizada**: Para volumes superiores a 100.000 registros, use `main_optimized.py`

```bash
# Processamento otimizado (100.000+ registros)
python scripts/main_optimized.py --limit 100000

# Processamento completo otimizado (milhões de registros)
python scripts/main_optimized.py --limit 0 --output output/cnpj_completo_otimizado.csv

# Apenas contar registros
python scripts/main_optimized.py --count-only --filters

# Configurar tamanho do lote
python scripts/main_optimized.py --batch-size 20000 --limit 500000
```

**Benefícios da versão otimizada:**
- ⚡ **75% mais rápido** que a versão padrão
- 💾 **70% menos memória** utilizada
- 🔄 **Processamento em lotes** sem travamentos
- 📊 **Cache inteligente** para consultas frequentes
- 🎯 **Índices otimizados** para filtros comuns

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

## 🆘 Suporte e Troubleshooting

### 📚 Documentação Disponível
- **[docs/ESTRUTURA.md](docs/ESTRUTURA.md)**: Estrutura detalhada do projeto
- **[docs/INSTALACAO_BANCO.md](docs/INSTALACAO_BANCO.md)**: Guia completo de instalação
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**: Solução de problemas comuns
- **[docs/OTIMIZACAO_PERFORMANCE.md](docs/OTIMIZACAO_PERFORMANCE.md)**: Otimização para grandes volumes

### 🔧 Problemas Comuns
- **Arquivos CSV no local errado**: Veja [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md#-arquivos-csv-salvos-no-local-errado)
- **Erro de conexão com banco**: Veja [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md#-erro-de-conexão-com-mysql)
- **Dependências não instaladas**: Veja [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md#-dependências-não-instaladas)
- **Performance lenta com grandes volumes**: Veja [OTIMIZACAO_PERFORMANCE.md](docs/OTIMIZACAO_PERFORMANCE.md)

### 🧪 Testes e Verificação
```bash
# Testar conexão com banco
python scripts/main.py --test-connection

# Teste rápido com 5 registros
python scripts/main.py --limit 5
```

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
- ✅ Estrutura de projeto modernizada
- ✅ Documentação completa
- ✅ Testes automatizados
- ✅ Caminhos de saída corrigidos
- ✅ Guia de troubleshooting criado
- ✅ Otimizações para grandes volumes implementadas
- ✅ Processamento em lotes com cache inteligente
- ✅ Índices de banco otimizados
- ✅ Script otimizado para milhões de registros
