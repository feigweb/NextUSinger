# Architecture

NextUSinger Studio is split into three layers.

## 1. Editor/UI

The React front end is intentionally thin. It edits a JSON project model and calls the local API. This allows later replacement with a heavier timeline/piano-roll renderer, WebAudio preview, or a native canvas engine without changing the backend.

## 2. Core backend

The FastAPI backend owns:

- voicebank discovery and manifest persistence;
- project validation;
- AI assistant endpoints;
- render orchestration;
- file export.

The data model is in `backend/nextusinger/models.py`. Use this as the stable contract between UI and engines.

## 3. Synthesis adapters

Real singing synthesis is implemented through adapters. The first adapter is `diffsinger-external`, which writes a neutral `nextusinger.score.v1` JSON and calls an external command specified by `NEXTUSINGER_DIFFSINGER_CMD`.

Why external instead of vendoring DiffSinger?

- Different DiffSinger/OpenVPI forks use different preprocessing and inference CLIs.
- Voicebank/model licenses are separate from the studio license.
- Users can keep GPU-specific environments isolated.

The fallback `mock-preview` engine is deliberately simple. It verifies note timing, export, front-end transport, and API shape only.

## Future milestones

1. Native OpenVPI config schema reader.
2. ONNX Runtime adapter for exported acoustic/vocoder models.
3. Real phoneme dictionary loading per voicebank.
4. Multi-track mixer and stems.
5. Project import/export for MIDI, USTX/OpenUTAU, MusicXML.
6. Plugin SDK for AI assistants and custom renderers.
