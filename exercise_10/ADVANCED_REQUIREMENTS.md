# Exercise 10: Advanced Requirements & Acceptance Criteria ✅

## Student Lab: Hands-On Implementation

### A. Streaming Chat with Optimistic Echo + Abort

**Learning Objective:** Implement responsive streaming with user-perceived latency < 1s and graceful abort handling.

---

#### **Requirement 1: Optimistic Echo**

**What is it?** Display user's message immediately (before server confirmation) to create perceived instant response.

**Implementation:**

```typescript
// frontend/src/components/chat/OptimisticChat.tsx
'use client';

import { useState, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  status: 'pending' | 'confirmed' | 'error';
  timestamp: Date;
}

export function OptimisticChat({ callId }: { callId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = async () => {
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: input,
      status: 'pending',
      timestamp: new Date()
    };

    // 1. Optimistic update - show immediately
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    // 2. Create assistant placeholder with streaming indicator
    const assistantMessageId = uuidv4();
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      status: 'pending',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, assistantMessage]);

    // 3. Stream response
    abortControllerRef.current = new AbortController();
    
    try {
      const response = await fetch(`/api/chat/${callId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) throw new Error('Failed to send message');

      // 4. Confirm user message
      setMessages(prev => prev.map(m => 
        m.id === userMessage.id ? { ...m, status: 'confirmed' } : m
      ));

      // 5. Stream assistant response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = '';

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            
            if (data.type === 'token') {
              accumulatedContent += data.content;
              
              // Update assistant message incrementally
              setMessages(prev => prev.map(m =>
                m.id === assistantMessageId
                  ? { ...m, content: accumulatedContent }
                  : m
              ));
            } else if (data.type === 'done') {
              // Mark as confirmed
              setMessages(prev => prev.map(m =>
                m.id === assistantMessageId
                  ? { ...m, status: 'confirmed' }
                  : m
              ));
            }
          }
        }
      }

    } catch (error: any) {
      if (error.name === 'AbortError') {
        // Mark as truncated but valid
        setMessages(prev => prev.map(m =>
          m.id === assistantMessageId
            ? { ...m, status: 'confirmed', content: m.content + ' [aborted]' }
            : m
        ));
      } else {
        // Mark as error
        setMessages(prev => prev.map(m =>
          m.id === userMessage.id
            ? { ...m, status: 'error' }
            : m
        ));
      }
    }
  };

  const abortStream = () => {
    abortControllerRef.current?.abort();
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map(msg => (
          <div
            key={msg.id}
            className={`message ${msg.role} ${msg.status}`}
          >
            <div className="content">{msg.content}</div>
            {msg.status === 'pending' && msg.role === 'assistant' && (
              <div className="typing-indicator">●●●</div>
            )}
            {msg.status === 'error' && (
              <div className="error-badge">Failed to send</div>
            )}
          </div>
        ))}
      </div>

      <div className="input-area">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && sendMessage()}
          placeholder="Type a message..."
        />
        <button onClick={sendMessage}>Send</button>
        <button onClick={abortStream} className="abort-btn">
          Stop
        </button>
      </div>
    </div>
  );
}
```

**Backend Support:**

```python
# backend/app/api/chat.py
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter()

@router.post("/api/chat/{call_id}")
async def chat_stream(call_id: str, request: Request):
    data = await request.json()
    user_message = data["message"]
    
    async def generate():
        try:
            # Start timer for latency measurement
            start_time = asyncio.get_event_loop().time()
            
            # Get AI response stream
            async for chunk in ai_agent.stream_response(user_message):
                # Check if client aborted
                if await request.is_disconnected():
                    print(f"Client disconnected, stopping stream for {call_id}")
                    break
                
                # Send token
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
                
                # Ensure first token < 1s
                if asyncio.get_event_loop().time() - start_time < 1.0:
                    # First token arrived quickly!
                    pass
            
            # Send completion
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        except asyncio.CancelledError:
            # Graceful abort - send truncation marker
            yield f"data: {json.dumps({'type': 'aborted'})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

