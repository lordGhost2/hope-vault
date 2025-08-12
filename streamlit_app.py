import streamlit as st
import requests
from urllib.parse import urljoin
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh

# ========= Config & Page setup =========
API_BASE_DEFAULT = "http://127.0.0.1:8000/api"
st.set_page_config(page_title="Hope Vault — Demo", layout="wide", page_icon=":sparkles:")

# Sidebar controls
API_BASE = st.sidebar.text_input("Backend base URL", API_BASE_DEFAULT)
USER_ID = st.sidebar.text_input("Demo user id", "demo-user")

# ======= Helpers =======
LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil"
}


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

# ======= Styling (MAANG-inspired clean theme) =======
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Hero */
    .hero { padding: 26px; border-radius:14px; margin-bottom:18px; display:flex; align-items:center; gap:18px; }
    .hero .title { font-size:28px; font-weight:800; margin:0; background:linear-gradient(90deg,#7b2ff7,#0a84ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent }
    .hero .subtitle { margin:0; color:var(--secondary); font-size:14px }

    /* Card */
    .card { padding:14px; border-radius:12px; background:var(--card-bg); box-shadow:0 8px 24px rgba(2,6,23,0.15); }

    /* Buttons */
    .stButton>button { border-radius:10px; padding:10px 14px; font-weight:600 }

    /* Small utilities */
    .muted { color: #6b7280; font-size:0.9rem }
    .entries { max-height: 280px; overflow:auto; padding-right:6px }

    /* Light/Dark adjustments */
    @media (prefers-color-scheme: dark) {
        :root { --card-bg: #0f1724; --secondary: #94a3b8 }
        .slide-caption { color: #e6eef8 }
    }
    @media (prefers-color-scheme: light) {
        :root { --card-bg: #ffffff; --secondary: #6b7280 }
        .slide-caption { color: #0b1220 }
    }

    /* Slideshow image sizing */
    img.fixed { width:100% !important; height:380px !important; object-fit:cover !important; border-radius:10px }
    </style>
    """,
    unsafe_allow_html=True,
)

# ======= Header / Hero =======
col_h1, col_h2 = st.columns([4,1])
with col_h1:
    st.markdown('<div class="hero card"><div><div class="title">Hope Vault</div><div class="subtitle">AI-powered memory vault → story → audio — gentle, private & wholesome</div></div></div>', unsafe_allow_html=True)
with col_h2:
    # Live Kolkata Clock (small)
    st_autorefresh(interval=1000, limit=None, key='header_clock')
    tz = pytz.timezone('Asia/Kolkata')
    st.caption('Local time (Kolkata)')
    st.markdown(f"<div style='font-weight:700;font-size:14px'>{datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)

st.markdown("---")

# ======= Slideshow =======
st.markdown("### Peaceful moments — click arrows or let it inspire you")
slides = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1400&q=80",
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1400&q=80",
    "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1400&q=80",
]
captions = [
    "Breathe — pastel horizons",
    "Shorelines — gentle reflection",
    "Mountains — stillness within",
]

if 'slide_idx' not in st.session_state:
    st.session_state['slide_idx'] = 0
if 'slide_autorefresh_prev' not in st.session_state:
    st.session_state['slide_autorefresh_prev'] = None

# Auto-rotate control
auto_rotate = st.checkbox('Auto-rotate slides', value=True, key='auto_rotate_slides')

# If auto-rotate enabled, use st_autorefresh to tick every 5 seconds
if auto_rotate:
    slideshow_tick = st_autorefresh(interval=5000, limit=None, key='slideshow_autorefresh')
    # when tick increments, advance slide index once
    if st.session_state.get('slide_autorefresh_prev') is None:
        st.session_state['slide_autorefresh_prev'] = slideshow_tick
    elif slideshow_tick != st.session_state['slide_autorefresh_prev']:
        st.session_state['slide_idx'] = (st.session_state.get('slide_idx', 0) + 1) % len(slides)
        st.session_state['slide_autorefresh_prev'] = slideshow_tick

# Render slideshow with manual controls
l, m, r = st.columns([1,8,1])
with l:
    if st.button('◀'):
        st.session_state['slide_idx'] = (st.session_state['slide_idx'] - 1) % len(slides)
        # reset autorefresh counter to avoid immediate auto-advance
        st.session_state['slide_autorefresh_prev'] = None
with m:
    idx = st.session_state['slide_idx']
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.image(slides[idx], use_container_width=True)
    st.markdown(f"<div class='slide-caption' style='padding:8px 6px'>{captions[idx]}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
with r:
    if st.button('▶'):
        st.session_state['slide_idx'] = (st.session_state['slide_idx'] + 1) % len(slides)
        st.session_state['slide_autorefresh_prev'] = None

st.markdown('---')

# ======= Main area as tabs for clean MAANG-like UX =======
tab1, tab2, tab3 = st.tabs(["Add Memory", "Vault & Story", "Translate & TTS"]) 

# ---- Tab 1: Add Memory ----
with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    with st.form('add_memory'):
        st.header('Add a memory (daily prompt)')
        with st.expander('Get a prompt from backend'):
            prompt_resp = api_get('prompt', params={'lang': 'en'})
            if 'prompt' in prompt_resp:
                st.info(prompt_resp['prompt'])
            else:
                st.warning('Could not fetch prompt. Backend URL okay?')

        text = st.text_area('Write a short memory', height=140)
        lang = st.selectbox('Language', options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x])
        if st.form_submit_button('Save memory'):
            if not text.strip():
                st.warning('Please write a short memory first.')
            else:
                payload = {'user_id': USER_ID, 'text': text.strip(), 'language': lang}
                res = api_post('entry', json=payload)
                if res.get('status') == 'saved':
                    st.success('Memory saved ✅')
                else:
                    st.error(f"Save failed: {res}")
    st.markdown('</div>', unsafe_allow_html=True)

# ---- Tab 2: Vault & Story ----
with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header('Your Hope Vault')
    if st.button('Refresh vault'):
        pass
    vault = api_get('vault', params={'user_id': USER_ID})
    if vault.get('entries') is None:
        st.error('Unable to fetch vault. Is backend running and CORS allowed?')
    else:
        entries = vault.get('entries', [])
        if not entries:
            st.info('No memories yet. Add one in the Add Memory tab.')
        else:
            st.markdown('<div class="entries">', unsafe_allow_html=True)
            for e in entries[::-1]:
                ts = e.get('timestamp','')[:19]
                st.markdown(f"**{ts}** — {e.get('text')}")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('---')
    st.header('Generate uplifting story')
    with st.form('gen_story'):
        theme = st.text_input('Theme (e.g., perseverance, hope)', value='perseverance')
        gen_lang = st.selectbox('Story language', options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x])
        max_len = st.slider('Max length (tokens)', min_value=80, max_value=400, value=200)
        if st.form_submit_button('Generate story'):
            with st.spinner('Generating story...'):
                payload = {'user_id': USER_ID, 'theme': theme, 'language': gen_lang, 'max_length': max_len}
                res = api_post('generate_story', json=payload)
                if res.get('error'):
                    st.error('Generation failed: ' + str(res.get('error')))
                    st.write(res)
                else:
                    story = res.get('story', {}).get('text') or (res.get('story') and res['story'].get('text'))
                    if not story:
                        story = res.get('story') if isinstance(res.get('story'), str) else None
                    if story:
                        st.success('Story generated ✅')
                        st.text_area('Generated Story (editable)', value=story, height=260, key='generated_story_text')
                    else:
                        st.error('No story text found in response. Response:')
                        st.write(res)
    st.markdown('</div>', unsafe_allow_html=True)

# ---- Tab 3: Translate & TTS ----
with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header('Translate & Text-to-Speech')
    st.write('If you want the story in another language, first generate a story → Translate → TTS')

    target_lang = st.selectbox('Select translation language', options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x])
    if st.button(f'Translate last story to {LANGUAGES[target_lang]}'):
        story_text = st.session_state.get('generated_story_text', '')
        if not story_text:
            st.warning('Generate a story first.')
        else:
            with st.spinner('Translating...'):
                res = api_post('translate', json={'text': story_text, 'target_lang': target_lang})
                if res.get('translatedText'):
                    st.session_state['translated_text'] = res['translatedText']
                    st.success(f"Translated to {LANGUAGES[target_lang]} ✅")
                else:
                    st.error('Translate failed: ' + str(res))

    if st.session_state.get('translated_text'):
        st.text_area('Translated story', value=st.session_state['translated_text'], height=220, key='translated_box')

    st.markdown('---')
    st.subheader('Text-to-Speech')
    tts_lang = st.selectbox('TTS language', options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x])
    tts_text = st.text_area('Text to speak (edit or paste story here)', value=st.session_state.get('translated_text') or st.session_state.get('generated_story_text',''), height=200, key='tts_text')
    slow = st.checkbox('Slow voice', value=False)
    if st.button('Generate audio'):
        if not tts_text.strip():
            st.warning('Provide text to convert to speech.')
        else:
            with st.spinner('Generating audio...'):
                res = api_post('text_to_speech', json={'text': tts_text, 'language': tts_lang, 'slow': slow})
                if res.get('error'):
                    st.error('TTS failed: ' + str(res))
                else:
                    public = res.get('public_url') or res.get('audio_file')
                    st.success('Audio ready')
                    st.write('Public URL:', public)
                    try:
                        st.audio(public)
                    except Exception:
                        st.info('If stream fails, open the public URL in a new tab to play the file.')
    st.markdown('</div>', unsafe_allow_html=True)

# ======= Reminder (30-min) =======
if 'last_notification' not in st.session_state:
    st.session_state['last_notification'] = datetime.now()

if datetime.now() - st.session_state['last_notification'] >= timedelta(minutes=30):
    st.balloons()
    st.info('💡 Take a moment to write something inspiring in your Hope Vault!')
    st.session_state['last_notification'] = datetime.now()
