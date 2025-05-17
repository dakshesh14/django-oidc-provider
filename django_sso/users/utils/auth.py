import json
import secrets

from django.conf import settings
from django.core.cache import cache

# django
from django.utils.timezone import now

# local
from django_sso.users.models import Application, User


def create_and_cache_auth_code(
    user: User,
    client: Application,
    redirect_uri: str,
    scopes: list[str],
    code_length=40,
):
    code = secrets.token_urlsafe(code_length)

    data = {
        "user_id": str(user.id),
        "client_id": str(client.id),
        "redirect_uri": redirect_uri,
        "issued_at": now().isoformat(),
        "scopes": scopes,
        "used": False,
    }

    cache.set(f"auth_code:{code}", json.dumps(data), timeout=settings.AUTH_CODE_TTL)

    return code
