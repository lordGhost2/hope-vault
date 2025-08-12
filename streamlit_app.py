import streamlit as st
from datetime import datetime, date
import time

# Page config
st.set_page_config(page_title="Hope Vault", layout="wide")

# Inject adaptive light/dark theme CSS
st.markdown("""
    <style>
    body {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #0e1117;
            --text-color: #ffffff;
        }
    }
    @media (prefers-color-scheme: light) {
        :root {
            --background-color: #ffffff;
            --text-color: #000000;
        }
    }
    .title-text {
        font-size: 3em;
        font-weight: bold;
        background: linear-gradient(90deg, #7b2ff7, #0a84ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<div class='title-text'>🌟 Hope Vault 🌟</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Your safe space for thoughts, peace, and inspiration</p>", unsafe_allow_html=True)

# Peace-themed image carousel
peace_images = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
]
current_img = st.session_state.get("img_idx", 0)
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.image(peace_images[current_img], use_column_width=True, caption="Peace & Serenity")
col1, col2, col3 = st.columns([1, 1, 1])
if col1.button("⬅ Prev"):
    st.session_state.img_idx = (current_img - 1) % len(peace_images)
if col3.button("Next ➡"):
    st.session_state.img_idx = (current_img + 1) % len(peace_images)

# Clock & calendar
colA, colB = st.columns(2)
with colA:
    st.subheader("📅 Calendar")
    selected_date = st.date_input("Pick a date", date.today())
with colB:
    st.subheader("⏰ Current Time")
    st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Journal section
st.subheader("📝 Your Thoughts")
thought = st.text_area("Write something...")
if st.button("Save Entry"):
    st.success("✅ Your thoughts have been saved securely.")

# Motivational timer (30 min alert)
if "last_alert" not in st.session_state:
    st.session_state.last_alert = time.time()

elapsed = time.time() - st.session_state.last_alert
if elapsed >= 1800:  # 30 mins
    st.warning("💡 Motivation: Take a deep breath and jot down one positive thing right now!")
    st.session_state.last_alert = time.time()
