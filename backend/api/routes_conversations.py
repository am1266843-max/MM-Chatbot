from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.core.database import get_db
from backend.models.conversation import Conversation
from backend.models.message import Message
from backend.schemas.conversation import (
    ConversationCreate, ConversationUpdate, ConversationRead,
    ConversationListItem, MessageRead
)
from backend.services.rag.vector_store import get_vector_store

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])

@router.get("", response_model=List[ConversationListItem])
def list_conversations(
    search: Optional[str] = Query(None, description="Search query for titles"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve all conversations, sorted newest first, with optional title search."""
    query = db.query(
        Conversation,
        func.count(Message.id).label("message_count")
    ).outerjoin(Message).group_by(Conversation.id).order_by(Conversation.updated_at.desc())

    if search:
        query = query.filter(Conversation.title.ilike(f"%{search}%"))

    results = query.limit(limit).all()

    items = []
    for conv, count in results:
        items.append(ConversationListItem(
            id=conv.id,
            title=conv.title,
            model_provider=conv.model_provider,
            model_name=conv.model_name,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=count
        ))
    return items

@router.post("", response_model=ConversationRead, status_code=201)
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db)
):
    """Create a new conversation session."""
    conv = Conversation(
        title=payload.title or "New Conversation",
        model_provider=payload.model_provider,
        model_name=payload.model_name
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

@router.get("/{conversation_id}", response_model=ConversationRead)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve a single conversation including its message thread."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@router.patch("/{conversation_id}", response_model=ConversationRead)
def update_conversation(
    conversation_id: str,
    payload: ConversationUpdate,
    db: Session = Depends(get_db)
):
    """Update conversation title or model configuration."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if payload.title is not None:
        conv.title = payload.title.strip() or "Untitled Conversation"
    if payload.model_provider is not None:
        conv.model_provider = payload.model_provider
    if payload.model_name is not None:
        conv.model_name = payload.model_name

    db.commit()
    db.refresh(conv)
    return conv

@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Delete a conversation, associated messages, documents, and vector index."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Clear scoped vector store files
    try:
        store = get_vector_store(conversation_id=conversation_id)
        store.clear()
    except Exception:
        pass

    db.delete(conv)
    db.commit()
    return None

@router.get("/{conversation_id}/messages", response_model=List[MessageRead])
def get_conversation_messages(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve all messages in chronological order for a conversation."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv.messages

@router.get("/{conversation_id}/export")
def export_conversation(
    conversation_id: str,
    format: str = Query("markdown", pattern="^(markdown|txt)$"),
    db: Session = Depends(get_db)
):
    """Export conversation transcript as Markdown or plain text."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    lines = [f"# {conv.title}\n", f"*Exported on: {conv.updated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}*\n\n---\n"]

    for msg in conv.messages:
        role_label = "**User**" if msg.role == "user" else "**Assistant**"
        time_str = msg.created_at.strftime('%H:%M:%S')
        lines.append(f"### {role_label} ({time_str})\n")
        lines.append(f"{msg.content}\n\n")

    content = "\n".join(lines)
    media_type = "text/markdown" if format == "markdown" else "text/plain"
    filename = f"conversation_{conversation_id[:8]}.{ 'md' if format == 'markdown' else 'txt' }"

    return PlainTextResponse(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

