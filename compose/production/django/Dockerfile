FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG APP_HOME=/app
ARG BUILD_ENVIRONMENT=production

ENV BUILD_ENV=${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

# System deps
RUN apt-get update && apt-get install --no-install-recommends -y \
    gcc \
    wait-for-it \
    netcat-openbsd \
    libpq-dev \
    gettext \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Install Python deps early to leverage caching
COPY ./requirements .
RUN pip install --no-cache-dir -r ${BUILD_ENVIRONMENT}.txt

# Create static/media dirs
RUN mkdir -p /vol/web/static /vol/web/media \
  && mkdir -p /app/staticfiles

# Copy entrypoint/start scripts
COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint && chmod +x /entrypoint

COPY ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start && chmod +x /start

# Copy app code
COPY . ${APP_HOME}

ENTRYPOINT ["/entrypoint"]
