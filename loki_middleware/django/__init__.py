"""Django middleware for logging request and response data to Loki."""

from .middleware import DjangoLokiMiddleware

__all__ = ["DjangoLokiMiddleware"]
