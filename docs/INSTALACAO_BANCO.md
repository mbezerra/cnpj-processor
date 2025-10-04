# 🗄️ Guia de Instalação do Banco de Dados

Este guia detalha como instalar e configurar o banco de dados MySQL para o CNPJ Processor.

## 📋 Pré-requisitos

- MySQL 5.7+ ou MariaDB 10.3+
- Usuário com privilégios de administrador (root)
- Acesso ao terminal/linha de comando

## 🚀 Instalação Passo a Passo

### 1. Criar o Banco de Dados

```bash
# Criar o banco com encoding UTF-8
mysql -u root -p -e "CREATE DATABASE cnpj CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 2. Criar a Estrutura das Tabelas

```bash
# Executar script DDL para criar todas as tabelas
mysql -u root -p cnpj < data/ddls.sql
```

**Tabelas criadas:**
- `cnpj_empresas` - Dados das empresas
- `cnpj_estabelecimentos` - Dados dos estabelecimentos
- `cnpj_socios` - Dados dos sócios
- `cnpj_cnaes` - Códigos de atividade econômica
- `cnpj_municipios` - Códigos de municípios
- `cnpj_paises` - Códigos de países
- `cnpj_naturezas_juridicas` - Naturezas jurídicas
- `cnpj_qualificacao_socios` - Qualificações de sócios
- `cnpj_motivos` - Motivos de situação cadastral
- `cnpj_simples` - Dados do Simples Nacional

### 3. Popular Tabelas de Referência

Execute os seguintes comandos na ordem indicada:

```bash
# CNAEs (Códigos de atividade econômica)
mysql -u root -p cnpj < data/insert-cnpj-cnaes.sql

# Países
mysql -u root -p cnpj < data/insert-cnpj-paises.sql

# Municípios brasileiros
mysql -u root -p cnpj < data/insert-cnpj-municipios.sql

# Naturezas jurídicas
mysql -u root -p cnpj < data/insert-cnpj-naturezas-juridicas.sql

# Qualificações de sócios
mysql -u root -p cnpj < data/insert-cnpj-qualificacao-socios.sql

# Motivos de situação cadastral
mysql -u root -p cnpj < data/insert-cnpj-motivos.sql
```

### 4. Verificar a Instalação

```bash
# Conectar ao banco e verificar as tabelas
mysql -u root -p cnpj -e "SHOW TABLES;"

# Verificar se as tabelas de referência foram populadas
mysql -u root -p cnpj -e "SELECT COUNT(*) as total_cnaes FROM cnpj_cnaes;"
mysql -u root -p cnpj -e "SELECT COUNT(*) as total_municipios FROM cnpj_municipios;"
mysql -u root -p cnpj -e "SELECT COUNT(*) as total_paises FROM cnpj_paises;"
```

**Resultados esperados:**
- CNAEs: ~1.500 registros
- Municípios: ~5.500 registros
- Países: ~280 registros

## 📊 Scripts Disponíveis

| Arquivo | Descrição | Tamanho Aprox. | Registros |
|---------|-----------|----------------|-----------|
| `ddls.sql` | Estrutura das tabelas | 5KB | - |
| `insert-cnpj-cnaes.sql` | Códigos CNAE | 200KB | ~1.500 |
| `insert-cnpj-paises.sql` | Códigos de países | 15KB | ~280 |
| `insert-cnpj-municipios.sql` | Códigos de municípios | 300KB | ~5.500 |
| `insert-cnpj-naturezas-juridicas.sql` | Naturezas jurídicas | 10KB | ~100 |
| `insert-cnpj-qualificacao-socios.sql` | Qualificações de sócios | 5KB | ~50 |
| `insert-cnpj-motivos.sql` | Motivos de situação | 5KB | ~20 |

## ⚠️ Dados das Empresas

**Importante:** Os dados reais das empresas CNPJ não estão incluídos no repositório por questões de:

- **Tamanho**: Os dados completos ocupam vários GB
- **Licenciamento**: Dados oficiais da Receita Federal
- **Atualização**: Dados são atualizados mensalmente

### Como obter os dados das empresas:

1. **Fonte oficial**: [Receita Federal](https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/cadastros/consultas/dados-publicos-cnpj)
2. **Formatos disponíveis**: CSV, TXT
3. **Processamento**: Use ferramentas específicas para importar os dados

### Estrutura dos arquivos de dados:

```
dados_empresas.sql          # Dados da tabela cnpj_empresas
dados_estabelecimentos.sql  # Dados da tabela cnpj_estabelecimentos  
dados_socios.sql           # Dados da tabela cnpj_socios
dados_simples.sql          # Dados da tabela cnpj_simples
```

## 🔧 Configuração de Usuário

### Criar usuário específico (recomendado):

```sql
-- Conectar como root
mysql -u root -p

-- Criar usuário
CREATE USER 'cnpj_user'@'localhost' IDENTIFIED BY 'senha_segura';

-- Conceder privilégios
GRANT SELECT, INSERT, UPDATE, DELETE ON cnpj.* TO 'cnpj_user'@'localhost';

-- Aplicar mudanças
FLUSH PRIVILEGES;
```

### Configurar arquivo .env:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=cnpj_user
DB_PASSWORD=senha_segura
DB_NAME=cnpj
DB_CHARSET=utf8mb4
```

## 🧪 Testando a Instalação

### 1. Teste de Conexão

```bash
python tests/test_connection.py
```

**Saída esperada:**
```
✅ Conexão com MySQL funcionando perfeitamente!
Total de empresas no banco: [número]
Total de estabelecimentos no banco: [número]
```

### 2. Teste com Filtros

```bash
python tests/test_exemplo_basico.py
```

**Saída esperada:**
```
🎉 TODOS OS TESTES PASSARAM COM SUCESSO!
📁 Verifique a pasta 'output' para o arquivo CSV gerado
```

## 🚨 Solução de Problemas

### Erro de Conexão

```
❌ Erro na conexão: (2003, "Can't connect to MySQL server")
```

**Soluções:**
1. Verificar se o MySQL está rodando: `sudo systemctl status mysql`
2. Verificar porta: `netstat -tlnp | grep 3306`
3. Verificar usuário/senha no arquivo `.env`

### Erro de Encoding

```
❌ Error: Incorrect string value
```

**Soluções:**
1. Recriar banco com UTF-8:
   ```sql
   DROP DATABASE cnpj;
   CREATE DATABASE cnpj CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

### Tabelas Vazias

```
⚠️ Nenhum registro encontrado
```

**Soluções:**
1. Verificar se os scripts INSERT foram executados
2. Verificar logs de erro do MySQL
3. Executar scripts novamente na ordem correta

## 📈 Performance

### Otimizações Recomendadas:

1. **Índices**: Os índices já estão criados no DDL
2. **Configuração MySQL**: Ajustar `innodb_buffer_pool_size`
3. **Dados**: Usar filtros para reduzir volume de dados processados

### Monitoramento:

```sql
-- Verificar tamanho das tabelas
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS "Size in MB"
FROM information_schema.TABLES 
WHERE table_schema = 'cnpj'
ORDER BY (data_length + index_length) DESC;
```

## ✅ Checklist de Instalação

- [ ] MySQL instalado e rodando
- [ ] Banco `cnpj` criado com UTF-8
- [ ] Tabelas criadas via `ddls.sql`
- [ ] Tabelas de referência populadas
- [ ] Arquivo `.env` configurado
- [ ] Teste de conexão funcionando
- [ ] Teste com filtros funcionando
- [ ] CSV gerado com sucesso

---

**🎉 Parabéns! Seu banco de dados CNPJ está pronto para uso!**
