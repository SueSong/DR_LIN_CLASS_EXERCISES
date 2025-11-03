'use client';

import { useEffect, useRef, useState } from 'react';
import coachAPI from '@/lib/coachApi';
import { Send, Sparkles, User, Bot, Loader2, CheckCircle2, Shield, Zap, Heart, Star, TrendingUp, ExternalLink, BookOpen } from 'lucide-react';
import { PERFORMANCE_CONFIG } from '@/config/performance';

interface Citation {
  id?: string;
  title?: string;
  source?: string;
  source_url?: string;
}

interface Msg { 
  id: string; 
  role: 'parent' | 'coach' | 'system' | 'mentor'; 
  text: string; 
  at: Date;
  citations?: Citation[];
}

export default function CoachChatPage() {
  const [parent, setParent] = useState<{ name: string } | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [sessionId, setSessionId] = useState('');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Msg[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const p = localStorage.getItem('parent');
    if (p) setParent(JSON.parse(p));
  }, []);

  useEffect(() => { 
    endRef.current?.scrollIntoView({ behavior: 'smooth' }); 
  }, [messages]);

  // Periodically check for mentor replies (poll every 10 seconds when connected)
  // Reduced frequency and added request deduplication
  useEffect(() => {
    if (!ws || !sessionId) return;
    
    let isPolling = true;
    let lastCheckTime = 0;
    const POLL_INTERVAL = 30000; // 30 seconds (reduced to save resources)
    const MIN_TIME_BETWEEN_REQUESTS = 25000; // Prevent duplicate requests
    
    const checkMentorReplies = async () => {
      // Prevent duplicate requests (React StrictMode in dev causes double calls)
      const now = Date.now();
      if (now - lastCheckTime < MIN_TIME_BETWEEN_REQUESTS) {
        return;
      }
      lastCheckTime = now;
      
      if (!isPolling) return;
      
      try {
        const response = await fetch(`http://localhost:8011/api/hitl/session/${sessionId}/replies`);
        if (!isPolling) return; // Check again after async operation
        
        if (response.ok) {
          const data = await response.json();
          if (data.replies && data.replies.length > 0) {
            // Get current messages to check for duplicates
            setMessages((currentMessages) => {
              if (!isPolling) return currentMessages;
              
              const existingReplyTexts = new Set(
                currentMessages
                  .filter(m => m.role === 'mentor')
                  .map(m => m.text)
              );
              
              // Find new replies that we don't have yet
              const newReplies = data.replies.filter(
                (reply: any) => reply.mentor_reply && !existingReplyTexts.has(reply.mentor_reply)
              );
              
              if (newReplies.length > 0) {
                // Add new replies
                const messagesToAdd = newReplies.map((reply: any) => ({
                  id: crypto.randomUUID(),
                  role: 'mentor' as const,
                  text: reply.mentor_reply,
                  at: new Date(reply.mentor_replied_at || new Date())
                }));
                return [...currentMessages, ...messagesToAdd];
              }
              
              return currentMessages;
            });
          }
        }
      } catch (error) {
        // Silently fail - mentor replies will come via WebSocket too
      }
    };
    
    // Initial check after 5 seconds
    const initialTimeout = setTimeout(checkMentorReplies, 5000);
    
    // Then poll every 30 seconds (reduced frequency to save resources)
    const interval = setInterval(checkMentorReplies, POLL_INTERVAL);
    
    return () => {
      isPolling = false;
      clearTimeout(initialTimeout);
      clearInterval(interval);
    };
  }, [ws, sessionId]); // Removed messages from deps to avoid infinite loop

  const start = async () => {
    if (!parent) return;
    setConnectionStatus('connecting');
    try {
      const { session_id, message } = await coachAPI.startSession(parent.name);
      setSessionId(session_id);
      setMessages((m) => [...m, { 
        id: crypto.randomUUID(), 
        role: 'system', 
        text: message, 
        at: new Date() 
      }]);
      
      const socket = new WebSocket(`ws://localhost:8011/ws/coach/${session_id}`);
      
      socket.onopen = () => {
        setWs(socket);
        setConnectionStatus('connected');
        inputRef.current?.focus();
      };
      
      socket.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data);
          if (data.type === 'advice') {
            setIsTyping(true);
            setTimeout(() => {
              setMessages((m) => [
                ...m,
                { 
                  id: crypto.randomUUID(), 
                  role: 'coach', 
                  text: data.text, 
                  citations: data.citations || [],
                  at: new Date() 
                },
              ]);
              setIsTyping(false);
            }, 1000);
          } else if (data.type === 'refusal') {
            // Safety guard blocked the message - show refusal
            setIsTyping(true);
            setTimeout(() => {
              setMessages((m) => [
                ...m,
                { 
                  id: crypto.randomUUID(), 
                  role: 'coach', 
                  text: data.text, 
                  at: new Date() 
                },
              ]);
              setIsTyping(false);
            }, 500);
          } else if (data.type === 'crisis_redirect') {
            // Crisis situation - show escalation message
            setIsTyping(true);
            setTimeout(() => {
              setMessages((m) => [
                ...m,
                { 
                  id: crypto.randomUUID(), 
                  role: 'system', 
                  text: data.text, 
                  at: new Date() 
                },
              ]);
              setIsTyping(false);
            }, 500);
          } else if (data.type === 'session_started') {
            setMessages((m) => [...m, { 
              id: crypto.randomUUID(), 
              role: 'system', 
              text: '✨ Session ready! How can I help you today?', 
              at: new Date() 
            }]);
          } else if (data.type === 'mentor_reply') {
            // Mentor reply from HITL queue
            setMessages((m) => [...m, {
              id: crypto.randomUUID(),
              role: 'mentor',
              text: data.text,
              at: new Date(data.timestamp || new Date())
            }]);
          }
        } catch {
          // ignore malformed messages
        }
      };
      
      socket.onclose = () => {
        setWs(null);
        setConnectionStatus('disconnected');
      };
      
      socket.onerror = () => {
        setConnectionStatus('disconnected');
      };
    } catch (error) {
      setConnectionStatus('disconnected');
      setMessages((m) => [...m, { 
        id: crypto.randomUUID(), 
        role: 'system', 
        text: '❌ Failed to connect. Please try again.', 
        at: new Date() 
      }]);
    }
  };

  const sendWithSSE = async () => {
    if (!input.trim() || !sessionId) {
      console.error('[SSE] Cannot send: sessionId=', sessionId, 'input=', input.trim());
      return;
    }
    
    const userMessage = input.trim();
    console.log('[SSE] Sending message via SSE:', userMessage);
    const userMsgId = crypto.randomUUID();
    
    // Add user message to chat
    setMessages((m) => [...m, { 
      id: userMsgId, 
      role: 'parent', 
      text: userMessage, 
      at: new Date() 
    }]);
    
    setInput('');
    setIsTyping(true);
    
    // Create streaming message ID for coach response
    const coachMsgId = crypto.randomUUID();
    let streamingText = '';
    let citations: Citation[] = [];
    let messageType: 'advice' | 'refusal' | 'crisis_redirect' = 'advice';
    
    // Add placeholder message that will be updated
    setMessages((m) => [...m, {
      id: coachMsgId,
      role: 'coach',
      text: '',
      at: new Date(),
      citations: []
    }]);
    
    try {
      // Record request start time (for first token measurement)
      const requestStartTime = Date.now();
      
      // Make SSE request
      const response = await fetch(`http://localhost:8011/api/coach/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId
        })
      });
      
      if (!response.body) {
        throw new Error('No response body');
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let startTime = Date.now();
      let firstChunkReceived = false;
      let firstTokenTime = 0;
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer
        
        let currentEvent = null;
        for (let i = 0; i < lines.length; i++) {
          const line = lines[i].trim();
          
          if (line.startsWith('event: ')) {
            currentEvent = line.substring(7).trim();
          } else if (line.startsWith('data: ')) {
            if (currentEvent) {
              try {
                const data = JSON.parse(line.substring(6));
              
                if (currentEvent === 'classification') {
                  // Classification received
                  // Continue to next iteration
                } else if (currentEvent === 'citations') {
                  citations = data.citations || [];
                  console.log('[SSE] Citations received:', citations.length, citations);
                } else if (currentEvent === 'start') {
                  messageType = data.type || 'advice';
                  startTime = Date.now(); // Reset timer for first chunk
                } else if (currentEvent === 'chunk') {
                  if (!firstChunkReceived) {
                    firstChunkReceived = true;
                    firstTokenTime = Date.now() - requestStartTime;
                    const timeSeconds = (firstTokenTime / 1000).toFixed(2);
                    
                    // Log to console with visual indicator
                    const threshold = PERFORMANCE_CONFIG.FIRST_TOKEN_THRESHOLD_MS;
                    const thresholdSeconds = PERFORMANCE_CONFIG.FIRST_TOKEN_THRESHOLD_SECONDS;
                    console.log(`%c⚡ First token received in ${firstTokenTime}ms (${timeSeconds}s)`, 
                      `color: ${firstTokenTime < threshold ? 'green' : 'orange'}; font-weight: bold; font-size: 14px;`);
                    
                    // Show visual indicator in UI (optional - you can add a toast notification)
                    if (firstTokenTime > threshold) {
                      console.warn(`⚠️ First token time (${timeSeconds}s) exceeds ${thresholdSeconds}s requirement!`);
                    } else {
                      console.log(`✅ First token time (${timeSeconds}s) meets requirement (<${thresholdSeconds}s)`);
                    }
                  }
                  
                  streamingText += data.content || '';
                  
                  // Update message in real-time
                  setMessages((m) => m.map(msg => 
                    msg.id === coachMsgId 
                      ? { ...msg, text: streamingText, citations: citations }
                      : msg
                  ));
                } else if (currentEvent === 'notice') {
                  // Budget notice (lite mode)
                  if (data.type === 'budget_limit' || data.mode === 'lite') {
                    // Show notice as a system message
                    setMessages((m) => [...m, {
                      id: crypto.randomUUID(),
                      role: 'system',
                      text: `⚠️ ${data.message || 'Daily budget exceeded. Using lite mode.'}`,
                      at: new Date()
                    }]);
                  }
                } else if (currentEvent === 'end') {
                  // Ensure citations are preserved when streaming ends
                  setMessages((m) => m.map(msg => 
                    msg.id === coachMsgId 
                      ? { ...msg, text: streamingText, citations: citations }
                      : msg
                  ));
                  setIsTyping(false);
                } else if (currentEvent === 'error') {
                  throw new Error(data.error || 'Streaming error');
                }
                
                currentEvent = null; // Reset for next event
              } catch (e) {
                console.error('Error parsing SSE data:', e);
              }
            } else if (line === '') {
              // Empty line marks end of event
              currentEvent = null;
            }
          }
        }
      }
      
      setIsTyping(false);
    } catch (error) {
      console.error('SSE streaming error:', error);
      setIsTyping(false);
      
      // Update message with error
      setMessages((m) => m.map(msg => 
        msg.id === coachMsgId 
          ? { ...msg, text: 'Sorry, there was an error processing your request. Please try again.' }
          : msg
      ));
    }
    
    inputRef.current?.focus();
  };

  const send = () => {
    if (!input.trim() || !ws) {
      console.error('[WS] Cannot send: ws=', !!ws, 'input=', input.trim());
      return;
    }
    const messageText = input.trim();
    console.log('[WS] Sending message via WebSocket:', messageText);
    try {
      ws.send(JSON.stringify({ type: 'text', text: messageText }));
      setMessages((m) => [...m, { 
        id: crypto.randomUUID(), 
        role: 'parent', 
        text: messageText, 
        at: new Date() 
      }]);
      setInput('');
      inputRef.current?.focus();
    } catch (error) {
      console.error('[WS] Error sending message:', error);
    }
  };

  // Handler for skip link - programmatically focus the target (newest messages)
  const handleSkipToContent = (e: React.MouseEvent<HTMLAnchorElement> | React.KeyboardEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    const target = document.getElementById('main-chat-content');
    if (target) {
      // Scroll to bottom (newest messages) where active conversation is
      // Use setTimeout to ensure scroll happens after focus
      setTimeout(() => {
        target.scrollTop = target.scrollHeight;
        // Also scroll the endRef if it exists (newest message marker)
        if (endRef.current) {
          endRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
      }, 100);
      target.focus();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-orange-50/40 to-amber-50/60 flex items-center py-8 relative">
      {/* Skip Link - Must be first in DOM order for Tab navigation */}
      <a
        href="#main-chat-content"
        onClick={handleSkipToContent}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            handleSkipToContent(e);
          }
        }}
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[9999] focus:bg-orange-600 focus:text-white focus:px-6 focus:py-3 focus:rounded-lg focus:font-bold focus:text-sm focus:outline-none focus:ring-4 focus:ring-orange-500 focus:shadow-xl"
        aria-label="Skip to newest messages (bottom of chat)"
      >
        Skip to newest messages
      </a>
      
      <div className="container mx-auto px-4 md:px-6 max-w-6xl w-full">
        
        {/* Header Card */}
        <div className="bg-gradient-to-r from-orange-500 via-amber-500 to-orange-500 backdrop-blur-xl rounded-[2.5rem] shadow-2xl border-3 border-orange-300/50 p-8 mb-8 animate-slide-up relative overflow-hidden">
          {/* Animated Background */}
          <div className="absolute inset-0 bg-gradient-to-r from-orange-400/20 to-amber-400/20 animate-pulse" />
          
          <div className="relative z-10 flex items-center justify-between flex-wrap gap-6">
            <div className="flex items-center gap-5">
              <div className="w-20 h-20 bg-white rounded-3xl flex items-center justify-center shadow-2xl">
                <Sparkles className="w-10 h-10 text-orange-500 animate-pulse" />
              </div>
              <div>
                <h1 className="text-3xl md:text-4xl font-black text-white drop-shadow-lg flex items-center gap-2">
                  Child Growth Assistant
                  <Star className="w-6 h-6 fill-white animate-pulse" />
                </h1>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-lg font-black text-orange-100">👋 {parent?.name || 'Loading...'}</span>
                  {connectionStatus === 'connected' && (
                    <>
                      <span className="text-orange-200">•</span>
                      <div className="flex items-center gap-2 bg-green-400/30 px-3 py-1 rounded-full border border-green-300/50">
                        <div className="w-2.5 h-2.5 bg-green-300 rounded-full animate-pulse shadow-lg" />
                        <span className="text-sm font-black text-white">Live</span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
            
            {connectionStatus === 'disconnected' ? (
              <button 
                onClick={start} 
                aria-label="Start coaching session"
                className="bg-white text-orange-700 rounded-2xl px-10 py-4 font-black text-lg hover:shadow-2xl hover:scale-110 transition-all duration-200 flex items-center gap-3 border-3 border-orange-300/50 shadow-xl"
              >
                <Zap className="w-6 h-6 fill-orange-600 animate-pulse" />
                Start Session
              </button>
            ) : connectionStatus === 'connecting' ? (
              <div 
                role="status"
                aria-live="polite"
                aria-label="Connecting to session"
                className="flex items-center gap-3 bg-white/20 px-6 py-3 rounded-2xl backdrop-blur-sm border border-white/30"
              >
                <Loader2 className="w-6 h-6 animate-spin text-white" aria-hidden="true" />
                <span className="font-black text-white">Connecting...</span>
              </div>
            ) : (
              <div 
                role="status"
                aria-live="polite"
                aria-label="Session active"
                className="flex items-center gap-3 bg-green-500 px-6 py-3 rounded-2xl shadow-xl border-2 border-green-300"
              >
                <CheckCircle2 className="w-6 h-6 text-white" aria-hidden="true" />
                <span className="font-black text-white">Active Session</span>
              </div>
            )}
          </div>
        </div>

        {/* Chat Container */}
        <div className="bg-white backdrop-blur-xl rounded-[2.5rem] shadow-2xl border-2 border-slate-100 overflow-hidden animate-scale-in">
          {/* Messages Area - Main content target for skip link */}
          <div 
            id="main-chat-content"
            role="log"
            aria-label="Chat messages"
            aria-live="polite"
            aria-atomic="false"
            tabIndex={0}
            className="h-[650px] overflow-y-auto p-8 md:p-10 space-y-8 bg-gradient-to-br from-slate-50/30 via-orange-50/20 to-amber-50/30 focus:outline-2 focus:outline-orange-500 focus:outline-offset-4"
          >
            {messages.length === 0 ? (
              <div 
                role="status"
                aria-live="polite"
                className="flex items-center justify-center h-full"
              >
                <div className="text-center max-w-2xl">
                  <div 
                    role="img"
                    aria-label="Coaching session ready"
                    className="inline-flex items-center justify-center w-32 h-32 bg-gradient-to-br from-orange-500 to-amber-500 rounded-[2rem] mb-8 shadow-2xl shadow-orange-500/50 relative"
                  >
                    <Heart className="w-16 h-16 text-white fill-white animate-pulse" aria-hidden="true" />
                    <div className="absolute -top-4 -right-4 w-16 h-16 bg-gradient-to-br from-rose-500 to-pink-500 rounded-full flex items-center justify-center shadow-xl animate-bounce">
                      <Sparkles className="w-8 h-8 text-white" aria-hidden="true" />
                    </div>
                  </div>
                  
                  <h3 className="text-4xl font-black mb-4">
                    <span className="bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
                      Ready to Start?
                    </span>
                  </h3>
                  <p className="text-slate-600 mb-10 text-xl font-semibold">
                    Click <span className="text-orange-600 font-black">"Start Session"</span> above to begin your personalized coaching
                  </p>
                  
                  <div className="flex flex-wrap gap-4 justify-center">
                    {[
                      { text: '😴 Sleep routines', gradient: 'from-blue-500 to-indigo-600' },
                      { text: '🤝 Sibling conflicts', gradient: 'from-purple-500 to-pink-600' },
                      { text: '📱 Screen time', gradient: 'from-orange-500 to-red-600' },
                      { text: '😢 Tantrums', gradient: 'from-rose-500 to-pink-600' }
                    ].map((topic) => (
                      <div 
                        key={topic.text} 
                        className={`px-6 py-3 bg-gradient-to-r ${topic.gradient} text-white rounded-full text-base font-bold shadow-lg hover:scale-110 transition-transform cursor-pointer`}
                      >
                        {topic.text}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <>
                {messages.map((m, idx) => {
                  // Determine appropriate ARIA role based on message type
                  let messageRole = 'article';
                  let ariaLabel = '';
                  
                  if (m.role === 'system') {
                    messageRole = 'status';
                    ariaLabel = 'System message';
                  } else if (m.role === 'mentor') {
                    messageRole = 'article';
                    ariaLabel = 'Mentor reply';
                  } else if (m.role === 'coach') {
                    messageRole = 'article';
                    ariaLabel = 'Coach advice';
                  } else {
                    messageRole = 'article';
                    ariaLabel = 'Your message';
                  }
                  
                  return (
                  <div 
                    key={m.id} 
                    role={messageRole}
                    aria-label={ariaLabel}
                    className={`flex ${m.role === 'parent' ? 'justify-end' : 'justify-start'} animate-slide-up`}
                    style={{ animationDelay: `${idx * 30}ms` }}
                  >
                    <div className={`flex gap-4 max-w-[80%] ${m.role === 'parent' ? 'flex-row-reverse' : 'flex-row'}`}>
                      {/* Avatar */}
                      {m.role !== 'system' && (
                        <div 
                          role="img"
                          aria-label={
                            m.role === 'coach' 
                              ? 'Coach avatar' 
                              : m.role === 'mentor' 
                              ? 'Mentor avatar' 
                              : 'Your avatar'
                          }
                          className={`flex-shrink-0 w-14 h-14 rounded-2xl flex items-center justify-center shadow-xl border-3 ${
                            m.role === 'coach'
                              ? 'bg-gradient-to-br from-amber-400 via-orange-500 to-amber-600 border-orange-300'
                              : m.role === 'mentor'
                              ? 'bg-gradient-to-br from-blue-500 via-indigo-600 to-purple-600 border-indigo-400'
                              : 'bg-gradient-to-br from-orange-600 via-orange-500 to-amber-600 border-orange-400'
                          }`}
                        >
                          {m.role === 'coach' ? (
                            <Bot className="w-7 h-7 text-white" aria-hidden="true" />
                          ) : m.role === 'mentor' ? (
                            <Sparkles className="w-7 h-7 text-white" aria-hidden="true" />
                          ) : (
                            <User className="w-7 h-7 text-white" aria-hidden="true" />
                          )}
                        </div>
                      )}
                      
                      {/* Message Bubble */}
                      <div className={`rounded-3xl px-7 py-5 shadow-xl border-3 ${
                        m.role === 'parent'
                          ? 'bg-gradient-to-br from-orange-600 via-orange-500 to-amber-600 text-white border-orange-400'
                          : m.role === 'coach'
                          ? 'bg-gradient-to-br from-amber-50 via-orange-50 to-amber-50 text-slate-900 border-orange-300'
                          : m.role === 'mentor'
                          ? 'bg-gradient-to-br from-indigo-50 via-blue-50 to-purple-50 text-slate-900 border-indigo-300'
                          : 'bg-gradient-to-br from-blue-50 to-cyan-50 text-slate-700 border-blue-300'
                      }`}>
                        {m.role === 'mentor' && (
                          <div className="flex items-center gap-2 mb-2">
                            <Sparkles className="w-4 h-4 text-indigo-600" />
                            <span className="text-xs font-bold text-indigo-700 uppercase tracking-wide">Mentor Reply</span>
                          </div>
                        )}
                        <p className={`leading-relaxed whitespace-pre-wrap font-semibold text-lg ${
                          m.role === 'coach' || m.role === 'mentor' ? 'text-slate-800' : ''
                        }`}>
                          {m.text}
                        </p>
                        
                        {/* Citation Badges */}
                        {m.citations && m.citations.length > 0 && m.role === 'coach' && (
                          <div 
                            role="region"
                            aria-label="Citation sources"
                            className="mt-4 pt-3 border-t border-orange-200"
                          >
                            <div className="flex items-center gap-2 mb-2">
                              <BookOpen className="w-4 h-4 text-orange-600" aria-hidden="true" />
                              <span className="text-xs font-bold text-orange-700 uppercase tracking-wide">Sources</span>
                            </div>
                            <nav 
                              aria-label="Reference sources"
                              className="flex flex-wrap gap-2"
                            >
                              {m.citations.map((citation, idx) => (
                                (citation.title || citation.source || citation.id) && (
                                  <a
                                    key={citation.id || idx}
                                    href={citation.source_url || '#'}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    aria-label={`Source: ${citation.title || citation.source || `Source ${idx + 1}`}`}
                                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-orange-100 to-amber-100 hover:from-orange-200 hover:to-amber-200 text-orange-800 rounded-lg text-xs font-semibold border border-orange-300 hover:border-orange-400 transition-all hover:shadow-md group"
                                  >
                                    <span className="max-w-[200px] truncate">
                                      {citation.title || citation.source || `Source ${idx + 1}`}
                                    </span>
                                    {citation.source_url && (
                                      <ExternalLink className="w-3 h-3 opacity-70 group-hover:opacity-100 flex-shrink-0" aria-label="Opens in new tab" />
                                    )}
                                  </a>
                                )
                              ))}
                            </nav>
                          </div>
                        )}
                        
                        <div className={`text-xs mt-3 font-bold flex items-center gap-2 ${
                          m.role === 'parent' ? 'text-white/80' : 'text-slate-600'
                        }`}>
                          <span>{m.at.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                          {m.role === 'parent' && <CheckCircle2 className="w-3.5 h-3.5" />}
                        </div>
                      </div>
                    </div>
                  </div>
                  );
                })}
                
                {/* Typing Indicator */}
                {isTyping && (
                  <div 
                    role="status"
                    aria-live="polite"
                    aria-label="Coach is typing"
                    className="flex gap-4 animate-slide-up"
                  >
                    <div className="w-14 h-14 rounded-2xl flex items-center justify-center bg-gradient-to-br from-amber-400 to-orange-500 shadow-xl border-3 border-orange-300">
                      <Bot className="w-7 h-7 text-white" aria-hidden="true" />
                    </div>
                    <div className="bg-gradient-to-br from-amber-50 to-orange-100 border-3 border-orange-300 rounded-3xl px-7 py-5 shadow-xl">
                      <div className="flex gap-2" aria-hidden="true">
                        <div className="w-4 h-4 bg-gradient-to-r from-orange-500 to-amber-500 rounded-full animate-bounce shadow-lg" />
                        <div className="w-4 h-4 bg-gradient-to-r from-orange-500 to-amber-500 rounded-full animate-bounce shadow-lg" style={{ animationDelay: '0.2s' }} />
                        <div className="w-4 h-4 bg-gradient-to-r from-orange-500 to-amber-500 rounded-full animate-bounce shadow-lg" style={{ animationDelay: '0.4s' }} />
                      </div>
                      <span className="sr-only">Coach is typing a response</span>
                    </div>
                  </div>
                )}
                <div ref={endRef} />
              </>
            )}
          </div>

          {/* Input Area */}
          <div 
            role="region"
            aria-label="Message input area"
            className="border-t-3 border-slate-200 p-8 bg-gradient-to-r from-orange-50/50 via-amber-50/50 to-orange-50/50 backdrop-blur-sm"
          >
            <div className="flex gap-4">
              <input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                aria-label="Type your message"
                aria-describedby="input-help-text"
                onKeyDown={(e) => { 
                  if (e.key === 'Enter' && !e.shiftKey) { 
                    e.preventDefault(); 
                    // Default to SSE if available, otherwise WS
                    if (sessionId) {
                      sendWithSSE(); 
                    } else if (ws) {
                      send();
                    }
                  } else if (e.key === 'Escape') {
                    // Clear input on Escape key
                    e.preventDefault();
                    setInput('');
                    inputRef.current?.blur(); // Remove focus from input
                  }
                }}
                placeholder={(sessionId || ws) ? 'Ask about routines, conflicts, screen time…' : 'Start session to begin chatting'}
                disabled={!sessionId && !ws}
                className="flex-1 border-3 border-orange-300 rounded-2xl px-7 py-5 focus:ring-4 focus:ring-orange-500/40 focus:border-orange-500 disabled:bg-slate-100 disabled:cursor-not-allowed outline-none transition-all text-slate-900 text-lg font-semibold placeholder:text-slate-500 hover:border-orange-400 bg-white shadow-inner"
              />
              <span id="input-help-text" className="sr-only">Press Enter to send, Escape to clear</span>
              <div className="flex gap-2">
                {/* WebSocket Send Button */}
                <button
                  onClick={send}
                  disabled={!ws || !input.trim()}
                  aria-label="Send message via WebSocket"
                  className="bg-gradient-to-r from-blue-600 via-blue-500 to-indigo-600 text-white rounded-2xl px-6 py-5 font-black disabled:opacity-40 disabled:cursor-not-allowed hover:shadow-2xl hover:shadow-blue-500/50 hover:scale-110 transition-all duration-200 flex items-center gap-2 group border-3 border-blue-400/50 shadow-xl"
                  title="Send via WebSocket"
                >
                  <Send className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                  <span className="hidden sm:inline text-base">WS</span>
                </button>
                
                {/* SSE Send Button */}
                <button
                  onClick={sendWithSSE}
                  disabled={!sessionId || !input.trim()}
                  aria-label="Send message via Server-Sent Events (Streaming)"
                  className="bg-gradient-to-r from-orange-600 via-orange-500 to-amber-600 text-white rounded-2xl px-6 py-5 font-black disabled:opacity-40 disabled:cursor-not-allowed hover:shadow-2xl hover:shadow-orange-500/50 hover:scale-110 transition-all duration-200 flex items-center gap-2 group border-3 border-orange-400/50 shadow-xl"
                  title="Send via Server-Sent Events (Streaming)"
                >
                  <Send className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                  <span className="hidden sm:inline text-base">SSE</span>
                </button>
              </div>
            </div>
            
            {/* Quick Tips */}
            {sessionId && messages.length < 2 && (
              <div className="mt-6 flex flex-wrap gap-3 items-center justify-center">
                <TrendingUp className="w-5 h-5 text-slate-500" />
                <span className="text-sm text-slate-600 font-black uppercase tracking-wide">Popular Topics:</span>
                {[
                  { text: 'Bedtime resistance', gradient: 'from-blue-500 to-cyan-600' },
                  { text: 'Picky eating', gradient: 'from-green-500 to-emerald-600' },
                  { text: 'Homework battles', gradient: 'from-purple-500 to-violet-600' }
                ].map((tip) => (
                  <button
                    key={tip.text}
                    onClick={() => setInput(tip.text)}
                    className={`text-sm px-5 py-2.5 bg-gradient-to-r ${tip.gradient} text-white rounded-full font-bold shadow-lg hover:scale-110 hover:shadow-xl transition-all border-2 border-white/50`}
                  >
                    {tip.text}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center gap-3 bg-white px-7 py-4 rounded-full border-2 border-slate-200 shadow-lg">
            <Shield className="w-5 h-5 text-orange-600" />
            <p className="text-sm text-slate-700 font-bold">
              <span className="text-orange-700 font-black">General guidance</span> · For urgent concerns, consult a professional
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
