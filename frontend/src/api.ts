import type { Project, Voicebank } from './types';

export const API_BASE = import.meta.env.VITE_NEXTUSINGER_API ?? 'http://127.0.0.1:7860';

async function json<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export function listVoicebanks(): Promise<Voicebank[]> {
  return json('/api/voicebanks');
}

export function importVoicebank(path: string): Promise<Voicebank> {
  return json('/api/voicebanks/import', { method: 'POST', body: JSON.stringify({ path }) });
}

export function renderProject(project: Project, voicebankId?: string | null) {
  return json<{ wav_path: string; engine: string; duration_seconds: number; diagnostics: string[] }>('/api/synthesis/render', {
    method: 'POST',
    body: JSON.stringify({ project, voicebank_id: voicebankId ?? undefined, mode: 'auto', output_name: `${project.title}.wav` }),
  });
}

export function lyrics(prompt: string) {
  return json<{ lines: string[]; tips: string[] }>('/api/ai/lyrics', { method: 'POST', body: JSON.stringify({ prompt, bars: 4 }) });
}

export function tune(project: Project) {
  const notes = project.tracks[0]?.notes ?? [];
  return json<{ pitch: { beat: number; cents: number }[]; comments: string[] }>('/api/ai/tune', {
    method: 'POST',
    body: JSON.stringify({ notes, strength: 0.65, style: 'natural' }),
  });
}

export function diagnose(project: Project) {
  return json<{ issues: string[]; suggestions: string[] }>('/api/ai/diagnose', {
    method: 'POST',
    body: JSON.stringify({ project }),
  });
}
