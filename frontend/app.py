import os
import base64
from pathlib import Path
import streamlit as st

from frontend.api_client import api_client
from frontend.components.sidebar import render_sidebar
from frontend.components.chat_message import render_message
from frontend.components.message_composer import render_attachment_bar
from frontend.components.settings_dialog import render_settings_dialog

# Set page configuration
st.set_page_config(
    page_title="Nexus AI - Multilingual Multimodal Voice Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = Path(__file__).parent / "styles" / "custom.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize Session State
if "current_conversation_id" not in st.session_state:
    st.session_state["current_conversation_id"] = None
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "attachment_image" not in st.session_state:
    st.session_state["attachment_image"] = None
if "transcribed_input" not in st.session_state:
    st.session_state["transcribed_input"] = ""
if "selected_model" not in st.session_state:
    st.session_state["selected_model"] = "mock-model"
if "selected_provider" not in st.session_state:
    st.session_state["selected_provider"] = "mock"
if "selected_language" not in st.session_state:
    st.session_state["selected_language"] = "auto"
if "voice_gender" not in st.session_state:
    st.session_state["voice_gender"] = "female"
if "auto_speak" not in st.session_state:
    st.session_state["auto_speak"] = True
if "supports_vision" not in st.session_state:
    st.session_state["supports_vision"] = True
if "use_rag" not in st.session_state:
    st.session_state["use_rag"] = True
if "use_web_search" not in st.session_state:
    st.session_state["use_web_search"] = False
if "structured_format" not in st.session_state:
    st.session_state["structured_format"] = "Normal"

# Render Sidebar
render_sidebar()

# Main Header & Settings Expander
st.title("🎙️ Nexus Multilingual Voice Assistant")
render_settings_dialog()

# Display Welcome Screen if conversation is empty
if not st.session_state["messages"]:
    selected_l = st.session_state.get("selected_language", "auto")
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%); border: 1px solid #bfdbfe; border-radius: 14px; padding: 22px; margin-bottom: 20px;">
            <h3 style="margin-top: 0; color: #1e3a8a;">👋 Welcome to Nexus AI Voice Assistant! / स्वागत है!</h3>
            <p style="color: #334155; font-size: 1rem; margin-bottom: 8px;">
                Nexus is a complete <strong>Multimodal & Multilingual AI Assistant</strong> capable of understanding and speaking 
                <strong>Hindi (हिन्दी), English, Hinglish, Spanish, French, German, Japanese, Bengali, and more</strong>.
            </p>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span style="background: #ffffff; padding: 4px 10px; border-radius: 12px; font-size: 0.82rem; border: 1px solid #cbd5e1;">🎙️ Voice Input & Output</span>
                <span style="background: #ffffff; padding: 4px 10px; border-radius: 12px; font-size: 0.82rem; border: 1px solid #cbd5e1;">🇮🇳 हिन्दी एवं 15+ भाषाएँ</span>
                <span style="background: #ffffff; padding: 4px 10px; border-radius: 12px; font-size: 0.82rem; border: 1px solid #cbd5e1;">📄 Document RAG (PDF, DOCX, CSV)</span>
                <span style="background: #ffffff; padding: 4px 10px; border-radius: 12px; font-size: 0.82rem; border: 1px solid #cbd5e1;">🖼️ Image Vision</span>
                <span style="background: #ffffff; padding: 4px 10px; border-radius: 12px; font-size: 0.82rem; border: 1px solid #cbd5e1;">🌐 Real-Time Web Search</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("##### 🚀 Quick Start Prompts (क्विक स्टार्ट सवाल)")
    c1, c2 = st.columns(2)

    prompt_to_send = None
    with c1:
        if st.button("🇮🇳 नमस्ते! आप हिन्दी में मेरी क्या मदद कर सकते हैं?", use_container_width=True):
            prompt_to_send = "नमस्ते! आप हिन्दी में मेरी क्या-क्या मदद कर सकते हैं?"
            st.session_state["selected_language"] = "hi"
        if st.button("📄 Explain how Retrieval-Augmented Generation (RAG) works", use_container_width=True):
            prompt_to_send = "Explain how Retrieval-Augmented Generation (RAG) works in detail with vector embeddings and retrieval."

    with c2:
        if st.button("🎙️ How does the Multilingual Voice Assistant work?", use_container_width=True):
            prompt_to_send = "How does your multilingual voice assistance, speech recognition, and neural text-to-speech work?"
        if st.button("📊 Compare PostgreSQL vs SQLite in a structured table", use_container_width=True):
            prompt_to_send = "Compare PostgreSQL vs SQLite for modern applications in a structured Markdown comparison table."

    if prompt_to_send:
        st.session_state["quick_prompt"] = prompt_to_send
        st.rerun()

