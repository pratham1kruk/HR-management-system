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