**Acceptance Test:**
```typescript
// Test 1: First token < 1s
test('first token arrives within 1 second', async () => {
  const start = Date.now();
  let firstTokenTime: number | null = null;

  const stream = await streamChat('test message');
  
  for await (const chunk of stream) {
    if (!firstTokenTime) {
      firstTokenTime = Date.now();
    }
  }

  expect(firstTokenTime! - start).toBeLessThan(1000);
});

// Test 2: Optimistic update immediate
test('user message appears immediately', () => {
  render(<OptimisticChat callId="test" />);
  
  const input = screen.getByPlaceholderText('Type a message...');
  fireEvent.change(input, { target: { value: 'Hello' } });
  fireEvent.click(screen.getByText('Send'));

  // Should appear instantly (before server response)
  expect(screen.getByText('Hello')).toBeInTheDocument();
  expect(screen.getByText('Hello')).toHaveClass('pending');
});

// Test 3: Abort yields valid truncated turn
test('abort preserves partial response', async () => {
  render(<OptimisticChat callId="test" />);
  
  // Start streaming
  fireEvent.click(screen.getByText('Send'));
  
  // Wait for partial response
  await waitFor(() => 
    expect(screen.getByText(/Hello/)).toBeInTheDocument()
  );
  
  // Abort
  fireEvent.click(screen.getByText('Stop'));
  
  // Should keep partial content
  const message = screen.getByText(/Hello/);
  expect(message).toBeInTheDocument();
  expect(message).toHaveClass('confirmed');
});
```

---

### B. Session Restore with Deterministic Replay

**Learning Objective:** Persist conversation state and restore it perfectly after page refresh or reconnect.

---

#### **Requirement 2: No Dupes After Refresh**

**Implementation:**

```typescript
// frontend/src/lib/session-manager.ts
import { v4 as uuidv4 } from 'uuid';

interface Turn {
  id: string;
  messages: Message[];
  timestamp: Date;
  committed: boolean;
}

export class SessionManager {
  private sessionId: string;
  private turns: Turn[] = [];
  
  constructor(callId: string) {
    this.sessionId = `session_${callId}`;
    this.loadFromStorage();
  }

  addTurn(messages: Message[]) {
    const turn: Turn = {
      id: uuidv4(),
      messages,
      timestamp: new Date(),
      committed: false
    };
    
    this.turns.push(turn);
    this.saveToStorage();
  }

  commitTurn(turnId: string) {
    const turn = this.turns.find(t => t.id === turnId);
    if (turn) {
      turn.committed = true;
      this.saveToStorage();
    }
  }

  getUncommittedTurns(): Turn[] {
    return this.turns.filter(t => !t.committed);
  }

  private saveToStorage() {
    // Use deterministic serialization
    const serialized = JSON.stringify(this.turns, null, 0);
    localStorage.setItem(this.sessionId, serialized);
    
    // Also save to IndexedDB for larger sessions
    this.saveToIndexedDB();
  }

  private loadFromStorage() {
    const stored = localStorage.getItem(this.sessionId);
    if (stored) {
      this.turns = JSON.parse(stored);
    }
  }

  private async saveToIndexedDB() {
    const db = await openDB('call-sessions', 1, {
      upgrade(db) {
        db.createObjectStore('sessions');
      }
    });
    
    await db.put('sessions', {
      id: this.sessionId,
      turns: this.turns,
      lastUpdated: new Date()
    });
  }

  async replay(): Promise<Message[]> {
    // Deterministic replay: reconstruct exact state
    const allMessages: Message[] = [];
    
    for (const turn of this.turns) {
      if (turn.committed) {
        allMessages.push(...turn.messages);
      }
    }
    
    return allMessages;
  }
}
```

