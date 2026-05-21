import os
import tempfile

db_path = os.path.join(tempfile.gettempdir(), "linkforge-test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_create_link_and_analytics() -> None:
    with TestClient(app) as client:
        created = client.post("/api/links", json={"original_url": "https://example.com/docs"})
        assert created.status_code == 201
        code = created.json()["code"]

        redirected = client.get(f"/{code}", follow_redirects=False)
        assert redirected.status_code == 307
        assert redirected.headers["location"] == "https://example.com/docs"

        analytics = client.get(f"/api/links/{code}/analytics")
        assert analytics.status_code == 200
        assert analytics.json()["total_clicks"] == 1
