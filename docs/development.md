# Development Guide

This guide covers the development workflow, project structure, testing, and code quality practices for the Django OIDC Provider.

## Development Environment Setup

Check the [Getting Started](getting-started.md) guide for initial setup instructions.

## Project Structure

```
django-oidc-provider/
├── config/                 # Django configuration
│   ├── settings/           # Environment-specific settings
│   │   ├── base.py        # Base settings
│   │   ├── local.py       # Development settings
│   │   ├── production.py  # Production settings
│   │   └── test.py        # Test settings
│   ├── urls.py            # Root URL configuration
│   └── celery_app.py      # Celery configuration
├── django_sso/            # Main Django app
│   ├── core/              # Core utilities
│   │   ├── db/           # Database models/utilities
│   │   └── email/        # Email utilities
│   ├── users/             # User management app
│   │   ├── api/          # REST API views
│   │   ├── web/          # Web views (OAuth flow)
│   │   ├── models.py     # User and Application models
│   │   ├── forms.py      # Django forms
│   │   └── utils/        # Authentication utilities
│   ├── templates/         # Django templates
│   ├── static/           # Static files (CSS, JS)
│   └── utils/            # Global utilities
├── requirements/          # Python dependencies
├── compose/              # Docker compose files
└── docs/                 # Documentation
```

## Configuration

### Settings Structure

The project uses environment-specific settings:

- `base.py` - Common settings for all environments
- `local.py` - Development settings (DEBUG=True, local cache)
- `production.py` - Production settings (security, AWS S3, etc.)
- `test.py` - Test settings (in-memory database, etc.)

## Development Workflow

### Running the Development Server

```bash
# Start Django development server
python manage.py runserver

# Start Celery worker (in separate terminal) preferred when testing email functionality
celery -A config.celery_app worker -l info

# Start Celery beat scheduler (if needed)
celery -A config.celery_app beat -l info
```

### Code Quality

The project uses several tools to maintain code quality:

#### Pre-commit Hooks

Configured in `.pre-commit-config.yaml`:

- Black (code formatting)
- isort (import sorting)
- flake8 (linting)
- mypy (type checking)

Run manually:

```bash
pre-commit run --all-files
```

#### Code Formatting

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .
```

### Testing

> Note: I am still working on writing test-cases for the project.

#### Running Tests

```bash
# Run all tests
python manage.py test
```

#### Test Structure

Tests are organized within each app:

```
django_sso/users/tests/
├── __init__.py
├── models/
│   ├── test_user.py
│   └── test_application.py
└── views/
    └── __init__.py
```

#### Writing Tests

I am very open to suggestions for writing tests. Here is a basic example of how to write tests for the `Application` model:

Example test structure:

```python
from django.test import TestCase
from django_sso.users.models import Application

class ApplicationModelTest(TestCase):
    def setUp(self):
        self.app_data = {
            "name": "Test App",
            "redirect_uris": "https://example.com/callback",
            "allowed_scopes": "openid email profile",
        }

    def test_application_creation(self):
        app = Application.objects.create(**self.app_data)
        self.assertTrue(app.client_id)
        self.assertTrue(app.client_secret)
```

## Database Management

### Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Database Schema

Key models:

- `User` - Extended Django user model with email verification
- `Application` - OAuth2/OIDC client applications

## API Development

Go to [API Documentation](api/endpoints.md) for detailed API endpoints.

### Celery Monitoring

Use Flower for Celery monitoring:

- Visit `http://localhost:5555`
- Username: `flower`, Password: `123`

## Contributing

For contribution guidelines, please see the main project repository's CONTRIBUTING.md file.
