from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .ai.diagnose import diagnose_project
from .ai.lyrics import generate_lyrics
from .ai.phonemes import draft_phonemes
from .ai.tuning import auto_tune, generate_harmony
from .models import (
    DiagnoseRequest,
    HarmonyRequest,
    LyricsRequest,
    PhonemeRequest,
    RenderRequest,
    TuneRequest,
    VoicebankImportRequest,
)
from .storage import TMP_DIR, ensure_dirs, list_voicebank_manifests, save_voicebank_manifest
from .synth.engine import render_project
from .voicebank import import_voicebank_zip, scan_voicebank

app = FastAPI(title="NextUSinger API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    ensure_dirs()


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "app": "NextUSinger", "version": "0.1.0"}


@app.post("/api/voicebanks/import")
def import_voicebank(req: VoicebankImportRequest):
    try:
        manifest = scan_voicebank(req.path)
        save_voicebank_manifest(manifest)
        return manifest
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/voicebanks/import-zip")
async def import_voicebank_zip_upload(file: UploadFile = File(...)):
    filename = file.filename or "voicebank.zip"
    if not filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip voicebank uploads are supported.")

    ensure_dirs()
    tmp_path = TMP_DIR / f"voicebank-upload-{uuid.uuid4().hex}.zip"

    try:
        with tmp_path.open("wb") as out:
            while chunk := await file.read(1024 * 1024):
                out.write(chunk)

        manifest = import_voicebank_zip(tmp_path, source_name=filename)
        save_voicebank_manifest(manifest)
        return manifest
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        tmp_path.unlink(missing_ok=True)


@app.get("/api/voicebanks")
def list_voicebanks():
    return list_voicebank_manifests()


@app.post("/api/synthesis/render")
def render(req: RenderRequest):
    try:
        return render_project(req.project, req.voicebank_id, req.track_id, req.mode, req.output_name)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/synthesis/file")
def get_wav(path: str):
    wav = Path(path).expanduser().resolve()
    if not wav.exists() or wav.suffix.lower() != ".wav":
        raise HTTPException(status_code=404, detail="WAV not found")
    return FileResponse(str(wav), media_type="audio/wav", filename=wav.name)


@app.post("/api/ai/lyrics")
def api_lyrics(req: LyricsRequest):
    return generate_lyrics(req)


@app.post("/api/ai/phonemes")
def api_phonemes(req: PhonemeRequest):
    return draft_phonemes(req)


@app.post("/api/ai/tune")
def api_tune(req: TuneRequest):
    return auto_tune(req)


@app.post("/api/ai/harmony")
def api_harmony(req: HarmonyRequest):
    return generate_harmony(req)


@app.post("/api/ai/diagnose")
def api_diagnose(req: DiagnoseRequest):
    return diagnose_project(req)
