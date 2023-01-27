from functools import wraps
from rest_framework import status
from rest_framework.response import Response


def check_app_name():
    """Decorator that checks if header app-name were passed in the request."""

    def decorator(function):
        @wraps(function)
        def wrapped(request, *args, **kwargs):
            if not request.headers["app-name"]:
                return Response(
                    "Client not specified.",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return function(request, *args, **kwargs)

        return wrapped

    return decorator


def check_credentials():
    """Decorator that checks if the credentials (email, password) were passed in the request."""

    def decorator(function):
        @wraps(function)
        def wrapped(request, *args, **kwargs):
            if not request.data.get("email") or not request.data.get("password"):
                return Response(
                    "Email or password not specified.",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return function(request, *args, **kwargs)

        return wrapped

    return decorator
