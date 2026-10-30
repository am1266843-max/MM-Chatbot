import streamlit as st
from typing import Dict, Any, List
from frontend.api_client import api_client

LANGUAGE_CHOICES = {
    "auto": "🌐 Auto-Detect (स्वचालित)",
    "hi": "🇮🇳 Hindi (हिन्दी)",
    "en": "🇺🇸 English (US)",
    "en-in": "🇮🇳 English (India)",
    "hi-en": "🇮🇳 Hinglish (मिक्स हिन्दी-English)",
    "es": "🇪🇸 Spanish (Español)",
    "fr": "🇫🇷 French (Français)",
    "de": "🇩🇪 German (Deutsch)",
    "ja": "🇯🇵 Japanese (日本語)",
    "zh": "🇨🇳 Chinese (中文)",
    "ar": "🇸🇦 Arabic (العربية)",
    "bn": "🇧🇩 Bengali (বাংলা)",
    "mr": "🇮🇳 Marathi (मराठी)",
    "ta": "🇮🇳 Tamil (தமிழ்)",
    "te": "🇮🇳 Telugu (తెలుగు)",
    "ru": "🇷🇺 Russian (Русский)",
    "pt": "🇧🇷 Portuguese (Português)"
}

def render_sidebar():
    """Renders the comprehensive sidebar with multilingual controls, voice assistance, model selector, and document library."""
    with st.sidebar:
        # App Title & Branding
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                <span style="font-size: 2.2rem;">🎙️</span>
                <div>
                    <h2 style="margin: 0; font-size: 1.3rem; font-weight: 700;">Nexus Voice AI</h2>
                    <span style="font-size: 0.8rem; color: #64748b;">Multilingual Multimodal Assistant</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # New Chat Button
        if st.button("➕ New Conversation", use_container_width=True, type="primary"):
            new_conv = api_client.create_conversation(
                title="New Conversation",
                provider=st.session_state.get("selected_provider"),
                model=st.session_state.get("selected_model")
            )
            if new_conv:
                st.session_state["current_conversation_id"] = new_conv["id"]
                st.session_state["messages"] = []
                st.session_state["attachment_image"] = None
                st.session_state["last_audio_base64"] = None
                st.rerun()

        st.markdown("---")

        # 1. Multilingual Support Section
        st.markdown("#### 🌐 Chatbot Language")
        current_lang = st.session_state.get("selected_language", "auto")
        lang_keys = list(LANGUAGE_CHOICES.keys())
        default_lang_idx = lang_keys.index(current_lang) if current_lang in lang_keys else 0

        chosen_lang = st.selectbox(
            "Primary Language",
            options=lang_keys,
            format_func=lambda k: LANGUAGE_CHOICES.get(k, k),
            index=default_lang_idx,
            key="sb_language_select"
        )
        st.session_state["selected_language"] = chosen_lang

        # 2. Voice Assistance Section
        st.markdown("#### 🎙️ Voice Assistance")
        st.session_state["auto_speak"] = st.toggle(
            "🔊 Auto-Speak Responses",
            value=st.session_state.get("auto_speak", True),
            help="Assistant automatically reads responses aloud for hands-free voice dialogue."
        )

        col_gender, col_voice_info = st.columns([0.5, 0.5])
        with col_gender:
            st.session_state["voice_gender"] = st.selectbox(
                "Voice",
                options=["female", "male"],
                format_func=lambda g: "👩 Female" if g == "female" else "👨 Male",
                index=0 if st.session_state.get("voice_gender", "female") == "female" else 1
            )

        with col_voice_info:
            active_lang = st.session_state.get("selected_language", "auto")
            voice_label = "Swara (हिन्दी)" if active_lang == "hi" else "Neerja (IN)" if active_lang in ["hi-en", "en-in"] else "Aria (US)"
            st.caption(f"Neural Voice:\n**{voice_label}**")

        st.markdown("---")

        # 3. Model Selector Section
        st.markdown("#### ⚙️ AI Model")
        models_data = api_client.get_models()
        available_models = models_data.get("models", [])

        if available_models:
            model_options = {m["id"]: f"{m['name']} {'(Ready)' if m['is_configured'] else '(Key Required)'}" for m in available_models}
            model_ids = list(model_options.keys())

            current_model_id = st.session_state.get("selected_model")
            if not current_model_id or current_model_id not in model_ids:
                current_model_id = models_data.get("default_model", model_ids[0])

            selected_idx = model_ids.index(current_model_id) if current_model_id in model_ids else 0

            chosen_id = st.selectbox(
                "Active Model",
                options=model_ids,
                format_func=lambda mid: model_options.get(mid, mid),
                index=selected_idx,
                label_visibility="collapsed"
            )

            matched_model = next((m for m in available_models if m["id"] == chosen_id), None)
            if matched_model:
                st.session_state["selected_model"] = matched_model["id"]
                st.session_state["selected_provider"] = matched_model["provider"]
                st.session_state["supports_vision"] = matched_model["supports_vision"]

                tags = []
                if matched_model["supports_vision"]:
                    tags.append("🖼️ Vision")
                else:
                    tags.append("📝 Text")
                if matched_model["is_configured"]:
                    tags.append("🟢 Ready")
                else:
                    tags.append("🟡 Mock AI")

                st.caption(" • ".join(tags))

        # Modality Toggles
        st.markdown("##### Features")
        st.session_state["use_rag"] = st.toggle("📚 Document RAG", value=st.session_state.get("use_rag", True))
        st.session_state["use_web_search"] = st.toggle("🌐 Web Search", value=st.session_state.get("use_web_search", False))

        st.markdown("---")

        # Document Library for Active Conversation
        active_conv_id = st.session_state.get("current_conversation_id")
        if active_conv_id:
            st.markdown("#### 📁 Conversation Files")
            docs = api_client.get_documents(conversation_id=active_conv_id)
            if docs:
                for d in docs:
                    cols = st.columns([0.7, 0.3])
                    status_icon = "✅" if d["processing_status"] == "processed" else "⚠️"
                    cols[0].caption(f"{status_icon} **{d['original_filename']}** ({d['chunk_count']} chunks)")
                    if cols[1].button("🗑️", key=f"del_doc_{d['id']}", help="Delete file"):
                        api_client.delete_document(d["id"])
                        st.toast("Document removed.")
                        st.rerun()
            else:
                st.caption("No files uploaded for this chat.")

            st.markdown("---")

        # Searchable Conversation History
        st.markdown("#### 💬 Chat History")
        search_query = st.text_input("🔍 Search chats", placeholder="Filter history...", label_visibility="collapsed")
        conversations = api_client.get_conversations(search=search_query)

        if conversations:
            for conv in conversations:
                is_active = (conv["id"] == active_conv_id)
                prefix = "▶ " if is_active else ""
                btn_label = f"{prefix}{conv['title'][:25]}"

                col_btn, col_actions = st.columns([0.75, 0.25])
                if col_btn.button(btn_label, key=f"conv_{conv['id']}", use_container_width=True, type="secondary" if not is_active else "primary"):
                    st.session_state["current_conversation_id"] = conv["id"]
                    full_conv = api_client.get_conversation(conv["id"])
                    st.session_state["messages"] = full_conv.get("messages", []) if full_conv else []
                    st.rerun()

                with col_actions.popover("⚙️"):
                    st.markdown(f"**Manage:** `{conv['title'][:18]}`")
                    new_title = st.text_input("Rename", value=conv["title"], key=f"ren_input_{conv['id']}")
                    if st.button("Save Name", key=f"save_ren_{conv['id']}"):
                        if new_title.strip():
                            api_client.update_conversation(conv["id"], title=new_title.strip())
                            st.rerun()

                    st.markdown(f"[📥 Export Markdown]({api_client.base_url}/api/conversations/{conv['id']}/export?format=markdown)")
                    st.markdown(f"[📄 Export Text]({api_client.base_url}/api/conversations/{conv['id']}/export?format=txt)")

                    st.markdown("---")
                    if st.button("🗑️ Delete Chat", key=f"del_conv_{conv['id']}", type="primary"):
                        api_client.delete_conversation(conv["id"])
                        if st.session_state.get("current_conversation_id") == conv["id"]:
                            st.session_state["current_conversation_id"] = None
                            st.session_state["messages"] = []
                        st.rerun()
        else:
            st.caption("No conversations found.")

        st.markdown("---")

        # System Status Footer
        health = api_client.get_health()
        status_color = "🟢" if health.get("status") == "healthy" else "🟡" if health.get("status") == "degraded" else "🔴"
        st.caption(f"{status_color} Backend: **{health.get('status', 'Offline').capitalize()}**")
        st.caption(f"💾 Storage: **{health.get('database', 'Unknown').capitalize()}**")
