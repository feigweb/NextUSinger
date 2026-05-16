export type Note = {
  id: string;
  start: number;
  duration: number;
  midi: number;
  lyric: string;
  phonemes: string[];
  velocity: number;
  tension: number;
  breathiness: number;
  energy: number;
  gender: number;
};

export type Track = {
  id: string;
  name: string;
  voicebank_id?: string | null;
  notes: Note[];
  pitch: { beat: number; cents: number }[];
  mute: boolean;
  solo: boolean;
};

export type Project = {
  schema_version: string;
  id: string;
  title: string;
  sample_rate: number;
  tempos: { beat: number; bpm: number }[];
  tracks: Track[];
  metadata: Record<string, unknown>;
};

export type Voicebank = {
  id: string;
  name: string;
  kind: string;
  root: string;
  sample_rate?: number | null;
  language?: string | null;
  warnings: string[];
  acoustic_models: string[];
  vocoders: string[];
  variance_models: string[];
};
