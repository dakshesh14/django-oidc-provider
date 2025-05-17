# djanog-sso-backend

## Setup - Local

### Install dependencies

```bash
pip install -r requirements/local.txt # in production -> requirements/production.txt
```

### Configure pre-commit

```bash
pre-commit install
```

### Configure environment variables

```bash
cp .env.example .env
```

### Run migrations

```bash
python manage.py migrate
```

### Run server

```bash
python manage.py runserver
```

## Setup

- Celery

```bash
celery -A config.celery_app worker -l info
celery -A config.celery_app worker -l info -P solo # for windows
```
