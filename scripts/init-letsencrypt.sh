#!/usr/bin/env bash

# SSL Certificate Initialization Script for Django OIDC Provider (Gum UI)
set -euo pipefail

# ------------------------------------------------------------------------------
#  ENVIRONMENT CHECK
# ------------------------------------------------------------------------------
if ! command -v gum &> /dev/null; then
  echo "❌ Gum is not installed. Install it from:"
  echo "   https://github.com/charmbracelet/gum#installation"
  exit 1
fi

ENV_FILE=".envs/.production/.core"

if [ ! -f "$ENV_FILE" ]; then
  gum style --foreground 1 --bold "❌ $ENV_FILE not found!"
  gum style "Run 'make init' to generate environment files."
  exit 1
fi

# Export only necessary vars
export $(grep -v '^#' "$ENV_FILE" | grep -E '^(DOMAIN|EMAIL_FOR_SSL)=' | xargs)

if [ -z "${DOMAIN:-}" ]; then
  gum style --foreground 1 "❌ DOMAIN not set in $ENV_FILE"
  gum style "Set: DOMAIN=yourdomain.com"
  exit 1
fi

if [ -z "${EMAIL_FOR_SSL:-}" ]; then
  gum style --foreground 1 "❌ EMAIL_FOR_SSL not set in $ENV_FILE"
  gum style "Set: EMAIL_FOR_SSL=admin@yourdomain.com"
  exit 1
fi

gum style --foreground 36 --bold "🔒 Initializing Let's Encrypt SSL certificates for $DOMAIN"

# ------------------------------------------------------------------------------
#  CREATE CERT DIRECTORIES
# ------------------------------------------------------------------------------
gum style --foreground 3 "📁 Creating certbot directories..."
mkdir -p "./data/certbot/conf"
mkdir -p "./data/certbot/www"

# ------------------------------------------------------------------------------
#  CHECK EXISTING CERTS
# ------------------------------------------------------------------------------
if [ -d "./data/certbot/conf/live/$DOMAIN" ]; then
  gum style --foreground 3 "⚠️  Certificates already exist for $DOMAIN"

  if ! gum confirm "Recreate certificates?"; then
    gum style --foreground 2 "✅ Keeping existing certificates."
    exit 0
  fi

  gum style --foreground 3 "🗑️  Removing existing certificates..."
  docker compose -f production.compose.yml run --rm --entrypoint "\
    rm -rf /etc/letsencrypt/live/$DOMAIN && \
    rm -rf /etc/letsencrypt/archive/$DOMAIN && \
    rm -rf /etc/letsencrypt/renewal/$DOMAIN.conf" certbot
fi

# ------------------------------------------------------------------------------
#  TEMPORARY NGINX FOR ACME CHALLENGE
# ------------------------------------------------------------------------------
gum style --foreground 3 "🌐 Starting temporary nginx on port 80 for ACME challenge..."

cat > /tmp/nginx-init.conf <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        try_files \$uri =404;
    }

    location / {
        return 200 'SSL setup in progress';
        add_header Content-Type text/plain;
    }
}
EOF

docker run --rm -d --name nginx-init \
  -p 80:80 \
  -v /tmp/nginx-init.conf:/etc/nginx/conf.d/default.conf:ro \
  -v "$(pwd)/data/certbot/www:/var/www/certbot" \
  nginx:1.25

gum style --foreground 3 "📋 Verifying domain accessibility..."
sleep 5

if ! curl -fs "http://$DOMAIN/.well-known/acme-challenge/test" > /dev/null 2>&1; then
  gum style --foreground 1 "❌ Domain $DOMAIN is not accessible via HTTP."
  gum style "Check:"
  gum style "1. DNS points to this server"
  gum style "2. Port 80 is open"
  gum style "3. No other service is using port 80"
  docker stop nginx-init
  exit 1
fi

gum style --foreground 2 "✅ Domain is accessible. Requesting cert via certbot..."

# ------------------------------------------------------------------------------
#  CERTBOT REQUEST
# ------------------------------------------------------------------------------
docker compose -f production.compose.yml run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
  --email $EMAIL_FOR_SSL \
  -d $DOMAIN \
  -d www.$DOMAIN \
  --rsa-key-size 4096 \
  --agree-tos \
  --non-interactive \
  --force-renewal" certbot

docker stop nginx-init

# ------------------------------------------------------------------------------
#  VALIDATE SUCCESS
# ------------------------------------------------------------------------------
if [ -d "./data/certbot/conf/live/$DOMAIN" ]; then
  gum style --foreground 2 --border normal --padding "1" "🎉 SSL certificates created!"
  gum style --foreground 6 "📁 Location: ./data/certbot/conf/live/$DOMAIN"

  gum style --foreground 3 "📝 Updating production.compose.yml volumes..."
  sed -i 's|certbot_conf:/etc/letsencrypt|./data/certbot/conf:/etc/letsencrypt|g' production.compose.yml
  sed -i 's|certbot_www:/var/www/certbot|./data/certbot/www:/var/www/certbot|g' production.compose.yml

  gum style --foreground 2 "✅ SSL setup complete. Run: make deploy"
  gum style --foreground 4 "🔄 Auto-renewal is configured (12h cycle)."
else
  gum style --foreground 1 --bold "❌ Certificate creation failed."
  gum style "Review the output above and try again."
  exit 1
fi
