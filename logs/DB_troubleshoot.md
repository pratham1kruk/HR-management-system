# Connect to the DB and run interactive SQL commands
docker exec -it hr_postgres psql -U hradmin -d hrdb

# Example inside psql shell:
# \dt           → list tables
# \dv           → list views

🔄 Backup Only Schema
docker exec hr_postgres pg_dump -U hradmin -d hrdb --schema-only > backup/hrdb_schema_backup.sql

📦 Want both schema + data?
docker exec hr_postgres pg_dump -U hradmin -d hrdb > backup/hrdb_full_backup.sql

🧪 Want only data?
docker exec hr_postgres pg_dump -U hradmin -d hrdb --data-only > backup/hrdb_data_backup.sql

🧱 1. If Your Backup is Schema-Only (structure only)
(e.g., backup/hrdb_schema_backup.sql)

✅ Restore Command:
docker exec -i hr_postgres psql -U hradmin -d hrdb < backup/hrdb_schema_backup.sql
📦 2. If You Have a Full Backup (schema + data)
(e.g., backup/hrdb_full_backup.sql)

✅ Restore Command:
docker exec -i hr_postgres psql -U hradmin -d hrdb < backup/hrdb_full_backup.sql
🧪 3. If You Have a Data-Only Backup
(e.g., backup/hrdb_data_backup.sql)

This will insert rows back into existing tables (schema must already exist).

✅ Restore Command:
docker exec -i hr_postgres psql -U hradmin -d hrdb < backup/hrdb_data_backup.sql

💡 Notes:
If you get foreign key or dependency errors while restoring, use:

sql

SET session_replication_role = replica;
-- your SQL inserts
SET session_replication_role = DEFAULT;


🎯makefile
restore-schema:
	docker exec -i hr_postgres psql -U hradmin -d hrdb < backup/hrdb_schema_backup.sql

restore-full:
	docker exec -i hr_postgres psql -U hradmin -d hrdb < backup/hrdb_full_backup.sql
