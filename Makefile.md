🚀 Core Commands
Command	Description
make up	Build and start containers, wait for DB, and initialize schema + seed data
make down	Stop and remove containers and volumes (⚠️ destroys DB)
make restart	Restart everything (calls down then up)
make logs	View real-time logs from all containers


🗃️ Database Commands
Command	Description
make init-db	Initialize the schema + insert seed data from SQL files
make reset-db	Backup schema, reset database by dropping everything and reinit
make wait-for-db	Wait for Postgres container (hr_postgres) to be ready


🔒 Backup Commands
Command	Description
make backup-schema	Save schema-only backup to backup/hrdb_schema_backup.sql
make backup-data	Save data-only backup to backup/hrdb_data_backup.sql
make backup-full	Save full DB (schema + data) to backup/hrdb_full_backup.sql


♻️ Restore Commands
Command	Description
make restore-schema	Restore schema from backup
make restore-data	Restore data only from backup
make restore-full	Restore full DB from backup


📁 Folder Expectations
SQL scripts in: db_init/
Backups saved in: backup/
PostgreSQL container name: hr_postgres
Database: hrdb | User: hradmin


📝 Notes
Ensure you have PostgreSQL client installed in WSL:
-sudo apt install postgresql-client

All docker exec operations depend on the hr_postgres container being up.

Use make backup-schema before make reset-db to preserve schema definitions.


# Connect to the DB and run interactive SQL commands
docker exec -it hr_postgres psql -U hradmin -d hrdb

# Example inside psql shell:
# \dt           → list tables
# \dv           → list views

Notes: for foreign key or dependency errors while restoring, use:

sql

SET session_replication_role = replica;
-- your SQL inserts
SET session_replication_role = DEFAULT;