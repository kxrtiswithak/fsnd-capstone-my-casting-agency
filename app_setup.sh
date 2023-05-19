#!/bin/bash
dropdb casting -ef --if-exists && createdb casting -e
psql casting < casting.sql

export DATABASE_URL="postgresql://postgres@localhost:5432/casting"

echo "app_setup.sh script executed successfully!"
echo "check \$DATABASE_URL has been correctly set:"
echo "\necho \$DATABASE_URL\n"
echo "if empty, then run script again with dot preceding it:"
echo "\n. ./app_setup.sh"