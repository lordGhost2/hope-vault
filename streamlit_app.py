import streamlit as st

# Page config
st.set_page_config(page_title="Hope Vault", page_icon="✨", layout="wide")

# Adaptive CSS for light/dark mode with premium MAANG-inspired style
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Pacifico&display=swap');
        
        html, body, [class*="css"]  {
            font-family: 'Poppins', sans-serif;
        }

        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(-10px);}
            to {opacity: 1; transform: translateY(0);}
        }

        h1 {
            font-family: 'Pacifico', cursive;
            font-size: 3rem;
            background: linear-gradient(45deg, #6a11cb, #2575fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: fadeIn 1s ease-in-out;
        }

        @media (prefers-color-scheme: light) {
            body {
                background: linear-gradient(135deg, #ffecd2, #fcb69f);
                color: #2c2c2c;
            }
            .stButton>button {
                background: linear-gradient(45deg, #6a11cb, #2575fc);
                color: white;
                box-shadow: 0 4px 15px rgba(106, 17, 203, 0.4);
            }
        }
        @media (prefers-color-scheme: dark) {
            body {
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: #f0f0f0;
            }
            .stButton>button {
                background: linear-gradient(45deg, #ff758c, #ff7eb3);
                color: white;
                box-shadow: 0 4px 15px rgba(255, 120, 180, 0.4);
            }
        }

        .stButton>button {
            font-size: 1.2rem;
            border-radius: 14px;
            padding: 0.7rem 1.4rem;
            transition: all 0.3s ease-in-out;
        }
        .stButton>button:hover {
            transform: scale(1.05) rotate(-1deg);
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("""<h1>Hope Vault</h1>
<p style='font-size:1.3rem; text-align:center;'>Your safe space to store memories, create uplifting stories, and translate hope into every language 🌸</p>""", unsafe_allow_html=True)

# Story generator
st.subheader("📝 Generate Your Story")
story_prompt = st.text_area("Enter your thoughts or a prompt:")
if st.button("Generate Story"):
    st.success("Here's your hopeful story ✨")
    st.write("Once upon a time in a vault full of dreams...")

# Memory saver
st.subheader("📂 Save a Memory")
memory_text = st.text_area("Write your special memory:")
if st.button("Save Memory"):
    st.success("Memory saved successfully 💖")

# Translation
st.subheader("🌍 Translate Your Story")
selected_lang = st.selectbox("Choose Language", ["Spanish", "French", "German"])
if st.button("Translate"):
    st.success(f"Story translated into {selected_lang} successfully 💫")

# Footer with subtle animation
st.markdown("""<hr><p style='text-align:center; font-size:0.95rem; opacity:0.85;'>Made with 💜 for dreamers everywhere</p>""", unsafe_allow_html=True)
