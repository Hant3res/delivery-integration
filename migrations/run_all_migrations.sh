#!/bin/bash

echo "Running migrations on SQL Server..."

# Wait for SQL Server to be ready
sleep 10

# Run migrations in order
for migration in 001_create_couriers.sql 002_create_deliveries.sql 003_create_tracking_history.sql 004_create_notifications.sql 005_seed_couriers.sql; do
    echo "Running: $migration"
    /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "YourStrong!Passw0rd" -d delivery_db -i "/migrations/$migration"
done

echo "All migrations completed!"
