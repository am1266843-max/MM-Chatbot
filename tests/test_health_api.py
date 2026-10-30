def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded"]
    assert "timestamp" in data

def test_models_endpoint(client):
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) > 0
    # Check default mock model is present
    model_ids = [m["id"] for m in data["models"]]
    assert "mock-model" in model_ids

def test_system_status_endpoint(client):
    response = client.get("/api/settings/status")
    assert response.status_code == 200
    data = response.json()
    assert "backend_status" in data
    assert "database_status" in data
    assert "providers" in data
    assert data["backend_status"] == "Online"

