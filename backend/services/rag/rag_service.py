import logging
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.models.document import Document, DocumentChunk
from backend.services.documents.parser import DocumentParser
from backend.services.documents.chunker import DocumentChunker
from backend.services.rag.embeddings import embedding_service
from backend.services.rag.vector_store import get_vector_store
from backend.schemas.chat import Citation

logger = logging.getLogger(__name__)

class RAGService:
    """Manages document indexing, vector storage, and scoped context retrieval."""

    def __init__(self):
        self.chunker = DocumentChunker(chunk_size=750, chunk_overlap=120)

    def process_and_index_document(self, document_id: str, db: Session) -> int:
        """
        Parses an uploaded document, chunks it, generates embeddings,
        saves chunks to DB and indexes in the conversation-scoped vector store.
        """
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document with ID {document_id} not found.")

        try:
            # 1. Parse file into pages/sections
            sections = DocumentParser.parse_file(doc.file_path, doc.original_filename)

            # 2. Split into overlapping chunks
            chunks_data = self.chunker.chunk_sections(sections)
            if not chunks_data:
                raise ValueError("No extractable text found in document.")

            # 3. Clean up any existing chunks in DB for this document
            db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()

            # 4. Save new chunks to DB
            db_chunks = []
            texts_to_embed = []
            metadatas = []

            for item in chunks_data:
                chunk_obj = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=item["chunk_index"],
                    extracted_text=item["text"],
                    page_number=item.get("page_number"),
                    section_title=item.get("section_title")
                )
                db.add(chunk_obj)
                db_chunks.append(chunk_obj)
                texts_to_embed.append(item["text"])

                metadatas.append({
                    "document_id": doc.id,
                    "document_name": doc.original_filename,
                    "chunk_index": item["chunk_index"],
                    "page_number": item.get("page_number"),
                    "section_title": item.get("section_title")
                })

            db.commit()

            # 5. Generate embeddings and store in conversation vector store
            conv_id = doc.conversation_id or "global"
            store = get_vector_store(conversation_id=conv_id)

            embeddings = embedding_service.embed_texts(texts_to_embed)
            store.add_texts(texts_to_embed, metadatas, embeddings)

            # Update document status
            doc.processing_status = "processed"
            doc.chunk_count = len(db_chunks)
            doc.error_message = None
            db.commit()

            return len(db_chunks)

        except Exception as e:
            logger.error(f"Failed to process and index document {document_id}: {e}")
            doc.processing_status = "failed"
            doc.error_message = str(e)
            db.commit()
            raise

    def retrieve_context(
        self,
        query: str,
        conversation_id: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> Tuple[str, List[Citation]]:
        """
        Retrieves relevant document chunks scoped strictly to the given conversation_id.
        Returns formatted context string and list of Citation objects.
        """
        k = top_k or settings.RAG_TOP_K
        threshold = score_threshold or settings.RAG_SCORE_THRESHOLD

        store = get_vector_store(conversation_id=conversation_id)
        query_emb = embedding_service.embed_query(query)

        search_results = store.search(query_emb, top_k=k)
        citations: List[Citation] = []
        context_snippets: List[str] = []

        for meta, score in search_results:
            if score >= threshold:
                doc_name = meta.get("document_name", "Unknown Document")
                page = meta.get("page_number")
                sec = meta.get("section_title")
                text = meta.get("text", "")

                citations.append(Citation(
                    document_name=doc_name,
                    page_number=page,
                    section_title=sec,
                    snippet=text[:250] + ("..." if len(text) > 250 else ""),
                    score=round(score, 3)
                ))

                loc_info = f" (Page {page})" if page else ""
                context_snippets.append(f"--- Source: {doc_name}{loc_info} ---\n{text}")

        context_str = "\n\n".join(context_snippets)
        return context_str, citations

    def remove_document_index(self, document_id: str, conversation_id: str) -> None:
        """Removes a document from the vector store."""
        store = get_vector_store(conversation_id=conversation_id)
        store.delete_document(document_id=document_id)

rag_service = RAGService()

