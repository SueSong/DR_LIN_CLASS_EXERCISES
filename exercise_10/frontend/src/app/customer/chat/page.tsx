'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Phone, PhoneOff, MessageSquare, User, Send, Mic, MicOff, Volume2 } from 'lucide-react';
import { useAudioCall } from '@/lib/useAudioCall';
import { playAudioChunk, enableAudioPlayback } from '@/lib/audioUtils';

interface Message {
  id: string;
  speaker: 'customer' | 'agent' | 'system';
  text: string;
  timestamp: Date;
}

export default function CustomerChatPage() {
  const router = useRouter();
  const [customer, setCustomer] = useState<any>(null);
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [waitingForAgent, setWaitingForAgent] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Audio call hook
  const {
    isAudioEnabled,
    isMuted,
    audioLevel,
    audioDevices,
    selectedDevice,
    startAudio,
    stopAudio,
    toggleMute,
    changeDevice
  } = useAudioCall(ws, {
    onTranscript: (text, speaker) => {
      addMessage(speaker, `[Voice] ${text}`);
    }
  });

  // Check if customer is logged in
  useEffect(() => {
    const customerData = localStorage.getItem('customer');
    if (!customerData) {
      router.push('/customer');
      return;
    }
    setCustomer(JSON.parse(customerData));
  }, [router]);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const connectToAgent = async () => {
    setWaitingForAgent(true);
    
    try {
      // Step 1: Request connection to backend matching service
      const callApiModule = await import('@/lib/callApi');
      const response = await callApiModule.callAPI.startCall('customer', customer?.name || 'Customer');
      
      console.log('📞 Call response:', response);
      
      // Step 2: Connect WebSocket with assigned call_id
      const websocket = new WebSocket(`ws://localhost:8000/ws/call/${response.call_id}`);
      websocket.binaryType = 'arraybuffer'; // Receive binary data as ArrayBuffer
      
      websocket.onopen = () => {
        console.log('✅ WebSocket connected with call_id:', response.call_id);
        
        // Notify backend that customer is ready
        websocket.send(JSON.stringify({
          type: 'start_call',
          call_id: response.call_id,
          customer_name: customer?.name,
          timestamp: new Date().toISOString()
        }));
        
        setConnected(true);
        setWaitingForAgent(false);
        
        // Show appropriate message based on match status
        if (response.matched && response.partner_name) {
          addMessage('system', `Connected to ${response.partner_name}! How can we help you today?`);
        } else {
          addMessage('system', `${response.message} You are in the queue.`);
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
          if (data.speaker === 'agent') {
            addMessage('agent', data.text);
          } else if (data.speaker === 'customer') {
            addMessage('customer', data.text);
          }
        } else if (data.type === 'call_ended') {
          addMessage('system', 'Agent ended the call. Thank you for contacting us!');
          disconnectFromAgent();
        } else if (data.type === 'call_started') {
          addMessage('system', 'Agent has joined the chat!');
        }
      } catch (e) {
        console.error('Error parsing message:', e);
      }
    };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        addMessage('system', '⚠️ Connection error. Please try again.');
        setConnected(false);
        setWaitingForAgent(false);
      };

      websocket.onclose = () => {
        console.log('WebSocket closed');
        setConnected(false);
      };

      setWs(websocket);
      
    } catch (error: any) {
      console.error('Failed to connect:', error);
      addMessage('system', `⚠️ Failed to connect: ${error.message || 'Please check if the server is running.'}`);
      setWaitingForAgent(false);
    }
  };

  const disconnectFromAgent = () => {
    if (ws) {
      ws.send(JSON.stringify({
        type: 'end_call',
        timestamp: new Date().toISOString()
      }));
      ws.close();
    }
    
    setConnected(false);
    setWs(null);
    addMessage('system', 'Disconnected from support');
  };

  const addMessage = (speaker: 'customer' | 'agent' | 'system', text: string) => {
    const message: Message = {
      id: `msg_${Date.now()}_${Math.random()}`,
      speaker,
      text,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const sendMessage = () => {
    if (!inputMessage.trim()) return;

    // Add to UI
    addMessage('customer', inputMessage);

    // Send via WebSocket
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'transcript',
        speaker: 'customer',
        text: inputMessage,
        timestamp: new Date().toISOString()
      }));
    }

    setInputMessage('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Quick message templates
  const quickMessages = [
    "I need help with my order",
    "I want to request a refund",
    "I have a billing question",
    "How do I upgrade my plan?"
  ];

  if (!customer) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Phone className="w-6 h-6 text-purple-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Customer Support</h1>
                <p className="text-sm text-gray-600">Welcome, {customer.name}</p>
              </div>
            </div>
            <button
              onClick={() => {
                if (connected) {
                  disconnectFromAgent();
                }
                localStorage.removeItem('customer');
                router.push('/');
              }}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Exit
            </button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-xl overflow-hidden flex flex-col h-[600px]">
            {/* Status Bar */}
            <div className={`px-6 py-4 ${connected ? 'bg-green-50 border-b border-green-200' : 'bg-gray-50 border-b border-gray-200'}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {connected ? (
                    <>
                      <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                      <span className="text-green-700 font-medium">Connected to Support</span>
                    </>
                  ) : waitingForAgent ? (
                    <>
                      <div className="w-3 h-3 bg-yellow-500 rounded-full animate-pulse" />
                      <span className="text-yellow-700 font-medium">Connecting...</span>
                    </>
                  ) : (
                    <>
                      <div className="w-3 h-3 bg-gray-400 rounded-full" />
                      <span className="text-gray-600">Not Connected</span>
                    </>
                  )}
                </div>
                
                {!connected && !waitingForAgent ? (
                  <button
                    onClick={connectToAgent}
                    className="flex items-center gap-2 bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition"
                  >
                    <Phone className="w-5 h-5" />
                    Connect to Agent
                  </button>
                ) : connected ? (
                  <button
                    onClick={disconnectFromAgent}
                    className="flex items-center gap-2 bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition"
                  >
                    <PhoneOff className="w-5 h-5" />
                    End Chat
                  </button>
                ) : null}
              </div>
            </div>

            {/* Audio Controls - Only show when connected */}
            {connected && (
              <div className="px-6 py-3 bg-gradient-to-r from-purple-50 to-pink-50 border-b border-purple-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    {/* Audio toggle button */}
                    {!isAudioEnabled ? (
                      <button
                        onClick={() => {
                          enableAudioPlayback();
                          startAudio();
                        }}
                        className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition"
                      >
                        <Mic className="w-4 h-4" />
                        Start Voice Call
                      </button>
                    ) : (
                      <button
                        onClick={stopAudio}
                        className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition"
                      >
                        <PhoneOff className="w-4 h-4" />
                        End Voice Call
                      </button>
                    )}
                    
                    {/* Mute toggle */}
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
                    
                    {/* Audio level indicator */}
                    {isAudioEnabled && (
                      <div className="flex items-center gap-2">
                        <Volume2 className="w-4 h-4 text-gray-500" />
                        <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-purple-500 transition-all duration-100"
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
                      className="text-sm border border-gray-300 rounded px-3 py-1 focus:outline-none focus:ring-2 focus:ring-purple-500"
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
                  <div className="mt-2 text-xs text-purple-600 flex items-center gap-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
                    {isMuted ? 'Microphone muted' : 'Voice call active - speak naturally'}
                  </div>
                )}
              </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 ? (
                <div className="text-center text-gray-400 mt-20">
                  <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p className="mb-6">Click "Connect to Agent" to start chatting</p>
                  
                  {/* Quick Messages */}
                  <div className="max-w-md mx-auto space-y-2">
                    <p className="text-sm text-gray-500 mb-3">Or select a quick message:</p>
                    {quickMessages.map((msg, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          if (!connected) {
                            setInputMessage(msg);
                          }
                        }}
                        className="block w-full bg-purple-50 hover:bg-purple-100 text-purple-700 px-4 py-2 rounded-lg text-sm transition"
                      >
                        {msg}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.speaker === 'customer' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[70%] rounded-lg px-4 py-3 ${
                        message.speaker === 'agent'
                          ? 'bg-purple-100 text-purple-900'
                          : message.speaker === 'customer'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-600 text-sm italic'
                      }`}
                    >
                      {message.speaker !== 'system' && (
                        <div className="flex items-center gap-2 mb-1">
                          {message.speaker === 'agent' && <User className="w-3 h-3" />}
                          <span className="text-xs font-semibold uppercase opacity-75">
                            {message.speaker === 'agent' ? 'Support Agent' : 'You'}
                          </span>
                          <span className="text-xs opacity-60">
                            {message.timestamp.toLocaleTimeString()}
                          </span>
                        </div>
                      )}
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
                  placeholder={connected ? "Type your message..." : "Connect to agent to send messages"}
                  disabled={!connected}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                />
                <button
                  onClick={sendMessage}
                  disabled={!connected || !inputMessage.trim()}
                  className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
              
              {/* Quick Messages when connected */}
              {connected && messages.length > 0 && (
                <div className="mt-3 flex gap-2 overflow-x-auto">
                  {quickMessages.map((msg, idx) => (
                    <button
                      key={idx}
                      onClick={() => setInputMessage(msg)}
                      className="flex-shrink-0 bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded-full text-xs transition"
                    >
                      {msg}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Info Card */}
          <div className="mt-6 bg-white rounded-lg shadow p-4">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                <MessageSquare className="w-5 h-5 text-purple-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">How it works</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Click "Connect to Agent" to start a conversation</li>
                  <li>• Type your message and press Enter to send</li>
                  <li>• Our agents will respond in real-time</li>
                  <li>• Click "End Chat" when you're done</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

