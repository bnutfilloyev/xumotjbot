#!/bin/bash

# Exit on any error
set -e

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILENAME="xumotjbot_backup_${TIMESTAMP}.gz"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

echo "📦 Creating MongoDB backup..."

# Backup MongoDB data
docker-compose exec -T mongodb mongodump --archive --gzip --db xumotjbot > "${BACKUP_DIR}/${BACKUP_FILENAME}"

# Check if backup was successful
if [ $? -eq 0 ]; then
  echo "✅ Backup created successfully: ${BACKUP_DIR}/${BACKUP_FILENAME}"
  
  # Clean up old backups (keep last 10)
  echo "🧹 Cleaning up old backups..."
  ls -t "${BACKUP_DIR}"/*.gz | tail -n +11 | xargs -r rm
  echo "✅ Backup process completed!"
else
  echo "❌ Error: Backup failed."
  exit 1
fi
