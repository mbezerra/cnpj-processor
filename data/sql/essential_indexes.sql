-- =====================================================
-- ÍNDICES ESSENCIAIS PARA PERFORMANCE
-- Versão simplificada e segura
-- =====================================================

-- IMPORTANTE: Execute este script para melhorar a performance
-- Estes são os índices mínimos necessários para otimização

-- =====================================================
-- ÍNDICES PRIMÁRIOS (CRÍTICOS)
-- =====================================================

-- 1. Índice principal para ordenação (mais importante)
CREATE INDEX IF NOT EXISTS idx_estabelecimentos_cnpj_data 
ON cnpj_estabelecimentos (cnpj_part1(8), data_inicio_atividade DESC);

-- 2. Índice para filtros geográficos mais comuns
CREATE INDEX IF NOT EXISTS idx_estabelecimentos_uf_situacao 
ON cnpj_estabelecimentos (uf, situacao_cadastral, data_inicio_atividade DESC);

-- 3. Índice para filtros de CNAE
CREATE INDEX IF NOT EXISTS idx_estabelecimentos_cnae_data 
ON cnpj_estabelecimentos (cnae, data_inicio_atividade DESC);

-- =====================================================
-- ÍNDICES PARA TABELAS DE LOOKUP
-- =====================================================

-- 4. Índice para tabela de empresas (se não existir)
CREATE INDEX IF NOT EXISTS idx_empresas_cnpj 
ON cnpj_empresas (cnpj_part1(8));

-- 5. Índice para tabela simples (se não existir)
CREATE INDEX IF NOT EXISTS idx_simples_cnpj 
ON cnpj_simples (cnpj_part1(8));

-- 6. Índice para tabela de sócios
CREATE INDEX IF NOT EXISTS idx_socios_cnpj 
ON cnpj_socios (cnpj_part1(8), codigo_qualificacao_socio);

-- =====================================================
-- ÍNDICES PARA FILTROS ESPECÍFICOS
-- =====================================================

-- 7. Índice para empresas com email
CREATE INDEX IF NOT EXISTS idx_estabelecimentos_email 
ON cnpj_estabelecimentos (correio_eletronico(50), cnpj_part1(8));

-- 8. Índice para empresas com telefone
CREATE INDEX IF NOT EXISTS idx_estabelecimentos_telefone 
ON cnpj_estabelecimentos (telefone1, cnpj_part1(8));

-- =====================================================
-- VERIFICAÇÃO DE ÍNDICES
-- =====================================================

-- Verificar se os índices foram criados
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX
FROM information_schema.STATISTICS 
WHERE TABLE_SCHEMA = DATABASE()
AND TABLE_NAME = 'cnpj_estabelecimentos'
AND INDEX_NAME LIKE 'idx_%'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;

-- =====================================================
-- ATUALIZAR ESTATÍSTICAS
-- =====================================================

-- Atualizar estatísticas para otimizador
ANALYZE TABLE cnpj_estabelecimentos;
ANALYZE TABLE cnpj_empresas;
ANALYZE TABLE cnpj_simples;
ANALYZE TABLE cnpj_socios;

-- =====================================================
-- TESTE DE PERFORMANCE
-- =====================================================

-- Teste simples para verificar se os índices estão sendo usados
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

-- =====================================================
-- NOTAS IMPORTANTES
-- =====================================================

/*
1. Execute este script ANTES de usar o processador ULTRA otimizado
2. Os índices podem levar alguns minutos para serem criados
3. Monitore o espaço em disco - os índices ocupam espaço adicional
4. Use EXPLAIN nas suas consultas para verificar se os índices estão sendo utilizados

Comandos úteis:
- EXPLAIN SELECT ... FROM cnpj_estabelecimentos WHERE ...;
- SHOW INDEX FROM cnpj_estabelecimentos;
- SHOW TABLE STATUS LIKE 'cnpj_estabelecimentos';
*/
