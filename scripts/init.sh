#!/usr/bin/env bash

set -e

# ------------------------------------------------------------------------------
#  PRECHECK
# ------------------------------------------------------------------------------
if ! command -v gum &> /dev/null; then
  echo "❌ Gum is not installed. Please install it:"
  echo "   https://github.com/charmbracelet/gum#installation"
  echo "💡 Or run the init-plain.sh script for a fallback."
  exit 1
fi

echo "📘 Please read docs/deployment.md before continuing."
echo "🛠️  This script sets up production .env files using secure defaults and your input."
echo ""


# ------------------------------------------------------------------------------
#  UTILITY FUNCTIONS
# ------------------------------------------------------------------------------
generate_secret() {
  openssl rand -hex 64
}
generate_password() {
  openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 40
}


# ------------------------------------------------------------------------------
#  AUTO-GENERATED VALUES
# ------------------------------------------------------------------------------
DJANGO_SECRET_KEY=$(generate_secret)
CELERY_FLOWER_USER=$(generate_secret)
CELERY_FLOWER_PASSWORD=$(generate_secret)


# ------------------------------------------------------------------------------
#  USER INPUT
# ------------------------------------------------------------------------------
ALLOWED_HOSTS=$(gum input --placeholder ".example.com,localhost" --prompt "Enter DJANGO_ALLOWED_HOSTS:")
DJANGO_SERVER_EMAIL=$(gum input --placeholder "alerts@example.com" --prompt "Enter DJANGO_SERVER_EMAIL (leave empty to skip):")
DJANGO_ADMIN_URL=$(gum input --placeholder "admin" --prompt "Enter DJANGO_ADMIN_URL:" --value "admin")
MAILGUN_API_KEY=$(gum input --placeholder "key-..." --prompt "Enter MAILGUN_API_KEY:")
MAILGUN_DOMAIN=$(gum input --placeholder "example.mailgun.org" --prompt "Enter MAILGUN_DOMAIN:")
DJANGO_DEFAULT_FROM_EMAIL=$(gum input --placeholder "noreply@example.com" --prompt "Enter DJANGO_DEFAULT_FROM_EMAIL:")
DJANGO_AWS_ACCESS_KEY_ID=$(gum input --placeholder "AKI..." --prompt "Enter AWS Access Key ID:")
DJANGO_AWS_SECRET_ACCESS_KEY=$(gum input --placeholder "secret..." --prompt "Enter AWS Secret Access Key:")
DJANGO_AWS_STORAGE_BUCKET_NAME=$(gum input --placeholder "bucket-name" --prompt "Enter AWS S3 Bucket Name:")


POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=dj-oidc-provider
POSTGRES_USER=$(generate_password)
POSTGRES_PASSWORD=$(generate_password)
DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"


# ------------------------------------------------------------------------------
#  WRITE FILES
# ------------------------------------------------------------------------------

echo ""
echo "🧩 Rendering .envs/.production/.django..."

DIR=$(dirname "$0")
"$DIR/render_template.sh" "$DIR/templates/.django.template" .envs/.production/.django \
  DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" \
  DJANGO_ALLOWED_HOSTS="$ALLOWED_HOSTS" \
  DJANGO_SERVER_EMAIL="$DJANGO_SERVER_EMAIL" \
  MAILGUN_API_KEY="$MAILGUN_API_KEY" \
  MAILGUN_DOMAIN="$MAILGUN_DOMAIN" \
  DJANGO_DEFAULT_FROM_EMAIL="$DJANGO_DEFAULT_FROM_EMAIL" \
  DJANGO_AWS_ACCESS_KEY_ID="$DJANGO_AWS_ACCESS_KEY_ID" \
  DJANGO_AWS_SECRET_ACCESS_KEY="$DJANGO_AWS_SECRET_ACCESS_KEY" \
  DJANGO_AWS_STORAGE_BUCKET_NAME="$DJANGO_AWS_STORAGE_BUCKET_NAME" \
  CELERY_FLOWER_USER="$CELERY_FLOWER_USER" \
  CELERY_FLOWER_PASSWORD="$CELERY_FLOWER_PASSWORD"


echo "🧩 Rendering .envs/.production/.postgres..."
POSTGRES_ENV_PATH=".envs/.production/.postgres"
cat > "$POSTGRES_ENV_PATH" <<EOF
# PostgreSQL
# ------------------------------------------------------------------------------
POSTGRES_HOST=${POSTGRES_HOST}
POSTGRES_PORT=${POSTGRES_PORT}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

DATABASE_URL=${DATABASE_URL}
EOF


# ------------------------------------------------------------------------------
#  DONE
# ------------------------------------------------------------------------------

echo "📁 Files generated:"
echo "  - .envs/.production/.django"
echo "  - .envs/.production/.postgres"
echo ""
echo "🚀 Next steps:"
echo "  → Run:  make deploy"
echo "  → Then: make migrate"
