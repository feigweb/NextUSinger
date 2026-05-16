# AI Feature Slots

The current implementation ships rule-based local assistants so the app works without API keys.

## Implemented local endpoints

- Lyrics idea generator
- Phoneme draft generator
- Pitch curve humanizer
- Harmony generator
- Project diagnostics

## Suggested advanced providers

You can add providers under `backend/nextusinger/ai/`:

- local LLM for lyric revision and pronunciation fixes;
- MIDI melody continuation model;
- F0 style transfer from reference singing;
- breath/tension/energy predictors;
- automatic mix/master assistant;
- prompt-to-song arrangement generator.

Provider code should return the same Pydantic response models, so the UI does not need to change.
