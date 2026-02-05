#!/bin/bash

# Cross Country Database Initialization Script
# This script creates the SQLite database and populates it with sample data

set -e  # Exit on error

DB_FILE="xc_database.db"

echo "Initializing Cross Country database..."

# Remove existing database if it exists
if [ -f "$DB_FILE" ]; then
    echo "Removing existing database..."
    rm "$DB_FILE"
fi

# Create database and tables
echo "Creating database schema..."
sqlite3 "$DB_FILE" < schema.sql

# Populate with sample data
echo "Inserting sample data..."
sqlite3 "$DB_FILE" < sample_data.sql

# Verify the database
echo ""
echo "Database created successfully!"
echo ""
echo "Database statistics:"
echo "==================="
sqlite3 "$DB_FILE" "SELECT COUNT(*) || ' athletes' FROM athletes;"
sqlite3 "$DB_FILE" "SELECT COUNT(*) || ' meets' FROM meets;"
sqlite3 "$DB_FILE" "SELECT COUNT(*) || ' results' FROM results;"
echo ""
echo "Database file: $DB_FILE"
echo "Done!"
