import os
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
import numpy as np
from backend.core.config import settings

logger = logging.getLogger(__name__)

class BaseVectorStore(ABC):
    """Abstract interface for local vector store implementations."""

    @abstractmethod
    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]], embeddings: np.ndarray) -> None:
        pass

    @abstractmethod
    def search(self, query_embedding: np.ndarray, top_k: int = 4) -> List[Tuple[Dict[str, Any], float]]:
        """Returns list of (metadata, score) pairs."""
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


class FAISSVectorStore(BaseVectorStore):
    """FAISS-based vector store scoped per conversation."""

    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.store_dir = os.path.join(settings.VECTOR_STORE_DIR, conversation_id)
        os.makedirs(self.store_dir, exist_ok=True)
        self.index_file = os.path.join(self.store_dir, "index.faiss")
        self.metadata_file = os.path.join(self.store_dir, "metadata.json")

        self.index = None
        self.metadata_list: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        try:
            import faiss
            if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
                self.index = faiss.read_index(self.index_file)
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    self.metadata_list = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load FAISS index for {self.conversation_id}: {e}")
            self.index = None
            self.metadata_list = []

    def _save(self) -> None:
        try:
            import faiss
            if self.index is not None:
                faiss.write_index(self.index, self.index_file)
                with open(self.metadata_file, "w", encoding="utf-8") as f:
                    json.dump(self.metadata_list, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist FAISS index: {e}")

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]], embeddings: np.ndarray) -> None:
        import faiss
        dim = embeddings.shape[1]

        if self.index is None:
            # Inner product index for cosine similarity of normalized vectors
            self.index = faiss.IndexFlatIP(dim)

        # Ensure float32 and normalized
        emb = embeddings.astype(np.float32)
        faiss.normalize_L2(emb)

        self.index.add(emb)

        for text, meta in zip(texts, metadatas):
            item = dict(meta)
            item["text"] = text
            self.metadata_list.append(item)

        self._save()

    def search(self, query_embedding: np.ndarray, top_k: int = 4) -> List[Tuple[Dict[str, Any], float]]:
        if self.index is None or self.index.ntotal == 0 or not self.metadata_list:
            return []

        import faiss
        q = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(q)

        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(q, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata_list) and idx != -1:
                results.append((self.metadata_list[idx], float(score)))

        return results

    def delete_document(self, document_id: str) -> None:
        """Filter out chunks belonging to document_id and rebuild index."""
        if not self.metadata_list:
            return

        retained = [m for m in self.metadata_list if m.get("document_id") != document_id]
        if len(retained) == len(self.metadata_list):
            return # Document not present

        self.clear()
        if retained:
            from backend.services.rag.embeddings import embedding_service
            texts = [m["text"] for m in retained]
            embeddings = embedding_service.embed_texts(texts)
            self.add_texts(texts, retained, embeddings)

    def clear(self) -> None:
        self.index = None
        self.metadata_list = []
        if os.path.exists(self.index_file):
            try:
                os.remove(self.index_file)
            except Exception:
                pass
        if os.path.exists(self.metadata_file):
            try:
                os.remove(self.metadata_file)
            except Exception:
                pass


class NumpyVectorStore(BaseVectorStore):
    """Pure NumPy vector store fallback (cosine similarity)."""

    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.store_dir = os.path.join(settings.VECTOR_STORE_DIR, conversation_id)
        os.makedirs(self.store_dir, exist_ok=True)
        self.data_file = os.path.join(self.store_dir, "numpy_store.json")
        self.vectors_file = os.path.join(self.store_dir, "numpy_vectors.npy")

        self.metadata_list: List[Dict[str, Any]] = []
        self.vectors: Optional[np.ndarray] = None
        self._load()

    def _load(self) -> None:
        try:
            if os.path.exists(self.data_file) and os.path.exists(self.vectors_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.metadata_list = json.load(f)
                self.vectors = np.load(self.vectors_file)
        except Exception as e:
            logger.warning(f"Failed to load numpy vector store: {e}")
            self.metadata_list = []
            self.vectors = None

    def _save(self) -> None:
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.metadata_list, f, indent=2)
            if self.vectors is not None:
                np.save(self.vectors_file, self.vectors)
        except Exception as e:
            logger.error(f"Failed to save numpy store: {e}")

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]], embeddings: np.ndarray) -> None:
        emb = embeddings.astype(np.float32)
        # Normalize
        norms = np.linalg.norm(emb, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        emb = emb / norms

        if self.vectors is None or len(self.vectors) == 0:
            self.vectors = emb
        else:
            self.vectors = np.vstack([self.vectors, emb])

        for text, meta in zip(texts, metadatas):
            item = dict(meta)
            item["text"] = text
            self.metadata_list.append(item)

        self._save()

    def search(self, query_embedding: np.ndarray, top_k: int = 4) -> List[Tuple[Dict[str, Any], float]]:
        if self.vectors is None or len(self.vectors) == 0 or not self.metadata_list:
            return []

        q = query_embedding.astype(np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm > 0:
            q = q / q_norm

        scores = np.dot(self.vectors, q)
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append((self.metadata_list[idx], float(scores[idx])))
        return results

    def delete_document(self, document_id: str) -> None:
        if not self.metadata_list:
            return
        retained = [(m, v) for m, v in zip(self.metadata_list, self.vectors) if m.get("document_id") != document_id]
        self.clear()
        if retained:
            self.metadata_list = [item[0] for item in retained]
            self.vectors = np.array([item[1] for item in retained])
            self._save()

    def clear(self) -> None:
        self.metadata_list = []
        self.vectors = None
        for p in [self.data_file, self.vectors_file]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass


def get_vector_store(conversation_id: str) -> BaseVectorStore:
    """Factory to retrieve vector store instance, prioritizing FAISS with fallback to Numpy."""
    try:
        import faiss
        return FAISSVectorStore(conversation_id=conversation_id)
    except ImportError:
        logger.info("FAISS not installed, using NumPy vector store fallback.")
        return NumpyVectorStore(conversation_id=conversation_id)

