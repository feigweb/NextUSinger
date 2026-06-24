from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from nextusinger.storage import save_voicebank_manifest  # noqa: E402
from nextusinger.voicebank import import_voicebank_zip, scan_voicebank  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a DiffSinger/OpenVPI voicebank directory or ZIP")
    parser.add_argument("voicebank", type=Path, help="Voicebank directory or .zip archive")
    parser.add_argument("--no-save", action="store_true", help="Only scan and print the manifest; do not register it")
    args = parser.parse_args()

    voicebank_path = args.voicebank.expanduser().resolve()
    if voicebank_path.suffix.lower() == ".zip":
        manifest = import_voicebank_zip(voicebank_path)
    else:
        manifest = scan_voicebank(voicebank_path)

    if not args.no_save:
        save_voicebank_manifest(manifest)

    print(manifest.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
