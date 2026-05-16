from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from ..models import Project, RenderMode, RenderResult, Track, VoicebankManifest
from ..storage import RENDER_DIR, ensure_dirs, load_voicebank_manifest
from .diffsinger import ExternalDiffSingerError, render_with_external_diffsinger
from .mock_engine import render_mock


def _select_track(project: Project, track_id: str | None) -> Track:
    if track_id:
        for track in project.tracks:
            if track.id == track_id:
                return track
        raise ValueError(f"Track not found: {track_id}")
    if not project.tracks:
        raise ValueError("Project has no tracks")
    return project.tracks[0]


def render_project(project: Project, voicebank_id: str | None, track_id: str | None, mode: RenderMode, output_name: str) -> RenderResult:
    ensure_dirs()
    track = _select_track(project, track_id)
    voicebank_id = voicebank_id or track.voicebank_id
    voicebank: VoicebankManifest | None = load_voicebank_manifest(voicebank_id) if voicebank_id else None
    safe_name = Path(output_name).name or f"render-{uuid4().hex}.wav"
    if not safe_name.lower().endswith(".wav"):
        safe_name += ".wav"
    output_path = RENDER_DIR / f"{uuid4().hex}-{safe_name}"

    diagnostics: list[str] = []
    if mode in {RenderMode.AUTO, RenderMode.DIFFSINGER_EXTERNAL} and voicebank is not None:
        try:
            path, duration, external_diags = render_with_external_diffsinger(project, track, voicebank, output_path)
            return RenderResult(
                wav_path=str(path),
                engine="diffsinger-external",
                sample_rate=project.sample_rate,
                duration_seconds=duration,
                diagnostics=external_diags,
            )
        except ExternalDiffSingerError as exc:
            if mode == RenderMode.DIFFSINGER_EXTERNAL:
                raise
            diagnostics.append(f"外部 DiffSinger 不可用，已回退到 mock engine：{exc}")

    path, duration = render_mock(project, track, output_path, voicebank)
    return RenderResult(
        wav_path=str(path),
        engine="mock-preview",
        sample_rate=project.sample_rate,
        duration_seconds=duration,
        diagnostics=diagnostics + ["当前音频由 mock engine 生成，仅用于验证工程/导出流程。"],
    )
