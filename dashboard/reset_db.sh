source .env
export PGPASSWORD=$DB_PASSWORD
psql -h $DB_HOST -U $DB_USER -p $DB_PORT $DB_NAME -f schema.sql