# Getting Started

This guide will help you set up the Django OIDC Provider quickly on your local machine. This is not a production setup guide, but rather a development environment setup to get you started with the project.

## Prerequisites

- Python 3.11 (check runtime.txt for specific version)
- Git
- Docker and Docker Compose (recommended)
- PostgreSQL (if not using Docker)
- Redis (if not using Docker)

## Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/<your_username>/django-oidc-provider.git
cd django-oidc-provider
```

### 2. Environment Setup using Docker Compose

I prefer to use Docker Compose for local development as it simplifies the setup process by managing dependencies like PostgreSQL, Redis, and MailHog. However, you can also set up the environment manually if you prefer.

Note: The main Django application is not running in Docker, but the dependencies such as PostgreSQL, Redis, and MailHog are managed through Docker Compose.

##### 1. Start the required services:

```bash
docker compose -f compose/dev.yml up -d
```

This will start:

- PostgreSQL database
- Redis cache
- MailHog (for email testing)
- Flower (Celery monitoring)

##### 2. Install Python dependencies:

```bash
pip install -r requirements/local.txt
```

##### 3. Set up environment variables:

```bash
cp .env.example .env
```

If you are using Docker you will only need to DATABASE_URL for project to run.

```bash
DATABASE_URL=postgres://postgres:123@localhost:5432/dj-oidc-provider
```

### 3. Database Setup

Apply database migrations:

```bash
python manage.py migrate
```

### 4. Create a Superuser

Create an admin user to manage applications:

```bash
python manage.py createsuperuser
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

The server will be available at `http://127.0.0.1:8000/`

### 6. Start Celery Worker (Optional)

For background email processing:

```bash
# In a separate terminal
celery -A config.celery_app worker -l info

# On Windows:
celery -A config.celery_app worker -l info -P solo
```

## Configure Pre-commit Hooks (Optional)

```bash
pre-commit install
```

## Verify Installation

1. Visit `http://127.0.0.1:8000/admin/` and log in with your superuser credentials
2. Go to "Users" → "Applications" to create your first OAuth2 application
3. Visit `http://127.0.0.1:8000/users/register/` to test user registration

## Service URLs

The following services are available:

- **Django App**: http://127.0.0.1:8000/
- **Django Admin**: http://127.0.0.1:8000/admin/
- **MailHog Web UI**: http://127.0.0.1:8025/
- **Flower (Celery)**: http://127.0.0.1:5555/ (user: `flower`, password: `123`)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Next Steps

- [Create your first OAuth2 application](applications.md)
- [Learn about the SSO flow](sso-flow.md)
- [Explore the API endpoints](api/endpoints.md)
- [Set up for development](development.md)

For more detailed development setup, see the [Development Guide](development.md).
