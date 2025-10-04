# Makefile para o CNPJ Processor

.PHONY: help install test clean run-dev run-prod

help: ## Mostra esta ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala as dependências
	pip install -r requirements.txt

test-connection: ## Testa a conexão com o banco
	python scripts/test_connection.py

run-dev: ## Executa em modo desenvolvimento (50 registros)
	python scripts/main.py --limit 50

run-prod: ## Executa em modo produção (sem limite)
	python scripts/main.py --no-limit

run-filters: ## Executa com filtros interativos
	python scripts/main.py --filters --limit 100

run-json: ## Executa com filtros JSON
	python scripts/main.py --json --limit 100

clean: ## Limpa arquivos temporários
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf output/*.csv
	rm -rf .pytest_cache

setup: install ## Configura o ambiente de desenvolvimento
	@echo "✅ Ambiente configurado com sucesso!"
	@echo "Execute 'make test-connection' para testar a conexão"
