import zipfile
from pathlib import Path

import pytest

from nextusinger.voicebank import import_voicebank_zip, scan_voicebank


def test_scan_voicebank(tmp_path: Path):
    (tmp_path / "config.yaml").write_text("name: Demo Singer\nsample_rate: 44100\nlanguage: zh\n", encoding="utf-8")
    (tmp_path / "acoustic.ckpt").write_bytes(b"fake")
    (tmp_path / "nsf_hifigan.onnx").write_bytes(b"fake")
    manifest = scan_voicebank(tmp_path)
    assert manifest.name == "Demo Singer"
    assert manifest.sample_rate == 44100
    assert manifest.acoustic_models == ["acoustic.ckpt"]
    assert manifest.vocoders == ["nsf_hifigan.onnx"]
    assert manifest.ready_for_external_engine


def test_import_voicebank_zip(tmp_path: Path):
    voicebank_dir = tmp_path / "DemoSinger"
    voicebank_dir.mkdir()
    (voicebank_dir / "config.yaml").write_text("name: Zip Singer\nsample_rate: 44100\n", encoding="utf-8")
    (voicebank_dir / "acoustic.ckpt").write_bytes(b"fake")

    zip_path = tmp_path / "voicebank.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        for path in voicebank_dir.rglob("*"):
            archive.write(path, path.relative_to(tmp_path))

    manifest = import_voicebank_zip(zip_path, target_root=tmp_path / "imports")
    assert manifest.name == "Zip Singer"
    assert manifest.acoustic_models == ["acoustic.ckpt"]
    assert manifest.raw_metadata["nextusinger_import"]["source"] == "zip"
    assert Path(manifest.root).exists()


def test_import_voicebank_zip_rejects_path_traversal(tmp_path: Path):
    zip_path = tmp_path / "bad.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("../evil.txt", "bad")

    with pytest.raises(ValueError):
        import_voicebank_zip(zip_path, target_root=tmp_path / "imports")
