import os
import tempfile
import numpy as np
from backend.core.security import sanitize_filename, validate_file_extension
from backend.services.documents.parser import DocumentParser
from backend.services.documents.chunker import DocumentChunker
from backend.services.rag.vector_store import NumpyVectorStore

def test_security_filename_sanitization():
    unsafe_name = "../../../etc/passwd"
    clean = sanitize_filename(unsafe_name)
    assert "/" not in clean
    assert "\\" not in clean
    assert ".." not in clean

def test_file_extension_validation():
    assert validate_file_extension("report.pdf") is True
    assert validate_file_extension("notes.txt") is True
    assert validate_file_extension("data.csv") is True
    assert validate_file_extension("slides.pptx") is True
    assert validate_file_extension("document.docx") is True
    assert validate_file_extension("malicious.exe") is False
    assert validate_file_extension("script.sh") is False

def test_plain_text_parser():
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("Line 1: Artificial intelligence.\nLine 2: Machine learning concepts.")
        tmp_path = f.name

    try:
        sections = DocumentParser.parse_file(tmp_path, "sample.txt")
        assert len(sections) == 1
        assert "Artificial intelligence" in sections[0]["text"]
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def test_csv_parser():
    with tempfile.NamedTemporaryFile("w+", suffix=".csv", delete=False, encoding="utf-8") as f:
        f.write("Name,Age,Role\nAlice,30,Engineer\nBob,25,Designer")
        tmp_path = f.name

    try:
        sections = DocumentParser.parse_file(tmp_path, "users.csv")
        assert len(sections) == 1
        assert "Alice" in sections[0]["text"]
        assert "Designer" in sections[0]["text"]
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def test_document_chunker():
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    long_text = "This is a sentence. " * 20 # 400 chars
    sections = [{"text": long_text, "page_number": 1, "section_title": "Section A"}]

    chunks = chunker.chunk_sections(sections)
    assert len(chunks) > 1
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["section_title"] == "Section A"

def test_vector_store_isolation():
    # Test that conversation A's vector store does not return conversation B's documents
    store_a = NumpyVectorStore(conversation_id="conv_a")
    store_b = NumpyVectorStore(conversation_id="conv_b")

    store_a.clear()
    store_b.clear()

    # Add text to conv_a
    emb_a = np.ones((1, 384), dtype=np.float32)
    store_a.add_texts(["Document A text about quantum physics"], [{"document_id": "doc_1", "document_name": "DocA.pdf"}], emb_a)

    # Search conv_b with identical query
    query_emb = np.ones(384, dtype=np.float32)
    res_b = store_b.search(query_emb, top_k=2)
    assert len(res_b) == 0 # Clean isolation!

    # Search conv_a
    res_a = store_a.search(query_emb, top_k=2)
    assert len(res_a) == 1
    assert res_a[0][0]["document_name"] == "DocA.pdf"

    # Clean up
    store_a.clear()
    store_b.clear()

def test_document_upload_api_and_rag(client):
    # Test uploading a document via the API
    sample_content = b"Quantum entanglement is a phenomenon where particles remain connected regardless of distance."
    response = client.post(
        "/api/documents/upload",
        files={"file": ("quantum.txt", sample_content, "text/plain")}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "processed"
    assert data["chunk_count"] >= 1
    doc_id = data["document_id"]

    # Test listing documents
    list_res = client.get("/api/documents")
    assert list_res.status_code == 200
    docs = list_res.json()
    assert any(d["id"] == doc_id for d in docs)

    # Test deleting the document
    del_res = client.delete(f"/api/documents/{doc_id}")
    assert del_res.status_code == 204


