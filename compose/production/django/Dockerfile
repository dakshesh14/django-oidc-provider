FROM python:3.11-slim AS python

FROM python AS python-build-stage

ARG BUILD_ENVIRONMENT=production

RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg dependencies
  libpq-dev

COPY ./requirements .

# Create Python Dependency and Sub-Dependency Wheels.
RUN pip wheel --wheel-dir /usr/src/app/wheels -r ${BUILD_ENVIRONMENT}.txt

FROM python AS python-run-stage

ARG BUILD_ENVIRONMENT=production
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV BUILD_ENV=${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

RUN addgroup --system django \
  && adduser --system --ingroup django django


RUN apt-get update && apt-get install --no-install-recommends -y \
  libpq5 \
  curl \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
  && rm -rf /wheels/


COPY --chown=django:django ./compose/production/django/start.sh /start.sh
COPY --chown=django:django ./compose/production/django/start-celeryworker.sh /start-celeryworker.sh
COPY --chown=django:django ./compose/production/django/start-celerybeat.sh /start-celerybeat.sh
COPY --chown=django:django ./compose/production/django/start-celeryflower.sh /start-celeryflower.sh

RUN chmod +x /start.sh /start-celeryworker.sh /start-celerybeat.sh /start-celeryflower.sh \
    && sed -i 's/\r$//g' /start.sh /start-celeryworker.sh /start-celerybeat.sh /start-celeryflower.sh


COPY --chown=django:django . ${APP_HOME}

USER django

CMD ["/start.sh"]
