import streamlit as st
import requests
from urllib.parse import urljoin

# ========== CONFIG ==========
API_BASE = st.sidebar.text_input("Backend base URL", "http://127.0.0.1:8000/api")
USER_ID = st.sidebar.text_input("Demo user id", "demo-user")
# ============================

st.set_page_config(page_title="Hope Vault — Demo", layout="centered")

st.markdown("""
<style>
/* Title gradient style */
.title {
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #8e2de2, #4a00e0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.3em;
}

/* Subtitle */
.subtitle {
    font-size: 1.2rem;
    text-align: center;
    margin-bottom: 1em;
    opacity: 0.85;
}

/* Buttons style */
.stButton>button {
    font-size: 1.1rem;
    border-radius: 12px;
    padding: 0.5em 1.3em;
    background: linear-gradient(135deg, #8e2de2, #4a00e0);
    color: white;
    border: none;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 15px rgba(142,45,226,0.5);
}

/* Text area style */
textarea {
    font-size: 1.1rem !important;
}

/* Layout for the three main sections */
.main-container {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
}
.section {
    flex: 1 1 320px;
    background: #f7f7f9;
    padding: 1.2rem 1rem;
    border-radius: 12px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}
@media (prefers-color-scheme: dark) {
    .section {
        background: #181820;
        color: #e0e0e0;
    }
}

/* Labels and selects */
select, input[type=text], input[type=number] {
    font-size: 1.1rem;
    padding: 0.3em 0.5em;
    border-radius: 8px;
    border: 1px solid #ccc;
}

/* Markdown entries */
.entries-list {
    max-height: 280px;
    overflow-y: auto;
    padding-right: 8px;
}
.entries-list p {
    font-size: 1rem;
    margin: 0.15rem 0;
}

/* Textarea for generated story & translation */
.generated-textarea {
    font-size: 1.1rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>Hope Vault — Demo</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI-powered memory vault → story → audio</div>", unsafe_allow_html=True)

# Language full names mapping
LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil"
}

# Helper functions for API calls
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

st.markdown("---")

# Layout container for 3 sections side-by-side on wide screen
container = st.container()
with container:
    cols = st.columns([1, 1, 1])

    # --- Left column: Add memory ---
    with cols[0]:
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        with st.form("add_memory"):
            st.subheader("Add a memory (daily prompt)")
            with st.expander("Get a prompt from backend"):
                prompt_resp = api_get("prompt", params={"lang": "en"})
                if "prompt" in prompt_resp:
                    st.info(prompt_resp["prompt"])
                else:
                    st.warning("Could not fetch prompt. Backend URL okay?")
            text = st.text_area("Write a short memory:", value="", height=120)
            lang = st.selectbox("Language", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=0)
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
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Middle column: List vault & generate story ---
    with cols[1]:
        st.markdown("<div class='section'>", unsafe_allow_html=True)
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
                st.markdown('<div class="entries-list">', unsafe_allow_html=True)
                for e in entries[::-1]:
                    ts = e.get("timestamp","")[:19]
                    st.markdown(f"**{ts}** — {e.get('text')}")
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("Generate uplifting story")
        with st.form("gen_story"):
            theme = st.text_input("Theme (e.g., perseverance, hope)", value="perseverance")
            gen_lang = st.selectbox("Story language", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=0)
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
                            st.text_area("Generated Story (editable)", value=story, height=260, key="generated_story_text", placeholder="Your generated story appears here...")
                        else:
                            st.error("No story text found in response. Response:")
                            st.write(res)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Right column: Translation & TTS ---
    with cols[2]:
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("Translate & Text-to-Speech")

        st.write("If you want the story in another language, first copy the story above → Translate → TTS")

        # Translation target language dropdown with full names
        target_lang = st.selectbox("Select translation language:", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x])

        translated_text = None
        if st.button(f"Translate last story to {LANGUAGES[target_lang]}"):
            story_text = st.session_state.get("generated_story_text", "")
            if not story_text:
                st.warning("Generate a story first.")
            else:
                with st.spinner("Translating..."):
                    res = api_post("translate", json={"text": story_text, "target_lang": target_lang})
                    if res.get("translatedText"):
                        translated_text = res["translatedText"]
                        st.session_state["translated_text"] = translated_text
                        st.success(f"Translated to {LANGUAGES[target_lang]} ✅")
                    else:
                        st.error("Translate failed: " + str(res))

        if st.session_state.get("translated_text"):
            st.text_area(f"Translated story ({LANGUAGES.get(target_lang)})", value=st.session_state["translated_text"], height=260, key="translated_box", placeholder="Translated story appears here...")

        st.markdown("**Text-to-Speech**")
        # TTS language dropdown with full names
        tts_lang = st.selectbox("TTS language code (gTTS):", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=0)
        tts_text = st.text_area("Text to speak (edit or paste story here)", 
                               value=st.session_state.get("translated_text") or st.session_state.get("generated_story_text",""),
                               height=200, key="tts_text", placeholder="Text to convert to speech")
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
