import os
import json
import uuid
from datetime import datetime
from typing import List
import requests

# Transformers
from transformers import pipeline, set_seed

# gTTS
from gtts import gTTS

# --- Config ---
DB_FILE = "hope_vault_db.json"
UPLOAD_DIR = "uploads"
AUDIO_DIR = "generated_audio"
LIBRETRANSLATE_URL = "https://libretranslate.de/translate"  # public instance
HF_MODEL_NAME = "distilgpt2"  # light local model; change if you want larger

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# initialize or load DB
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"users": {}}, f, indent=2)

def _read_db():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _write_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Initialize text generator pipeline (takes time on first load)
try:
    text_generator = pipeline("text-generation", model=HF_MODEL_NAME)
    set_seed(42)
    print("Text generator pipeline loaded:", HF_MODEL_NAME)
except Exception as e:
    text_generator = None
    print("Warning: transformer pipeline failed to load:", e)


# -----------------------
# Basic UI helpers
# -----------------------
def get_daily_prompt(lang="en"):
    prompts = {
        "en": "What's one small thing that made you smile today?",
        "hi": "आज आपको किस छोटी सी बात ने खुश किया?",
        "bn": "আজ আপনার কোন ছোট্ট ঘটনা আপনাকে হাসিয়েছে?",
        "ta": "இன்று உங்களை மகிழ வைத்த ஒரு சிறு விஷயம் என்ன?"
    }
    return prompts.get(lang, prompts["en"])


# -----------------------
# Memory storage
# -----------------------
def save_memory(user_id: str, text: str, language: str = "en"):
    db = _read_db()
    if user_id not in db["users"]:
        db["users"][user_id] = {"entries": [], "stories": []}
    entry = {
        "id": str(uuid.uuid4()),
        "text": text,
        "language": language,
        "timestamp": datetime.utcnow().isoformat()
    }
    db["users"][user_id]["entries"].append(entry)
    _write_db(db)
    return {"status": "saved", "entry": entry}


def get_user_vault(user_id: str):
    db = _read_db()
    user = db["users"].get(user_id)
    if not user:
        return {"user_id": user_id, "entries": [], "stories": []}
    return {"user_id": user_id, "entries": user.get("entries", []), "stories": user.get("stories", [])}


# -----------------------
# Story generation (updated to avoid HF warnings)
# -----------------------
def _build_story_prompt(entries: List[dict], theme: str, language: str):
    header = f"Write a short, warm, uplifting story in {language} about resilience and hope. Use the theme: {theme}.\n\n"
    header += "Here are some brief memories:\n"
    for e in entries[-5:]:
        ts = e.get("timestamp", "")[:10]
        header += f"- {ts}: {e.get('text','')}\n"
    header += "\nNow write a gentle uplifting narrative (120-220 words) that weaves these memories and ends with a positive affirmation."
    return header

def generate_uplifting_story(user_id: str, theme: str = "perseverance", language: str = "en", max_length: int = 200):
    db = _read_db()
    user = db["users"].get(user_id)
    if not user or not user.get("entries"):
        return {"error": "No entries found for user. Add memories first via /api/entry."}

    entries = user["entries"]
    prompt = _build_story_prompt(entries, theme, language)

    # --- NEW: explicit generation params to avoid HF warnings ---
    max_new_tokens = min(256, max(64, max_length))
    try:
        if text_generator is None:
            story = " ".join([e["text"] for e in entries[-3:]])
            story = f"{story}\n\n(Unable to generate full narrative because model unavailable.)"
        else:
            gen = text_generator(
                prompt,
                max_new_tokens=max_new_tokens,
                truncation=True,
                do_sample=True,
                top_p=0.95,
                temperature=0.8,
                num_return_sequences=1
            )
            # Hugging Face returns generated_text or text depending on model/pipeline version
            story = gen[0].get("generated_text") or gen[0].get("text") or str(gen[0])
    except Exception as e:
        story = "Error generating story: " + str(e)

    # Save story in DB
    story_record = {
        "id": str(uuid.uuid4()),
        "text": story,
        "theme": theme,
        "language": language,
        "timestamp": datetime.utcnow().isoformat()
    }
    db["users"][user_id].setdefault("stories", []).append(story_record)
    _write_db(db)
    return {"story": story_record}


# -----------------------
# Translation via LibreTranslate
# -----------------------
def translate_text(text: str, target_lang: str = "hi"):
    try:
        resp = requests.post(
            LIBRETRANSLATE_URL,
            data={
                "q": text,
                "source": "auto",
                "target": target_lang,
                "format": "text"
            },
            timeout=15
        )
        resp.raise_for_status()
        translated = resp.json().get("translatedText")
        return {"translatedText": translated}
    except Exception as e:
        return {"error": f"Translation failed: {e}"}


# -----------------------
# Text-to-Speech (gTTS)
# -----------------------
def text_to_speech(text: str, language: str = "en", slow: bool = False):
    try:
        filename = f"{AUDIO_DIR}/story_{uuid.uuid4().hex}.mp3"
        tts = gTTS(text=text, lang=language, slow=slow)
        tts.save(filename)
        return {"audio_file": filename}
    except Exception as e:
        return {"error": f"TTS failed: {e}"}


# -----------------------
# Simple upload saving (images/audio)
# -----------------------
async def save_upload(user_id: str, upload):
    fname = f"{user_id}_{uuid.uuid4().hex}_{upload.filename}"
    path = os.path.join(UPLOAD_DIR, fname)
    with open(path, "wb") as f:
        content = await upload.read()
        f.write(content)
    return path
