import logging
from unittest.mock import patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from loki_middleware.fastapi.middleware import FastapiLokiMiddleware


@pytest.fixture(autouse=True)
def mock_external_services():
    """Empêche toute tentative de connexion HTTP réelle vers Loki ou Telegram."""
    with patch("logging_loki.LokiHandler.emit"), \
         patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        yield


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()

    # Ajout du middleware
    app.add_middleware(
        FastapiLokiMiddleware,
        exclude_paths=[],  # Exclut le chemin /ping du logging
    )

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"message": "pong"}

    @app.get("/error")
    def raise_error() -> None:
        raise HTTPException(status_code=400, detail="Bad Request")

    @app.get("/server-error")
    def raise_server_error() -> None:
        raise RuntimeError("Internal Server Error")

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    # On désactive raise_server_exceptions pour vérifier la gestion des erreurs 500 par le middleware
    return TestClient(app, raise_server_exceptions=False)


def test_successful_request(client: TestClient) -> None:
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_request_id_header_generated(client: TestClient) -> None:
    response = client.get("/ping")
    print(response.headers)
    assert response.status_code == 200
    assert "x-api-request-id" in response.headers or "X-API-Request-ID" in response.headers

def test_loki_accessibility_on_ping(client: TestClient, caplog) -> None:
    # Capturer les logs de niveau INFO
    with caplog.at_level(logging.INFO):
        response = client.get("/ping")
        
        # 1. Vérifier que la route répond correctement
        assert response.status_code == 200
        
        # 2. S'assurer que le message de succès Loki est présent dans les logs capturés
        assert "Loki est accessible et prêt à recevoir les logs" in caplog.text

def test_http_exception_handling(client: TestClient) -> None:
    response = client.get("/error")
    assert response.status_code == 400


def test_unhandled_exception_handling(client: TestClient) -> None:
    response = client.get("/server-error")
    assert response.status_code == 500