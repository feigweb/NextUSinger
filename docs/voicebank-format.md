# Voicebank Import Format

NextUSinger does not require one fixed layout. It scans a directory and records what it finds.

## Recommended layout

```text
MySinger/
  manifest.json                 # optional but recommended
  configs/
    acoustic.yaml
    variance.yaml
  checkpoints/
    acoustic.ckpt
    variance.ckpt
  vocoders/
    nsf_hifigan.onnx
  dictionaries/
    pinyin.dict
  character.png
```

## Minimal `manifest.json`

```json
{
  "name": "My Singer",
  "speaker": "MySinger",
  "language": "zh",
  "sample_rate": 44100,
  "engine": "openvpi-diffsinger"
}
```

## Import result

The scanner creates a `nextusinger.voicebank.v1` manifest under `~/.nextusinger/voicebanks`. It does not copy large model files by default; it keeps absolute references to the original directory.

## Safety and licensing

Only import voicebanks you have permission to use. Do not commit model weights to GitHub unless the model license explicitly allows redistribution.
