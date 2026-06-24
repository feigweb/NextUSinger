import { useEffect, useMemo, useState, type CSSProperties, type MouseEvent } from 'react';
import { Download, Mic2, Music2, Sparkles, UploadCloud, Wand2 } from 'lucide-react';
import type { Note, Project, Voicebank } from './types';
import { API_BASE, diagnose, importVoicebank, importVoicebankZip, listVoicebanks, lyrics, renderProject, tune } from './api';

const makeNote = (id: string, start: number, midi: number, lyric: string, duration = 1): Note => ({
  id,
  start,
  duration,
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

const MIDI_MIN = 36;
const MIDI_MAX = 84;
const TOTAL_BEATS = 16;
const BASE_STEP = 0.25; // 1/16 note reference grid.
const TOTAL_STEPS = TOTAL_BEATS / BASE_STEP;
const MIDI_ROWS = Array.from({ length: MIDI_MAX - MIDI_MIN + 1 }, (_, index) => MIDI_MAX - index);
const BLACK_KEY_PCS = new Set([1, 3, 6, 8, 10]);

const LENGTH_OPTIONS = [
  { label: '四分音符 1/4', value: 1 },
  { label: '八分音符 1/8', value: 0.5 },
  { label: '十六分音符 1/16', value: 0.25 },
  { label: '三十二分音符 1/32', value: 0.125 },
];

const SNAP_OPTIONS = [
  { label: '1/4', value: 1 },
  { label: '1/8', value: 0.5 },
  { label: '1/16', value: 0.25 },
  { label: '1/32', value: 0.125 },
  { label: '自由', value: 0 },
];

function midiName(midi: number): string {
  const names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
  return `${names[midi % 12]}${Math.floor(midi / 12) - 1}`;
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function quantize(beat: number, snap: number) {
  if (!snap) return Number(beat.toFixed(3));
  return Number((Math.round(beat / snap) * snap).toFixed(3));
}

function PianoRoll({ project, setProject }: { project: Project; setProject: (p: Project) => void }) {
  const notes = project.tracks[0]?.notes ?? [];
  const [snap, setSnap] = useState(0.25);
  const [defaultDuration, setDefaultDuration] = useState(0.5);
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null);

  const updateNote = (id: string, patch: Partial<Note>) => {
    const next = structuredClone(project);
    next.tracks[0].notes = next.tracks[0].notes
      .map((n) => (n.id === id ? { ...n, ...patch } : n))
      .sort((a, b) => a.start - b.start || a.midi - b.midi);
    setProject(next);
  };

  const deleteNote = (id: string) => {
    const next = structuredClone(project);
    next.tracks[0].notes = next.tracks[0].notes.filter((n) => n.id !== id);
    setProject(next);
    setSelectedNoteId(null);
  };

  const addNoteAt = (midi: number, rawBeat: number) => {
    const duration = defaultDuration;
    const start = clamp(quantize(rawBeat, snap), 0, TOTAL_BEATS - duration);
    const next = structuredClone(project);
    next.tracks[0].notes.push(makeNote(`n-${Date.now()}-${Math.round(midi)}-${Math.round(start * 1000)}`, start, midi, 'la', duration));
    next.tracks[0].notes.sort((a, b) => a.start - b.start || a.midi - b.midi);
    setProject(next);
  };

  const addMiddleC = () => addNoteAt(60, 0);

  const onCellClick = (midi: number, step: number) => {
    addNoteAt(midi, step * BASE_STEP);
  };

  const changeDuration = (note: Note, delta: number) => {
    updateNote(note.id, { duration: clamp(Number((note.duration + delta).toFixed(3)), 0.125, TOTAL_BEATS - note.start) });
  };

  return (
    <section className="panel roll-panel">
      <div className="panel-head">
        <h2><Music2 size={18}/> Piano Roll</h2>
        <div className="roll-tools">
          <label>
            吸附
            <select value={snap} onChange={(e) => setSnap(Number(e.target.value))}>
              {SNAP_OPTIONS.map((option) => <option value={option.value} key={option.label}>{option.label}</option>)}
            </select>
          </label>
          <label>
            新音符
            <select value={defaultDuration} onChange={(e) => setDefaultDuration(Number(e.target.value))}>
              {LENGTH_OPTIONS.map((option) => <option value={option.value} key={option.label}>{option.label}</option>)}
            </select>
          </label>
          <button onClick={addMiddleC}>C4 音符</button>
        </div>
      </div>

      <p className="roll-hint">点击任意轨道格创建自由音符；网格含小节号、MIDI/音名标号、八分与十六分参考线。选中音符后可改歌词、增减长度或删除。</p>

      <div className="piano-roll" style={{ '--step-count': TOTAL_STEPS, '--row-count': MIDI_ROWS.length } as CSSProperties}>
        <div className="ruler-corner">音高</div>
        <div className="beat-ruler">
          {Array.from({ length: TOTAL_STEPS }).map((_, step) => (
            <div
              key={step}
              className={`ruler-cell ${step % 4 === 0 ? 'downbeat' : step % 2 === 0 ? 'eighth' : 'sixteenth'}`}
              title={`${(step * BASE_STEP).toFixed(2)} beat`}
            >
              {step % 4 === 0 ? Math.floor(step / 4) + 1 : step % 2 === 0 ? '1/8' : ''}
            </div>
          ))}
        </div>

        <div className="keyboard">
          {MIDI_ROWS.map((midi) => (
            <div className={`piano-key ${BLACK_KEY_PCS.has(midi % 12) ? 'black' : 'white'}`} key={midi}>
              <span>{midiName(midi)}</span>
              <small>{midi}</small>
            </div>
          ))}
        </div>

        <div className="roll-grid">
          {MIDI_ROWS.flatMap((midi, rowIndex) => (
            Array.from({ length: TOTAL_STEPS }).map((_, step) => (
              <button
                type="button"
                key={`${midi}-${step}`}
                className={`cell ${BLACK_KEY_PCS.has(midi % 12) ? 'black-row' : ''} ${step % 4 === 0 ? 'downbeat' : step % 2 === 0 ? 'eighth' : 'sixteenth'}`}
                style={{ gridRow: rowIndex + 1, gridColumn: step + 1 }}
                title={`${midiName(midi)} · beat ${(step * BASE_STEP).toFixed(2)}`}
                onClick={() => onCellClick(midi, step)}
              />
            ))
          ))}

          {notes.map((note) => {
            const row = MIDI_MAX - note.midi + 1;
            const col = Math.round(note.start / BASE_STEP) + 1;
            const span = Math.max(1, Math.round(note.duration / BASE_STEP));
            const isSelected = selectedNoteId === note.id;

            return (
              <div
                key={note.id}
                className={`note ${isSelected ? 'selected' : ''}`}
                style={{ gridRow: row, gridColumn: `${col} / span ${span}` }}
                title={`${note.lyric} · ${midiName(note.midi)} · ${note.start} beat`}
                onClick={(event: MouseEvent<HTMLDivElement>) => {
                  event.stopPropagation();
                  setSelectedNoteId(note.id);
                }}
              >
                <input
                  value={note.lyric}
                  onClick={(event) => event.stopPropagation()}
                  onChange={(event) => updateNote(note.id, { lyric: event.target.value })}
                  aria-label="音符歌词"
                />
                <span className="note-meta">{midiName(note.midi)}</span>
                <div className="note-actions">
                  <button type="button" onClick={(event) => { event.stopPropagation(); changeDuration(note, -BASE_STEP); }}>−</button>
                  <button type="button" onClick={(event) => { event.stopPropagation(); changeDuration(note, BASE_STEP); }}>＋</button>
                  <button type="button" onClick={(event) => { event.stopPropagation(); deleteNote(note.id); }}>×</button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

export function App() {
  const [project, setProject] = useState<Project>(initialProject);
  const [voicebanks, setVoicebanks] = useState<Voicebank[]>([]);
  const [voicebankPath, setVoicebankPath] = useState('');
  const [zipFile, setZipFile] = useState<File | null>(null);
  const [selectedVoicebank, setSelectedVoicebank] = useState<string | null>(null);
  const [log, setLog] = useState<string[]>(['启动 NextUSinger Studio。']);
  const [audioPath, setAudioPath] = useState<string | null>(null);
  const audioUrl = useMemo(() => audioPath ? `${API_BASE}/api/synthesis/file?path=${encodeURIComponent(audioPath)}` : null, [audioPath]);

  useEffect(() => {
    listVoicebanks().then(setVoicebanks).catch((err) => setLog((x) => [...x, `加载声库失败：${err.message}`]));
  }, []);

  const addLog = (text: string) => setLog((x) => [text, ...x].slice(0, 10));

  const attachVoicebankToTrack = (voicebankId: string) => {
    const next = structuredClone(project);
    next.tracks[0].voicebank_id = voicebankId;
    setProject(next);
    setSelectedVoicebank(voicebankId);
  };

  const onImport = async () => {
    const vb = await importVoicebank(voicebankPath);
    setVoicebanks(await listVoicebanks());
    attachVoicebankToTrack(vb.id);
    addLog(`已导入声库目录：${vb.name} (${vb.kind})`);
  };

  const onZipImport = async () => {
    if (!zipFile) return;
    const vb = await importVoicebankZip(zipFile);
    setVoicebanks(await listVoicebanks());
    attachVoicebankToTrack(vb.id);
    addLog(`已上传并导入 ZIP 声库：${vb.name} (${vb.kind})`);
    setZipFile(null);
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
            <button onClick={onImport} disabled={!voicebankPath}>导入目录</button>
          </div>

          <div className="upload-box">
            <label className="file-picker">
              <UploadCloud size={16}/>
              <span>{zipFile ? zipFile.name : '选择 DiffSinger/OpenVPI ZIP'}</span>
              <input type="file" accept=".zip,application/zip" onChange={(e) => setZipFile(e.target.files?.[0] ?? null)} />
            </label>
            <button onClick={onZipImport} disabled={!zipFile}>上传 ZIP</button>
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
