.PHONY: up down restart logs init-db init-mongo reset-db wait-for-db wait-for-mongo \
        backup-schema backup-full backup-data restore-schema restore-full restore-data

# Start all containers and initialize both databases
up:
	docker-compose up -d --build
	$(MAKE) wait-for-db
	$(MAKE) wait-for-mongo
	$(MAKE) init-db
	$(MAKE) init-mongo

# Stop and remove containers and volumes
down:
	docker-compose down -v

# Restart containers and reinitialize databases
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

# Wait for MongoDB to be ready
wait-for-mongo:
	@echo "⏳ Waiting for MongoDB to be ready..."
	@until docker exec hr_mongo mongosh --quiet -u root -p example --authenticationDatabase admin --eval "db.adminCommand('ping')" | grep -q '"ok" : 1'; do \
		sleep 1; \
	done
	@echo "✅ MongoDB is ready."

# Initialize PostgreSQL schema and seed data
init-db:
	docker exec -i hr_postgres psql -U hradmin -d hrdb < db_init/professional_info.sql
	docker exec -i hr_postgres psql -U hradmin -d hrdb < db_init/init_employee.sql

# Initialize MongoDB with seed data
init-mongo:
	docker cp db_init/personnel_info.json hr_mongo:/tmp/personnel_info.json
	docker exec hr_mongo mongosh -u root -p example --authenticationDatabase admin \
	  --eval 'const fs = require("fs"); const data = JSON.parse(fs.readFileSync("/tmp/personnel_info.json")); db.createCollection("employees_info"); db.employees_info.insertMany(data);'
	@echo "✅ MongoDB seeded with personnel_info.json"

# Reset the PostgreSQL database
reset-db: backup-schema
	docker exec -i hr_postgres psql -U hradmin -d hrdb < db_init/reset_db.sql
	$(MAKE) init-db

# 🔒 PostgreSQL BACKUPS

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

# ♻️ PostgreSQL RESTORES

restore-schema:
	docker exec -i hr_postgres psql -U hradmin -d hrdb < backup/hrdb_schema_backup.sql
	@echo "✅ Schema restored."

restore-full:
	docker exec -i hr_postgres psql -U hradmin -d hrdb < backup/hrdb_full_backup.sql
	@echo "✅ Full DB restored."

restore-data:
	docker exec -i hr_postgres psql -U hradmin -d hrdb < backup/hrdb_data_backup.sql
	@echo "✅ Data restored."
