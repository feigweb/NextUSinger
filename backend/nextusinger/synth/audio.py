from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf


def midi_to_hz(midi: float) -> float:
    return 440.0 * (2.0 ** ((midi - 69.0) / 12.0))


def write_wav(path: str | Path, audio: np.ndarray, sample_rate: int = 44100) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if audio.ndim == 1:
        audio = audio[:, None]
    audio = np.clip(audio, -1.0, 1.0)
    sf.write(path, audio, sample_rate)


def soft_limiter(audio: np.ndarray, drive: float = 1.2) -> np.ndarray:
    return np.tanh(audio * drive) / np.tanh(drive)
