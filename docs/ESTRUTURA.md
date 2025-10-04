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
│   ├── main.py                 # Script principal
│   └── test_connection.py      # Teste de conexão
├── docs/                       # Documentação
│   ├── ESTRUTURA.md           # Este arquivo
│   └── relacionamentos_tabelas.md
├── examples/                   # Exemplos e templates
│   └── exemplos_filtros.json
├── tests/                     # Testes (futuro)
├── data/                      # Dados de entrada
│   ├── ddls.sql
│   └── to-vestuario-calcados.csv
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
- `test_connection.py` → `scripts/test_connection.py`
- `exemplos_filtros.json` → `examples/exemplos_filtros.json`
- `relacionamentos_tabelas.md` → `docs/relacionamentos_tabelas.md`

### 🔧 **Imports Atualizados**
- Todos os imports foram atualizados para a nova estrutura
- Paths relativos configurados corretamente
- Compatibilidade mantida

### 📋 **Próximos Passos**
1. Testar todos os scripts na nova estrutura
2. Adicionar testes unitários em `tests/`
3. Configurar CI/CD
4. Adicionar documentação de API
