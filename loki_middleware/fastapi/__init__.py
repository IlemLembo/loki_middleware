"""FastAPI integration for loki_middleware."""

from .middleware import FastapiLokiMiddleware
from .middleware import FastapiLokiMiddleware as LokiLoggingMiddleware

__all__ = ["FastapiLokiMiddleware", "LokiLoggingMiddleware"]