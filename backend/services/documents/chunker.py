from typing import List, Dict, Any

class DocumentChunker:
    """Splits document text into overlapping chunks while preserving metadata."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes raw parsed sections and returns chunks:
        [{
            "chunk_index": int,
            "text": str,
            "page_number": Optional[int],
            "section_title": Optional[str]
        }]
        """
        chunks = []
        global_index = 0

        for section in sections:
            text = section.get("text", "").strip()
            page_number = section.get("page_number")
            section_title = section.get("section_title")

            if not text:
                continue

            # If text is smaller than chunk size, take as single chunk
            if len(text) <= self.chunk_size:
                chunks.append({
                    "chunk_index": global_index,
                    "text": text,
                    "page_number": page_number,
                    "section_title": section_title
                })
                global_index += 1
                continue

            # Split with overlap
            start = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))

                # Try to break at a natural boundary (newline or period or space)
                if end < len(text):
                    last_break = max(
                        text.rfind("\n", start + self.chunk_overlap, end),
                        text.rfind(". ", start + self.chunk_overlap, end),
                        text.rfind(" ", start + self.chunk_overlap, end)
                    )
                    if last_break != -1 and last_break > start:
                        end = last_break + 1

                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunks.append({
                        "chunk_index": global_index,
                        "text": chunk_text,
                        "page_number": page_number,
                        "section_title": section_title
                    })
                    global_index += 1

                if end >= len(text):
                    break

                start += max(1, self.chunk_size - self.chunk_overlap)

        return chunks

