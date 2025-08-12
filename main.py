# main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# import router after app is created (safe)
from routes import router

# 1) create FastAPI app first
app = FastAPI(
    title="Hope Vault - Free-tier Prototype",
    description="Generative Hope Vault: story generation + translation + TTS (local/free components).",
    version="0.1",
)

# 2) add middleware (CORS) AFTER creating the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # ok for local dev; restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) include router(s)
app.include_router(router)

# 4) mount static directory for audio files
AUDIO_DIR = "generated_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=AUDIO_DIR), name="media")


@app.get("/")
def root():
    return {"ok": True, "message": "Hope Vault backend is running."}
