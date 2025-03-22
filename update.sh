#!/bin/bash

# Exit on any error
set -e

echo "🔄 Updating XumotjBot..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "❌ Error: Docker is not running. Please start Docker and try again."
  exit 1
fi

# Create backup before updating
echo "📦 Creating backup before update..."
./backup.sh

# Pull latest changes if in a Git repository
if [ -d .git ]; then
  echo "📥 Pulling latest changes..."
  git pull
fi

# Rebuild and restart the containers
echo "🏗️ Rebuilding and restarting containers..."
docker-compose -f docker-compose.prod.yml up -d --build

# Check if containers are running
echo "🔍 Checking container status..."
if docker-compose -f docker-compose.prod.yml ps | grep -q 'Exit'; then
  echo "❌ Error: One or more containers failed to start. Check logs with 'docker-compose logs'."
  exit 1
fi

echo "✅ Update completed successfully!"
echo "📊 Admin panel is running"
echo "🤖 Bot is running"
