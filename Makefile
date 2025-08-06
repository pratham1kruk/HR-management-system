.PHONY: up down restart logs init-db reset-db wait-for-db

# Start the containers and initialize the database
up:
	docker-compose up -d --build
	$(MAKE) wait-for-db
	$(MAKE) init-db

# Stop and remove containers and volumes
down:
	docker-compose down -v

# Restart containers and reinitialize the database
restart: down up

# View real-time logs
logs:
	docker-compose logs -f

# Wait for PostgreSQL to be ready
wait-for-db:
	@echo "⏳ Waiting for Postgres to be ready..."
	@until docker exec hr_postgres pg_isready -U hradmin -d hrdb; do \
		sleep 1; \
	done
	@echo "✅ Postgres is ready."

# Initialize database schema and seed data
init-db:
	docker exec -i hr_postgres psql -U hradmin -d hrdb < db_init/professional_info.sql
	docker exec -i hr_postgres psql -U hradmin -d hrdb < db_init/init_employee.sql

# Reset the database (drops everything)
reset-db:
	docker exec -i hr_postgres psql -U hradmin -d hrdb < db_init/reset_db.sql
