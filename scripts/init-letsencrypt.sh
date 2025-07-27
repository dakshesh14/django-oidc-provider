#!/usr/bin/env bash

# SSL Certificate Initialization Script for Django OIDC Provider (No Gum)
set -euo pipefail

# ------------------------------------------------------------------------------
#  ENVIRONMENT CHECK
# ------------------------------------------------------------------------------
ENV_FILE=".envs/.production/.core"

if [ ! -f "$ENV_FILE" ]; then
  echo -e "\033[0;31m❌ $ENV_FILE not found!\033[0m"
  echo "Run 'make init' to generate environment files."
  exit 1
fi

# Export only necessary vars
export $(grep -v '^#' "$ENV_FILE" | grep -E '^(DOMAIN|EMAIL_FOR_SSL)=' | xargs)

if [ -z "${DOMAIN:-}" ]; then
  echo -e "\033[0;31m❌ DOMAIN not set in $ENV_FILE\033[0m"
  echo "Set: DOMAIN=yourdomain.com"
  exit 1
fi

if [ -z "${EMAIL_FOR_SSL:-}" ]; then
  echo -e "\033[0;31m❌ EMAIL_FOR_SSL not set in $ENV_FILE\033[0m"
  echo "Set: EMAIL_FOR_SSL=admin@yourdomain.com"
  exit 1
fi

echo -e "\033[1;36m🔒 Initializing Let's Encrypt SSL certificates for $DOMAIN\033[0m"

# ------------------------------------------------------------------------------
#  CREATE CERT DIRECTORIES
# ------------------------------------------------------------------------------
echo -e "\033[1;33m📁 Creating certbot directories...\033[0m"
mkdir -p "./data/certbot/conf"
mkdir -p "./data/certbot/www"

# ------------------------------------------------------------------------------
#  CHECK EXISTING CERTS
# ------------------------------------------------------------------------------
if [ -d "./data/certbot/conf/live/$DOMAIN" ]; then
  echo -e "\033[1;33m⚠️  Certificates already exist for $DOMAIN\033[0m"

  read -p "Recreate certificates? (y/N): " confirm
  if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo -e "\033[0;32m✅ Keeping existing certificates.\033[0m"
    exit 0
  fi

  echo -e "\033[1;33m🗑️  Removing existing certificates...\033[0m"
  docker compose -f production.compose.yml run --rm --entrypoint "\
    rm -rf /etc/letsencrypt/live/$DOMAIN && \
    rm -rf /etc/letsencrypt/archive/$DOMAIN && \
    rm -rf /etc/letsencrypt/renewal/$DOMAIN.conf" certbot
fi

# ------------------------------------------------------------------------------
#  TEMPORARY NGINX FOR ACME CHALLENGE
# ------------------------------------------------------------------------------
echo -e "\033[1;33m🌐 Starting temporary nginx on port 80 for ACME challenge...\033[0m"

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

mkdir -p ./data/certbot/www/.well-known/acme-challenge
echo "test" > ./data/certbot/www/.well-known/acme-challenge/test

docker run --rm -d --name nginx-init \
  -p 80:80 \
  -v /tmp/nginx-init.conf:/etc/nginx/conf.d/default.conf:ro \
  -v "$(pwd)/data/certbot/www:/var/www/certbot" \
  nginx:1.25

echo -e "\033[1;33m📋 Verifying domain accessibility...\033[0m"
sleep 5

if ! curl -fs "http://$DOMAIN/.well-known/acme-challenge/test" > /dev/null 2>&1; then
  echo -e "\033[0;31m❌ Domain $DOMAIN is not accessible via HTTP.\033[0m"
  echo "Check:"
  echo "1. DNS points to this server"
  echo "2. Port 80 is open"
  echo "3. No other service is using port 80"
  docker stop nginx-init
  exit 1
fi

echo -e "\033[0;32m✅ Domain is accessible. Requesting cert via certbot...\033[0m"

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
  echo -e "\033[1;32m🎉 SSL certificates created!\033[0m"
  echo -e "\033[0;36m📁 Location: ./data/certbot/conf/live/$DOMAIN\033[0m"

  echo -e "\033[1;33m📝 Updating production.compose.yml volumes...\033[0m"
  sed -i 's|certbot_conf:/etc/letsencrypt|./data/certbot/conf:/etc/letsencrypt|g' production.compose.yml
  sed -i 's|certbot_www:/var/www/certbot|./data/certbot/www:/var/www/certbot|g' production.compose.yml

  echo -e "\033[0;32m✅ SSL setup complete. Run: make deploy\033[0m"
  echo -e "\033[0;34m🔄 Auto-renewal is configured (12h cycle).\033[0m"
else
  echo -e "\033[0;31m❌ Certificate creation failed.\033[0m"
  echo "Review the output above and try again."
  exit 1
fi
