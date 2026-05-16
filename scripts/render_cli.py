from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from nextusinger.models import Project, RenderMode  # noqa: E402
from nextusinger.synth.engine import render_project  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a NextUSinger project to WAV")
    parser.add_argument("project", type=Path)
    parser.add_argument("--voicebank-id", default=None)
    parser.add_argument("--track-id", default=None)
    parser.add_argument("--out", default="render.wav")
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()

    project = Project.model_validate(json.loads(args.project.read_text(encoding="utf-8")))
    result = render_project(project, args.voicebank_id, args.track_id, RenderMode.MOCK if args.mock else RenderMode.AUTO, Path(args.out).name)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    Path(result.wav_path).replace(out)
    print(json.dumps({**result.model_dump(), "wav_path": str(out)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
