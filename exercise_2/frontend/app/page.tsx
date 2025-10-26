'use client';

import { useState } from 'react';

type Msg = { role: 'user' | 'assistant' | 'system'; content: string };

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_BASE || 'http://localhost:8000';

export default function Page() {
  const [messages, setMessages] = useState<Msg[]>([{ role: 'system', content: 'You are a helpful assistant.' }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  async function send() {
    if (!input.trim()) return;
    const newMsgs = [...messages, { role: 'user', content: input } as Msg];
    setMessages(newMsgs);
    setInput('');
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMsgs, model: 'gpt-4o-mini', temperature: 0.3 }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setMessages((prev) => [...prev, { role: 'assistant', content: data.reply }]);
    } catch (e: any) {
      setMessages((prev) => [...prev, { role: 'assistant', content: `Error: ${e.message}` }]);
    } finally {
      setLoading(false);
    }
  }

  function onKey(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: '40px auto', padding: 16 }}>
      <h1 style={{ margin: 0, marginBottom: 12 }}>Exercise 2 — Chat</h1>
      <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 12, minHeight: 300 }}>
        {messages.map((m, i) => (
          // Missing stable key on purpose for lint demo; using index key triggers warnings
          <div key={Math.random()} style={{ margin: '8px 0' }}>
            <strong style={{ color: m.role === 'user' ? '#2563eb' : m.role === 'assistant' ? '#16a34a' : '#6b7280' }}>
              {m.role}
            </strong>
            : {m.content}
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKey}
          placeholder="Type a message and press Enter..."
          style={{ flex: 1, padding: 10, borderRadius: 6, border: '1px solid #d1d5db' }}
        />
        <button onClick={() => void send()} disabled={loading} style={{ padding: '10px 14px' }}>
          {loading ? 'Sending…' : 'Send'}
        </button>
      </div>
      <p style={{ color: '#6b7280', marginTop: 8 }}>Backend: {BACKEND}</p>
    </div>
  );
}


