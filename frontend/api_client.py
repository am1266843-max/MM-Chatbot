import os
import requests
from typing import Dict, Any, List, Optional

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

class APIClient:
    """HTTP client wrapping FastAPI backend endpoints."""

    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip("/")

    def get_health(self) -> Dict[str, Any]:
        try:
            res = requests.get(f"{self.base_url}/health", timeout=5)
            if res.status_code == 200:
                return res.json()
            return {"status": "degraded", "database": "unknown"}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    def get_models(self) -> Dict[str, Any]:
        try:
            res = requests.get(f"{self.base_url}/api/models", timeout=5)
            if res.status_code == 200:
                return res.json()
            return {"models": [], "default_provider": "mock", "default_model": "mock-model"}
        except Exception:
            return {"models": [], "default_provider": "mock", "default_model": "mock-model"}

    def get_languages(self) -> List[Dict[str, Any]]:
        try:
            res = requests.get(f"{self.base_url}/api/audio/languages", timeout=5)
            if res.status_code == 200:
                return res.json().get("languages", [])
            return []
        except Exception:
            return []

    def get_system_status(self) -> Dict[str, Any]:
        try:
            res = requests.get(f"{self.base_url}/api/settings/status", timeout=5)
            if res.status_code == 200:
                return res.json()
            return {}
        except Exception:
            return {}

    def get_conversations(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            params = {}
            if search:
                params["search"] = search
            res = requests.get(f"{self.base_url}/api/conversations", params=params, timeout=5)
            if res.status_code == 200:
                return res.json()
            return []
        except Exception:
            return []

    def create_conversation(self, title: str = "New Conversation", provider: Optional[str] = None, model: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            payload = {"title": title, "model_provider": provider, "model_name": model}
            res = requests.post(f"{self.base_url}/api/conversations", json=payload, timeout=5)
            if res.status_code == 201:
                return res.json()
            return None
        except Exception:
            return None

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        try:
            res = requests.get(f"{self.base_url}/api/conversations/{conversation_id}", timeout=5)
            if res.status_code == 200:
                return res.json()
            return None
        except Exception:
            return None

    def update_conversation(self, conversation_id: str, title: Optional[str] = None, provider: Optional[str] = None, model: Optional[str] = None) -> bool:
        try:
            payload = {}
            if title is not None:
                payload["title"] = title
            if provider is not None:
                payload["model_provider"] = provider
            if model is not None:
                payload["model_name"] = model
            res = requests.patch(f"{self.base_url}/api/conversations/{conversation_id}", json=payload, timeout=5)
            return res.status_code == 200
        except Exception:
            return False

    def delete_conversation(self, conversation_id: str) -> bool:
        try:
            res = requests.delete(f"{self.base_url}/api/conversations/{conversation_id}", timeout=5)
            return res.status_code == 204
        except Exception:
            return False

    def send_chat(self, chat_payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            res = requests.post(f"{self.base_url}/api/chat", json=chat_payload, timeout=60)
            if res.status_code == 200:
                return res.json()
            return {
                "reply": f"⚠️ Error {res.status_code}: {res.text}",
                "model_provider": chat_payload.get("provider", "unknown"),
                "model_name": chat_payload.get("model", "unknown"),
                "citations": [],
                "web_sources": []
            }
        except Exception as e:
            return {
                "reply": f"⚠️ Failed to reach backend API ({e}). Ensure the FastAPI server is running on port 8000.",
                "model_provider": chat_payload.get("provider", "unknown"),
                "model_name": chat_payload.get("model", "unknown"),
                "citations": [],
                "web_sources": []
            }

    def upload_document(self, file_bytes: bytes, filename: str, content_type: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        try:
            files = {"file": (filename, file_bytes, content_type)}
            data = {}
            if conversation_id:
                data["conversation_id"] = conversation_id
            res = requests.post(f"{self.base_url}/api/documents/upload", files=files, data=data, timeout=30)
            return res.json()
        except Exception as e:
            return {"status": "failed", "message": str(e), "chunk_count": 0}

    def get_documents(self, conversation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            params = {}
            if conversation_id:
                params["conversation_id"] = conversation_id
            res = requests.get(f"{self.base_url}/api/documents", params=params, timeout=5)
            if res.status_code == 200:
                return res.json()
            return []
        except Exception:
            return []

    def delete_document(self, document_id: str) -> bool:
        try:
            res = requests.delete(f"{self.base_url}/api/documents/{document_id}", timeout=5)
            return res.status_code == 204
        except Exception:
            return False

    def transcribe_audio(self, audio_bytes: bytes, filename: str = "audio.wav", language: str = "auto") -> Dict[str, Any]:
        try:
            files = {"file": (filename, audio_bytes, "audio/wav")}
            data = {"language": language}
            res = requests.post(f"{self.base_url}/api/audio/transcribe", files=files, data=data, timeout=30)
            if res.status_code == 200:
                return res.json()
            return {"success": False, "text": "", "error": res.text}
        except Exception as e:
            return {"success": False, "text": "", "error": str(e)}

    def synthesize_audio(
        self,
        text: str,
        voice: Optional[str] = None,
        language: str = "auto",
        gender: str = "female"
    ) -> Dict[str, Any]:
        try:
            payload = {
                "text": text,
                "voice": voice,
                "language": language,
                "gender": gender
            }
            res = requests.post(f"{self.base_url}/api/audio/synthesize", json=payload, timeout=25)
            if res.status_code == 200:
                return res.json()
            return {"success": False, "error": res.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

api_client = APIClient()
