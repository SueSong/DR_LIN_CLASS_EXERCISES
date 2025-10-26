'use client';

import { useEffect, useState } from 'react';
import { AudioStreamer } from '@/lib/webrtc';

interface Props {
  callId: string;
  onStreamReady?: () => void;
}

export function AudioStream({ callId, onStreamReady }: Props) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [streamer] = useState(() => new AudioStreamer());

  const startCall = async () => {
    try {
      await streamer.start(callId, 'ws://localhost:8000');
      setIsStreaming(true);
      onStreamReady?.();
      
      // Update audio level indicator
      const interval = setInterval(() => {
        setAudioLevel(streamer.getAudioLevel());
      }, 100);
      
      return () => clearInterval(interval);
    } catch (error) {
      console.error('Failed to start audio stream:', error);
    }
  };

  const endCall = () => {
    streamer.stop();
    setIsStreaming(false);
  };

  return (
    <div className="audio-stream-panel">
      <div className="flex items-center gap-4">
        {!isStreaming ? (
          <button
            onClick={startCall}
            className="btn btn-primary"
          >
            🎤 Start Call
          </button>
        ) : (
          <button
            onClick={endCall}
            className="btn btn-danger"
          >
            📞 End Call
          </button>
        )}
        
        {isStreaming && (
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            <span className="text-sm text-gray-600">Recording</span>
          </div>
        )}
      </div>
      
      {/* Audio level indicator */}
      {isStreaming && (
        <div className="mt-4">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 transition-all duration-100"
              style={{ width: `${audioLevel * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}