**Usage in Component:**

```typescript
// frontend/src/components/chat/ResumableChat.tsx
'use client';

import { useEffect, useState } from 'react';
import { SessionManager } from '@/lib/session-manager';

export function ResumableChat({ callId }: { callId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionManager] = useState(() => new SessionManager(callId));
  const [isRestoring, setIsRestoring] = useState(true);

  useEffect(() => {
    // Restore session on mount
    const restore = async () => {
      const restored = await sessionManager.replay();
      
      // Deduplicate by message ID
      const uniqueMessages = Array.from(
        new Map(restored.map(m => [m.id, m])).values()
      );
      
      setMessages(uniqueMessages);
      setIsRestoring(false);
    };
    
    restore();
  }, [callId]);

  const sendMessage = async (content: string) => {
    const turnId = uuidv4();
    const userMsg = { id: uuidv4(), role: 'user', content };
    const assistantMsg = { id: uuidv4(), role: 'assistant', content: '' };
    
    // Add to session (uncommitted)
    sessionManager.addTurn([userMsg, assistantMsg]);
    setMessages(prev => [...prev, userMsg, assistantMsg]);
    
    try {
      // Stream response
      let fullResponse = '';
      const stream = await streamChat(content);
      
      for await (const chunk of stream) {
        fullResponse += chunk;
        setMessages(prev => prev.map(m =>
          m.id === assistantMsg.id ? { ...m, content: fullResponse } : m
        ));
      }
      
      // Commit turn (no duplicates on refresh now)
      sessionManager.commitTurn(turnId);
      
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  if (isRestoring) {
    return <div className="loading">Restoring session...</div>;
  }

  return (
    <div className="chat">
      <div className="messages">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>
      {/* ... input ... */}
    </div>
  );
}
```

**Backend Sync:**

```python
# backend/app/api/session.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class Turn(BaseModel):
    id: str
    messages: List[dict]
    timestamp: str
    committed: bool

@router.post("/api/session/{call_id}/sync")
async def sync_session(call_id: str, turns: List[Turn]):
    """Sync local session with server (conflict resolution)"""
    
    # Get server's version
    server_turns = await db.get_turns(call_id)
    
    # Merge using turn IDs (deterministic)
    merged = {}
    for turn in server_turns + turns:
        if turn.id not in merged or turn.committed:
            merged[turn.id] = turn
    
    # Save merged version
    await db.save_turns(call_id, list(merged.values()))
    
    return {"status": "synced", "turn_count": len(merged)}

@router.get("/api/session/{call_id}/replay")
async def replay_session(call_id: str):
    """Get deterministic replay of session"""
    turns = await db.get_turns(call_id, committed_only=True)
    
    messages = []
    for turn in sorted(turns, key=lambda t: t.timestamp):
        messages.extend(turn.messages)
    
    return {"messages": messages}
```

**Acceptance Test:**

```typescript
test('no duplicate messages after refresh', async () => {
  // Send 3 messages
  const chat = render(<ResumableChat callId="test" />);
  await sendMessages(['Hello', 'How are you?', 'Goodbye']);
  
  // Refresh page
  chat.unmount();
  const restored = render(<ResumableChat callId="test" />);
  
  // Should have exactly 6 messages (3 user + 3 assistant)
  await waitFor(() => {
    const messages = screen.getAllByRole('article');
    expect(messages).toHaveLength(6);
    
    // No duplicates
    const ids = messages.map(m => m.getAttribute('data-id'));
    expect(new Set(ids).size).toBe(6);
  });
});
```

---

### C. NextAuth: Roles & Protected Routes

**Learning Objective:** Implement role-based access control with proper authentication.

---

#### **Requirement 3: Role Gates Honored**

**Implementation:**

