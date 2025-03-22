#!/bin/bash

# Exit on any error
set -e

# Configuration
BACKUP_DIR="./backups"

# Check if a backup file is provided
if [ -z "$1" ]; then
  echo "❌ Error: No backup file specified."
  echo "Usage: ./restore.sh <backup_filename>"
  echo "Available backups:"
  ls -1 "${BACKUP_DIR}"/*.gz 2>/dev/null || echo "  No backups found in ${BACKUP_DIR}"
  exit 1
fi

BACKUP_FILE="${BACKUP_DIR}/$1"

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
  echo "❌ Error: Backup file not found: ${BACKUP_FILE}"
  exit 1
fi

echo "🔄 Restoring MongoDB from backup: ${BACKUP_FILE}"

# Restore MongoDB data
cat "${BACKUP_FILE}" | docker-compose exec -T mongodb mongorestore --archive --gzip --drop

# Check if restore was successful
if [ $? -eq 0 ]; then
  echo "✅ Restore completed successfully!"
else
  echo "❌ Error: Restore failed."
  exit 1
fi
