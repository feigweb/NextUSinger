from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable

from .models import VoicebankManifest


APP_DIR = Path(os.environ.get("NEXTUSINGER_HOME", Path.home() / ".nextusinger"))
VOICEBANK_DIR = APP_DIR / "voicebanks"
RENDER_DIR = APP_DIR / "renders"
TMP_DIR = APP_DIR / "tmp"


def ensure_dirs() -> None:
    for path in (APP_DIR, VOICEBANK_DIR, RENDER_DIR, TMP_DIR):
        path.mkdir(parents=True, exist_ok=True)


def save_voicebank_manifest(manifest: VoicebankManifest) -> Path:
    ensure_dirs()
    path = VOICEBANK_DIR / f"{manifest.id}.json"
    path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_voicebank_manifest(voicebank_id: str) -> VoicebankManifest | None:
    ensure_dirs()
    path = VOICEBANK_DIR / f"{voicebank_id}.json"
    if not path.exists():
        return None
    return VoicebankManifest.model_validate_json(path.read_text(encoding="utf-8"))


def list_voicebank_manifests() -> list[VoicebankManifest]:
    ensure_dirs()
    manifests: list[VoicebankManifest] = []
    for path in sorted(VOICEBANK_DIR.glob("*.json")):
        try:
            manifests.append(VoicebankManifest.model_validate_json(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return manifests


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
