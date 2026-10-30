import os
import uuid
import shutil
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import get_db
from backend.core.security import sanitize_filename, validate_file_extension
from backend.models.document import Document
from backend.models.conversation import Conversation
from backend.schemas.document import DocumentRead, DocumentUploadResponse
from backend.services.rag.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a document (PDF, DOCX, PPTX, CSV, TXT, MD), validate,
    extract text, generate embeddings, and index into the conversation-scoped vector store.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")

    # Validate extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: PDF, DOCX, PPTX, CSV, TXT, MD, Images."
        )

    # Check conversation exists if provided
    if conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

    clean_filename = sanitize_filename(file.filename)
    unique_id = str(uuid.uuid4())
    stored_name = f"{unique_id}_{clean_filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, stored_name)

    # Read and validate file size
    try:
        content = await file.read()
        file_size = len(content)
        max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024

        if file_size > max_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_MB} MB."
            )

        with open(file_path, "wb") as f:
            f.write(content)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail=f"File storage error: {str(e)}")

    # Create Document record
    doc = Document(
        id=unique_id,
        conversation_id=conversation_id,
        original_filename=clean_filename,
        stored_filename=stored_name,
        file_path=file_path,
        mime_type=file.content_type or "application/octet-stream",
        file_size=file_size,
        processing_status="pending"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Process and index
    try:
        chunk_count = rag_service.process_and_index_document(doc.id, db)
        return DocumentUploadResponse(
            document_id=doc.id,
            filename=clean_filename,
            file_size=file_size,
            status="processed",
            chunk_count=chunk_count,
            message=f"Successfully extracted {chunk_count} chunk(s) and indexed into vector search."
        )
    except Exception as e:
        logger.error(f"Indexing failed for {doc.id}: {e}")
        return DocumentUploadResponse(
            document_id=doc.id,
            filename=clean_filename,
            file_size=file_size,
            status="failed",
            chunk_count=0,
            message=f"Text extraction / vector indexing failed: {str(e)}"
        )

@router.get("", response_model=List[DocumentRead])
def list_documents(
    conversation_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List uploaded documents, optionally filtered by conversation_id."""
    query = db.query(Document)
    if conversation_id:
        query = query.filter(Document.conversation_id == conversation_id)
    return query.order_by(Document.created_at.desc()).all()

@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Delete document from disk, remove from vector store, and delete DB record."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    conv_id = doc.conversation_id or "global"
    rag_service.remove_document_index(document_id=doc.id, conversation_id=conv_id)

    # Delete disk file
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            logger.warning(f"Could not delete physical file: {e}")

    db.delete(doc)
    db.commit()
    return None

@router.post("/{document_id}/reindex", response_model=DocumentUploadResponse)
def reindex_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Re-run text parsing and rebuild embeddings for a document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        chunk_count = rag_service.process_and_index_document(doc.id, db)
        return DocumentUploadResponse(
            document_id=doc.id,
            filename=doc.original_filename,
            file_size=doc.file_size,
            status="processed",
            chunk_count=chunk_count,
            message=f"Successfully reindexed {chunk_count} chunk(s)."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindexing failed: {str(e)}")

