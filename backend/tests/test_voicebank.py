from pathlib import Path

from nextusinger.voicebank import scan_voicebank


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
