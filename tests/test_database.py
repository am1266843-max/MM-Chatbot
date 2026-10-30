import uuid
from backend.models.conversation import Conversation
from backend.models.message import Message
from backend.models.document import Document, DocumentChunk
from backend.models.setting import Setting

def test_create_conversation_model(db_session):
    conv = Conversation(title="Test Conversation", model_provider="mock", model_name="mock-model")
    db_session.add(conv)
    db_session.commit()

    retrieved = db_session.query(Conversation).filter(Conversation.id == conv.id).first()
    assert retrieved is not None
    assert retrieved.title == "Test Conversation"
    assert retrieved.model_provider == "mock"

def test_cascade_delete_messages(db_session):
    conv = Conversation(title="Delete Cascade Test")
    db_session.add(conv)
    db_session.commit()

    msg1 = Message(conversation_id=conv.id, role="user", content="Hello")
    msg2 = Message(conversation_id=conv.id, role="assistant", content="Hi there!")
    db_session.add_all([msg1, msg2])
    db_session.commit()

    assert len(conv.messages) == 2

    # Delete conversation
    db_session.delete(conv)
    db_session.commit()

    remaining_msgs = db_session.query(Message).filter(Message.conversation_id == conv.id).all()
    assert len(remaining_msgs) == 0

def test_document_and_chunks(db_session):
    doc = Document(
        original_filename="sample.txt",
        stored_filename="uuid_sample.txt",
        file_path="/tmp/uuid_sample.txt",
        mime_type="text/plain",
        file_size=1024,
        processing_status="processed"
    )
    db_session.add(doc)
    db_session.commit()

    chunk1 = DocumentChunk(document_id=doc.id, chunk_index=0, extracted_text="Chunk one", page_number=1)
    chunk2 = DocumentChunk(document_id=doc.id, chunk_index=1, extracted_text="Chunk two", page_number=1)
    db_session.add_all([chunk1, chunk2])
    db_session.commit()

    assert len(doc.chunks) == 2
    assert doc.chunks[0].extracted_text == "Chunk one"

def test_setting_model(db_session):
    s = Setting(setting_key="test_theme", setting_value="dark")
    db_session.add(s)
    db_session.commit()

    found = db_session.query(Setting).filter(Setting.setting_key == "test_theme").first()
    assert found is not None
    assert found.setting_value == "dark"

