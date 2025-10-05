# 📊 Índices de Banco de Dados

## 📋 Visão Geral

Este documento explica como aplicar e gerenciar os índices de banco de dados para otimizar a performance do processador CNPJ.

## 🗂️ Arquivos de Índices

### ✅ **Arquivo Atual: `essential_indexes.sql`**
- **Localização**: `data/sql/essential_indexes.sql`
- **Tamanho**: ~110 linhas
- **Índices**: 8 índices essenciais
- **Status**: ✅ **RECOMENDADO**

### ❌ **Arquivo Removido: `ultra_optimization_indexes.sql`**
- **Status**: Removido (era muito complexo)
- **Motivo**: Causava erros e era desnecessário

## 🛠️ Como Aplicar os Índices

### 1. **Executar Script Essencial**
```bash
# Comando principal
mysql -u seu_usuario -p sua_database < data/sql/essential_indexes.sql

# Exemplo específico
mysql -u root -p cnpj < data/sql/essential_indexes.sql
```

### 2. **Verificar se Funcionou**
```sql
-- Conectar ao MySQL
mysql -u seu_usuario -p sua_database

-- Verificar índices criados
SHOW INDEX FROM cnpj_estabelecimentos WHERE Key_name LIKE 'idx_%';

-- Verificar estatísticas
SHOW TABLE STATUS LIKE 'cnpj_estabelecimentos';
```

## 📊 Índices Incluídos

### **Índices Primários (Críticos)**
1. `idx_estabelecimentos_cnpj_data` - Ordenação principal
2. `idx_estabelecimentos_uf_situacao` - Filtros geográficos
3. `idx_estabelecimentos_cnae_data` - Filtros de CNAE

### **Índices de Lookup**
4. `idx_empresas_cnpj` - Tabela de empresas
5. `idx_simples_cnpj` - Tabela simples nacional
6. `idx_socios_cnpj` - Tabela de sócios

### **Índices Específicos**
7. `idx_estabelecimentos_email` - Empresas com email
8. `idx_estabelecimentos_telefone` - Empresas com telefone

## ⚡ Performance Esperada

### **Antes dos Índices**
- Consultas simples: 5-10 segundos
- Consultas com filtros: 30-60 segundos
- Consultas complexas: 2-5 minutos

### **Depois dos Índices**
- Consultas simples: 0.1-0.5 segundos
- Consultas com filtros: 1-3 segundos
- Consultas complexas: 5-15 segundos

## 🔍 Verificação de Performance

### **Teste de Consulta**
```sql
-- Teste simples
EXPLAIN SELECT 
    est.cnpj_part1,
    est.data_inicio_atividade,
    e.razao_social
FROM cnpj_estabelecimentos est
INNER JOIN cnpj_empresas e ON est.cnpj_part1 = e.cnpj_part1
WHERE est.uf = 'SP'
AND est.situacao_cadastral = 2
ORDER BY est.cnpj_part1, est.data_inicio_atividade DESC
LIMIT 1000;
```

### **O que Procurar no EXPLAIN**
- **type**: Deve ser `ref` ou `range` (não `ALL`)
- **key**: Deve mostrar o nome do índice usado
- **rows**: Deve ser um número baixo (não milhões)

## 🚨 Troubleshooting

### **Erro: "Table doesn't exist"**
```bash
# Verificar se as tabelas existem
mysql -u seu_usuario -p sua_database -e "SHOW TABLES;"
```

### **Erro: "Access denied"**
```bash
# Verificar permissões
mysql -u seu_usuario -p sua_database -e "SHOW GRANTS;"
```

### **Índices não sendo usados**
```sql
-- Atualizar estatísticas
ANALYZE TABLE cnpj_estabelecimentos;
ANALYZE TABLE cnpj_empresas;
ANALYZE TABLE cnpj_simples;
ANALYZE TABLE cnpj_socios;
```

## 📈 Monitoramento

### **Verificar Uso de Índices**
```sql
-- Estatísticas de uso
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    CARDINALITY
FROM information_schema.STATISTICS 
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'cnpj_estabelecimentos'
ORDER BY CARDINALITY DESC;
```

### **Verificar Tamanho dos Índices**
```sql
-- Tamanho dos índices
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    ROUND(STAT_VALUE * @@innodb_page_size / 1024 / 1024, 2) AS 'Index Size (MB)'
FROM information_schema.INNODB_SYS_TABLESTATS 
WHERE TABLE_NAME LIKE 'cnpj_%';
```

## 🔄 Manutenção

### **Atualização Periódica**
```sql
-- Executar mensalmente
ANALYZE TABLE cnpj_estabelecimentos;
ANALYZE TABLE cnpj_empresas;
ANALYZE TABLE cnpj_simples;
ANALYZE TABLE cnpj_socios;
```

### **Limpeza de Índices Não Utilizados**
```sql
-- Verificar índices não utilizados (cuidado!)
-- Só execute se souber o que está fazendo
SELECT 
    OBJECT_SCHEMA,
    OBJECT_NAME,
    INDEX_NAME,
    COUNT_FETCH,
    COUNT_INSERT,
    COUNT_UPDATE,
    COUNT_DELETE
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE OBJECT_SCHEMA = DATABASE()
AND OBJECT_NAME = 'cnpj_estabelecimentos'
AND COUNT_STAR = 0;
```

## 📝 Notas Importantes

1. **Execute os índices ANTES** de usar os processadores otimizados
2. **Monitore o espaço em disco** - índices ocupam espaço adicional
3. **Faça backup** antes de aplicar índices em produção
4. **Teste em ambiente de desenvolvimento** primeiro
5. **Use EXPLAIN** para verificar se os índices estão sendo utilizados

## 🎯 Resultado Esperado

Com os índices aplicados corretamente, você deve ver uma melhoria de **10-50x** na performance das consultas, especialmente em tabelas com milhões de registros.
