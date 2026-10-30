import base64
import streamlit as st
from typing import Dict, Any, List
from frontend.api_client import api_client

def render_message(msg: Dict[str, Any], idx: int, is_last_message: bool = False):
    """Renders a single chat message with citations, web sources, and voice output."""
    role = msg.get("role", "user")
    content = msg.get("content", "")
    metadata = msg.get("extra_metadata") or {}

    avatar = "🧑‍💻" if role == "user" else "🤖"

    with st.chat_message(role, avatar=avatar):
        # Render image attachment if user message has one
        if metadata.get("has_image") and metadata.get("image_preview_b64"):
            st.image(
                base64.b64decode(metadata["image_preview_b64"]),
                caption="Attached Image",
                use_container_width=False,
                width=320
            )

        # Render message content
        st.markdown(content)

        # Render Citations (RAG)
        citations: List[Dict[str, Any]] = metadata.get("citations", [])
        if citations:
            with st.expander(f"📚 Document Sources ({len(citations)} cited)", expanded=False):
                for c in citations:
                    doc_name = c.get("document_name", "Document")
                    page = f" (Page {c.get('page_number')})" if c.get("page_number") else ""
                    score = f" [Score: {c.get('score')}]" if c.get("score") else ""
                    st.markdown(f"**{doc_name}**{page}{score}")
                    st.caption(f"_{c.get('snippet', '')}_")
                    st.divider()

        # Render Web Search Sources
        web_sources: List[Dict[str, Any]] = metadata.get("web_sources", [])
        if web_sources:
            with st.expander(f"🌐 Web Sources ({len(web_sources)} found)", expanded=False):
                for s in web_sources:
                    title = s.get("title", "Web Link")
                    url = s.get("url", "#")
                    snippet = s.get("snippet", "")
                    st.markdown(f"- [{title}]({url})")
                    if snippet:
                        st.caption(f"_{snippet[:180]}..._")

        # Action bar for Assistant messages
        if role == "assistant":
            col_audio, col_meta = st.columns([0.35, 0.65])

            audio_key = f"audio_{idx}"
            msg_lang = metadata.get("language") or st.session_state.get("selected_language", "auto")
            gender = st.session_state.get("voice_gender", "female")

            # Check if auto_speak provided audio in message metadata
            if metadata.get("audio_base64") and audio_key not in st.session_state:
                st.session_state[audio_key] = metadata["audio_base64"]

            # Text-to-Speech button
            btn_label = "🔊 Read Aloud" if audio_key not in st.session_state else "🔄 Re-play"
            if col_audio.button(btn_label, key=f"tts_btn_{idx}", help="Speak response aloud"):
                with st.spinner("Synthesizing voice..."):
                    res = api_client.synthesize_audio(
                        content,
                        language=msg_lang,
                        gender=gender
                    )
                    if res.get("success") and res.get("audio_base64"):
                        st.session_state[audio_key] = res["audio_base64"]
                        st.rerun()
                    else:
                        st.error(f"Speech failed: {res.get('error', 'Unknown error')}")

            # Audio Player widget
            if audio_key in st.session_state:
                audio_bytes = base64.b64decode(st.session_state[audio_key])
                # Autoplay only if it's the latest assistant message or user just requested it
                should_autoplay = is_last_message and st.session_state.get("auto_speak", False)
                st.audio(audio_bytes, format="audio/mp3", autoplay=should_autoplay)

            # Metadata display
            provider = metadata.get("provider")
            model = metadata.get("model")
            voice_info = metadata.get("voice_used")
            info_parts = []
            if model or provider:
                info_parts.append(f"`{model or provider}`")
            if msg_lang and msg_lang != "auto":
                info_parts.append(f"Lang: **{msg_lang.upper()}**")
            if voice_info:
                info_parts.append(f"Voice: *{voice_info}*")

            if info_parts:
                col_meta.caption(" • ".join(info_parts))
