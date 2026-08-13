import logging
import os
import sys

from logging_loki import LokiHandler

loki_url = os.getenv("LOKI_URL")

console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)


# LokiHandler personnalisé pour envoyer les logs à Loki
# Créer le handler Loki
loki_handler = LokiHandler(
    url=loki_url,
    tags={
        "application": os.getenv("LOKI_APPLICATION", "app"),
        "environment": os.getenv("LOKI_ENVIRONMENT", "development"),
        "service": os.getenv("LOKI_SERVICE", "backend"),
    },
    version="1",
)
loki_handler.setLevel(logging.INFO)
