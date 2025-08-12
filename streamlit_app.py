# streamlit_app.py
import streamlit as st
import requests
import time
from urllib.parse import urljoin

# ========== CONFIG ==========
API_BASE = st.sidebar.text_input("Backend base URL", "https://hope-vault.onrender.com")
USER_ID = st.sidebar.text_input("Demo user id", "demo-user")
# ============================

st.set_page_config(page_title="Hope Vault — Demo", layout="centered")

st.title("Hope Vault — Demo")
st.write("AI-powered memory vault → story → audio (Streamlit demo)")

# Helper functions
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

# ---- Left column: add memory ----
with st.form("add_memory"):
    st.subheader("Add a memory (daily prompt)")
    # show backend prompt
    with st.expander("Get a prompt from backend"):
        prompt_resp = api_get("prompt", params={"lang": "en"})
        if "prompt" in prompt_resp:
            st.info(prompt_resp["prompt"])
        else:
            st.warning("Could not fetch prompt. Backend URL okay?")
    text = st.text_area("Write a short memory:", value="", height=120)
    lang = st.selectbox("Language code", options=["en","hi","bn","ta"], index=0)
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

st.markdown("---")

# ---- Middle: list vault & generate story ----
st.subheader("Your Hope Vault")
if st.button("Refresh vault"):
    pass

vault = api_get("vault", params={"user_id": USER_ID})
if vault.get("entries") is None:
    st.error("Unable to fetch vault. Is backend running and CORS allowed?")
else:
    entries = vault.get("entries", [])
    if not entries:
        st.info("No memories yet. Add one above.")
    else:
        for e in entries[::-1]:
            ts = e.get("timestamp","")[:19]
            st.markdown(f"**{ts}** — {e.get('text')}")
    st.markdown("---")

st.subheader("Generate uplifting story")
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
                    # fallback: maybe response directly contains story text
                    story = res.get("story") if isinstance(res.get("story"), str) else None
                if story:
                    st.success("Story generated ✅")
                    st.text_area("Generated Story (editable)", value=story, height=260, key="generated_story_text")
                else:
                    st.error("No story text found in response. Response:")
                    st.write(res)

st.markdown("---")

# ---- Right: translation & TTS ----
st.subheader("Translate & Text-to-Speech")

st.write("If you want the story in another language, first copy the story above -> Translate -> TTS")

translated_text = None
if st.button("Translate last story to Hindi"):
    # copy story from textarea
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
                st.write("Public URL:", public)
                # try to play via Streamlit
                try:
                    st.audio(public)
                except Exception:
                    st.info("If stream fails, open the public URL in a new tab to play the file.")

st.markdown("---")
st.caption("Tip: Use the sidebar to change backend URL if your FastAPI isn't on localhost.")

