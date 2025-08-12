import streamlit as st
from datetime import datetime
import pytz
import requests

st.set_page_config(page_title="Hope Vault", layout="wide")

BACKEND_URL = "http://localhost:8000/api"  # Change if needed
USER_ID = "user_123"

def api_get(endpoint, params=None):
    try:
        r = requests.get(f"{BACKEND_URL}/{endpoint}", params=params, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def api_post(endpoint, json=None):
    try:
        r = requests.post(f"{BACKEND_URL}/{endpoint}", json=json, timeout=20)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# === CSS Styling same as before ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}
.title {
    font-size: 3.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, #8e2de2, #4a00e0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    text-shadow: 0 0 15px rgba(142,45,226,0.5);
    margin-bottom: 0.2rem;
    user-select: none;
}
.subtitle {
    font-size: 1.3rem;
    text-align: center;
    opacity: 0.85;
    margin-bottom: 1.8rem;
    user-select: none;
}
.stButton>button {
    font-size: 1.1rem;
    border-radius: 12px;
    padding: 0.5em 1.2em;
    background: linear-gradient(135deg, #8e2de2, #4a00e0);
    color: white;
    border: none;
    transition: all 0.3s ease;
    cursor: pointer;
    user-select: none;
}
.stButton>button:hover {
    transform: scale(1.06);
    box-shadow: 0 6px 18px rgba(142,45,226,0.5);
}
</style>
""", unsafe_allow_html=True)

# Title & Subtitle
st.markdown("<div class='title'>Hope Vault</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Your secure place for inspiration & memories ✨</div>", unsafe_allow_html=True)

# Date and Live Kolkata time
tz = pytz.timezone("Asia/Kolkata")
now = datetime.now(tz)
st.markdown(f"### 📅 Today: {now.strftime('%Y-%m-%d')} | ⏰ Current time (Kolkata): {now.strftime('%H:%M:%S')}")

st.markdown("---")

# Choose panel
panel = st.radio("Choose Section", ["Add Memory", "Your Vault & Story", "Translate & Text-to-Speech"], horizontal=True)

if panel == "Add Memory":
    with st.form("add_memory"):
        st.subheader("Add a memory (daily prompt)")
        with st.expander("Get a prompt from backend"):
            prompt_resp = api_get("prompt", params={"lang": "en"})
            if "prompt" in prompt_resp:
                st.info(prompt_resp["prompt"])
            else:
                st.warning("Could not fetch prompt. Backend URL okay?")
        text = st.text_area("Write a short memory:", value="", height=120)
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

elif panel == "Your Vault & Story":
    st.subheader("Your Hope Vault")
    if st.button("Refresh vault"):
        pass

    vault = api_get("vault", params={"user_id": USER_ID})
    if vault.get("entries") is None:
        st.error("Unable to fetch vault. Is backend running and CORS allowed?")
    else:
        entries = vault.get("entries", [])
        if not entries:
            st.info("No memories yet. Add one in the 'Add Memory' tab.")
        else:
            for e in entries[::-1]:
                ts = e.get("timestamp", "")[:19]
                st.markdown(f"**{ts}** — {e.get('text')}")

    st.markdown("---")

    st.subheader("Generate uplifting story")
    with st.form("gen_story"):
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
                        st.text_area("Generated Story (editable)", value=story, height=260, key="generated_story_text")
                    else:
                        st.error("No story text found in response. Response:")
                        st.write(res)

else:  # Translate & TTS
    st.subheader("Translate & Text-to-Speech")
    st.write("If you want the story in another language, first copy the story above -> Translate -> TTS")

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
    tts_text = st.text_area("Text to speak (edit or paste story here)", 
                           value=st.session_state.get("translated_text") or st.session_state.get("generated_story_text",""),
                           height=200, key="tts_text")
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
                    try:
                        st.audio(public)
                    except Exception:
                        st.info("If stream fails, open the public URL in a new tab to play the file.")
