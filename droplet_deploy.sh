#!/bin/bash

# Exit on any error
set -e

echo "🚀 Deploying XumotjBot to DigitalOcean Droplet..."

# Install required dependencies if they're not already installed
echo "📦 Checking dependencies..."
if ! command -v docker &> /dev/null; then
    echo "🔧 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "🔧 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
fi

# Install Nginx
echo "🔧 Installing Nginx..."
sudo apt-get update
sudo apt-get install -y nginx

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️ Warning: .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it with your configuration before continuing."
        nano .env
    else
        echo "❌ Error: .env.example file not found."
        exit 1
    fi
fi

# Setup directories
echo "📁 Setting up directories..."
mkdir -p mongodb/data
mkdir -p backups

# Set proper permissions
echo "🔒 Setting permissions..."
sudo chown -R $USER:$USER .
sudo chmod +x *.sh

# Configure Nginx - using server IP if no domain
echo "🔧 Configuring Nginx..."
# Get server IP address
SERVER_IP=$(curl -s https://ipinfo.io/ip)

read -p "Do you have a domain name? (y/n): " HAS_DOMAIN
if [ "$HAS_DOMAIN" = "y" ] || [ "$HAS_DOMAIN" = "Y" ]; then
    read -p "Enter your domain name (e.g., example.com): " DOMAIN
    USE_DOMAIN=true
else
    echo "No domain provided. Using server IP address: $SERVER_IP"
    DOMAIN=$SERVER_IP
    USE_DOMAIN=false
fi

# Create Nginx config file
cat > /tmp/xumotjbot.conf << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias /home/$USER/xumotjbot/admin/static/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
}
EOF

sudo mv /tmp/xumotjbot.conf /etc/nginx/sites-available/xumotjbot.conf
sudo ln -sf /etc/nginx/sites-available/xumotjbot.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Set up SSL with Let's Encrypt only if using a domain
if [ "$USE_DOMAIN" = true ]; then
    echo "🔐 Setting up SSL with Let's Encrypt..."
    sudo apt-get install -y certbot python3-certbot-nginx
    read -p "Enter your email for SSL certificate notifications: " SSL_EMAIL
    sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $SSL_EMAIL
fi

# Pull latest changes if in a Git repository
if [ -d .git ]; then
    echo "📥 Pulling latest changes..."
    git pull
fi

# Build and start the containers
echo "🏗️ Building and starting containers..."
docker-compose -f docker-compose.prod.yml up -d --build

# Setup a systemd service for automatic startup
echo "🔄 Creating systemd service for auto-restart..."
cat > /tmp/xumotjbot.service << EOF
[Unit]
Description=XumotjBot Docker Compose Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/$USER/xumotjbot
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/xumotjbot.service /etc/systemd/system/xumotjbot.service
sudo systemctl enable xumotjbot.service

# Setup automatic backups
echo "📊 Setting up automatic backups..."
(crontab -l 2>/dev/null; echo "0 3 * * * /home/$USER/xumotjbot/backup.sh > /home/$USER/xumotjbot/backup.log 2>&1") | crontab -

# Check if containers are running
echo "🔍 Checking container status..."
if docker-compose -f docker-compose.prod.yml ps | grep -q 'Exit'; then
    echo "❌ Error: One or more containers failed to start. Check logs with 'docker-compose logs'."
    exit 1
fi

echo "✅ Deployment completed successfully!"
if [ "$USE_DOMAIN" = true ] && [ "$HAS_DOMAIN" = "y" ]; then
    echo "📊 Admin panel: https://$DOMAIN/admin"
else
    echo "📊 Admin panel: http://$SERVER_IP/admin"
fi
echo "🤖 Bot is running!"
echo ""
echo "💡 Useful commands:"
echo "  • View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  • Restart services: sudo systemctl restart xumotjbot"
echo "  • Manual backup: ./backup.sh"
echo "  • Update deployment: ./droplet_deploy.sh"
