from fastapi.testclient import TestClient

from api.main import app


def test_metrics_endpoint_exposes_http_metrics():
    client = TestClient(app)
    client.get("/instruments/1")  # generate at least one request before scraping
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "# HELP" in resp.text
    assert "http_request" in resp.text