# Render Message Thread
total_msgs = len(st.session_state["messages"])
for idx, message in enumerate(st.session_state["messages"]):
    render_message(message, idx, is_last_message=(idx == total_msgs - 1))

# Render Media & Document Attachment Bar
render_attachment_bar()

# Active image preview indicator before sending
if st.session_state.get("attachment_image"):
    img_info = st.session_state["attachment_image"]
    st.info(f"🖼️ Attached: **{img_info['name']}** ({len(img_info['bytes']) // 1024} KB)")

# Determine prompt input (check for transcribed text or quick prompt)
default_text = ""
if st.session_state.get("quick_prompt"):
    default_text = st.session_state.pop("quick_prompt")
elif st.session_state.get("transcribed_input"):
    default_text = st.session_state.pop("transcribed_input")

# Chat Input Box
curr_lang = st.session_state.get("selected_language", "auto")
input_hint = "प्रश्न पूछें या बोलें (Ask in Hindi, English, etc.)..." if curr_lang == "hi" else "Ask a question, speak, upload documents or images..."
user_prompt = st.chat_input(placeholder=default_text or input_hint)

# Use default_text if chat_input wasn't manually typed but triggered via prompt card or voice button
active_query = user_prompt or (default_text if user_prompt is None and default_text else None)

if active_query:
    # 1. Prepare user message payload
    image_b64 = None
    image_mime = None
    user_extra_meta = {
        "language": st.session_state.get("selected_language", "auto")
    }

    if st.session_state.get("attachment_image"):
        img = st.session_state["attachment_image"]
        image_b64 = img["b64"]
        image_mime = img["mime"]
        user_extra_meta["has_image"] = True
        user_extra_meta["image_preview_b64"] = image_b64

    user_msg_entry = {
        "role": "user",
        "content": active_query,
        "extra_metadata": user_extra_meta
    }
    st.session_state["messages"].append(user_msg_entry)

    # Reset image attachment after submission
    st.session_state["attachment_image"] = None

    # 2. Render user message immediately
    with st.chat_message("user", avatar="🧑‍💻"):
        if user_extra_meta.get("has_image"):
            st.image(base64.b64decode(image_b64), width=300)
        st.markdown(active_query)

    # 3. Call Backend Chat Endpoint with spinner
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Assistant thinking & speaking..."):
            format_choice = st.session_state.get("structured_format", "Normal")
            format_map = {
                "Executive Summary": "summary",
                "Checklist": "checklist",
                "Comparison Table": "table",
                "JSON": "json"
            }
            mapped_fmt = format_map.get(format_choice)

            chat_req = {
                "conversation_id": st.session_state.get("current_conversation_id"),
                "message": active_query,
                "provider": st.session_state.get("selected_provider"),
                "model": st.session_state.get("selected_model"),
                "language": st.session_state.get("selected_language", "auto"),
                "voice_gender": st.session_state.get("voice_gender", "female"),
                "auto_speak": st.session_state.get("auto_speak", True),
                "use_rag": st.session_state.get("use_rag", True),
                "use_web_search": st.session_state.get("use_web_search", False),
                "image_base64": image_b64,
                "image_mime_type": image_mime,
                "structured_format": mapped_fmt
            }

            resp = api_client.send_chat(chat_req)

            # Update conversation ID if newly created
            if resp.get("conversation_id"):
                st.session_state["current_conversation_id"] = resp["conversation_id"]

            reply_text = resp.get("reply", "No response generated.")
            audio_b64 = resp.get("audio_base64")

            assistant_extra_meta = {
                "citations": resp.get("citations", []),
                "web_sources": resp.get("web_sources", []),
                "provider": resp.get("model_provider"),
                "model": resp.get("model_name"),
                "language": resp.get("language"),
                "voice_used": resp.get("voice_used"),
                "audio_base64": audio_b64
            }

            # If auto-speak audio was generated, store it in session state for instant playback
            if audio_b64:
                msg_idx = len(st.session_state["messages"])
                st.session_state[f"audio_{msg_idx}"] = audio_b64

            assistant_msg_entry = {
                "role": "assistant",
                "content": reply_text,
                "extra_metadata": assistant_extra_meta
            }
            st.session_state["messages"].append(assistant_msg_entry)

    # Rerun to synchronize view
    st.rerun()
