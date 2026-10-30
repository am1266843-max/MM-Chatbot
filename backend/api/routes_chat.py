import base64
import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.config import settings
from backend.core.languages import (
    SUPPORTED_LANGUAGES,
    detect_text_language,
    get_voice_for_language
)
from backend.models.conversation import Conversation
from backend.models.message import Message
from backend.schemas.chat import ChatRequest, ChatResponse, Citation, WebSearchSource
from backend.services.ai.provider_factory import get_ai_provider
from backend.services.rag.rag_service import rag_service
from backend.services.search.search_service import search_service
from backend.services.audio.audio_service import audio_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Multimodal & Multilingual chat endpoint supporting:
    - Text chat with persistent conversation memory
    - Multilingual conversation (Hindi, English, Spanish, French, German, etc.)
    - Direct Voice Assistance with optional auto-speech synthesis
    - Image understanding via vision models
    - RAG document retrieval scoped to the conversation
    - Real-time web search integration
    - Structured output formats
    """
    # 1. Resolve or create conversation
    conv_id = payload.conversation_id
    if conv_id:
        conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Generate initial title from first user message
        title_summary = payload.message.strip().split("\n")[0][:45]
        if len(payload.message.strip()) > 45:
            title_summary += "..."
        conv = Conversation(
            title=title_summary or "New Conversation",
            model_provider=payload.provider or settings.AI_PROVIDER,
            model_name=payload.model or settings.AI_MODEL
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conv_id = conv.id

    # 2. Save User Message
    user_metadata: Dict[str, Any] = {}
    image_bytes: Optional[bytes] = None

    if payload.image_base64:
        try:
            image_bytes = base64.b64decode(payload.image_base64)
            user_metadata["has_image"] = True
            user_metadata["image_mime"] = payload.image_mime_type or "image/jpeg"
            user_metadata["image_size_bytes"] = len(image_bytes)
        except Exception as e:
            logger.warning(f"Failed to decode image base64: {e}")

    # Detect user's input language
    user_detected_lang = detect_text_language(payload.message)
    target_lang = payload.language or "auto"
    effective_lang = user_detected_lang if target_lang == "auto" else target_lang

    user_metadata["detected_language"] = user_detected_lang
    user_metadata["target_language"] = target_lang

    user_msg = Message(
        conversation_id=conv_id,
        role="user",
        content=payload.message,
        status="completed"
    )
    user_msg.metadata_dict = user_metadata
    db.add(user_msg)
    db.commit()

    # 3. Context Retrieval (RAG)
    citations: List[Citation] = []
    rag_context = ""
    if payload.use_rag:
        try:
            rag_context, citations = rag_service.retrieve_context(
                query=payload.message,
                conversation_id=conv_id
            )
        except Exception as e:
            logger.warning(f"RAG retrieval encountered an error: {e}")

    # 4. Web Search
    web_sources: List[WebSearchSource] = []
    web_context = ""
    if payload.use_web_search:
        try:
            search_res = await search_service.search(query=payload.message, max_results=4)
            if search_res.results:
                formatted_search = []
                for idx, r in enumerate(search_res.results):
                    source_item = WebSearchSource(
                        title=r.title,
                        url=r.url,
                        snippet=r.snippet,
                        published_date=r.published_date
                    )
                    web_sources.append(source_item)
                    formatted_search.append(f"[{idx+1}] \"{r.title}\" ({r.url})\n{r.snippet}")
                web_context = "\n\n".join(formatted_search)
        except Exception as e:
            logger.warning(f"Web search error: {e}")

    # 5. Build Multilingual System Prompt & Instructions
    system_instructions = [
        "You are a helpful, courteous, and highly intelligent Multimodal AI Voice Assistant.",
        "You answer clearly with proper Markdown formatting, tables, lists, and code blocks."
    ]

    # Multilingual instruction injection
    if target_lang == "hi":
        system_instructions.append(
            "\n### LANGUAGE INSTRUCTION: HINDI (हिन्दी)\n"
            "You MUST respond fluently and naturally in Hindi (हिन्दी) using clean Devanagari script. "
            "Maintain a polite, helpful, and culturally respectful tone."
        )
    elif target_lang == "hi-en":
        system_instructions.append(
            "\n### LANGUAGE INSTRUCTION: HINGLISH\n"
            "You MUST respond in conversational Hinglish (Hindi written in English alphabet with natural mixing, "
            "e.g., 'Aap kaise hain? Mai aapki poori madad kar sakta hu')."
        )
    elif target_lang in SUPPORTED_LANGUAGES and target_lang != "auto":
        lang_name = SUPPORTED_LANGUAGES[target_lang]["name"]
        system_instructions.append(
            f"\n### LANGUAGE INSTRUCTION: {lang_name.upper()}\n"
            f"You MUST communicate and respond fluently in {lang_name}."
        )
    else:
        # Auto-detect language instruction
        system_instructions.append(
            "\n### MULTILINGUAL CAPABILITY:\n"
            "You know many languages including Hindi (हिन्दी), English, Hinglish, Spanish, French, German, Japanese, "
            "Bengali, Marathi, Arabic, and more. "
            "Carefully detect the language the user speaks or writes in, and respond in that exact same language naturally."
        )

    if rag_context:
        system_instructions.append(
            "\n### RETRIEVED DOCUMENT CONTEXT (RAG):\n"
            "Use the following excerpts from the user's uploaded documents to answer accurately. "
            "Cite document names and page numbers when available. "
            "If the documents do not contain enough information, state so clearly in the response language.\n\n"
            f"{rag_context}"
        )

    if web_context:
        system_instructions.append(
            "\n### RETRIEVED REAL-TIME WEB SEARCH RESULTS:\n"
            "Use the following recent web search results to provide accurate up-to-date facts. "
            "Distinguish retrieved web information from your general knowledge and cite sources:\n\n"
            f"{web_context}"
        )

    if payload.structured_format:
        fmt = payload.structured_format.lower()
        if fmt == "summary":
            system_instructions.append("\nFORMAT REQUIREMENT: Provide a structured executive summary with key takeaways and bullet points.")
        elif fmt == "checklist":
            system_instructions.append("\nFORMAT REQUIREMENT: Provide an actionable, step-by-step checklist using Markdown checkboxes (- [ ]).")
        elif fmt == "table":
            system_instructions.append("\nFORMAT REQUIREMENT: Format your primary comparison or data response as a clean Markdown table.")
        elif fmt == "json":
            system_instructions.append("\nFORMAT REQUIREMENT: Output strictly valid JSON without extraneous text.")

    final_system_prompt = "\n".join(system_instructions)

    # 6. Load recent conversation history (last 10 messages)
    recent_msgs = db.query(Message).filter(
        Message.conversation_id == conv_id
    ).order_by(Message.created_at.desc()).limit(10).all()
    recent_msgs.reverse()

    history_payload = []
    for m in recent_msgs:
        history_payload.append({
            "role": m.role,
            "content": m.content
        })

    # 7. Execute AI Model Generation
    provider = get_ai_provider(
        provider_name=payload.provider or conv.model_provider,
        model_name=payload.model or conv.model_name
    )

    try:
        reply_text = await provider.generate_response(
            messages=history_payload,
            system_prompt=final_system_prompt,
            image_bytes=image_bytes,
            image_mime_type=payload.image_mime_type,
            temperature=0.7,
            max_tokens=2000
        )
    except ValueError as ve:
        reply_text = f"⚠️ **Configuration / Model Notice:** {str(ve)}"
    except Exception as exc:
        logger.error(f"AI Generation exception: {exc}")
        reply_text = (
            f"⚠️ **Inference Error:** Failed to generate response from `{provider.model_name}`. "
            f"Details: {str(exc)}\n\n"
            f"Please check your API key and connection in the Settings panel."
        )

    # 8. Interactive Voice Assistance: Auto-Synthesis if requested
    audio_b64: Optional[str] = None
    voice_used: Optional[str] = None

    if payload.auto_speak:
        try:
            detected_reply_lang = detect_text_language(reply_text)
            speech_lang = target_lang if target_lang != "auto" else detected_reply_lang
            voice_used = get_voice_for_language(
                speech_lang,
                text=reply_text,
                gender=payload.voice_gender or "female"
            )
            audio_bytes = await audio_service.synthesize_speech(
                reply_text,
                voice=voice_used,
                language=speech_lang,
                gender=payload.voice_gender or "female"
            )
            if audio_bytes:
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        except Exception as e:
            logger.warning(f"Auto-speech synthesis failed: {e}")

    # 9. Save Assistant Message
    assistant_metadata: Dict[str, Any] = {
        "citations": [c.model_dump() for c in citations],
        "web_sources": [s.model_dump() for s in web_sources],
        "provider": payload.provider or conv.model_provider or settings.AI_PROVIDER,
        "model": provider.model_name,
        "language": effective_lang,
        "voice_used": voice_used
    }

    assistant_msg = Message(
        conversation_id=conv_id,
        role="assistant",
        content=reply_text,
        status="completed"
    )
    assistant_msg.metadata_dict = assistant_metadata
    db.add(assistant_msg)

    # Update conversation updated_at
    conv.model_provider = payload.provider or conv.model_provider
    conv.model_name = provider.model_name
    db.commit()
    db.refresh(assistant_msg)

    return ChatResponse(
        conversation_id=conv_id,
        message_id=assistant_msg.id,
        reply=reply_text,
        model_provider=assistant_metadata["provider"],
        model_name=provider.model_name,
        language=effective_lang,
        audio_base64=audio_b64,
        voice_used=voice_used,
        citations=citations,
        web_sources=web_sources
    )
