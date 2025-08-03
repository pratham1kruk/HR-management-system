# Makefile for managing Docker-based Flask app

.PHONY: up down restart logs

up:
	docker-compose up --build

down:
	docker-compose down

restart: down up

logs:
	docker-compose logs -f
