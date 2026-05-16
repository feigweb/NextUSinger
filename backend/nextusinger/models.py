from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field


class Note(BaseModel):
    id: str
    start: float = Field(..., description="Start time in beats")
    duration: float = Field(..., gt=0, description="Duration in beats")
    midi: int = Field(..., ge=0, le=127)
    lyric: str = "la"
    phonemes: list[str] = Field(default_factory=list)
    velocity: float = Field(1.0, ge=0.0, le=2.0)
    tension: float = Field(0.0, ge=-1.0, le=1.0)
    breathiness: float = Field(0.0, ge=-1.0, le=1.0)
    energy: float = Field(0.0, ge=-1.0, le=1.0)
    gender: float = Field(0.0, ge=-1.0, le=1.0)


class PitchPoint(BaseModel):
    beat: float
    cents: float = Field(0.0, ge=-2400.0, le=2400.0)


class TempoEvent(BaseModel):
    beat: float = 0.0
    bpm: float = Field(120.0, ge=20.0, le=300.0)


class Track(BaseModel):
    id: str
    name: str = "Vocal"
    voicebank_id: str | None = None
    notes: list[Note] = Field(default_factory=list)
    pitch: list[PitchPoint] = Field(default_factory=list)
    mute: bool = False
    solo: bool = False


class Project(BaseModel):
    schema_version: str = "nextusinger.project.v1"
    id: str
    title: str = "Untitled"
    sample_rate: int = 44100
    tempos: list[TempoEvent] = Field(default_factory=lambda: [TempoEvent()])
    tracks: list[Track] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @computed_field
    @property
    def default_bpm(self) -> float:
        return self.tempos[0].bpm if self.tempos else 120.0


class VoicebankKind(str, Enum):
    DIFFSINGER = "diffsinger"
    OPENVPI = "openvpi-diffsinger"
    ONNX = "onnx"
    UNKNOWN = "unknown"


class VoicebankManifest(BaseModel):
    schema_version: str = "nextusinger.voicebank.v1"
    id: str
    name: str
    kind: VoicebankKind = VoicebankKind.UNKNOWN
    root: str
    sample_rate: int | None = None
    language: str | None = None
    speaker: str | None = None
    config_files: list[str] = Field(default_factory=list)
    acoustic_models: list[str] = Field(default_factory=list)
    vocoders: list[str] = Field(default_factory=list)
    variance_models: list[str] = Field(default_factory=list)
    dictionaries: list[str] = Field(default_factory=list)
    icon: str | None = None
    warnings: list[str] = Field(default_factory=list)
    raw_metadata: dict[str, Any] = Field(default_factory=dict)

    @computed_field
    @property
    def ready_for_external_engine(self) -> bool:
        return bool(self.acoustic_models or self.config_files)


class VoicebankImportRequest(BaseModel):
    path: str


class RenderMode(str, Enum):
    AUTO = "auto"
    DIFFSINGER_EXTERNAL = "diffsinger-external"
    MOCK = "mock"


class RenderRequest(BaseModel):
    project: Project
    voicebank_id: str | None = None
    track_id: str | None = None
    mode: RenderMode = RenderMode.AUTO
    output_name: str = "render.wav"


class RenderResult(BaseModel):
    wav_path: str
    engine: str
    sample_rate: int
    duration_seconds: float
    diagnostics: list[str] = Field(default_factory=list)


class LyricsRequest(BaseModel):
    prompt: str
    language: str = "zh"
    bars: int = 4
    mood: str = "清新"


class LyricsResponse(BaseModel):
    lines: list[str]
    tips: list[str] = Field(default_factory=list)


class PhonemeRequest(BaseModel):
    lyrics: str
    language: str = "zh"


class PhonemeResponse(BaseModel):
    phonemes: list[str]
    normalized_lyrics: str


class TuneRequest(BaseModel):
    notes: list[Note]
    strength: float = Field(0.6, ge=0.0, le=1.0)
    style: Literal["natural", "stable", "expressive"] = "natural"


class TuneResponse(BaseModel):
    pitch: list[PitchPoint]
    comments: list[str]


class HarmonyRequest(BaseModel):
    notes: list[Note]
    interval: Literal["third_up", "third_down", "fifth_up", "octave_down"] = "third_up"


class HarmonyResponse(BaseModel):
    notes: list[Note]


class DiagnoseRequest(BaseModel):
    project: Project


class DiagnoseResponse(BaseModel):
    issues: list[str]
    suggestions: list[str]
