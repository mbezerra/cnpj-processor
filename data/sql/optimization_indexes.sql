-- =====================================================
-- OTIMIZAÇÕES DE PERFORMANCE PARA GRANDES VOLUMES
-- =====================================================

-- Índices compostos para consultas frequentes
-- Estes índices melhoram significativamente a performance de JOINs e filtros

-- Índice composto para filtros geográficos mais comuns
CREATE INDEX idx_estabelecimentos_uf_municipio_situacao 
ON cnpj_estabelecimentos (uf, codigo_municipio, situacao_cadastral);

-- Índice composto para filtros de atividade
CREATE INDEX idx_estabelecimentos_cnae_data_inicio 
ON cnpj_estabelecimentos (cnae, data_inicio_atividade);

-- Índice composto para filtros de contato
CREATE INDEX idx_estabelecimentos_email_telefone 
ON cnpj_estabelecimentos (correio_eletronico, telefone1);

-- Índice para filtros de capital social (já existe, mas vamos otimizar)
CREATE INDEX idx_empresas_capital_porte 
ON cnpj_empresas (capital_social, porte_empresa);

-- Índice para tabela de sócios (melhora consultas de sócios)
CREATE INDEX idx_socios_cnpj_qualificacao 
ON cnpj_socios (cnpj_part1(8), codigo_qualificacao_socio);

-- Índice para tabela simples (melhora filtros MEI/Simples)
CREATE INDEX idx_simples_opcoes 
ON cnpj_simples (opcao_simples, opcao_mei);

-- =====================================================
-- OTIMIZAÇÕES DE CONSULTA
-- =====================================================

-- Configurações de sessão para otimizar consultas grandes
-- Estes comandos devem ser executados antes de consultas grandes

-- Aumentar buffer de ordenação para grandes datasets
SET SESSION sort_buffer_size = 256*1024*1024;  -- 256MB

-- Aumentar buffer de JOIN para melhor performance
SET SESSION join_buffer_size = 128*1024*1024;  -- 128MB

-- Otimizar para consultas grandes
SET SESSION read_buffer_size = 64*1024*1024;   -- 64MB

-- Desabilitar cache de query para consultas únicas grandes
SET SESSION query_cache_type = OFF;

-- =====================================================
-- VIEWS OTIMIZADAS PARA CONSULTAS FREQUENTES
-- =====================================================

-- View para empresas ativas (mais comum)
CREATE OR REPLACE VIEW vw_empresas_ativas AS
SELECT 
    est.cnpj_part1,
    est.cnpj_part2,
    est.cnpj_part3,
    e.razao_social,
    est.nome_fantasia,
    est.uf,
    est.codigo_municipio,
    m.municipio,
    est.cnae,
    cnae.descricao as cnae_descricao,
    est.data_inicio_atividade,
    e.capital_social,
    est.correio_eletronico,
    est.telefone1,
    est.ddd1
FROM cnpj_estabelecimentos est
INNER JOIN cnpj_empresas e ON est.cnpj_part1 = e.cnpj_part1
LEFT JOIN cnpj_cnaes cnae ON est.cnae = cnae.cnae
LEFT JOIN cnpj_municipios m ON est.codigo_municipio = m.codigo
WHERE est.situacao_cadastral = 2  -- Apenas ativas
AND est.cnpj_part1 IS NOT NULL;

-- View para empresas com contato completo
CREATE OR REPLACE VIEW vw_empresas_com_contato AS
SELECT 
    est.cnpj_part1,
    est.cnpj_part2,
    est.cnpj_part3,
    e.razao_social,
    est.nome_fantasia,
    est.uf,
    est.codigo_municipio,
    m.municipio,
    est.cnae,
    cnae.descricao as cnae_descricao,
    est.data_inicio_atividade,
    e.capital_social,
    est.correio_eletronico,
    est.telefone1,
    est.ddd1,
    s.opcao_mei
FROM cnpj_estabelecimentos est
INNER JOIN cnpj_empresas e ON est.cnpj_part1 = e.cnpj_part1
LEFT JOIN cnpj_cnaes cnae ON est.cnae = cnae.cnae
LEFT JOIN cnpj_municipios m ON est.codigo_municipio = m.codigo
LEFT JOIN cnpj_simples s ON est.cnpj_part1 = s.cnpj_part1
WHERE est.situacao_cadastral = 2  -- Apenas ativas
AND est.correio_eletronico IS NOT NULL 
AND est.correio_eletronico != ''
AND est.telefone1 IS NOT NULL 
AND est.telefone1 != ''
AND est.cnpj_part1 IS NOT NULL;

-- =====================================================
-- PROCEDURES PARA CONSULTAS OTIMIZADAS
-- =====================================================

DELIMITER //

-- Procedure para consulta paginada otimizada
CREATE PROCEDURE sp_consulta_paginada(
    IN p_limit INT,
    IN p_offset INT,
    IN p_uf VARCHAR(2),
    IN p_situacao INT
)
BEGIN
    -- Usar variáveis de sessão para otimização
    SET SESSION sort_buffer_size = 256*1024*1024;
    SET SESSION join_buffer_size = 128*1024*1024;
    
    SELECT 
        est.cnpj_part1,
        est.cnpj_part2,
        est.cnpj_part3,
        e.razao_social,
        est.nome_fantasia,
        est.situacao_cadastral,
        est.uf,
        est.codigo_municipio,
        m.municipio,
        est.cnae,
        cnae.descricao as cnae_descricao,
        est.data_inicio_atividade,
        e.capital_social,
        est.correio_eletronico,
        est.telefone1,
        est.ddd1
    FROM cnpj_estabelecimentos est
    INNER JOIN cnpj_empresas e ON est.cnpj_part1 = e.cnpj_part1
    LEFT JOIN cnpj_cnaes cnae ON est.cnae = cnae.cnae
    LEFT JOIN cnpj_municipios m ON est.codigo_municipio = m.codigo
    WHERE est.cnpj_part1 IS NOT NULL
    AND (p_uf IS NULL OR est.uf = p_uf)
    AND (p_situacao IS NULL OR est.situacao_cadastral = p_situacao)
    ORDER BY est.cnpj_part1
    LIMIT p_limit OFFSET p_offset;
END //

DELIMITER ;

-- =====================================================
-- CONFIGURAÇÕES DE PERFORMANCE DO MYSQL
-- =====================================================

-- Estas configurações devem ser adicionadas ao my.cnf para otimização permanente
/*
[mysqld]
# Otimizações para grandes volumes de dados
innodb_buffer_pool_size = 2G              # 50-70% da RAM disponível
innodb_log_file_size = 256M               # Log files maiores
innodb_log_buffer_size = 64M              # Buffer de log maior
innodb_flush_log_at_trx_commit = 2        # Menos I/O síncrono
innodb_flush_method = O_DIRECT            # Evita duplo buffering

# Otimizações de consulta
query_cache_size = 256M                   # Cache de consultas
query_cache_limit = 64M                   # Limite por consulta
tmp_table_size = 256M                     # Tabelas temporárias
max_heap_table_size = 256M                # Tabelas em memória

# Conexões e threads
max_connections = 200                     # Mais conexões simultâneas
thread_cache_size = 16                    # Cache de threads
table_open_cache = 4000                   # Cache de tabelas abertas

# Otimizações de I/O
innodb_read_io_threads = 8                # Mais threads de leitura
innodb_write_io_threads = 8               # Mais threads de escrita
innodb_io_capacity = 2000                 # Capacidade de I/O
*/
