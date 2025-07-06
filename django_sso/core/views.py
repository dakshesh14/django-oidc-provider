import time

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods


# TODO: find a way to secure this endpoint, as it is currently open to the public.
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

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        services["database"] = "healthy"
    except Exception as e:
        services["database"] = f"unhealthy: {str(e)}"
        overall_status = "unhealthy"
        status_code = 503

    # Check cache connection
    try:
        cache_key = f"health_check_{time.time()}"
        cache.set(cache_key, "test", 30)
        cache.get(cache_key)
        cache.delete(cache_key)
        services["cache"] = "healthy"
    except Exception as e:
        services["cache"] = f"unhealthy: {str(e)}"
        overall_status = "unhealthy"
        status_code = 503

    response_data = {
        "status": overall_status,
        "services": services,
        "timestamp": time.time(),
    }

    return JsonResponse(response_data, status=status_code)
