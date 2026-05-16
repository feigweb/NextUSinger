from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path

from ..models import Project, Track, VoicebankManifest
from ..storage import TMP_DIR, write_json
from .ds_project import project_to_score_json


class ExternalDiffSingerError(RuntimeError):
    pass


def _format_command(template: str, score_json: Path, voicebank_dir: Path, output_wav: Path) -> list[str]:
    command = template.format(
        score_json=str(score_json),
        voicebank_dir=str(voicebank_dir),
        output_wav=str(output_wav),
    )
    return shlex.split(command)


def render_with_external_diffsinger(
    project: Project,
    track: Track,
    voicebank: VoicebankManifest,
    output_path: Path,
) -> tuple[Path, float, list[str]]:
    template = os.environ.get("NEXTUSINGER_DIFFSINGER_CMD")
    if not template:
        raise ExternalDiffSingerError("NEXTUSINGER_DIFFSINGER_CMD is not set")

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    score_path = TMP_DIR / f"{project.id}-{track.id}.score.json"
    write_json(score_path, project_to_score_json(project, track))

    cmd = _format_command(template, score_path, Path(voicebank.root), output_path)
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3600)
    diagnostics = []
    if proc.stdout.strip():
        diagnostics.append(proc.stdout.strip()[-2000:])
    if proc.stderr.strip():
        diagnostics.append(proc.stderr.strip()[-2000:])
    if proc.returncode != 0:
        raise ExternalDiffSingerError(f"External DiffSinger command failed with code {proc.returncode}: {' '.join(cmd)}")
    if not output_path.exists():
        raise ExternalDiffSingerError("External DiffSinger command completed but did not create output wav")

    try:
        import soundfile as sf

        info = sf.info(str(output_path))
        duration = info.frames / info.samplerate
    except Exception:
        duration = 0.0
    return output_path, duration, diagnostics
