.PHONY: up down restart logs init-db reset-db wait-for-db backup-schema backup-full backup-data restore-schema restore-full restore-data

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

# Reset the database (drops everything after taking backup)
reset-db: backup-schema
	docker exec -i hr_postgres psql -U hradmin -d hrdb < db_init/reset_db.sql
	$(MAKE) init-db

# 🔒 BACKUPS

backup-schema:
	@mkdir -p backup
	docker exec hr_postgres pg_dump -U hradmin -d hrdb --schema-only > backup/hrdb_schema_backup.sql
	@echo "🗄️ Schema backup saved to backup/hrdb_schema_backup.sql"

backup-full:
	@mkdir -p backup
	docker exec hr_postgres pg_dump -U hradmin -d hrdb > backup/hrdb_full_backup.sql
	@echo "🗃️ Full backup saved to backup/hrdb_full_backup.sql"

backup-data:
	@mkdir -p backup
	docker exec hr_postgres pg_dump -U hradmin -d hrdb --data-only > backup/hrdb_data_backup.sql
	@echo "📦 Data backup saved to backup/hrdb_data_backup.sql"

# ♻️ RESTORE TARGETS

restore-schema:
	docker exec -i hr_postgres psql -U hradmin -d hrdb < backup/hrdb_schema_backup.sql
	@echo "✅ Schema restored."

restore-full:
	docker exec -i hr_postgres psql -U hradmin -d hrdb < backup/hrdb_full_backup.sql
	@echo "✅ Full DB restored."

restore-data:
	docker exec -i hr_postgres psql -U hradmin -d hrdb < backup/hrdb_data_backup.sql
	@echo "✅ Data restored."
