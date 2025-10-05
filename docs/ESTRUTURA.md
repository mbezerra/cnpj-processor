# Estrutura do Projeto

## Organização Moderna

O projeto foi reorganizado seguindo as melhores práticas de desenvolvimento Python moderno:

```
cnpj-processor/
├── src/                          # Código fonte principal
│   ├── __init__.py              # Pacote principal
│   ├── cnpj_processor/          # Módulo de processamento
│   │   ├── __init__.py
│   │   ├── cnpj_processor.py           # Processador padrão
│   │   ├── cnpj_processor_optimized.py # Processador otimizado
│   │   ├── cnpj_processor_ultra_optimized.py # Processador ultra otimizado
│   │   └── cnpj_processor_streaming.py # Processador streaming
│   ├── filters/                 # Módulo de filtros
│   │   ├── __init__.py
│   │   └── filters.py
│   └── config/                  # Módulo de configuração
│       ├── __init__.py
│       └── config.py
├── scripts/                     # Scripts executáveis
│   ├── main.py                 # Script principal de processamento
│   ├── main_optimized.py       # Script otimizado para grandes volumes
│   ├── main_ultra_optimized.py # Script ultra otimizado para máxima performance
│   ├── main_streaming.py       # Script com processamento em streaming
│   ├── benchmark_performance.py # Script de benchmark de performance
│   ├── carregar_dados_completo.py # Script para carregar todos os dados em sequência
│   ├── monitor_carregamento.py # Script para monitorar progresso dos carregamentos
│   ├── cnpj_empresas.py       # Carregamento de dados das empresas
│   ├── cnpj_estabelecimentos.py # Carregamento de dados dos estabelecimentos
│   ├── cnpj_socios.py         # Carregamento de dados dos sócios
│   └── cnpj_simples.py        # Carregamento de dados do Simples Nacional
├── tests/                       # Testes automatizados
│   ├── test_connection.py      # Teste de conexão com banco
│   └── test_exemplo_basico.py  # Teste com filtros e geração de CSV
├── docs/                       # Documentação
│   ├── ESTRUTURA.md           # Este arquivo
│   └── relacionamentos_tabelas.md
├── examples/                   # Exemplos e templates
│   └── exemplos_filtros.json
├── data/                      # Dados e scripts de banco
│   ├── csv_source/           # Arquivos CSV originais da Receita Federal
│   │   ├── K3241.K03200Y0.D50913.EMPRECSV # Arquivos de empresas
│   │   ├── K3241.K03200Y1.D50913.EMPRECSV # (10 arquivos total)
│   │   └── ...               # Outros arquivos CSV grandes (gitignored)
│   └── sql/                  # Scripts de banco de dados
│       ├── ddls.sql          # Estrutura das tabelas (CREATE TABLE)
│       ├── insert-cnpj-cnaes.sql # Dados de CNAEs (~1.500 registros)
│       ├── insert-cnpj-paises.sql # Dados de países (~280 registros)
│       ├── insert-cnpj-municipios.sql # Dados de municípios (~5.500 registros)
│       ├── insert-cnpj-naturezas-juridicas.sql # Naturezas jurídicas
│       ├── insert-cnpj-qualificacao-socios.sql # Qualificações de sócios
│       └── insert-cnpj-motivos.sql # Motivos de situação cadastral
├── output/                    # Dados de saída (gerado automaticamente)
├── requirements.txt           # Dependências Python
├── pyproject.toml            # Configuração do projeto
├── Makefile                  # Comandos de desenvolvimento
├── config.example.env        # Exemplo de configuração
├── .gitignore               # Arquivos ignorados pelo Git
└── README.md                # Documentação principal
```

## Benefícios da Nova Estrutura

### 🏗️ **Organização Lógica**
- **`src/`**: Código fonte organizado em módulos
- **`scripts/`**: Scripts executáveis separados
- **`docs/`**: Documentação centralizada
- **`examples/`**: Exemplos e templates
- **`tests/`**: Preparado para testes futuros

