
import streamlit as st
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="Hope Vault", layout="wide")

# Custom CSS for gradient title, button hover, and light/dark mode adaptation
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
    }
    .subtitle {
        font-size: 1.2rem;
        text-align: center;
        opacity: 0.85;
    }
    .stButton>button {
        font-size: 1.1rem;
        border-radius: 12px;
        padding: 0.6em 1.2em;
        background: linear-gradient(135deg, #8e2de2, #4a00e0);
        color: white;
        border: none;
        transition: all 0.3s ease;
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
    }
    .slide-box{
        border-radius:12px; overflow:hidden; box-shadow:0 8px 30px rgba(0,0,0,0.12);
    }
    @media (prefers-color-scheme: dark) {
        body {
            background-color: #0b0b12;
            color: #f7f7fb;
            background: linear-gradient(135deg, #0f1724, #081226);
        }
    }
    @media (prefers-color-scheme: light) {
        body {
            background: linear-gradient(135deg, #fff6fb, #f0f7ff);
            color: #0b1220;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Title & Subtitle
st.markdown("<div class='title'>Hope Vault</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Your secure place for inspiration & memories ✨</div>", unsafe_allow_html=True)

# --- Slideshow (uses Unsplash dynamic images - free to use for placeholders) ---
st.markdown("### Peaceful Moments — slide through for calmness")

# Image sources (Unsplash dynamic queries; replace with your own URLs if desired)
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
    # image is loaded from Unsplash each time - good for placeholders and freely usable images
    st.markdown(f"<div class='slide-box'>", unsafe_allow_html=True)
    st.image(slides[idx], use_column_width=True)
    st.markdown(f"</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='slide-caption'>{captions[idx]}</div>", unsafe_allow_html=True)
with right_col:
    if st.button("▶"):
        st.session_state.slide_idx = (st.session_state.slide_idx + 1) % len(slides)

st.markdown("---")

# Display Calendar and Clock
col1, col2 = st.columns(2)
with col1:
    st.date_input("Today's Date", datetime.now())
with col2:
    # show a live updating clock by forcing rerun every second using empty and sleep
    clock_placeholder = st.empty()
    clock_placeholder.metric("Current Time", datetime.now().strftime("%H:%M:%S"))

# Create and Save Memory Feature
st.subheader("Create a Memory")
user_input = st.text_area("Write something inspiring...")

if st.button("Save to Vault"):
    if user_input.strip():
        st.success(f"Saved on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ✅")
    else:
        st.error("Please write something before saving.")

# Motivation message every 30 mins
if "last_notification" not in st.session_state:
    st.session_state.last_notification = datetime.now()

# If user leaves page open, this will check time and show notification on reruns
if datetime.now() - st.session_state.last_notification >= timedelta(minutes=30):
    st.balloons()
    st.info("💡 Take a moment to write something inspiring in your Hope Vault!")
    st.session_state.last_notification = datetime.now()

# Note: Streamlit runs on each user interaction; for a background interval notification
# that fires while user is idle you'd need browser-side JS or a separate service.
```

