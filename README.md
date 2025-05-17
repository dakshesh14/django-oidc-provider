# Django-based OAuth2 and OpenID Connect (OIDC) Identity Provider

A Django implementation of an OAuth2 and OpenID Connect (OIDC) Identity Provider, featuring token issuance, user authentication, and user info endpoints.

https://github.com/user-attachments/assets/ca7f345b-1a28-478a-837d-4244728cde6b

## Setup

1. Clone the repository:

```bash
git clone https://github.com/dakshesh14/django-oidc-provider.git
```

2. Install dependencies:

```bash
pip install -r requirements/local.txt # for production -> requirements/production.txt
```

3. Configure pre-commit hooks:

```bash
pre-commit install
```

4. Environment Setup

   1. Copy and update environment variables if you’re not using Docker Compose:

   ```bash
   cp .env.example .env
   ```

   2. Start services with Docker Compose (optional, but recommended):

   ```bash
   docker compose -f compose/dev.yaml up -d
   ```

5. Apply database migrations:

```bash
python manage.py migrate
```

6. Run the development server:

```bash
python manage.py runserver
```

7. (Optional) Start Celery worker:

```bash
celery -A config.celery_app worker -l info
# for windows:
celery -A config.celery_app worker -l info -P solo
```

## How to create applications

Currently, only public applications (suitable for SPAs) are supported.

1. Create a superuser.
2. Visit http://127.0.0.1:8000/admin.
3. Under the "Users" section in the sidebar, go to "Applications".
4. Click "Add Application".
5. Fill in all the required details.
6. Save the application.
7. Copy the client secret immediately — it is hashed and stored, so you won’t be able to retrieve it later.

Once created, you can use the client ID and client secret in your projects. I might work on adding API docs and improving URL patterns.

![add application page](https://github.com/user-attachments/assets/3fe50a59-742f-4d72-bfc6-0ff3575fc870)

## Future plans

Before using in production, I plan to work on:

- [ ] Fix URL pattern to follow best practices
- [ ] Add discovery endpoints
- [ ] Add JWKS support
- [ ] Improving error handling
- [ ] Add more application types

# Contributing

Contributions are welcome! Feel free to open issues or submit pull requests. Please open an issue first for major changes. You can also help by working on the tasks listed above.

## Acknowledgements

This project would not be possible without the amazing open-source community and resources:

- [Django](https://www.djangoproject.com/)
- [Django REST framework](https://www.django-rest-framework.org/)
- [RFC6749](https://datatracker.ietf.org/doc/html/rfc6749)
- [RFC6750](https://datatracker.ietf.org/doc/html/rfc6750)
- [OpenID Connect Core Spec](https://openid.net/specs/openid-connect-core-1_0.html)

## Conclusion

This project can serve as a solid foundation (or even a ready solution) for building a production-ready Identity Provider. If you find it useful, please consider giving it a star!

To connect or learn more about me, find me here:

- [LinkedIn](https://www.linkedin.com/in/dakshesh-jain/)
- [Twitter](https://twitter.com/_dakshesh)
- [GitHub](https://github.com/dakshesh14)
- [Reddit](https://www.reddit.com/user/_dakshesh/)
- [Portfolio](https://dakshesh.me)