### 📦 **Pacotes Python**
- Cada módulo é um pacote Python com `__init__.py`
- Imports organizados e claros
- Facilita manutenção e extensão

### 🛠️ **Ferramentas de Desenvolvimento**
- **`Makefile`**: Comandos automatizados
- **`pyproject.toml`**: Configuração moderna do projeto
- **`.gitignore`**: Controle de versão limpo
- **`config.example.env`**: Template de configuração
- **`data/sql/ddls.sql`**: Scripts para criar estrutura do banco

### 📁 **Estrutura de Saída**
- **`output/`**: Pasta para arquivos CSV gerados
- **Caminhos absolutos**: Sistema detecta automaticamente a raiz do projeto
- **Criação automática**: Diretórios são criados automaticamente quando necessário
- **Localização fixa**: Arquivos sempre salvos em `output/` na raiz, independente do diretório de execução

### 🚀 **Comandos Disponíveis**
```bash
make help              # Mostra ajuda
make install           # Instala dependências
make test-connection   # Testa conexão
make run-dev          # Executa em desenvolvimento
make run-prod         # Executa em produção
make clean            # Limpa arquivos temporários
```

## Migração

### ✅ **Arquivos Movidos**
- `cnpj_processor.py` → `src/cnpj_processor/cnpj_processor.py`
- `filters.py` → `src/filters/filters.py`
- `config.py` → `src/config/config.py`
- `main.py` → `scripts/main.py`
- `test_connection.py` → `tests/test_connection.py`
- `test_exemplo_basico.py` → `tests/test_exemplo_basico.py` (novo)
- `exemplos_filtros.json` → `examples/exemplos_filtros.json`
- `relacionamentos_tabelas.md` → `docs/relacionamentos_tabelas.md`

### 📂 **Nova Estrutura de Dados**
- **`data/sql/`**: Scripts SQL organizados (DDL e DML)
  - `ddls.sql`: Estrutura das tabelas
  - `insert-*.sql`: Dados de referência (CNAEs, municípios, etc.)
- **`data/csv_source/`**: Arquivos CSV originais da Receita Federal
  - Arquivos grandes são ignorados pelo Git (gitignored)
  - `.gitkeep` mantém a pasta no repositório
- **Scripts de carregamento**: Atualizados para usar novos caminhos

### 🔧 **Imports Atualizados**
- Todos os imports foram atualizados para a nova estrutura
- Paths relativos configurados corretamente
- Compatibilidade mantida

## Configuração do Banco de Dados

### 🗄️ **Estrutura do Banco**
O sistema utiliza um banco MySQL com as seguintes tabelas principais:
- `cnpj_empresas` - Dados das empresas
- `cnpj_estabelecimentos` - Dados dos estabelecimentos
- `cnpj_socios` - Dados dos sócios
- `cnpj_municipios` - Códigos de municípios
- `cnpj_paises` - Códigos de países
- `cnpj_cnaes` - Códigos de atividade econômica
- `cnpj_simples` - Dados do Simples Nacional

### ⚙️ **Configuração**
1. **Criar banco:**
   ```bash
   mysql -u root -p -e "CREATE DATABASE cnpj CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   ```

2. **Criar estrutura das tabelas:**
   ```bash
   mysql -u root -p cnpj < data/ddls.sql
   ```

3. **Popular tabelas de referência (obrigatório):**
   ```bash
   mysql -u root -p cnpj < data/insert-cnpj-cnaes.sql
   mysql -u root -p cnpj < data/insert-cnpj-paises.sql
   mysql -u root -p cnpj < data/insert-cnpj-municipios.sql
   mysql -u root -p cnpj < data/insert-cnpj-naturezas-juridicas.sql
   mysql -u root -p cnpj < data/insert-cnpj-qualificacao-socios.sql
   mysql -u root -p cnpj < data/insert-cnpj-motivos.sql
   ```

4. **Carregar dados das empresas (opcional):**
   ```bash
   # Apenas se você tiver os arquivos CSV originais da Receita Federal
   python scripts/cnpj_empresas.py
   python scripts/cnpj_estabelecimentos.py
   python scripts/cnpj_socios.py
   python scripts/cnpj_simples.py
   ```

