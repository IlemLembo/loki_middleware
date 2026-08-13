# tests/test_django_middleware.py
import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from loki_middleware.django.middleware import DjangoLokiMiddleware  # Adjust import path

# Define a simple view function for testing the middleware response
def sample_view(request):
    return HttpResponse("OK", status=200)

@pytest.fixture
def rf():
    return RequestFactory()

def test_django_middleware_execution(rf):
    # 1. Create a fake request
    request = rf.get("/health")
    
    # 2. Instantiate the middleware with a dummy get_response callable
    middleware = DjangoLokiMiddleware(get_response=sample_view)
    
    # 3. Process request
    response = middleware(request)
    
    # 4. Assert response and behavior
    assert response.status_code == 200
    assert response.content == b"OK"