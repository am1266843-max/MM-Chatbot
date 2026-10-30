import streamlit as st
from frontend.api_client import api_client

def render_settings_dialog():
    """Renders comprehensive system status and configuration guide."""
    with st.expander("🛠️ System Health & Provider Configuration", expanded=False):
        status = api_client.get_system_status()
        if not status:
            st.warning("Could not reach backend settings service. Ensure FastAPI is running.")
            return

        c1, c2, c3 = st.columns(3)
        c1.metric("Backend Status", status.get("backend_status", "Offline"))
        c2.metric("Database Type", status.get("database_type", "Unknown"))
        c3.metric("Upload Limit", f"{status.get('upload_limit_mb', 15)} MB")

        st.markdown("##### AI Model Providers")
        providers = status.get("providers", [])
        if providers:
            p_cols = st.columns(len(providers))
            for idx, p in enumerate(providers):
                p_cols[idx].markdown(
                    f"**{p['name']}**\n\n"
                    f"`{p['status_label']}`"
                )

        st.markdown("---")
        st.markdown("##### Feature Readiness")
        f1, f2, f3 = st.columns(3)
        f1.write(f"🌐 Web Search: {'🟢 Ready' if status.get('search_configured') else '🔴 Offline'}")
        f2.write(f"🔊 Voice Synthesis: {'🟢 Ready' if status.get('voice_configured') else '🔴 Offline'}")
        f3.write(f"📚 Vector RAG: {'🟢 Ready' if status.get('rag_configured') else '🔴 Offline'}")

        st.markdown("---")
        st.info(
            "💡 **To configure API keys:** Open `.env` in the root folder and add your "
            "`GROQ_API_KEY`, `OPENAI_API_KEY`, or `HUGGINGFACE_API_KEY`, then restart the server."
        )

