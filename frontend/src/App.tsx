import { useEffect, useMemo, useState } from 'react';
import { Download, Mic2, Music2, Sparkles, Wand2 } from 'lucide-react';
import type { Note, Project, Voicebank } from './types';
import { API_BASE, diagnose, importVoicebank, listVoicebanks, lyrics, renderProject, tune } from './api';

const makeNote = (id: string, start: number, midi: number, lyric: string): Note => ({
  id,
  start,
  duration: 1,
  midi,
  lyric,
  phonemes: [],
  velocity: 1,
  tension: 0,
  breathiness: 0,
  energy: 0,
  gender: 0,
});

const initialProject: Project = {
  schema_version: 'nextusinger.project.v1',
  id: crypto.randomUUID(),
  title: 'NextUSinger Demo',
  sample_rate: 44100,
  tempos: [{ beat: 0, bpm: 120 }],
  tracks: [
    {
      id: crypto.randomUUID(),
      name: 'Main Vocal',
      voicebank_id: null,
      notes: [
        makeNote('n1', 0, 60, '你'),
        makeNote('n2', 1, 62, '好'),
        makeNote('n3', 2, 64, '世'),
        makeNote('n4', 3, 67, '界'),
      ],
      pitch: [],
      mute: false,
      solo: false,
    },
  ],
  metadata: {},
};

function PianoRoll({ project, setProject }: { project: Project; setProject: (p: Project) => void }) {
  const notes = project.tracks[0]?.notes ?? [];
  const minMidi = 48;
  const maxMidi = 72;
  const beats = 8;
  const updateNote = (id: string, patch: Partial<Note>) => {
    const next = structuredClone(project);
    next.tracks[0].notes = next.tracks[0].notes.map((n) => (n.id === id ? { ...n, ...patch } : n));
    setProject(next);
  };
  const addNote = () => {
    const next = structuredClone(project);
    const idx = next.tracks[0].notes.length + 1;
    next.tracks[0].notes.push(makeNote(`n${idx}-${Date.now()}`, idx % beats, 60 + (idx % 8), 'la'));
    setProject(next);
  };
  return (
    <section className="panel roll-panel">
      <div className="panel-head">
        <h2><Music2 size={18}/> Piano Roll</h2>
        <button onClick={addNote}>添加音符</button>
      </div>
      <div className="roll" style={{ gridTemplateRows: `repeat(${maxMidi - minMidi + 1}, 20px)`, gridTemplateColumns: `repeat(${beats * 4}, 28px)` }}>
        {Array.from({ length: (maxMidi - minMidi + 1) * beats * 4 }).map((_, i) => <div key={i} className="cell" />)}
        {notes.map((n) => {
          const row = maxMidi - n.midi + 1;
          const col = Math.floor(n.start * 4) + 1;
          const span = Math.max(1, Math.floor(n.duration * 4));
          return (
            <div key={n.id} className="note" style={{ gridRow: row, gridColumn: `${col} / span ${span}` }} title={`${n.lyric} MIDI ${n.midi}`}>
              <input value={n.lyric} onChange={(e) => updateNote(n.id, { lyric: e.target.value })} />
              <span>{n.midi}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

export function App() {
  const [project, setProject] = useState<Project>(initialProject);
  const [voicebanks, setVoicebanks] = useState<Voicebank[]>([]);
  const [voicebankPath, setVoicebankPath] = useState('');
  const [selectedVoicebank, setSelectedVoicebank] = useState<string | null>(null);
  const [log, setLog] = useState<string[]>(['启动 NextUSinger Studio。']);
  const [audioPath, setAudioPath] = useState<string | null>(null);
  const audioUrl = useMemo(() => audioPath ? `${API_BASE}/api/synthesis/file?path=${encodeURIComponent(audioPath)}` : null, [audioPath]);

  useEffect(() => {
    listVoicebanks().then(setVoicebanks).catch((err) => setLog((x) => [...x, `加载声库失败：${err.message}`]));
  }, []);

  const addLog = (text: string) => setLog((x) => [text, ...x].slice(0, 10));

  const onImport = async () => {
    const vb = await importVoicebank(voicebankPath);
    setVoicebanks(await listVoicebanks());
    setSelectedVoicebank(vb.id);
    const next = structuredClone(project);
    next.tracks[0].voicebank_id = vb.id;
    setProject(next);
    addLog(`已导入声库：${vb.name} (${vb.kind})`);
  };

  const onLyrics = async () => {
    const resp = await lyrics(project.title);
    addLog(`AI 歌词：${resp.lines.join(' / ')}`);
  };

  const onTune = async () => {
    const resp = await tune(project);
    const next = structuredClone(project);
    next.tracks[0].pitch = resp.pitch;
    setProject(next);
    addLog(resp.comments.join(' '));
  };

  const onDiagnose = async () => {
    const resp = await diagnose(project);
    addLog([...resp.issues, ...resp.suggestions].join('；'));
  };

  const onRender = async () => {
    const resp = await renderProject(project, selectedVoicebank);
    setAudioPath(resp.wav_path);
    addLog(`渲染完成：${resp.engine}，${resp.duration_seconds.toFixed(2)}s。${resp.diagnostics.join(' ')}`);
  };

  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">DiffSinger-compatible singing workstation</p>
          <h1>NextUSinger Studio</h1>
          <p>导入 DiffSinger/OpenVPI 声库，编辑歌唱工程，并用 AI 辅助歌词、调音与和声。</p>
        </div>
        <div className="actions">
          <button onClick={onLyrics}><Sparkles size={16}/> AI 歌词</button>
          <button onClick={onTune}><Wand2 size={16}/> AI 调音</button>
          <button onClick={onDiagnose}>诊断</button>
          <button className="primary" onClick={onRender}><Download size={16}/> 导出 WAV</button>
        </div>
      </header>

      <section className="grid">
        <aside className="panel">
          <h2><Mic2 size={18}/> 声库</h2>
          <div className="import-box">
            <input placeholder="/path/to/diffsinger_voicebank" value={voicebankPath} onChange={(e) => setVoicebankPath(e.target.value)} />
            <button onClick={onImport} disabled={!voicebankPath}>导入</button>
          </div>
          <select value={selectedVoicebank ?? ''} onChange={(e) => setSelectedVoicebank(e.target.value || null)}>
            <option value="">未选择声库</option>
            {voicebanks.map((vb) => <option value={vb.id} key={vb.id}>{vb.name} · {vb.kind}</option>)}
          </select>
          <ul className="vb-list">
            {voicebanks.map((vb) => (
              <li key={vb.id}>
                <b>{vb.name}</b><br />
                <small>{vb.acoustic_models.length} acoustic · {vb.vocoders.length} vocoder · {vb.variance_models.length} variance</small>
                {vb.warnings.map((w) => <em key={w}>{w}</em>)}
              </li>
            ))}
          </ul>
        </aside>

        <PianoRoll project={project} setProject={setProject} />
      </section>

      <section className="panel transport">
        <div>
          <label>标题 <input value={project.title} onChange={(e) => setProject({ ...project, title: e.target.value })} /></label>
          <label>BPM <input type="number" value={project.tempos[0].bpm} onChange={(e) => setProject({ ...project, tempos: [{ beat: 0, bpm: Number(e.target.value) }] })} /></label>
        </div>
        {audioUrl && <audio controls src={audioUrl} />}
      </section>

      <section className="panel log">
        <h2>日志</h2>
        {log.map((l, i) => <p key={i}>{l}</p>)}
      </section>
    </main>
  );
}
