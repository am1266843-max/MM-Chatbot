import base64
import streamlit as st
from frontend.api_client import api_client

def render_attachment_bar():
    """Renders attachment controls: Voice Assistant, Image, and Document input."""
    with st.expander("📎 Voice Assistant, Media & Documents", expanded=False):
        col_voice, col_img, col_doc = st.columns(3)

        # 1. Voice Assistant Input (Speech-to-Text)
        with col_voice:
            active_lang = st.session_state.get("selected_language", "auto")
            lang_label = "हिन्दी" if active_lang == "hi" else "English" if "en" in active_lang else "Multilingual"
            st.markdown(f"**🎙️ Voice Input ({lang_label})**")

            # Check for Streamlit native audio input
            if hasattr(st, "audio_input"):
                audio_val = st.audio_input("Record Voice", key="mic_recorder", label_visibility="collapsed")
                if audio_val:
                    col_t1, col_t2 = st.columns(2)
                    if col_t1.button("🗣️ Transcribe", key="btn_transcribe_voice", use_container_width=True):
                        with st.spinner("Recognizing speech..."):
                            audio_bytes = audio_val.read()
                            res = api_client.transcribe_audio(
                                audio_bytes,
                                filename="voice.wav",
                                language=active_lang
                            )
                            if res.get("success") and res.get("text"):
                                st.session_state["transcribed_input"] = res["text"]
                                st.success("Transcribed! Click Send or edit below.")
                                st.rerun()
                            else:
                                st.error(f"Error: {res.get('error', 'Could not recognize speech')}")

                    if col_t2.button("🚀 Speak & Send", key="btn_speak_and_send", type="primary", use_container_width=True):
                        with st.spinner("Processing speech..."):
                            audio_bytes = audio_val.read()
                            res = api_client.transcribe_audio(
                                audio_bytes,
                                filename="voice.wav",
                                language=active_lang
                            )
                            if res.get("success") and res.get("text"):
                                st.session_state["quick_prompt"] = res["text"]
                                st.rerun()
                            else:
                                st.error(f"Error: {res.get('error', 'Could not recognize speech')}")
            else:
                audio_file = st.file_uploader(
                    "Audio File",
                    type=["wav", "mp3", "ogg"],
                    key="audio_file_uploader",
                    label_visibility="collapsed"
                )
                if audio_file:
                    if st.button("Transcribe Audio", key="btn_transcribe_file"):
                        with st.spinner("Transcribing..."):
                            res = api_client.transcribe_audio(
                                audio_file.read(),
                                filename=audio_file.name,
                                language=active_lang
                            )
                            if res.get("success") and res.get("text"):
                                st.session_state["transcribed_input"] = res["text"]
                                st.success("Transcribed!")
                                st.rerun()
                            else:
                                st.error(f"Error: {res.get('error')}")

        # 2. Image Upload (Multimodal Vision)
        with col_img:
            st.markdown("**🖼️ Image (Vision)**")
            uploaded_img = st.file_uploader(
                "Upload Image",
                type=["png", "jpg", "jpeg", "webp"],
                key="composer_img_uploader",
                label_visibility="collapsed"
            )
            if uploaded_img:
                img_bytes = uploaded_img.read()
                st.session_state["attachment_image"] = {
                    "bytes": img_bytes,
                    "b64": base64.b64encode(img_bytes).decode("utf-8"),
                    "name": uploaded_img.name,
                    "mime": uploaded_img.type
                }
                st.image(img_bytes, width=140, caption="Attached Image")
                if st.button("❌ Remove Image", key="remove_img"):
                    st.session_state["attachment_image"] = None
                    st.rerun()

        # 3. Document Upload (RAG)
        with col_doc:
            st.markdown("**📄 Document (RAG)**")
            uploaded_doc = st.file_uploader(
                "Upload Document",
                type=["pdf", "docx", "pptx", "csv", "txt", "md"],
                key="composer_doc_uploader",
                label_visibility="collapsed"
            )
            if uploaded_doc:
                if st.button("📤 Index Document", key="btn_index_doc"):
                    with st.spinner("Extracting & Indexing..."):
                        active_conv_id = st.session_state.get("current_conversation_id")
                        res = api_client.upload_document(
                            file_bytes=uploaded_doc.read(),
                            filename=uploaded_doc.name,
                            content_type=uploaded_doc.type or "application/octet-stream",
                            conversation_id=active_conv_id
                        )
                        if res.get("status") == "processed":
                            st.success(f"Indexed: {res.get('chunk_count', 0)} chunks!")
                        else:
                            st.error(f"Failed: {res.get('message', 'Upload error')}")

        # Structured format selector
        st.markdown("---")
        fmt_cols = st.columns([0.4, 0.6])
        fmt_cols[0].markdown("**Structured Output Mode:**")
        st.session_state["structured_format"] = fmt_cols[1].selectbox(
            "Output Format",
            options=["Normal", "Executive Summary", "Checklist", "Comparison Table", "JSON"],
            index=0,
            label_visibility="collapsed"
        )
