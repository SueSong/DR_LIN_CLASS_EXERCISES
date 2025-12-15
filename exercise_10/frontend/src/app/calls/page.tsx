'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Phone, PhoneOff, Mic, MicOff, User, Clock, MessageSquare, Volume2 } from 'lucide-react';
import { useAudioCall } from '@/lib/useAudioCall';
import { playAudioChunk, enableAudioPlayback } from '@/lib/audioUtils';

interface Message {
  id: string;
  speaker: 'customer' | 'agent';
  text: string;
  timestamp: Date;
}

interface AISuggestion {
  id: string;
  suggestion: string;
  reasoning: string;
  action: string;
  confidence: number;
  timestamp: string;
}

export default function CallsPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [inCall, setInCall] = useState(false);
  const [muted, setMuted] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [aiSuggestions, setAiSuggestions] = useState<AISuggestion[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [callDuration, setCallDuration] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const callTimerRef = useRef<NodeJS.Timeout | null>(null);
  
  // Audio call hook
  const {
    isAudioEnabled,
    isMuted,
    audioLevel,
    audioDevices,
    selectedDevice,
    enableMonitoring,
    startAudio,
    stopAudio,
    toggleMute,
    toggleMonitoring,
    changeDevice
  } = useAudioCall(ws, {
    onTranscript: (text, speaker) => {
      addMessage(speaker === 'agent' ? 'agent' : 'customer', `[Voice] ${text}`);
    },
    // Enable monitoring by default so you can hear your own voice
    // Note: Monitoring may be disabled if headphones aren't detected (to prevent feedback)
  });

  // Check authentication
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (!userData) {
      router.push('/auth/signin');
      return;
    }
    setUser(JSON.parse(userData));
  }, [router]);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Call timer
  useEffect(() => {
    if (inCall) {
      callTimerRef.current = setInterval(() => {
        setCallDuration(prev => prev + 1);
      }, 1000);
    } else {
      if (callTimerRef.current) {
        clearInterval(callTimerRef.current);
      }
      setCallDuration(0);
    }

    return () => {
      if (callTimerRef.current) {
        clearInterval(callTimerRef.current);
      }
    };
  }, [inCall]);

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startCall = async () => {
    setInCall(true);
    
    try {
      // Step 1: Request connection to backend matching service
      const callApiModule = await import('@/lib/callApi');
      const response = await callApiModule.callAPI.startCall('agent', user?.username || 'Agent');
      
      console.log('📞 Agent call response:', response);
      
      // Step 2: Connect WebSocket with assigned call_id
      const websocket = new WebSocket(`ws://localhost:8000/ws/call/${response.call_id}`);
      websocket.binaryType = 'arraybuffer'; // Receive binary data as ArrayBuffer
      
      websocket.onopen = () => {
        console.log('✅ Agent WebSocket connected with call_id:', response.call_id);
        
        websocket.send(JSON.stringify({
          type: 'start_call',
          call_id: response.call_id,
          agent_name: user?.username,
          timestamp: new Date().toISOString()
        }));
        
        // Show appropriate message based on match status
        if (response.matched && response.partner_name) {
          addMessage('system', `Connected to customer: ${response.partner_name}`);
        } else {
          addMessage('system', `${response.message} Waiting for incoming calls...`);
        }
      };

      websocket.onmessage = (event) => {
        // Handle binary audio data (raw PCM)
        if (event.data instanceof ArrayBuffer) {
          playAudioChunk(event.data);
          return;
        }
        
        // Handle Blob (convert to ArrayBuffer)
        if (event.data instanceof Blob) {
          event.data.arrayBuffer().then((arrayBuffer) => {
            playAudioChunk(arrayBuffer);
          });
          return;
        }
        
        // Handle text/JSON messages
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'transcript') {
            // Display transcripts from both agent and customer
            if (data.speaker === 'customer') {
              addMessage('customer', data.text);
            } else if (data.speaker === 'agent') {
              addMessage('agent', data.text);
            }
          } else if (data.type === 'ai_suggestion') {
            // Handle AI suggestions (only agents receive these)
            setAiSuggestions(prev => [...prev, {
              id: Date.now().toString(),
              suggestion: data.suggestion,
              reasoning: data.reasoning || '',
              action: data.action || '',
              confidence: data.confidence || 0,
              timestamp: data.timestamp
            }]);
          } else if (data.type === 'call_ended') {
            addMessage('system', 'Customer ended the call');
            endCall();
          } else if (data.type === 'call_started') {
            addMessage('system', 'Customer connected to the call');
          }
        } catch (e) {
          console.error('Error parsing message:', e);
        }
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        addMessage('system', '⚠️ Connection error. Please check if backend is running.');
      };

      websocket.onclose = () => {
        console.log('WebSocket closed');
      };

      setWs(websocket);
      
    } catch (error: any) {
      console.error('Failed to start call:', error);
      addMessage('system', `⚠️ Failed to connect: ${error.message || 'Please check if the server is running on port 8000.'}`);
      setInCall(false);
    }
  };

  const endCall = () => {
    if (ws) {
      ws.send(JSON.stringify({
        type: 'end_call',
        timestamp: new Date().toISOString()
      }));
      ws.close();
    }
    
    setInCall(false);
    setWs(null);
    setAiSuggestions([]); // Clear AI suggestions
    addMessage('system', 'Call ended');
  };

  const addMessage = (speaker: 'customer' | 'agent' | 'system', text: string) => {
    const message: Message = {
      id: `msg_${Date.now()}_${Math.random()}`,
      speaker: speaker as any,
      text,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const sendMessage = () => {
    if (!inputMessage.trim()) return;

    // Add to UI
    addMessage('agent', inputMessage);

    // Send via WebSocket
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'transcript',
        speaker: 'agent',
        text: inputMessage,
        timestamp: new Date().toISOString()
      }));
    }

    setInputMessage('');
  };

  // Test function to trigger AI suggestion manually (for testing)
  const testAISuggestion = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      // Simulate a customer message to trigger AI suggestion
      ws.send(JSON.stringify({
        type: 'transcript',
        speaker: 'customer',
        text: 'I need help with my order. It has not arrived yet and I am frustrated.',
        timestamp: new Date().toISOString()
      }));
      addMessage('customer', 'I need help with my order. It has not arrived yet and I am frustrated.');
      console.log('🧪 Test: Sent customer message to trigger AI suggestion');
    } else {
      alert('WebSocket not connected. Please start a call first.');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Phone className="w-6 h-6 text-blue-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Call Center</h1>
                <p className="text-sm text-gray-600">Agent: {user.fullName}</p>
              </div>
            </div>
            <button
              onClick={() => {
                localStorage.removeItem('user');
                router.push('/');
              }}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Chat Area */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg overflow-hidden flex flex-col h-[600px]">
              {/* Call Status Bar */}
              <div className={`px-6 py-4 ${inCall ? 'bg-green-50 border-b border-green-200' : 'bg-gray-50 border-b border-gray-200'}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {inCall ? (
                      <>
                        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                        <span className="text-green-700 font-medium">In Call</span>
                        <Clock className="w-4 h-4 text-green-600 ml-2" />
                        <span className="text-green-700 font-mono">{formatDuration(callDuration)}</span>
                      </>
                    ) : (
                      <>
                        <div className="w-3 h-3 bg-gray-400 rounded-full" />
                        <span className="text-gray-600">Idle - Ready to take calls</span>
                      </>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {inCall && (
                      <button
                        onClick={() => setMuted(!muted)}
                        className={`p-2 rounded-lg transition ${muted ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                      >
                        {muted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                      </button>
                    )}
                    
                    {!inCall ? (
                      <button
                        onClick={startCall}
                        className="flex items-center gap-2 bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition"
                      >
                        <Phone className="w-5 h-5" />
                        Start Call
                      </button>
                    ) : (
                      <button
                        onClick={endCall}
                        className="flex items-center gap-2 bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition"
                      >
                        <PhoneOff className="w-5 h-5" />
                        End Call
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* Audio Controls - Only show when in call */}
              {inCall && (
                <div className="px-6 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-blue-100">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      {/* Audio toggle button */}
                      {!isAudioEnabled ? (
                        <button
                          onClick={() => {
                            enableAudioPlayback();
                            startAudio();
                          }}
                          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                        >
                          <Mic className="w-4 h-4" />
                          Enable Voice
                        </button>
                      ) : (
                        <button
                          onClick={stopAudio}
                          className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition"
                        >
                          <PhoneOff className="w-4 h-4" />
                          Disable Voice
                        </button>
                      )}
                      
                      {/* Mute toggle (using audio hook's mute) */}
                      {isAudioEnabled && (
                        <button
                          onClick={toggleMute}
                          className={`p-2 rounded-lg transition ${
                            isMuted 
                              ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                          title={isMuted ? 'Unmute' : 'Mute'}
                        >
                          {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                        </button>
                      )}
                      
                      {/* Monitoring toggle (hear your own voice) */}
                      {isAudioEnabled && (
                        <button
                          onClick={toggleMonitoring}
                          className={`p-2 rounded-lg transition ${
                            enableMonitoring 
                              ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                          title={enableMonitoring ? 'Disable voice monitoring' : 'Enable voice monitoring (hear yourself)'}
                        >
                          <Volume2 className={`w-5 h-5 ${enableMonitoring ? '' : 'opacity-50'}`} />
                        </button>
                      )}
                      
                      {/* Audio level indicator */}
                      {isAudioEnabled && (
                        <div className="flex items-center gap-2">
                          <Volume2 className="w-4 h-4 text-gray-500" />
                          <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-blue-500 transition-all duration-100"
                              style={{ width: `${Math.min(audioLevel * 100, 100)}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {/* Device selector */}
                    {isAudioEnabled && audioDevices.length > 1 && (
                      <select
                        value={selectedDevice}
                        onChange={(e) => changeDevice(e.target.value)}
                        className="text-sm border border-gray-300 rounded px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        {audioDevices.map((device) => (
                          <option key={device.deviceId} value={device.deviceId}>
                            {device.label}
                          </option>
                        ))}
                      </select>
                    )}
                  </div>
                  
                  {/* Status message */}
                  {isAudioEnabled && (
                    <div className="mt-2 text-xs text-blue-600 flex items-center gap-2">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                      {isMuted ? 'Microphone muted' : 'Listening... Speak to the customer'}
                      {enableMonitoring && (
                        <span className="ml-2 text-green-600">• Monitoring enabled (you can hear yourself)</span>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-400 mt-20">
                    <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No messages yet. Start a call to begin conversation.</p>
                  </div>
                ) : (
                  messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.speaker === 'agent' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[70%] rounded-lg px-4 py-3 ${
                          message.speaker === 'customer'
                            ? 'bg-blue-100 text-blue-900'
                            : message.speaker === 'agent'
                            ? 'bg-green-100 text-green-900'
                            : 'bg-gray-100 text-gray-600 text-sm italic'
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-semibold uppercase">
                            {message.speaker}
                          </span>
                          <span className="text-xs opacity-60">
                            {message.timestamp.toLocaleTimeString()}
                          </span>
                        </div>
                        <p>{message.text}</p>
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t border-gray-200 p-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={inCall ? "Type your response..." : "Start a call to send messages"}
                    disabled={!inCall}
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!inCall || !inputMessage.trim()}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Customer Info */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <User className="w-5 h-5" />
                Customer Info
              </h3>
              {inCall ? (
                <div className="space-y-3 text-sm">
                  <div>
                    <span className="text-gray-600">Name:</span>
                    <p className="font-medium">John Doe</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Account:</span>
                    <p className="font-medium">#ACC00001</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Tier:</span>
                    <p className="font-medium">🥇 Gold</p>
                  </div>
                  <div>
                    <span className="text-gray-600">LTV:</span>
                    <p className="font-medium">$2,340</p>
                  </div>
                </div>
              ) : (
                <p className="text-gray-400 text-sm">Start a call to see customer information</p>
              )}
            </div>

            {/* AI Suggestions */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  <span>🤖 AI Suggestions</span>
                  {aiSuggestions.length > 0 && (
                    <span className="bg-blue-100 text-blue-600 text-xs px-2 py-1 rounded-full">
                      {aiSuggestions.length}
                    </span>
                  )}
                </h3>
                {inCall && (
                  <button
                    onClick={testAISuggestion}
                    className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded transition"
                    title="Test AI suggestion (simulates customer message)"
                  >
                    🧪 Test
                  </button>
                )}
              </div>
              {inCall ? (
                aiSuggestions.length > 0 ? (
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {aiSuggestions.slice(-5).reverse().map((suggestion) => {
                      const confidenceColor = suggestion.confidence >= 0.8 
                        ? 'bg-green-50 border-green-200 text-green-900'
                        : suggestion.confidence >= 0.6
                        ? 'bg-blue-50 border-blue-200 text-blue-900'
                        : 'bg-yellow-50 border-yellow-200 text-yellow-900';
                      
                      const actionEmoji = {
                        'ask_question': '❓',
                        'offer_solution': '💡',
                        'escalate': '⬆️',
                        'offer_refund': '💰',
                        'provide_information': 'ℹ️',
                        'empathize': '❤️'
                      }[suggestion.action] || '💬';

                      return (
                        <div key={suggestion.id} className={`border rounded-lg p-3 ${confidenceColor}`}>
                          <div className="flex items-start gap-2 mb-2">
                            <span className="text-lg">{actionEmoji}</span>
                            <div className="flex-1">
                              <p className="text-sm font-medium mb-1">
                                {suggestion.suggestion}
                              </p>
                              {suggestion.reasoning && (
                                <p className="text-xs opacity-75 mt-1">
                                  {suggestion.reasoning}
                                </p>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center justify-between mt-2 pt-2 border-t border-current opacity-50">
                            <span className="text-xs capitalize">{suggestion.action.replace('_', ' ')}</span>
                            <span className="text-xs font-semibold">
                              {Math.round(suggestion.confidence * 100)}% confidence
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className="text-gray-400 text-sm">Listening... AI suggestions will appear as the customer speaks</p>
                )
              ) : (
                <p className="text-gray-400 text-sm">AI suggestions will appear during calls</p>
              )}
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                Quick Actions
              </h3>
              <div className="space-y-2">
                <button className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm transition">
                  Transfer Call
                </button>
                <button className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm transition">
                  Create Ticket
                </button>
                <button className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm transition">
                  Schedule Callback
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

