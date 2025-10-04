# Estrutura do Projeto

## Organização Moderna

O projeto foi reorganizado seguindo as melhores práticas de desenvolvimento Python moderno:

```
cnpj-processor/
├── src/                          # Código fonte principal
│   ├── __init__.py              # Pacote principal
│   ├── cnpj_processor/          # Módulo de processamento
│   │   ├── __init__.py
│   │   └── cnpj_processor.py
│   ├── filters/                 # Módulo de filtros
│   │   ├── __init__.py
│   │   └── filters.py
│   └── config/                  # Módulo de configuração
│       ├── __init__.py
│       └── config.py
├── scripts/                     # Scripts executáveis
│   └── main.py                 # Script principal
├── tests/                       # Testes automatizados
│   ├── test_connection.py      # Teste de conexão com banco
│   └── test_exemplo_basico.py  # Teste com filtros e geração de CSV
├── docs/                       # Documentação
│   ├── ESTRUTURA.md           # Este arquivo
│   └── relacionamentos_tabelas.md
├── examples/                   # Exemplos e templates
│   └── exemplos_filtros.json
├── data/                      # Scripts de banco de dados
│   └── ddls.sql              # Scripts DDL para criar tabelas CNPJ
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
- **`data/ddls.sql`**: Scripts para criar estrutura do banco

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
   mysql -u root -p -e "CREATE DATABASE cnpj;"
   ```

2. **Importar estrutura:**
   ```bash
   mysql -u root -p cnpj < data/ddls.sql
   ```

3. **Configurar variáveis:**
   ```bash
   cp config.example.env .env
   # Editar .env com suas credenciais
   ```

### 📋 **Próximos Passos**
1. ✅ Testar todos os scripts na nova estrutura
2. ✅ Adicionar testes automatizados em `tests/`
3. 🔄 Configurar CI/CD
4. 🔄 Adicionar documentação de API
5. 🔄 Implementar testes unitários adicionais
6. 🔄 Configurar cobertura de testes
