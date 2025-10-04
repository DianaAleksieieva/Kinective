'use client';

import { useEffect, useRef, useState } from 'react';

export default function LiveDemo() {
  const [baseUrl, setBaseUrl] = useState('http://127.0.0.1:8000');
  const [imgSrc, setImgSrc] = useState('http://127.0.0.1:8000/video_feed');
  const [reps, setReps] = useState(null);
  const [state, setState] = useState('');
  const [error, setError] = useState('');
  const timerRef = useRef(null);

  useEffect(() => { setImgSrc(`${trimSlash(baseUrl)}/video_feed`); }, [baseUrl]);

  useEffect(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${trimSlash(baseUrl)}/metrics`, { cache: 'no-store' });
        if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
        const j = await res.json();
        setReps(j.reps ?? null);
        setState(j.state ?? '');
        setError('');
      } catch (e) {
        setError(`Metrics error: ${e?.message || String(e)}`);
      }
    }, 800);
    return () => timerRef.current && clearInterval(timerRef.current);
  }, [baseUrl]);

  return (
    <div style={{ minHeight: '100vh', padding: 24, background: '#f6f6f7' }}>
      <div style={{ maxWidth: 960, margin: '0 auto' }}>
        <h1 style={{ fontSize: 24, fontWeight: 600, marginBottom: 12 }}>
          Kinective • Local Stream Demo
        </h1>

        <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 12 }}>
          <label style={{ fontSize: 12, opacity: 0.8, width: 100 }}>Backend URL:</label>
          <input
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
            placeholder="http://127.0.0.1:8000"
            style={{ flex: 1, padding: '8px 10px', border: '1px solid #ddd', borderRadius: 8 }}
          />
          <button
            onClick={() => setImgSrc(`${trimSlash(baseUrl)}/video_feed?ts=${Date.now()}`)}
            style={{ padding: '8px 10px', borderRadius: 8, border: '1px solid #000', background: '#000', color: '#fff' }}
            title="Reload stream"
          >
            Reload
          </button>
        </div>

        <div style={{ border: '1px solid #ddd', background: '#fff', borderRadius: 12, overflow: 'hidden' }}>
          <img
            src={imgSrc}
            alt="Live pose stream"
            style={{ display: 'block', width: '100%' }}
            onError={() => setError('Stream error: could not load /video_feed (check server running, CORS, or URL).')}
            onLoad={() => setError('')}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12, marginTop: 12 }}>
          <Card label="Reps" value={reps ?? '—'} />
          <Card label="State" value={state || '—'} />
          <Card label="Stream URL" value={imgSrc} mono />
          <Card label="Metrics URL" value={`${trimSlash(baseUrl)}/metrics`} mono />
        </div>

        {error && (
          <div style={{ marginTop: 12, padding: '10px 12px', borderRadius: 8, background: '#fee2e2', color: '#991b1b' }}>
            {error}
          </div>
        )}
      </div>
    </div>
  );
}

function Card({ label, value, mono = false }) {
  return (
    <div style={{ border: '1px solid #eee', background: '#fff', borderRadius: 10, padding: '10px 12px' }}>
      <div style={{ fontSize: 12, color: '#6b7280' }}>{label}</div>
      <div style={{ fontSize: 18, fontWeight: 600, fontFamily: mono ? 'ui-monospace, SFMono-Regular, Menlo, monospace' : 'inherit' }}>
        {value}
      </div>
    </div>
  );
}

function trimSlash(u) { return u.replace(/\/+$/, ''); }
