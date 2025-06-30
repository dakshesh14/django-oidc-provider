import secrets

from django.core.cache import cache


def generate_email_verification_token(user_id):
    """Generate a new email verification token and store it in Redis"""
    token = secrets.token_urlsafe(32)
    cache_key = f"email_verification:{token}"

    cache.set(cache_key, user_id, timeout=24 * 60 * 60)

    return token


def verify_email_token(token):
    """Verify email verification token and return user_id if valid"""
    cache_key = f"email_verification:{token}"
    user_id = cache.get(cache_key)

    if user_id:
        cache.delete(cache_key)
        return user_id

    return None
