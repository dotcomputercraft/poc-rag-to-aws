.DEFAULT_GOAL := help
.PHONY: help dev


up: ## Run the service aws_rag_app
	docker compose up

down: ## shutdown the serviceaws_rag_app
	docker compose down

build: ## Build the docker image used by the 'aws_rag_app' service in the docker-compose.yml
	docker compose build aws_rag_app

build-no-cache: ## Build the docker image, without the the docker build cache, used by the 'aws_rag_app' service in the docker-compose.yml
	docker compose build aws_rag_app --no-cache
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