5. **Configurar variáveis:**
   ```bash
   cp config.example.env .env
   # Editar .env com suas credenciais
   ```

6. **Testar instalação:**
   ```bash
   python tests/test_connection.py
   python tests/test_exemplo_basico.py
   ```

## 🚀 Processadores Disponíveis

O projeto oferece **4 processadores diferentes** para diferentes cenários de uso:

### **1. CNPJProcessor (Padrão)**
- **Arquivo**: `src/cnpj_processor/cnpj_processor.py`
- **Script**: `scripts/main.py`
- **Uso**: Desenvolvimento e testes (até 10.000 registros)
- **Características**: Simples, fácil de usar, ideal para testes

### **2. CNPJProcessorOptimized**
- **Arquivo**: `src/cnpj_processor/cnpj_processor_optimized.py`
- **Script**: `scripts/main_optimized.py`
- **Uso**: Volumes médios (10.000 - 100.000 registros)
- **Características**: Paginação, cache básico, consultas otimizadas

### **3. CNPJProcessorUltraOptimized**
- **Arquivo**: `src/cnpj_processor/cnpj_processor_ultra_optimized.py`
- **Script**: `scripts/main_ultra_optimized.py`
- **Uso**: Volumes grandes (100.000+ registros)
- **Características**: Cache agressivo, consultas mínimas, máximo desempenho

### **4. CNPJProcessorStreaming**
- **Arquivo**: `src/cnpj_processor/cnpj_processor_streaming.py`
- **Script**: `scripts/main_streaming.py`
- **Uso**: Volumes extremos com memória limitada
- **Características**: Processamento linha por linha, mínimo uso de memória

### **5. Benchmark de Performance**
- **Arquivo**: `scripts/benchmark_performance.py`
- **Uso**: Comparar performance entre processadores
- **Características**: Testa todos os processadores com métricas detalhadas

## 🚀 Scripts de Carregamento de Dados

O projeto inclui scripts especializados para carregar os dados originais da Receita Federal:

### **1. Carregamento Automático Completo**
- **Arquivo**: `scripts/carregar_dados_completo.py`
- **Uso**: Carregar todos os dados em sequência automaticamente
- **Características**:
  - Executa automaticamente: empresas → estabelecimentos → sócios → simples
  - Logs detalhados em arquivo e console
  - Verificação de processos em execução
  - Resumo final com estatísticas
  - Tempo estimado: 10-20 horas

### **2. Monitor de Carregamento**
- **Arquivo**: `scripts/monitor_carregamento.py`
- **Uso**: Monitorar progresso dos carregamentos em tempo real
- **Características**:
  - Estatísticas em tempo real do banco de dados
  - Lista processos de carregamento em execução
  - Atualização automática a cada 30 segundos
  - Interface interativa

### **3. Scripts Individuais**
- **`cnpj_empresas.py`**: Carregamento de dados das empresas
- **`cnpj_estabelecimentos.py`**: Carregamento de dados dos estabelecimentos
- **`cnpj_socios.py`**: Carregamento de dados dos sócios
- **`cnpj_simples.py`**: Carregamento de dados do Simples Nacional

## 📊 Performance Esperada

| Processador | Volume Ideal | Velocidade | Memória | Complexidade |
|-------------|--------------|------------|---------|--------------|
| Padrão | < 10k | 1x | 1x | Baixa |
| Otimizado | 10k - 100k | 3x | 0.7x | Média |
| ULTRA | 100k+ | 10x | 0.3x | Alta |
| Streaming | Qualquer | 5x | 0.1x | Média |

### 📋 **Próximos Passos**
1. ✅ Testar todos os scripts na nova estrutura
2. ✅ Adicionar testes automatizados em `tests/`
3. ✅ Implementar múltiplos processadores
4. ✅ Criar scripts de benchmark
5. 🔄 Configurar CI/CD
6. 🔄 Adicionar documentação de API
7. 🔄 Implementar testes unitários adicionais
8. 🔄 Configurar cobertura de testes
