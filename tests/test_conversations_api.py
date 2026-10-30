def test_create_and_get_conversation(client):
    # 1. Create
    res = client.post("/api/conversations", json={"title": "Project Planning", "model_provider": "mock", "model_name": "mock-model"})
    assert res.status_code == 201
    created = res.json()
    assert created["title"] == "Project Planning"
    conv_id = created["id"]

    # 2. Get
    res_get = client.get(f"/api/conversations/{conv_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == conv_id

def test_update_conversation_title(client):
    res = client.post("/api/conversations", json={"title": "Old Name"})
    conv_id = res.json()["id"]

    res_patch = client.patch(f"/api/conversations/{conv_id}", json={"title": "Updated Title"})
    assert res_patch.status_code == 200
    assert res_patch.json()["title"] == "Updated Title"

def test_delete_conversation(client):
    res = client.post("/api/conversations", json={"title": "To Delete"})
    conv_id = res.json()["id"]

    res_del = client.delete(f"/api/conversations/{conv_id}")
    assert res_del.status_code == 204

    # Verify not found
    res_check = client.get(f"/api/conversations/{conv_id}")
    assert res_check.status_code == 404

def test_export_conversation(client):
    # Create conversation and send a chat message
    res = client.post("/api/chat", json={"message": "Hello Nexus Assistant!"})
    assert res.status_code == 200
    conv_id = res.json()["conversation_id"]

    # Export markdown
    res_export = client.get(f"/api/conversations/{conv_id}/export?format=markdown")
    assert res_export.status_code == 200
    assert "text/markdown" in res_export.headers.get("content-type", "")
    assert "Hello Nexus Assistant!" in res_export.text

def test_multilingual_hindi_chat(client):
    # Test chat in Hindi
    res = client.post("/api/chat", json={
        "message": "नमस्ते, आप कौन हैं?",
        "language": "hi",
        "auto_speak": False
    })
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert "नमस्ते" in data["reply"] or "सहायक" in data["reply"]
    assert data["language"] == "hi"
