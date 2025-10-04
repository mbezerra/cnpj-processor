-- cnpj.cnpj_cnaes definição

CREATE TABLE `cnpj_cnaes` (
  `cnae` bigint NOT NULL,
  `descricao` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`cnae`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- cnpj.cnpj_empresas definição

CREATE TABLE `cnpj_empresas` (
  `cnpj_part1` varchar(8) NOT NULL,
  `razao_social` varchar(255) DEFAULT NULL,
  `natureza_juridica` bigint DEFAULT NULL,
  `qualificacao_socio` bigint DEFAULT NULL,
  `capital_social` double DEFAULT NULL,
  `porte_empresa` double DEFAULT NULL,
  PRIMARY KEY (`cnpj_part1`),
  KEY `cnpj_empresas_capital_social_IDX` (`capital_social`) USING BTREE,
  KEY `cnpj_empresas_porte_empresa_IDX` (`porte_empresa`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- cnpj.cnpj_estabelecimentos definição

CREATE TABLE `cnpj_estabelecimentos` (
  `cnpj_part1` varchar(8) DEFAULT NULL,
  `cnpj_part2` varchar(4) DEFAULT NULL,
  `cnpj_part3` varchar(2) DEFAULT NULL,
  `identificador_matriz_filial` tinyint DEFAULT NULL,
  `nome_fantasia` varchar(255) DEFAULT NULL,
  `situacao_cadastral` int DEFAULT NULL,
  `data_situacao_cadastral` varchar(8) DEFAULT NULL,
  `motivo_situacao_cadastral` int DEFAULT NULL,
  `cidade_estrangeira` varchar(100) DEFAULT NULL,
  `codigo_pais` int DEFAULT NULL,
  `data_inicio_atividade` varchar(8) DEFAULT NULL,
  `cnae` int DEFAULT NULL,
  `cnaes_secundarios` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `tipo_logradouro` varchar(20) DEFAULT NULL,
  `logradouro` varchar(255) DEFAULT NULL,
  `numero` varchar(20) DEFAULT NULL,
  `complemento` varchar(255) DEFAULT NULL,
  `bairro` varchar(255) DEFAULT NULL,
  `cep` varchar(8) DEFAULT NULL,
  `uf` varchar(2) DEFAULT NULL,
  `codigo_municipio` int DEFAULT NULL,
  `ddd1` int DEFAULT NULL,
  `telefone1` varchar(9) DEFAULT NULL,
  `ddd2` int DEFAULT NULL,
  `telefone2` varchar(9) DEFAULT NULL,
  `ddd_fax` int DEFAULT NULL,
  `fax` varchar(9) DEFAULT NULL,
  `correio_eletronico` varchar(255) DEFAULT NULL,
  `situacao_especial` varchar(100) DEFAULT NULL,
  `data_situacao_especial` varchar(8) DEFAULT NULL,
  KEY `cnpj_estabelecimentos_cnpj_part1_IDX` (`cnpj_part1`) USING BTREE,
  KEY `cnpj_estabelecimentos_data_inicio_atividade_IDX` (`data_inicio_atividade`) USING BTREE,
  KEY `cnpj_estabelecimentos_cnae_IDX` (`cnae`) USING BTREE,
  KEY `cnpj_estabelecimentos_uf_IDX` (`uf`) USING BTREE,
  KEY `cnpj_estabelecimentos_codigo_municipio_IDX` (`codigo_municipio`) USING BTREE,
  KEY `cnpj_estabelecimentos_situacao_cadastral_IDX` (`situacao_cadastral`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- cnpj.cnpj_motivos definição

CREATE TABLE `cnpj_motivos` (
  `codigo` bigint NOT NULL,
  `descricao` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- cnpj.cnpj_municipios definição

CREATE TABLE `cnpj_municipios` (
  `codigo` varchar(4) NOT NULL,
  `municipio` varchar(150) NOT NULL,
  `uf` varchar(2) DEFAULT NULL,
  PRIMARY KEY (`codigo`),
  KEY `uf` (`uf`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- cnpj.cnpj_naturezas_juridicas definição

CREATE TABLE `cnpj_naturezas_juridicas` (
  `codigo` bigint NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- cnpj.cnpj_paises definição

CREATE TABLE `cnpj_paises` (
  `codigo` bigint NOT NULL,
  `pais` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- cnpj.cnpj_qualificacao_socios definição

CREATE TABLE `cnpj_qualificacao_socios` (
  `codigo` bigint NOT NULL,
  `qualificacao` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- cnpj.cnpj_simples definição

CREATE TABLE `cnpj_simples` (
  `cnpj_part1` varchar(8) NOT NULL,
  `opcao_simples` varchar(1) DEFAULT NULL,
  `data_opcao_simples` varchar(8) DEFAULT NULL,
  `data_exclusao_simples` varchar(8) DEFAULT NULL,
  `opcao_mei` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `data_opcao_mei` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `data_exclusao_opcao_mei` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`cnpj_part1`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- cnpj.cnpj_socios definição

CREATE TABLE `cnpj_socios` (
  `cnpj_part1` text,
  `identificador_socio` bigint DEFAULT NULL,
  `nome_socio` text,
  `codigo_qualificacao_socio` bigint DEFAULT NULL,
  `data_entrada_sociedade` bigint DEFAULT NULL,
  `nome_representante_legal` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
