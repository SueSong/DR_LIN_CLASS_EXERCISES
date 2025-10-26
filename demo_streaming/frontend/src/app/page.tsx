'use client';

import { useState, useEffect, useRef } from 'react';
import { Radio, Wifi, RefreshCw, Trash2, User, Shield, Crown, Send, Zap } from 'lucide-react';

type StreamingMode = 'sse' | 'websocket';
type Role = 'user' | 'agent' | 'admin';

interface Message {
  id: string;
  role: string;
  content: string;
  timestamp: string;
  mode: string;
  streaming?: boolean;
}

interface Capabilities {
  can_chat: boolean;
  can_view_history: boolean;
  can_restore: boolean;
  can_delete: boolean;
  can_interrupt: boolean;
  can_prioritize: boolean;
}

export default function StreamingDemo() {
  const [mode, setMode] = useState<StreamingMode>('sse');
  const [role, setRole] = useState<Role>('user');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [capabilities, setCapabilities] = useState<Capabilities>({
    can_chat: true,
    can_view_history: true,
    can_restore: false,
    can_delete: false,
    can_interrupt: false,
    can_prioritize: false
  });
  
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const currentStreamIdRef = useRef<string | null>(null);

  // Fetch capabilities when role changes
  useEffect(() => {
    fetch(`http://localhost:8100/api/capabilities/${role}`)
      .then(res => res.json())
      .then(data => setCapabilities(data))
      .catch(err => console.error('Failed to fetch capabilities:', err));
  }, [role]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Setup WebSocket if in WS mode
  useEffect(() => {
    if (mode === 'websocket') {
      const ws = new WebSocket('ws://localhost:8100/ws/chat');
      
      ws.onopen = () => {
        console.log('✅ WebSocket connected');
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'ack') {
          setSessionId(data.session_id);
        } else if (data.type === 'start') {
          currentStreamIdRef.current = data.id;
          setMessages(prev => [...prev, {
            id: data.id,
            role: 'assistant',
            content: '',
            timestamp: data.timestamp,
            mode: 'websocket',
            streaming: true
          }]);
        } else if (data.type === 'chunk') {
          setMessages(prev => prev.map(msg =>
            msg.id === data.id
              ? { ...msg, content: msg.content + data.content }
              : msg
          ));
        } else if (data.type === 'end') {
          setMessages(prev => prev.map(msg =>
            msg.id === data.id
              ? { ...msg, streaming: false }
              : msg
          ));
          setIsStreaming(false);
          currentStreamIdRef.current = null;
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      ws.onclose = () => {
        console.log('WebSocket closed');
      };
      
      wsRef.current = ws;
      
      return () => {
        ws.close();
      };
    }
  }, [mode]);

  const sendMessage = async () => {
    if (!input.trim() || isStreaming) return;
    
    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: role,
      content: input,
      timestamp: new Date().toISOString(),
      mode: mode
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);
    
    if (mode === 'sse') {
      // SSE Mode
      try {
        const response = await fetch('http://localhost:8100/api/chat/sse', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            role: role,
            content: userMessage.content,
            session_id: sessionId
          })
        });
        
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        
        let currentMessage: Message = {
          id: '',
          role: 'assistant',
          content: '',
          timestamp: new Date().toISOString(),
          mode: 'sse',
          streaming: true
        };
        
        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
              if (line.startsWith('event:')) {
                const event = line.substring(6).trim();
                
                if (event === 'session') {
                  // Next line is data
                } else if (event === 'start') {
                  // Next line is data with message ID
                } else if (event === 'chunk') {
                  // Next line is data with content
                } else if (event === 'end') {
                  setMessages(prev => prev.map(msg =>
                    msg.id === currentMessage.id
                      ? { ...msg, streaming: false }
                      : msg
                  ));
                  setIsStreaming(false);
                }
              } else if (line.startsWith('data:')) {
                const data = JSON.parse(line.substring(5).trim());
                
                if (data.session_id && !sessionId) {
                  setSessionId(data.session_id);
                } else if (data.id && !currentMessage.id) {
                  currentMessage = {
                    ...currentMessage,
                    id: data.id,
                    timestamp: data.timestamp
                  };
                  setMessages(prev => [...prev, currentMessage]);
                } else if (data.content) {
                  currentMessage.content += data.content;
                  setMessages(prev => prev.map(msg =>
                    msg.id === currentMessage.id
                      ? { ...msg, content: currentMessage.content }
                      : msg
                  ));
                }
              }
            }
          }
        }
      } catch (error) {
        console.error('SSE error:', error);
        setIsStreaming(false);
      }
    } else {
      // WebSocket Mode
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'chat',
          role: role,
          content: userMessage.content,
          session_id: sessionId
        }));
      }
    }
  };

  const restoreSession = async () => {
    if (!sessionId || !capabilities.can_restore) return;
    
    setMessages([]);
    
    try {
      const response = await fetch(`http://localhost:8100/api/sessions/${sessionId}/restore`, {
        method: 'POST'
      });
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('event: message')) {
              // Next line has data
            } else if (line.startsWith('data:')) {
              const data = JSON.parse(line.substring(5).trim());
              
              if (data.message) {
                setMessages(prev => [...prev, data.message]);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Restore error:', error);
    }
  };

  const clearSession = async () => {
    if (!sessionId || !capabilities.can_delete) return;
    
    try {
      await fetch(`http://localhost:8100/api/sessions/${sessionId}`, {
        method: 'DELETE'
      });
      setMessages([]);
      setSessionId(null);
    } catch (error) {
      console.error('Delete error:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-xl p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            🎬 Streaming UI Demo
          </h1>
          <p className="text-gray-600">
            Live switching between SSE and WebSockets • Session Restoration • Role-Based Actions
          </p>
        </div>

        {/* Control Panel */}
        <div className="bg-white rounded-lg shadow-xl p-6 mb-6">
          <div className="grid md:grid-cols-3 gap-6">
            {/* Streaming Mode */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <Zap className="w-4 h-4" />
                Streaming Mode
              </h3>
              <div className="space-y-2">
                <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition">
                  <input
                    type="radio"
                    name="mode"
                    checked={mode === 'sse'}
                    onChange={() => setMode('sse')}
                    className="w-4 h-4"
                  />
                  <Radio className="w-5 h-5 text-blue-600" />
                  <div>
                    <div className="font-medium">SSE</div>
                    <div className="text-xs text-gray-500">Server-Sent Events</div>
                  </div>
                </label>
                <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition">
                  <input
                    type="radio"
                    name="mode"
                    checked={mode === 'websocket'}
                    onChange={() => setMode('websocket')}
                    className="w-4 h-4"
                  />
                  <Wifi className="w-5 h-5 text-green-600" />
                  <div>
                    <div className="font-medium">WebSocket</div>
                    <div className="text-xs text-gray-500">Bidirectional</div>
                  </div>
                </label>
              </div>
            </div>

            {/* Role Selection */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Your Role
              </h3>
              <div className="space-y-2">
                <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition">
                  <input
                    type="radio"
                    name="role"
                    checked={role === 'user'}
                    onChange={() => setRole('user')}
                    className="w-4 h-4"
                  />
                  <User className="w-5 h-5 text-gray-600" />
                  <div>
                    <div className="font-medium">User</div>
                    <div className="text-xs text-gray-500">Basic access</div>
                  </div>
                </label>
                <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition">
                  <input
                    type="radio"
                    name="role"
                    checked={role === 'agent'}
                    onChange={() => setRole('agent')}
                    className="w-4 h-4"
                  />
                  <Shield className="w-5 h-5 text-blue-600" />
                  <div>
                    <div className="font-medium">Agent</div>
                    <div className="text-xs text-gray-500">Can restore</div>
                  </div>
                </label>
                <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition">
                  <input
                    type="radio"
                    name="role"
                    checked={role === 'admin'}
                    onChange={() => setRole('admin')}
                    className="w-4 h-4"
                  />
                  <Crown className="w-5 h-5 text-yellow-600" />
                  <div>
                    <div className="font-medium">Admin</div>
                    <div className="text-xs text-gray-500">Full access</div>
                  </div>
                </label>
              </div>
            </div>

            {/* Actions */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Actions</h3>
              <div className="space-y-2">
                <button
                  onClick={restoreSession}
                  disabled={!capabilities.can_restore || !sessionId}
                  className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <RefreshCw className="w-4 h-4" />
                  Restore Session
                </button>
                <button
                  onClick={clearSession}
                  disabled={!capabilities.can_delete || !sessionId}
                  className="w-full flex items-center justify-center gap-2 bg-red-600 text-white px-4 py-3 rounded-lg hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete Session
                </button>
                {sessionId && (
                  <div className="text-xs text-gray-500 text-center mt-2">
                    Session: {sessionId.substring(0, 8)}...
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Capabilities Badge */}
          <div className="mt-4 pt-4 border-t">
            <div className="text-sm text-gray-600">
              <strong>Your Capabilities:</strong>
              <div className="flex flex-wrap gap-2 mt-2">
                {capabilities.can_chat && (
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">Chat</span>
                )}
                {capabilities.can_view_history && (
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">View History</span>
                )}
                {capabilities.can_restore && (
                  <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">Restore</span>
                )}
                {capabilities.can_interrupt && (
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-xs">Interrupt</span>
                )}
                {capabilities.can_prioritize && (
                  <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs">Prioritize</span>
                )}
                {capabilities.can_delete && (
                  <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs">Delete</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="bg-white rounded-lg shadow-xl overflow-hidden flex flex-col h-[500px]">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-gray-400 mt-20">
                <p className="text-lg">Start a conversation!</p>
                <p className="text-sm mt-2">
                  Current mode: <strong>{mode === 'sse' ? 'SSE' : 'WebSocket'}</strong>
                </p>
                <p className="text-sm">
                  Role: <strong>{role}</strong>
                </p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'assistant' ? 'justify-start' : 'justify-end'}`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg px-4 py-3 ${
                      message.role === 'assistant'
                        ? 'bg-gray-100 text-gray-800'
                        : role === 'admin'
                        ? 'bg-yellow-500 text-white'
                        : role === 'agent'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-500 text-white'
                    }`}
                  >
                    <div className="text-sm">
                      {message.content}
                      {message.streaming && (
                        <span className="inline-block w-2 h-4 bg-current ml-1 animate-pulse">|</span>
                      )}
                    </div>
                    <div className="text-xs opacity-70 mt-1 flex items-center gap-2">
                      <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
                      <span>•</span>
                      <span className="uppercase">{message.mode}</span>
                    </div>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                disabled={!capabilities.can_chat || isStreaming}
                className="flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              />
              <button
                onClick={sendMessage}
                disabled={!capabilities.can_chat || isStreaming || !input.trim()}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                Send
              </button>
            </div>
            {isStreaming && (
              <div className="text-sm text-gray-500 mt-2 flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                Streaming response...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

