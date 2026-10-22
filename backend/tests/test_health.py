from fastapi.testclient import TestClient

from trendbaker.api.main import app

client = TestClient(app)


def test_health_returns_healthy_status():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
