from flask.testing import FlaskClient


def test_health_check_success(client: FlaskClient) -> None:
    """Ensures the health check endpoint returns 200 OK and expected payload."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert data.get("status") == "ok"
    assert data.get("message") == "The Python 3.14 Flask Container is running"


def test_404_handling(client: FlaskClient) -> None:
    """Ensures that unknown routes are handled securely without exposing stack traces."""
    response = client.get("/invalid-route-that-does-not-exist")
    assert response.status_code == 404
