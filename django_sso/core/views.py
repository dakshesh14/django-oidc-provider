import time

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.utils.timezone import now
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods


@never_cache
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Returns:
        - 200 OK if all services are healthy
        - 503 Service Unavailable if any service is down
    """
    services = {}
    overall_status = "healthy"
    status_code = 200

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        services["database"] = "healthy"
    except Exception:
        services["database"] = "unhealthy"
        overall_status = "unhealthy"
        status_code = 503

    try:
        cache_key = f"health_check_{int(time.time())}"
        cache.set(cache_key, "test", timeout=30)
        value = cache.get(cache_key)
        cache.delete(cache_key)
        if value == "test":
            services["cache"] = "healthy"
        else:
            raise Exception("Unexpected cache value")
    except Exception:
        services["cache"] = "unhealthy"
        overall_status = "unhealthy"
        status_code = 503

    return JsonResponse(
        {
            "status": overall_status,
            "services": services,
            "timestamp": now().isoformat(),
        },
        status=status_code,
    )
