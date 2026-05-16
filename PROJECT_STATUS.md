# Project Status

This package is a working prototype scaffold.

## Working now

- Backend starts with FastAPI.
- Voicebank scanner can import real directories and write manifests.
- Render endpoint exports WAV with mock engine.
- External DiffSinger command adapter is implemented.
- Frontend can import voicebank paths, show scanned metadata, edit simple notes, call AI helper endpoints, and render WAV.
- Tests cover scanner and AI pitch/harmony helpers.

## Not yet production-grade

- The front-end piano roll is a minimal grid, not a full DAW-grade editor.
- Real DiffSinger inference depends on your external environment and voicebank format.
- No bundled voicebanks or model weights.
- No native packaging pipeline yet, only optional Electron shell.
