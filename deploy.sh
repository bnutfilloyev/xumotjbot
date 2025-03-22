#!/bin/bash

# Exit on any error
set -e

echo "🚀 Deploying XumotjBot..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "❌ Error: Docker is not running. Please start Docker and try again."
  exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
  echo "⚠️ Warning: .env file not found. Creating from .env.example..."
  if [ -f bot/.env.example ]; then
    cp bot/.env.example .env
    echo "✅ Created .env file. Please edit it with your configuration before continuing."
    exit 0
  else
    echo "❌ Error: .env.example file not found."
    exit 1
  fi
fi

# Pull latest changes if in a Git repository
if [ -d .git ]; then
  echo "📥 Pulling latest changes..."
  git pull
fi

# Build and start the containers
echo "🏗️ Building and starting containers..."
docker-compose up -d --build

# Check if containers are running
echo "🔍 Checking container status..."
if docker-compose ps | grep -q 'Exit'; then
  echo "❌ Error: One or more containers failed to start. Check logs with 'docker-compose logs'."
  exit 1
fi

echo "✅ Deployment completed successfully!"
echo "📊 Admin panel: http://localhost:8000/admin"
echo "📊 MongoDB Express: http://localhost:32123"
echo "🤖 Bot is running!"