```typescript
// frontend/src/lib/auth.ts
import { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        // Authenticate with backend
        const res = await fetch(`${process.env.API_URL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(credentials)
        });

        const user = await res.json();
        
        if (res.ok && user) {
          return {
            id: user.id,
            name: user.name,
            email: user.email,
            role: user.role // 'agent' | 'supervisor' | 'admin'
          };
        }
        
        return null;
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = user.role;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.role = token.role;
      }
      return session;
    }
  },
  pages: {
    signIn: '/auth/signin',
  }
};
```

**Protected Route Component:**

```typescript
// frontend/src/components/auth/ProtectedRoute.tsx
'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface Props {
  children: React.ReactNode;
  allowedRoles: string[];
}

export function ProtectedRoute({ children, allowedRoles }: Props) {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'loading') return;

    // Not authenticated
    if (!session) {
      router.push('/auth/signin');
      return;
    }

    // Not authorized (wrong role)
    if (!allowedRoles.includes(session.user.role)) {
      router.push('/unauthorized');
    }
  }, [session, status, allowedRoles, router]);

  if (status === 'loading') {
    return <div>Loading...</div>;
  }

  if (!session || !allowedRoles.includes(session.user.role)) {
    return null;
  }

  return <>{children}</>;
}
```

**Usage:**

```typescript
// frontend/src/app/admin/page.tsx
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export default function AdminPage() {
  return (
    <ProtectedRoute allowedRoles={['admin', 'supervisor']}>
      <div>
        <h1>Admin Dashboard</h1>
        {/* Only admins and supervisors can see this */}
      </div>
    </ProtectedRoute>
  );
}

// frontend/src/app/call/[id]/page.tsx
export default function CallPage() {
  return (
    <ProtectedRoute allowedRoles={['agent', 'supervisor', 'admin']}>
      <div>
        <h1>Active Call</h1>
        {/* All roles can access calls */}
      </div>
    </ProtectedRoute>
  );
}
```

**Middleware Protection:**

```typescript
// frontend/src/middleware.ts
import { withAuth } from 'next-auth/middleware';

export default withAuth(
  function middleware(req) {
    // Additional role checks can go here
  },
  {
    callbacks: {
      authorized: ({ token, req }) => {
        const path = req.nextUrl.pathname;
        
        // Public routes
        if (path.startsWith('/auth')) return true;
        
        // Require authentication for all other routes
        if (!token) return false;
        
        // Role-based path protection
        if (path.startsWith('/admin') && token.role !== 'admin') {
          return false;
        }
        
        return true;
      }
    }
  }
);

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)']
};
```

**Acceptance Test:**

```typescript
test('unauthorized users redirected to signin', async () => {
  // Clear session
  mockSession(null);
  
  render(<CallPage />);
  
  // Should redirect to signin
  await waitFor(() => {
    expect(mockRouter.push).toHaveBeenCalledWith('/auth/signin');
  });
});

test('agents cannot access admin routes', async () => {
  mockSession({ user: { role: 'agent' } });
  
  render(<AdminPage />);
  
  await waitFor(() => {
    expect(mockRouter.push).toHaveBeenCalledWith('/unauthorized');
  });
});

test('supervisors can access admin routes', async () => {
  mockSession({ user: { role: 'supervisor' } });
  
  render(<AdminPage />);
  
  expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
});
```

---

### D. Publish @agent/ui with Stories & Tests

**Learning Objective:** Create reusable component library with documentation and tests.

---

#### **Requirement 4: Package Builds ESM+Types**

**Project Structure:**

```
packages/
└── agent-ui/
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── src/
    │   ├── index.ts                 # Main export
    │   ├── components/
    │   │   ├── AudioStream/
    │   │   │   ├── AudioStream.tsx
    │   │   │   ├── AudioStream.stories.tsx
    │   │   │   └── AudioStream.test.tsx
    │   │   ├── Transcription/
    │   │   │   ├── Transcription.tsx
    │   │   │   ├── Transcription.stories.tsx
    │   │   │   └── Transcription.test.tsx
    │   │   └── AISuggestions/
    │   │       ├── AISuggestions.tsx
    │   │       ├── AISuggestions.stories.tsx
    │   │       └── AISuggestions.test.tsx
    │   ├── hooks/
    │   │   ├── useSSE.ts
    │   │   └── useWebSocket.ts
    │   └── types/
    │       └── index.ts
    └── .storybook/
        ├── main.ts
        └── preview.tsx
