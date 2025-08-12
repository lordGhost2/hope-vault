# streamlit_app_beautified.py
# A visually improved Streamlit UI for Hope Vault — Demo
# This file keeps the same backend endpoints and internal logic as the original
# streamlit_app.py but reorganizes layout, adds styling, icons and a friendlier UX.

import streamlit as st
import requests
import time
from urllib.parse import urljoin

# ========== CONFIG (kept same behavior as original) ==========
API_BASE = st.sidebar.text_input("Backend base URL", "http://127.0.0.1:8000/api")
USER_ID = st.sidebar.text_input("Demo user id", "demo-user")
# ==============================================================

st.set_page_config(page_title="Hope Vault — Demo", layout="wide", page_icon=":sparkles:")

# --- Styling ---
st.markdown(
    """
    <style>
    .header {
        background: linear-gradient(90deg,#6dd5ed, #2193b0);
        padding: 18px;
        border-radius: 12px;
        color: white;
    }
    .card {
        background: linear-gradient(180deg, rgba(255,255,255,0.85), rgba(255,255,255,0.75));
        padding: 14px;
        border-radius: 12px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    }
    .muted { color: #6c757d }
    .small { font-size:0.9rem }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
st.markdown(
    "<div class='header'><h1 style='margin:0'>✨ Hope Vault — Demo</h1><div class='small muted'>AI-powered memory vault → story → audio</div></div>",
    unsafe_allow_html=True,
)

st.write("\n")

# Helper functions (same semantics as original)

def api_get(path, params=None):
    try:
        r = requests.get(urljoin(API_BASE + "/", path.lstrip("/")), params=params, timeout=20)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def api_post(path, json=None, files=None):
    try:
        r = requests.post(urljoin(API_BASE + "/", path.lstrip("/")), json=json, files=files, timeout=60)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# --- Top metrics and quick actions ---
col1, col2, col3 = st.columns([1.8, 1, 1])
with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Your Hope Vault")
    st.markdown("<div class='small muted'>Save personal memories, convert them into uplifting stories and audio.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.metric("Backend", API_BASE)

with col3:
    st.metric("User ID", USER_ID)

st.markdown("---")

# --- Layout using tabs for clearer UX ---
tab_add, tab_vault, tab_story, tab_translate = st.tabs(["Add Memory ✍️", "Vault 📚", "Generate Story ✨", "Translate & TTS 🔊"])

# ---- Add Memory Tab ----
with tab_add:
    with st.container():
        left, right = st.columns([3, 1])
        with left:
            with st.form("add_memory_form"):
                st.markdown("**Daily prompt (from backend)**")
                with st.expander("Get a prompt from backend"):
                    prompt_resp = api_get("prompt", params={"lang": "en"})
                    if "prompt" in prompt_resp:
                        st.info(prompt_resp["prompt"])
                    else:
                        st.warning("Could not fetch prompt. Backend URL okay?")

                text = st.text_area("Write a short memory:", value="", height=160)
                lang = st.selectbox("Language code", options=["en", "hi", "bn", "ta"], index=0)
                submitted = st.form_submit_button("Save memory")
                if submitted:
                    if not text.strip():
                        st.warning("Please write a short memory first.")
                    else:
                        payload = {"user_id": USER_ID, "text": text.strip(), "language": lang}
                        res = api_post("entry", json=payload)
                        if res.get("status") == "saved":
                            st.success("Memory saved ✅")
                        else:
                            st.error(f"Save failed: {res}")
        with right:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write("**Tips**")
            st.markdown("- Keep memories short (1–4 lines).\n- Use present tense for vividness.\n- Try to add an emotion (hope, pride, gratitude).")
            st.markdown("</div>", unsafe_allow_html=True)

# ---- Vault Tab ----
with tab_vault:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if st.button("Refresh vault"):
        # intentionally simple: refresh triggers rerun
        pass

    vault = api_get("vault", params={"user_id": USER_ID})
    if vault.get("entries") is None:
        st.error("Unable to fetch vault. Is backend running and CORS allowed?")
    else:
        entries = vault.get("entries", [])
        if not entries:
            st.info("No memories yet. Add one in Add Memory tab.")
        else:
            # show reverse chronological with subtle separators
            for e in entries[::-1]:
                ts = e.get("timestamp", "")[:19]
                st.markdown(f"**{ts}** — {e.get('text')}")
                st.markdown("---")
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Generate Story Tab ----
with tab_story:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    with st.form("gen_story_form"):
        theme = st.text_input("Theme (e.g., perseverance, hope)", value="perseverance")
        gen_lang = st.selectbox("Story language code", options=["en", "hi", "bn", "ta"], index=0)
        max_len = st.slider("Max length (tokens)", min_value=80, max_value=400, value=200)
        gen_submit = st.form_submit_button("Generate story")
        if gen_submit:
            with st.spinner("Generating story..."):
                payload = {"user_id": USER_ID, "theme": theme, "language": gen_lang, "max_length": max_len}
                res = api_post("generate_story", json=payload)
                if res.get("error"):
                    st.error("Generation failed: " + str(res.get("error")))
                    st.write(res)
                else:
                    story = res.get("story", {}).get("text") or (res.get("story") and res["story"].get("text"))
                    if not story:
                        story = res.get("story") if isinstance(res.get("story"), str) else None
                    if story:
                        st.success("Story generated ✅")
                        # store in session state for other tabs
                        st.session_state["generated_story_text"] = story
                        st.text_area("Generated Story (editable)", value=story, height=260, key="generated_story_text")
                    else:
                        st.error("No story text found in response. Response:")
                        st.write(res)
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Translate & TTS Tab ----
with tab_translate:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("If you want the story in another language, first copy the story above → Translate → TTS")

    translated_text = None
    if st.button("Translate last story to Hindi"):
        story_text = st.session_state.get("generated_story_text", "")
        if not story_text:
            st.warning("Generate a story first.")
        else:
            with st.spinner("Translating..."):
                res = api_post("translate", json={"text": story_text, "target_lang": "hi"})
                if res.get("translatedText"):
                    translated_text = res["translatedText"]
                    st.session_state["translated_text"] = translated_text
                    st.success("Translated ✅")
                else:
                    st.error("Translate failed: " + str(res))

    if st.session_state.get("translated_text"):
        st.text_area("Translated story", value=st.session_state["translated_text"], height=260, key="translated_box")

    st.markdown("**Text-to-Speech**")
    tts_text = st.text_area(
        "Text to speak (edit or paste story here)",
        value=st.session_state.get("translated_text") or st.session_state.get("generated_story_text", ""),
        height=200,
        key="tts_text",
    )
    tts_lang = st.selectbox("TTS language code (gTTS):", options=["en", "hi", "bn", "ta"], index=0)
    slow = st.checkbox("Slow voice", value=False)
    if st.button("Generate audio"):
        if not tts_text.strip():
            st.warning("Provide text to convert to speech.")
        else:
            with st.spinner("Generating audio..."):
                res = api_post("text_to_speech", json={"text": tts_text, "language": tts_lang, "slow": slow})
                if res.get("error"):
                    st.error("TTS failed: " + str(res))
                else:
                    public = res.get("public_url") or res.get("audio_file")
                    st.success("Audio ready")
                    st.write("Public URL:", public)
                    try:
                        st.audio(public)
                    except Exception:
                        st.info("If stream fails, open the public URL in a new tab to play the file.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Tip: Use the sidebar to change backend URL if your FastAPI isn't on localhost.")
