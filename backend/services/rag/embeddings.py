import logging
import numpy as np
from typing import List, Optional
from backend.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Provides vector embeddings using SentenceTransformers with an offline fallback."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model = None
        self._fallback_mode = False

    def _load_model(self):
        if self._model is not None or self._fallback_mode:
            return

        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer '{self.model_name}' ({e}). Falling back to built-in embedding.")
            self._fallback_mode = True

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate normalized vector embeddings for a list of strings."""
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        self._load_model()

        if self._model is not None:
            try:
                embeddings = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
                return np.array(embeddings, dtype=np.float32)
            except Exception as e:
                logger.error(f"Error generating embeddings via model: {e}")

        # Built-in lightweight TF-IDF/Character Hash Fallback (384-dimensional)
        vectors = []
        for text in texts:
            vec = np.zeros(384, dtype=np.float32)
            for idx, word in enumerate(text.lower().split()):
                h = hash(word) % 384
                vec[h] += 1.0 / (idx + 1)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec)

        return np.array(vectors, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single search query."""
        res = self.embed_texts([query])
        return res[0]

# Singleton instance
embedding_service = EmbeddingService()