```

**Package Configuration:**

```json
// packages/agent-ui/package.json
{
  "name": "@agent/ui",
  "version": "1.0.0",
  "type": "module",
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "require": "./dist/index.cjs",
      "types": "./dist/index.d.ts"
    },
    "./styles": "./dist/style.css"
  },
  "files": [
    "dist"
  ],
  "scripts": {
    "build": "vite build && tsc --emitDeclarationOnly",
    "test": "vitest",
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build"
  },
  "devDependencies": {
    "@storybook/react": "^7.6.0",
    "@storybook/react-vite": "^7.6.0",
    "@testing-library/react": "^14.0.0",
    "@types/react": "^18.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0"
  },
  "peerDependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }
}
```

**Vite Build Config:**

```typescript
// packages/agent-ui/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import dts from 'vite-plugin-dts';

export default defineConfig({
  plugins: [
    react(),
    dts({
      insertTypesEntry: true,
    }),
  ],
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      name: 'AgentUI',
      formats: ['es', 'cjs'],
      fileName: (format) => `index.${format === 'es' ? 'js' : 'cjs'}`
    },
    rollupOptions: {
      external: ['react', 'react-dom'],
      output: {
        globals: {
          react: 'React',
          'react-dom': 'ReactDOM'
        }
      }
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test-setup.ts'
  }
});
```

**Component Example:**

```typescript
// packages/agent-ui/src/components/AudioStream/AudioStream.tsx
import { useState, useEffect } from 'react';

export interface AudioStreamProps {
  /** Unique call identifier */
  callId: string;
  /** WebSocket URL */
  wsUrl: string;
  /** Callback when streaming starts */
  onStreamStart?: () => void;
  /** Callback when streaming stops */
  onStreamStop?: () => void;
  /** Custom className */
  className?: string;
}

/**
 * AudioStream component for WebRTC audio capture and streaming
 * 
 * @example
 * ```tsx
 * <AudioStream
 *   callId="call-123"
 *   wsUrl="ws://localhost:8000"
 *   onStreamStart={() => console.log('Started')}
 * />
 * ```
 */
export function AudioStream({
  callId,
  wsUrl,
  onStreamStart,
  onStreamStop,
  className = ''
}: AudioStreamProps) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);

  // Implementation...

  return (
    <div className={`audio-stream ${className}`}>
      {/* UI */}
    </div>
  );
}
```

**Storybook Story:**

```typescript
// packages/agent-ui/src/components/AudioStream/AudioStream.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { AudioStream } from './AudioStream';

const meta: Meta<typeof AudioStream> = {
  title: 'Components/AudioStream',
  component: AudioStream,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    callId: { control: 'text' },
    wsUrl: { control: 'text' },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    callId: 'call-123',
    wsUrl: 'ws://localhost:8000',
  },
};

export const Streaming: Story = {
  args: {
    callId: 'call-456',
    wsUrl: 'ws://localhost:8000',
  },
  play: async ({ canvasElement }) => {
    // Simulate streaming state
  },
};

export const WithCustomStyling: Story = {
  args: {
    callId: 'call-789',
    wsUrl: 'ws://localhost:8000',
    className: 'custom-audio-stream',
  },
};
```

**Unit Test:**

```typescript
// packages/agent-ui/src/components/AudioStream/AudioStream.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { AudioStream } from './AudioStream';

