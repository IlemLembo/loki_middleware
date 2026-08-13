"""Top-level package for loki_middleware."""

from .django.middleware import DjangoLokiMiddleware
from .fastapi.middleware import FastapiLokiMiddleware
from .utils import LokiLogger, console_handler, loki_handler, notify_on_telegram

__all__ = [
    "DjangoLokiMiddleware",
    "FastapiLokiMiddleware",
    "LokiLogger",
    "console_handler",
    "loki_handler",
    "notify_on_telegram",
]


def hello() -> str:
    return "Hello from loki-middleware!"
