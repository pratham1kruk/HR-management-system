-- MongoDB Backup: employees_info, qualifications, and related collections
-- Exported using mongoexport (recommended for JSON backup)

-- Export employees_info collection
-- Command:
-- mongoexport --uri="mongodb://<user>:<password>@mongo:27017/<dbname>?authSource=admin" --collection=employees_info --out=employees_info_backup.json

-- Export qualifications collection (if exists)
-- Command:
-- mongoexport --uri="mongodb://<user>:<password>@mongo:27017/<dbname>?authSource=admin" --collection=qualifications --out=qualifications_backup.json

-- Export other relevant collections as needed
-- Example:
-- mongoexport --uri="mongodb://<user>:<password>@mongo:27017/<dbname>?authSource=admin" --collection=other_collection --out=other_collection_backup.json

-- Restore with mongoimport:
-- mongoimport --uri="mongodb://<user>:<password>@mongo:27017/<dbname>?authSource=admin" --collection=employees_info --file=employees_info_backup.json --jsonArray
