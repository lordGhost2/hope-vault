from fastapi import APIRouter, UploadFile, File, Form, Request
from pydantic import BaseModel
from typing import Optional
import services
import os

router = APIRouter(prefix="/api", tags=["hopevault"])


class EntryIn(BaseModel):
    user_id: str
    text: str
    language: Optional[str] = "en"


class StoryReq(BaseModel):
    user_id: str
    theme: Optional[str] = "perseverance"
    language: Optional[str] = "en"
    max_length: Optional[int] = 200


class TranslateReq(BaseModel):
    text: str
    target_lang: str


class TTSReq(BaseModel):
    text: str
    language: str = "en"
    slow: bool = False


@router.get("/prompt")
def get_prompt(lang: Optional[str] = "en"):
    return {"prompt": services.get_daily_prompt(lang)}


@router.post("/entry")
async def add_entry(payload: EntryIn):
    res = services.save_memory(payload.user_id, payload.text, payload.language)
    return res


@router.get("/vault")
def get_vault(user_id: str):
    return services.get_user_vault(user_id)


@router.post("/generate_story")
def generate_story(req: StoryReq):
    return services.generate_uplifting_story(req.user_id, req.theme, req.language, req.max_length)


@router.post("/translate")
def translate(req: TranslateReq):
    return services.translate_text(req.text, req.target_lang)


@router.post("/text_to_speech")
def text_to_speech(req_body: TTSReq, request: Request):
    res = services.text_to_speech(req_body.text, req_body.language, req_body.slow)
    if "error" in res:
        return res
    local_path = res.get("audio_file")
    filename = os.path.basename(local_path)
    base = str(request.base_url).rstrip("/")
    public_url = f"{base}/media/{filename}"
    return {"audio_file": local_path, "public_url": public_url}


# Optional: upload image / audio files (saved locally) - minimal example
@router.post("/upload")
async def upload_file(user_id: str = Form(...), file: UploadFile = File(...)):
    path = await services.save_upload(user_id, file)
    return {"uploaded_to": path}
