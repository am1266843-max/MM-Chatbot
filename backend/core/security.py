import re
import os
from pathlib import Path
from typing import Set

ALLOWED_EXTENSIONS: Set[str] = {
    ".pdf", ".docx", ".pptx", ".txt", ".md", ".csv",
    ".png", ".jpg", ".jpeg", ".webp"
}

ALLOWED_MIME_TYPES: Set[str] = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "text/markdown",
    "text/csv",
    "image/png",
    "image/jpeg",
    "image/webp",
    "audio/wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/webm",
    "audio/ogg"
}

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and invalid characters."""
    # Strip directory components
    clean_name = os.path.basename(filename)
    # Replace non-alphanumeric, dot, underscore, dash with underscore
    clean_name = re.sub(r"[^a-zA-Z0-9._-]", "_", clean_name)
    # Limit filename length
    if len(clean_name) > 100:
        base, ext = os.path.splitext(clean_name)
        clean_name = base[:90] + ext
    return clean_name or "uploaded_file"

def validate_file_extension(filename: str) -> bool:
    """Check if file extension is among allowed types."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def mask_secret(secret: str) -> str:
    """Mask sensitive API keys for safe display in UI or logs."""
    if not secret:
        return "Not Set"
    if len(secret) <= 8:
        return "********"
    return f"{secret[:4]}...{secret[-4:]}"

