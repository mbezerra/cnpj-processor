# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [2.0.0] - 2025-10-18

### 🚀 Versão Ultra Otimizada v2.0

#### ✨ Adicionado
- **Correção automática do país** (COLIS POSTAUX → BRASIL)
- **Reordenação das colunas** (códigos seguidos de descrições)
- **Paginação baseada em cursor** para performance consistente
- **Busca de sócios sempre incluída** (dados essenciais)
- **Ajuste dinâmico do tamanho do lote** baseado na performance
- **Documentação de melhorias recentes** (`docs/MELHORIAS_RECENTES.md`)

#### 🔧 Melhorias
- **Performance consistente** sem degradação ao longo do tempo
- **Processamento nunca para** prematuramente
- **Dados de sócios sempre incluídos** nos resultados
- **Ordem lógica das colunas** no CSV de saída
- **Correção do mapeamento do país** aplicada na ordem correta

#### 🐛 Corrigido
- **País 105** agora aparece corretamente como "BRASIL"
- **Colunas desorganizadas** agora seguem ordem lógica
- **Processo parando prematuramente** resolvido com paginação por cursor
- **Performance degradando** resolvida com otimizações
- **Sócios omitidos** resolvido com busca sempre incluída

#### 📊 Impacto
- ✅ **Dados consistentes** - país correto para todas as empresas brasileiras
- ✅ **CSV organizado** - colunas em ordem lógica
- ✅ **Performance estável** - sem degradação ao longo do tempo
- ✅ **Processamento completo** - nunca para prematuramente
- ✅ **Dados completos** - todos os sócios sempre incluídos

## [1.0.0] - 2025-10-04

### 🎉 Lançamento Inicial

#### ✨ Adicionado
- **Sistema de Processamento CNPJ** completo
- **Detecção inteligente de celulares** baseada no terceiro dígito
- **Validação de emails** com regex robusta
- **Filtros interativos** para seleção de critérios
- **Filtros JSON** para automação
- **Correção automática de dados** (código país, concatenação)
- **Estrutura moderna** com pacotes Python organizados
- **Comandos Make** para desenvolvimento
- **Documentação completa** com exemplos

#### 🔧 Funcionalidades
- **Processamento de dados** de múltiplas tabelas CNPJ
- **JOINs otimizados** entre empresas, estabelecimentos, sócios
- **Concatenação automática** de DDD + telefone/fax
- **Detecção de celular** com algoritmo baseado no terceiro dígito
- **Validação de email** com suporte a padrões internacionais
- **Filtros geográficos** (UF, município, país)
- **Filtros de atividade** (CNAE, situação, data)
- **Filtros de contato** (email, telefone, tipo)
- **Filtros tributários** (MEI, capital social)

#### 🏗️ Arquitetura
- **Estrutura moderna** com `src/`, `scripts/`, `docs/`
- **Pacotes Python** organizados com `__init__.py`
- **Configuração moderna** com `pyproject.toml`
- **Comandos automatizados** com `Makefile`
- **Controle de versão** com `.gitignore`

#### 📊 Dados Processados
- **64+ milhões** de empresas
- **67+ milhões** de estabelecimentos
- **Dados completos** de sócios, endereços, CNAEs
- **Regime tributário** (Simples Nacional, MEI)
- **Correções automáticas** de dados inconsistentes

#### 🚀 Comandos Disponíveis
```bash
make help              # Mostra todos os comandos
make setup             # Configura o ambiente
make test-connection   # Testa conexão
make run-dev          # Executa em desenvolvimento
make run-prod         # Executa em produção
make run-filters      # Executa com filtros
make run-json         # Executa com JSON
```

#### 📋 Exemplos de Uso
- **Desenvolvimento**: `python scripts/main.py --limit 50`
- **Produção**: `python scripts/main.py --no-limit`
- **Filtros**: `python scripts/main.py --filters`
- **JSON**: `python scripts/main.py --json`

#### 🔧 Tecnologias
- **Python 3.8+**
- **MySQL** com PyMySQL
- **Pandas** para processamento
- **SQLAlchemy** para ORM
- **Argparse** para CLI
- **Make** para automação

#### 📚 Documentação
- **README.md** completo com exemplos
- **docs/ESTRUTURA.md** detalhada
- **exemplos_filtros.json** práticos
- **Comentários** em todo o código

---

## [0.1.0] - 2025-10-04

### 🔄 Renomeação do Projeto

#### ✨ Mudanças
- **Nome do projeto**: `iaAgent` → `cnpj-processor`
- **Autor**: `Prospectar Team` → `Marcos Bezerra`
- **Repositório**: Atualizado para `mbezerra/cnpj-processor`
- **Documentação**: Atualizada com novo nome
- **Scripts**: Atualizados com nova identidade

#### 📋 Arquivos Atualizados
- `README.md` - Título e referências
- `pyproject.toml` - Metadados do projeto
- `src/__init__.py` - Informações do pacote
- `scripts/main.py` - Descrição do parser
- `scripts/test_connection.py` - Cabeçalho
- `src/cnpj_processor/cnpj_processor.py` - Cabeçalho
- `docs/ESTRUTURA.md` - Estrutura do projeto
- `Makefile` - Comentários

#### ✅ Funcionalidades Mantidas
- **Todas as funcionalidades** permanecem inalteradas
- **Comandos Make** funcionando normalmente
- **Scripts** executando corretamente
- **Estrutura** mantida intacta
