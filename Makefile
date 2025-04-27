ifneq ("$(wildcard .env)","")
    include .env
    export $(shell sed 's/=.*//' .env)
else
endif

WORKDIR := $(shell pwd)
.ONESHELL:
.EXPORT_ALL_VARIABLES:
DOCKER_BUILDKIT=1


help: ## Display help message
	@echo "Please use \`make <target>' where <target> is one of"
	@perl -nle'print $& if m{^[\.a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

run_app:  ## Run application
	docker compose up -d

run_and_build_app:  ## Run & build application
	docker compose up -d --build

drop_all_containers: ## Drop all containers
	docker compose down -v --remove-orphans

lint_check: run_app
	docker compose exec bot poetry install --only dev --no-root
	docker compose exec bot poetry run black . && poetry run isort . --profile black

open_shell: ## Open shell to the app container
	docker compose exec bot bash

open_log: ## Open api log
	docker compose logs -f bot

build: ## Rebuild application
	docker compose build
