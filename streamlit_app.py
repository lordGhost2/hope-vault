# streamlit_app_out_of_box.py
# An "out-of-the-box" visually rich UI for Hope Vault — Demo
# Keeps the same backend endpoints and behavior as the original streamlit_app.py

import streamlit as st
import requests
import json
from urllib.parse import urljoin
import base64

# ========== CONFIG (identical behavior) ==========
API_BASE = st.sidebar.text_input("Backend base URL", "http://127.0.0.1:8000/api")
USER_ID = st.sidebar.text_input("Demo user id", "demo-user")
# =================================================

st.set_page_config(page_title="Hope Vault — Demo", layout="wide", page_icon=":rainbow:")

# ---------- CUSTOM STYLING & UTILS ----------
st.markdown(
    """
    <style>
    /* page background gradient */
    .stApp {
        background: radial-gradient(circle at 10% 10%, rgba(255,255,255,0.02), transparent 10%),
                    linear-gradient(135deg, #f4f9ff 0%, #ffffff 40%, #fef7ff 100%);
        background-attachment: fixed;
    }

    /* header */
    .hero {
        border-radius: 18px;
        padding: 28px;
        background: linear-gradient(90deg, rgba(118,75,162,0.95), rgba(44,169,225,0.95));
        color: white;
        box-shadow: 0 8px 30px rgba(44,169,225,0.12);
    }
    .hero h1 { margin: 0; font-size: 34px; }
    .hero p { margin: 6px 0 0 0; opacity: 0.95 }

    /* small cards */
    .card {
        background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,255,255,0.85));
        border-radius: 14px;
        padding: 16px;
        box-shadow: 0 6px 18px rgba(13,38,76,0.06);
    }

    /* fancy gradient button */
    .btn-gradient {
        background: linear-gradient(90deg,#ff9a9e,#fecfef,#a1c4fd);
        border: none;
        color: #111827;
        padding: 10px 18px;
        border-radius: 10px;
        font-weight: 600;
        transition: transform .12s ease, box-shadow .12s ease;
        box-shadow: 0 6px 18px rgba(16,24,40,0.08);
    }
    .btn-gradient:hover { transform: translateY(-4px); box-shadow: 0 12px 36px rgba(16,24,40,0.12); }

    /* small muted text */
    .muted { color: #6b7280; font-size:0.95rem }

    /* story textarea styling */
    textarea[aria-label="Generated Story (editable)"] { min-height: 260px }

    /* sparkle animation */
    .sparkle { position: relative }
    .sparkle:after {
        content: '';
        position: absolute;
        top: -6px; right: -6px;
        width: 18px; height: 18px;
        background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.9), rgba(255,255,255,0.2));
        border-radius: 50%;
        opacity: 0.9;
        animation: blink 2.8s infinite;
        filter: drop-shadow(0 6px 10px rgba(0,0,0,0.08));
    }
    @keyframes blink { 0%{opacity:0.9}50%{opacity:0.2}100%{opacity:0.9} }

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Helpers (unchanged behavior) ----------

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

# ---------- HERO / TOP BAR ----------
hero_col1, hero_col2 = st.columns([3,1])
with hero_col1:
    st.markdown(
        "<div class='hero'><h1>Hope Vault ✨</h1><p>Turn small daily memories into uplifting stories and shareable audio — powered by simple, empathetic AI.</p></div>",
        unsafe_allow_html=True,
    )
with hero_col2:
    st.markdown("<div class='card'><div style='text-align:center'><strong style='font-size:18px'>Vault Health</strong><div class='muted'>Progress toward 50 memories</div><br></div></div>", unsafe_allow_html=True)

# show vault fullness as progress (visual flourish)
vault_preview = api_get("vault", params={"user_id": USER_ID})
entries_count = len(vault_preview.get("entries", [])) if isinstance(vault_preview, dict) else 0
progress = min(1.0, entries_count / 50.0)
st.progress(progress)

st.markdown("---")

# ---------- FEATURE HIGHLIGHTS ----------
f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("<div class='card'><h3>✨ Capture</h3><div class='muted'>Quick daily prompts to help you remember the tiny moments.</div></div>", unsafe_allow_html=True)
with f2:
    st.markdown("<div class='card'><h3>📖 Transform</h3><div class='muted'>AI crafts a gentle, uplifting story from your memories.</div></div>", unsafe_allow_html=True)
with f3:
    st.markdown("<div class='card'><h3>🔊 Share</h3><div class='muted'>Translate and convert to voice for sharing with loved ones.</div></div>", unsafe_allow_html=True)

st.markdown("---")

# ---------- MAIN CONTENT IN TABS (keeps same endpoints) ----------
tab_add, tab_vault, tab_story, tab_translate = st.tabs(["Add Memory ✍️", "Vault 📚", "Generate Story ✨", "Translate & TTS 🔊"])

# ---- Add Memory Tab ----
with tab_add:
    col_left, col_right = st.columns([3,1])
    with col_left:
        with st.form("add_memory"):
            st.markdown("### Add a memory (daily prompt)")
            with st.expander("Get a prompt from backend"):
                prompt_resp = api_get("prompt", params={"lang": "en"})
                if "prompt" in prompt_resp:
                    st.success(prompt_resp["prompt"])
                else:
                    st.warning("Could not fetch prompt. Backend URL okay?")

            text = st.text_area("Write a short memory:", value="", height=140)
            lang = st.selectbox("Language code", options=["en","hi","bn","ta"], index=0)
            submitted = st.form_submit_button("Save memory", help="Save this memory into your Hope Vault", on_click=None)
            if submitted:
                if not text.strip():
                    st.warning("Please write a short memory first.")
                else:
                    payload = {"user_id": USER_ID, "text": text.strip(), "language": lang}
                    res = api_post("entry", json=payload)
                    if res.get("status") == "saved":
                        st.balloons()
                        st.success("Memory saved — nice! ✅")
                    else:
                        st.error(f"Save failed: {res}")
    with col_right:
        st.markdown("<div class='card'><strong>Tips for vivid memories</strong><ul class='muted'><li>Be specific — add small details</li><li>Mention an emotion</li><li>Write in present tense</li></ul></div>", unsafe_allow_html=True)
        # sample memory download
        sample = "Today I noticed the neighbor's cat sleeping on the windowsill. I felt calm and grateful."
        st.download_button("Download sample memory", sample, file_name="sample_memory.txt")

# ---- Vault Tab ----
with tab_vault:
    st.markdown("<div class='card'><h3>Your Hope Vault</h3><div class='muted'>Recent memories — newest first</div></div>", unsafe_allow_html=True)
    if st.button("Refresh vault"):
        pass
    vault = api_get("vault", params={"user_id": USER_ID})
    if vault.get("entries") is None:
        st.error("Unable to fetch vault. Is backend running and CORS allowed?")
    else:
        entries = vault.get("entries", [])
        if not entries:
            st.info("No memories yet. Add one in Add Memory tab.")
        else:
            for e in entries[::-1]:
                ts = e.get("timestamp","")[:19]
                st.markdown(f"<div class='card'><div style='display:flex;justify-content:space-between;align-items:center'><div><strong>{ts}</strong><div class='muted'>{e.get('text')}</div></div><div class='muted' style='text-align:right'>Lang: {e.get('language','-')}</div></div></div>", unsafe_allow_html=True)
                st.write("")

# ---- Generate Story Tab ----
with tab_story:
    st.markdown("<div class='card'><h3 class='sparkle'>Generate uplifting story</h3><div class='muted'>Use your memories as seeds for a gentle, hopeful story.</div></div>", unsafe_allow_html=True)
    with st.form("gen_story"):
        theme = st.text_input("Theme (e.g., perseverance, hope)", value="perseverance")
        gen_lang = st.selectbox("Story language code", options=["en","hi","bn","ta"], index=0)
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
                        st.session_state["generated_story_text"] = story
                        st.success("Story generated ✅")
                        st.text_area("Generated Story (editable)", value=story, height=300, key="generated_story_text")
                        # visual flourish: offer to download or copy
                        st.download_button("Download story", story, file_name="hope_story.txt")
                    else:
                        st.error("No story text found in response. Response:")
                        st.write(res)

# ---- Translate & TTS Tab ----
with tab_translate:
    st.markdown("<div class='card'><h3>Translate & Text-to-Speech</h3><div class='muted'>Translate generated story and make a voice file to share.</div></div>", unsafe_allow_html=True)

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
    tts_text = st.text_area("Text to speak (edit or paste story here)", value=st.session_state.get("translated_text") or st.session_state.get("generated_story_text",""), height=200, key="tts_text")
    tts_lang = st.selectbox("TTS language code (gTTS):", options=["en","hi","bn","ta"], index=0)
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
                    st.markdown("<div class='muted'>Public URL below — try the player or open in a new tab</div>", unsafe_allow_html=True)
                    st.write(public)
                    try:
                        st.audio(public)
                    except Exception:
                        st.info("If stream fails, open the public URL in a new tab to play the file.")

st.markdown("---")
st.caption("Tip: Use the sidebar to change backend URL if your FastAPI isn't on localhost. Want brand colors or a logo? Tell me the hex values or upload an SVG and I'll adapt the UI.")
