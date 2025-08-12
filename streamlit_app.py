# ------------------------------
# 1. Merged Version (Everything in One Streamlit File)
# ------------------------------

import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Hope Vault", layout="wide")

# Custom CSS for Gen Z gradient, glow, and light/dark adaptation
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
    @media (prefers-color-scheme: dark) {
        body {
            background-color: #121212;
            color: white;
        }
    }
    @media (prefers-color-scheme: light) {
        body {
            background-color: #ffffff;
            color: black;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Title & Subtitle
st.markdown("<div class='title'>Hope Vault</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Your secure place for inspiration & memories ✨</div>", unsafe_allow_html=True)

# Example feature: Create and save a story
st.subheader("Create a Memory")
user_input = st.text_area("Write something inspiring...")

if st.button("Save to Vault"):
    if user_input.strip():
        st.success(f"Saved on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ✅")
    else:
        st.error("Please write something before saving.")
