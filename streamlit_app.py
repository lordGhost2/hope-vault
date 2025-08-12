import streamlit as st
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh

# Page config
st.set_page_config(page_title="Hope Vault", layout="wide")

# Inject CSS for styling and dark/light mode
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    .title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #8e2de2, #4a00e0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        text-shadow: 0px 0px 15px rgba(142,45,226,0.4);
        margin-bottom: 0;
    }
    .subtitle {
        font-size: 1.2rem;
        text-align: center;
        opacity: 0.85;
        margin-top: 0;
        margin-bottom: 30px;
    }
    .stButton>button {
        font-size: 1.1rem;
        border-radius: 12px;
        padding: 0.6em 1.2em;
        background: linear-gradient(135deg, #8e2de2, #4a00e0);
        color: white;
        border: none;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0px 4px 15px rgba(142,45,226,0.5);
    }
    .slide-caption {
        font-size: 1.05rem;
        text-align: center;
        color: rgba(255,255,255,0.95);
        padding-top: 8px;
        user-select: none;
    }
    .slide-box {
        border-radius: 12px; 
        overflow: hidden; 
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        user-select: none;
    }
    @media (prefers-color-scheme: dark) {
        body {
            background: linear-gradient(135deg, #0f1724, #081226);
            color: #f7f7fb;
        }
    }
    @media (prefers-color-scheme: light) {
        body {
            background: linear-gradient(135deg, #fff6fb, #f0f7ff);
            color: #0b1220;
        }
    }
    img.fixed-image {
        width: 100%;
        height: 400px;
        object-fit: cover;
        border-radius: 12px;
        user-select: none;
    }
    </style>
""", unsafe_allow_html=True)

# Title and subtitle
st.markdown("<h1 class='title'>Hope Vault</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your secure place for inspiration & memories ✨</p>", unsafe_allow_html=True)

# --- Image slideshow ---
st.markdown("### Peaceful Moments — slide through for calmness")

slides = [
    "https://source.unsplash.com/1200x700/?pastel,landscape",
    "https://source.unsplash.com/1200x700/?pastel,beach",
    "https://source.unsplash.com/1200x700/?pastel,mountains",
    "https://source.unsplash.com/1200x700/?pastel,sunrise",
    "https://source.unsplash.com/1200x700/?calm,sea"
]

captions = [
    "Breathe — gentle pastel horizons",
    "Peaceful shorelines — let your thoughts settle",
    "Quiet mountains — find stillness within",
    "Soft sunrises — a fresh start always possible",
    "Calm waters — reflection brings clarity"
]

if "slide_idx" not in st.session_state:
    st.session_state.slide_idx = 0

left_col, mid_col, right_col = st.columns([1,6,1])
with left_col:
    if st.button("◀"):
        st.session_state.slide_idx = (st.session_state.slide_idx - 1) % len(slides)
with mid_col:
    idx = st.session_state.slide_idx
    st.markdown(f"<div class='slide-box'>", unsafe_allow_html=True)
    st.image(slides[idx], use_container_width=True, output_format="auto", caption=captions[idx], clamp=False)
    st.markdown(f"</div>", unsafe_allow_html=True)
with right_col:
    if st.button("▶"):
        st.session_state.slide_idx = (st.session_state.slide_idx + 1) % len(slides)

st.markdown("---")

# --- Calendar & live Kolkata clock ---
col1, col2 = st.columns(2)
with col1:
    st.date_input("Today's Date", datetime.now().date())
with col2:
    # Autorefresh every second to update clock
    st_autorefresh(interval=1000, limit=None, key="liveclock")
    kolkata_tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(kolkata_tz)
    st.markdown(f"<h3 style='text-align:center;'>🕒 Asia/Kolkata Time: {now.strftime('%Y-%m-%d %H:%M:%S')}</h3>", unsafe_allow_html=True)

st.markdown("---")

# --- Thoughts input area ---
st.subheader("📝 Your Thoughts")
thought = st.text_area("Write something inspiring...")

if st.button("Save to Vault"):
    if thought.strip():
        st.success(f"Saved on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ✅")
    else:
        st.error("Please write something before saving.")

# --- Motivational message every 30 minutes ---
if "last_notification" not in st.session_state:
    st.session_state.last_notification = datetime.now()

if datetime.now() - st.session_state.last_notification >= timedelta(minutes=30):
    st.balloons()
    st.info("💡 Take a moment to write something inspiring in your Hope Vault!")
    st.session_state.last_notification = datetime.now()
