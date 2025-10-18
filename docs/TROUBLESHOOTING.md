# 🔧 Guia de Solução de Problemas

Este guia ajuda a resolver problemas comuns encontrados ao usar o CNPJ Processor.

## 📁 Problemas de Localização de Arquivos

### ❌ Arquivos CSV salvos no local errado

**Problema**: Arquivos sendo salvos em `scripts/output/` em vez de `output/`

**Causa**: Script executado de dentro da pasta `scripts/` com caminhos relativos

**✅ Solução**: 
- Execute sempre da raiz do projeto: `python scripts/main.py`
- O sistema agora detecta automaticamente a raiz e corrige os caminhos
- Arquivos serão salvos em `output/` independentemente do diretório de execução

### ❌ Pasta output não encontrada

**Problema**: Erro "No such file or directory: output/"

**✅ Solução**: 
- A pasta `output/` é criada automaticamente
- Se não for criada, execute: `mkdir -p output/`
- O sistema criará automaticamente no primeiro processamento

## 🗄️ Problemas de Banco de Dados

### ❌ Erro de conexão com MySQL

**Problema**: `ConnectionError` ou `Access denied`

**✅ Soluções**:
1. Verificar se o MySQL está rodando:
   ```bash
   sudo systemctl status mysql
   ```

2. Verificar credenciais no arquivo `.env`:
   ```bash
   cat .env
   ```

3. Testar conexão manualmente:
   ```bash
   mysql -u root -p -e "SHOW DATABASES;"
   ```

### ❌ País aparece como "COLIS POSTAUX" em vez de "BRASIL"

**Problema**: Empresas brasileiras aparecem com país incorreto

**✅ Solução**: 
- **RESOLVIDO** na versão atual
- O sistema agora corrige automaticamente o código do país 0 para 105 (BRASIL)
- A correção é aplicada antes do mapeamento para garantir consistência
- Execute: `python scripts/main_ultra_optimized.py --limit 100` para verificar

### ❌ Colunas desorganizadas no CSV

**Problema**: Colunas de códigos e descrições espalhadas pelo arquivo

**✅ Solução**: 
- **RESOLVIDO** na versão atual
- O sistema agora reordena automaticamente as colunas:
  - `codigo_pais` → `pais`
  - `codigo_municipio` → `municipio`
  - `cnae_codes` → `cnae_fiscal`
- Execute: `python scripts/main_ultra_optimized.py --limit 100` para verificar

### ❌ Banco de dados não existe

**Problema**: `Unknown database 'cnpj'`

**✅ Solução**:
```bash
mysql -u root -p -e "CREATE DATABASE cnpj CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### ❌ Tabelas não encontradas

**Problema**: `Table 'cnpj.xxx' doesn't exist`

**✅ Solução**:
```bash
# Criar estrutura das tabelas
mysql -u root -p cnpj < data/sql/ddls.sql
```

## 📊 Problemas de Dados

### ❌ Tabelas vazias

**Problema**: Consultas retornam 0 registros

**✅ Verificações**:
1. Verificar se dados foram carregados:
   ```bash
   mysql -u root -p cnpj -e "SELECT COUNT(*) FROM cnpj_empresas;"
   ```

2. Se vazio, carregar dados:
   ```bash
   python scripts/cnpj_empresas.py
   ```

### ❌ Arquivos CSV não encontrados

**Problema**: `FileNotFoundError` ao executar scripts de carregamento

**✅ Solução**:
1. Verificar se arquivos estão em `data/csv_source/`:
   ```bash
   ls -la data/csv_source/
   ```

2. Arquivos esperados:
   - `K3241.K03200Y0.D50913.EMPRECSV` (empresas)
   - `K3241.K03200Y1.D50913.EMPRECSV` (empresas)
   - ... (arquivos 2-9 das empresas)
   - `K3241.K03200Y.D50913.ESTABELE` (estabelecimentos)
   - `K3241.K03200Y.D50913.SOCIOCSV` (sócios)
   - `F.K03200$W.SIMPLES.CSV.D50913` (simples)

## 🔧 Problemas de Configuração

### ❌ Arquivo .env não encontrado

**Problema**: `FileNotFoundError: [Errno 2] No such file or directory: '.env'`

**✅ Solução**:
```bash
# Copiar arquivo de exemplo
cp config.example.env .env

# Editar com suas configurações
nano .env
```

### ❌ Dependências não instaladas

**Problema**: `ModuleNotFoundError`

**✅ Solução**:
```bash
# Instalar dependências
pip install -r requirements.txt

# Ou usando pip3
pip3 install -r requirements.txt
```

## 🚀 Problemas de Performance

### ❌ Processamento muito lento

**Problema**: Sistema demora muito para processar

**✅ Otimizações**:
1. Usar limites menores para testes:
   ```bash
   python scripts/main.py --limit 100
   ```

2. Usar filtros para reduzir dados:
   ```bash
   python scripts/main.py --filters --limit 1000
   ```

3. Processar por lotes:
   ```bash
   python scripts/main.py --limit 10000 --output output/lote_1.csv
   python scripts/main.py --limit 10000 --output output/lote_2.csv
   ```

### ❌ Memória insuficiente

**Problema**: `MemoryError` ou sistema travando

**✅ Soluções**:
1. Reduzir limite de registros
2. Fechar outros aplicativos
3. Usar processamento em lotes menores

## ⚡ Problemas de Performance

### ❌ Processo para prematuramente

**Problema**: Script para no lote 4 ou 5 sem completar

**✅ Solução**: 
- **RESOLVIDO** na versão atual
- O sistema agora usa paginação baseada em cursor em vez de OFFSET
- Ajuste dinâmico do tamanho do lote baseado na performance
- Execute: `python scripts/main_ultra_optimized.py --limit 200000` para verificar

### ❌ Performance degrada ao longo do tempo

**Problema**: Cada lote demora mais que o anterior

**✅ Solução**: 
- **RESOLVIDO** na versão atual
- Paginação baseada em cursor elimina degradação de performance
- Cache otimizado para lookup tables
- Execute: `python scripts/main_ultra_optimized.py --limit 100000` para verificar

### ❌ Sócios não aparecem nos resultados

**Problema**: Dados de sócios ausentes ou incompletos

**✅ Solução**: 
- **RESOLVIDO** na versão atual
- Busca de sócios sempre incluída (nunca omitida)
- Busca direta sem cache para evitar problemas de memória
- Execute: `python scripts/main_ultra_optimized.py --limit 100` para verificar

## 📝 Logs e Debug

### 🔍 Habilitar logs detalhados

```bash
# Executar com verbose
python scripts/main.py --limit 10 --output output/debug.csv
```

### 🔍 Verificar status do banco

```bash
# Testar conexão
python scripts/main.py --test-connection

# Verificar tabelas
mysql -u root -p cnpj -e "SHOW TABLES;"
```

## 🆘 Suporte

Se os problemas persistirem:

1. **Verificar logs**: Observe as mensagens de erro detalhadas
2. **Testar conexão**: Use `--test-connection` para diagnosticar
3. **Verificar estrutura**: Confirme se todos os arquivos estão no lugar correto
4. **Consultar documentação**: Veja [docs/INSTALACAO_BANCO.md](INSTALACAO_BANCO.md)

---

> 💡 **Dica**: Sempre execute os comandos da raiz do projeto (`/home/user/cnpj-processor/`) para evitar problemas de caminho.
