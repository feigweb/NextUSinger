from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

from .models import VoicebankKind, VoicebankManifest

MODEL_EXTS = {".ckpt", ".pth", ".pt", ".onnx", ".safetensors"}
CONFIG_EXTS = {".yaml", ".yml", ".json"}
DICT_EXTS = {".dict", ".txt", ".csv"}
AUDIO_EXTS = {".wav", ".flac", ".mp3"}


def _slug(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_.-]+", "-", text.strip()).strip("-").lower()
    return text or "voicebank"


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _read_metadata_file(path: Path) -> dict[str, Any]:
    try:
        if path.suffix.lower() in {".yaml", ".yml"}:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _flatten_dict(data: dict[str, Any]) -> str:
    parts: list[str] = []
    for key, value in data.items():
        if isinstance(value, dict):
            parts.append(f"{key} {_flatten_dict(value)}")
        else:
            parts.append(f"{key} {value}")
    return " ".join(parts).lower()


def scan_voicebank(root: str | Path) -> VoicebankManifest:
    base = Path(root).expanduser().resolve()
    if not base.exists() or not base.is_dir():
        raise FileNotFoundError(f"Voicebank directory does not exist: {base}")

    files = [p for p in base.rglob("*") if p.is_file()]
    metadata_candidates = [
        p for p in files
        if p.name.lower() in {"manifest.json", "voicebank.json", "character.yaml", "character.yml", "config.yaml", "config.yml"}
    ]

    raw_metadata: dict[str, Any] = {}
    for candidate in metadata_candidates:
        raw_metadata.update(_read_metadata_file(candidate))

    name = (
        raw_metadata.get("name")
        or raw_metadata.get("speaker")
        or raw_metadata.get("spk")
        or raw_metadata.get("title")
        or base.name
    )
    speaker = raw_metadata.get("speaker") or raw_metadata.get("spk") or raw_metadata.get("singer")
    language = raw_metadata.get("language") or raw_metadata.get("lang")
    sample_rate = raw_metadata.get("sample_rate") or raw_metadata.get("audio_sample_rate") or raw_metadata.get("sampling_rate")

    fingerprint = hashlib.sha1(str(base).encode("utf-8")).hexdigest()[:10]
    voicebank_id = f"{_slug(str(name))}-{fingerprint}"

    config_files: list[str] = []
    acoustic_models: list[str] = []
    vocoders: list[str] = []
    variance_models: list[str] = []
    dictionaries: list[str] = []
    warnings: list[str] = []
    icon: str | None = None

    for path in files:
        rel = _rel(base, path)
        lower = rel.lower()
        suffix = path.suffix.lower()

        if suffix in CONFIG_EXTS and any(k in lower for k in ["config", "manifest", "character", "params"]):
            config_files.append(rel)
        if suffix in MODEL_EXTS:
            if any(k in lower for k in ["vocoder", "hifigan", "nsf", "pc-ddsp", "wav"]):
                vocoders.append(rel)
            elif any(k in lower for k in ["variance", "pitch", "f0", "energy", "breath", "dur"]):
                variance_models.append(rel)
            else:
                acoustic_models.append(rel)
        if suffix in DICT_EXTS and any(k in lower for k in ["dict", "dictionary", "phoneme", "pinyin", "g2p"]):
            dictionaries.append(rel)
        if suffix in {".png", ".jpg", ".jpeg", ".webp"} and any(k in lower for k in ["icon", "avatar", "portrait", "character"]):
            icon = icon or rel

    corpus_text = " ".join([base.name.lower(), *[p.lower() for p in config_files], _flatten_dict(raw_metadata)])
    if "openvpi" in corpus_text or "variance" in corpus_text or "breathiness" in corpus_text:
        kind = VoicebankKind.OPENVPI
    elif any(p.endswith(".onnx") for p in acoustic_models + vocoders + variance_models):
        kind = VoicebankKind.ONNX
    elif "diffsinger" in corpus_text or acoustic_models:
        kind = VoicebankKind.DIFFSINGER
    else:
        kind = VoicebankKind.UNKNOWN

    if not acoustic_models and not config_files:
        warnings.append("未找到明显的声学模型或配置文件；请确认这是 DiffSinger/OpenVPI 声库根目录。")
    if not vocoders:
        warnings.append("未识别到 vocoder；真实推理时可能需要在外部 DiffSinger 环境中配置。")
    if kind == VoicebankKind.UNKNOWN:
        warnings.append("声库类型无法确定，将以通用 DiffSinger 兼容目录处理。")

    try:
        sample_rate_int = int(sample_rate) if sample_rate else None
    except Exception:
        sample_rate_int = None

    return VoicebankManifest(
        id=voicebank_id,
        name=str(name),
        kind=kind,
        root=str(base),
        sample_rate=sample_rate_int,
        language=str(language) if language else None,
        speaker=str(speaker) if speaker else None,
        config_files=sorted(config_files),
        acoustic_models=sorted(acoustic_models),
        vocoders=sorted(vocoders),
        variance_models=sorted(variance_models),
        dictionaries=sorted(dictionaries),
        icon=icon,
        warnings=warnings,
        raw_metadata=raw_metadata,
    )