describe('AudioStream', () => {
  it('renders start button initially', () => {
    render(<AudioStream callId="test" wsUrl="ws://localhost" />);
    expect(screen.getByText(/Start Call/i)).toBeInTheDocument();
  });

  it('calls onStreamStart when started', async () => {
    const onStreamStart = vi.fn();
    render(
      <AudioStream
        callId="test"
        wsUrl="ws://localhost"
        onStreamStart={onStreamStart}
      />
    );

    fireEvent.click(screen.getByText(/Start Call/i));

    await waitFor(() => {
      expect(onStreamStart).toHaveBeenCalledTimes(1);
    });
  });

  it('displays audio level indicator when streaming', async () => {
    render(<AudioStream callId="test" wsUrl="ws://localhost" />);
    
    fireEvent.click(screen.getByText(/Start Call/i));

    await waitFor(() => {
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });
  });
});
```

**Main Export:**

```typescript
// packages/agent-ui/src/index.ts
// Components
export { AudioStream } from './components/AudioStream/AudioStream';
export { Transcription } from './components/Transcription/Transcription';
export { AISuggestions } from './components/AISuggestions/AISuggestions';

// Hooks
export { useSSE } from './hooks/useSSE';
export { useWebSocket } from './hooks/useWebSocket';

// Types
export type * from './types';
```

**Usage in Main App:**

```typescript
// frontend/src/app/call/[id]/page.tsx
import { AudioStream, Transcription, AISuggestions } from '@agent/ui';
import '@agent/ui/styles';

export default function CallPage({ params }: { params: { id: string } }) {
  return (
    <div>
      <AudioStream
        callId={params.id}
        wsUrl={process.env.NEXT_PUBLIC_WS_URL!}
      />
      <Transcription callId={params.id} />
      <AISuggestions callId={params.id} />
    </div>
  );
}
```

**Publish:**

```bash
# Build package
cd packages/agent-ui
npm run build

# Run tests
npm test

# Build storybook
npm run build-storybook

# Publish to npm
npm publish --access public
```

---

## 🎯 Acceptance Criteria Checklist

### Performance
- [ ] **First token < 1s** (local)
  - Measure with `performance.now()`
  - Optimize prompt caching
  - Use streaming immediately
  
### Reliability
- [ ] **No dupes after refresh**
  - Test: Refresh 5 times, count messages
  - Verify deterministic replay
  - Check turn IDs unique

### User Experience
- [ ] **Abort yields valid truncated turn**
  - Test: Abort mid-stream
  - Verify partial content preserved
  - Check status marked correctly

### Security
- [ ] **Role gates honored**
  - Test: Agent accessing admin routes
  - Test: Unauthenticated redirect
  - Test: Middleware blocks properly

### Package Quality
- [ ] **Package builds ESM+types**
  - Check `dist/index.js` exists
  - Check `dist/index.d.ts` exists
  - Verify imports work
  
- [ ] **Storybook + basic tests pass**
  - All stories render
  - No console errors
  - Unit tests > 80% coverage

---

## 🧪 Testing Commands

```bash
# Run all tests
npm test

# Test streaming performance
npm run test:perf

# Test auth flows
npm run test:auth

# Build and verify package
cd packages/agent-ui
npm run build
npm run test
npm run storybook

# E2E test
npm run test:e2e
```

---

## 📝 Grading Rubric

| Criteria | Points | Requirements |
|----------|--------|--------------|
| Optimistic UI | 20 | Messages appear instantly, proper loading states |
| Streaming Performance | 20 | First token < 1s, smooth rendering |
| Abort Handling | 15 | Graceful abort, valid truncated turn |
| Session Restore | 15 | No duplicates, deterministic replay |
| Authentication | 15 | NextAuth working, roles enforced |
| Package Quality | 10 | Builds ESM+CJS+types, documented |
| Tests | 5 | Unit + Storybook passing |

**Total: 100 points**

---

This ensures production-quality streaming UI with all modern best practices! ✅

