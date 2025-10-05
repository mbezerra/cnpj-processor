-- =====================================================
-- ÍNDICES ESSENCIAIS PARA PERFORMANCE - VERSÃO SEGURA
-- Versão que trata erros de índices duplicados
-- =====================================================

-- IMPORTANTE: Execute este script para melhorar a performance
-- Esta versão trata automaticamente erros de índices duplicados

-- =====================================================
-- FUNÇÃO PARA CRIAR ÍNDICE COM TRATAMENTO DE ERRO
-- =====================================================

DELIMITER $$

CREATE PROCEDURE CreateIndexIfNotExists(
    IN table_name VARCHAR(128),
    IN index_name VARCHAR(128),
    IN column_spec VARCHAR(512)
)
BEGIN
    DECLARE CONTINUE HANDLER FOR 1061
        BEGIN
            SELECT CONCAT('Índice ', index_name, ' já existe, ignorando...') AS message;
        END;
    
    SET @sql = CONCAT('CREATE INDEX ', index_name, ' ON ', table_name, ' (', column_spec, ')');
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END$$

DELIMITER ;

-- =====================================================
-- CRIAR ÍNDICES USANDO A FUNÇÃO SEGURA
-- =====================================================

-- 1. Índice principal para ordenação (mais importante)
CALL CreateIndexIfNotExists('cnpj_estabelecimentos', 'idx_estabelecimentos_cnpj_data', 'cnpj_part1(8), data_inicio_atividade DESC');

-- 2. Índice para filtros geográficos mais comuns
CALL CreateIndexIfNotExists('cnpj_estabelecimentos', 'idx_estabelecimentos_uf_situacao', 'uf, situacao_cadastral, data_inicio_atividade DESC');

-- 3. Índice para filtros de CNAE
CALL CreateIndexIfNotExists('cnpj_estabelecimentos', 'idx_estabelecimentos_cnae_data', 'cnae, data_inicio_atividade DESC');

-- 4. Índice para tabela de empresas
CALL CreateIndexIfNotExists('cnpj_empresas', 'idx_empresas_cnpj', 'cnpj_part1(8)');

-- 5. Índice para tabela simples
CALL CreateIndexIfNotExists('cnpj_simples', 'idx_simples_cnpj', 'cnpj_part1(8)');

-- 6. Índice para tabela de sócios
CALL CreateIndexIfNotExists('cnpj_socios', 'idx_socios_cnpj', 'cnpj_part1(8), codigo_qualificacao_socio');

-- 7. Índice para empresas com email
CALL CreateIndexIfNotExists('cnpj_estabelecimentos', 'idx_estabelecimentos_email', 'correio_eletronico(50), cnpj_part1(8)');

-- 8. Índice para empresas com telefone
CALL CreateIndexIfNotExists('cnpj_estabelecimentos', 'idx_estabelecimentos_telefone', 'telefone1, cnpj_part1(8)');

-- =====================================================
-- LIMPAR PROCEDURE TEMPORÁRIA
-- =====================================================

DROP PROCEDURE IF EXISTS CreateIndexIfNotExists;

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
