# tests/test_django_middleware.py
import django
from django.conf import settings


def pytest_configure():
    """Minimal Django configuration required for middleware testing."""
    if not settings.configured:
        settings.configure(
            SECRET_KEY="test-secret-key-for-loki-middleware",
            DEBUG=True,
            ALLOWED_HOSTS=["*"],
            ROOT_URLCONF=__name__,
            MIDDLEWARE=[
                "loki_middleware.django.DjangoLokiMiddleware",
            ],
            DATABASES={},
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
            ],
        )
        django.setup()
