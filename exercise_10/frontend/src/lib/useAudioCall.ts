import { useState, useEffect, useRef, useCallback } from 'react';
import { AudioRecorder, stopMediaStream } from './audioUtils';

interface UseAudioCallOptions {
  onTranscript?: (text: string, speaker: 'agent' | 'customer') => void;
  onAudioLevel?: (level: number) => void;
  autoSendAudio?: boolean;
}

export function useAudioCall(ws: WebSocket | null, options: UseAudioCallOptions = {}) {
  const [isAudioEnabled, setIsAudioEnabled] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [audioDevices, setAudioDevices] = useState<{ deviceId: string; label: string }[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>('');
  const [audioLevel, setAudioLevel] = useState(0);
  const [enableMonitoring, setEnableMonitoring] = useState(true); // Enable monitoring by default
  
  const recorderRef = useRef<AudioRecorder | null>(null);
  const audioLevelIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  
  // Load available audio devices
  useEffect(() => {
    loadAudioDevices();
  }, []);
  
  const loadAudioDevices = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const audioInputs = devices
        .filter(device => device.kind === 'audioinput')
        .map(device => ({
          deviceId: device.deviceId,
          label: device.label || `Microphone ${device.deviceId.substring(0, 5)}`
        }));
      
      setAudioDevices(audioInputs);
      if (audioInputs.length > 0 && !selectedDevice) {
        setSelectedDevice(audioInputs[0].deviceId);
      }
    } catch (error) {
      console.error('Error loading audio devices:', error);
    }
  };
  
  const startAudio = useCallback(async () => {
    if (recorderRef.current) {
      console.log('⚠️ Audio already started');
      return; // Already started
    }
    
    if (!ws) {
      console.error('❌ WebSocket not available - cannot start audio');
      alert('WebSocket not connected. Please wait for connection.');
      return;
    }
    
    if (ws.readyState !== WebSocket.OPEN) {
      console.error(`❌ WebSocket not open (state: ${ws.readyState})`);
      alert('WebSocket not ready. Please wait for connection.');
      return;
    }
    
    console.log('🎙️ Starting audio recorder...');
    console.log('🔌 WebSocket state:', ws.readyState, ws.OPEN === WebSocket.OPEN);
    
    let chunkCounter = 0;
    const recorder = new AudioRecorder(
      // onAudioChunk - now sends raw PCM (ArrayBuffer)
      (chunk) => {
        chunkCounter++;
        
        // Log first few chunks to verify callback is being called
        if (chunkCounter <= 5) {
          console.log(`🎤 onAudioChunk called #${chunkCounter}, size: ${chunk.byteLength} bytes`);
        }
        
        if (!ws) {
          if (chunkCounter <= 3) {
            console.warn('⚠️ WebSocket not available, dropping audio chunk');
          }
          return;
        }
        
        if (ws.readyState !== WebSocket.OPEN) {
          if (chunkCounter <= 3) {
            console.warn(`⚠️ WebSocket not open (state: ${ws.readyState}), dropping audio chunk`);
          }
          return;
        }
        
        if (isMuted) {
          if (chunkCounter <= 3) {
            console.log('🔇 Chunk dropped - muted');
          }
          return; // Don't send if muted
        }
        
        try {
          // Send raw PCM audio chunk to backend
          ws.send(chunk);
          if (chunkCounter <= 10) {
            console.log('📤 Sent PCM chunk:', chunk.byteLength, 'bytes');
          }
        } catch (error) {
          console.error('❌ Error sending audio chunk:', error);
        }
      },
      // onTranscript (simulated)
      (text) => {
        if (options.onTranscript) {
          options.onTranscript(text, 'customer');
        }
      },
      // enableMonitoring - allow user to hear themselves
      enableMonitoring
    );
    
    console.log('🎙️ Attempting to start recorder with device:', selectedDevice);
    const started = await recorder.start(selectedDevice);
    
    if (started) {
      console.log('✅ Audio recorder started successfully');
      recorderRef.current = recorder;
      setIsAudioEnabled(true);
      
      // Set up persistent audio level monitoring
      const stream = recorder.getStream();
      if (stream) {
        try {
          audioContextRef.current = new AudioContext();
          analyserRef.current = audioContextRef.current.createAnalyser();
          analyserRef.current.fftSize = 256;
          
          const microphone = audioContextRef.current.createMediaStreamSource(stream);
          microphone.connect(analyserRef.current);
          
          const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
          
          // Start monitoring audio level
          audioLevelIntervalRef.current = setInterval(() => {
            if (analyserRef.current && !isMuted) {
              analyserRef.current.getByteFrequencyData(dataArray);
              const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
              const level = average / 255; // Normalize to 0-1
              
              setAudioLevel(level);
              if (options.onAudioLevel) {
                options.onAudioLevel(level);
              }
            } else if (isMuted) {
              setAudioLevel(0);
            }
          }, 100);
          
          console.log('🎙️ Audio started with level monitoring');
        } catch (error) {
          console.error('❌ Error setting up audio level monitoring:', error);
        }
      }
    } else {
      console.error('❌ Failed to start audio recorder');
      alert('Failed to start audio. Please check microphone permissions.');
    }
  }, [ws, selectedDevice, isMuted, enableMonitoring, options]);
  
  const stopAudio = useCallback(() => {
    if (recorderRef.current) {
      recorderRef.current.stop();
      recorderRef.current = null;
      setIsAudioEnabled(false);
      setAudioLevel(0);
      
      if (audioLevelIntervalRef.current) {
        clearInterval(audioLevelIntervalRef.current);
        audioLevelIntervalRef.current = null;
      }
      
      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
        analyserRef.current = null;
      }
      
      console.log('🛑 Audio stopped');
    }
  }, []);
  
  const toggleMute = useCallback(() => {
    setIsMuted(prev => !prev);
  }, []);
  
  const changeDevice = useCallback((deviceId: string) => {
    setSelectedDevice(deviceId);
    
    // If audio is currently enabled, restart with new device
    if (isAudioEnabled) {
      stopAudio();
      setTimeout(() => startAudio(), 100);
    }
  }, [isAudioEnabled, stopAudio, startAudio]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopAudio();
    };
  }, [stopAudio]);
  
  const toggleMonitoring = useCallback(() => {
    setEnableMonitoring(prev => !prev);
    // Restart audio with new monitoring setting
    if (isAudioEnabled) {
      stopAudio();
      setTimeout(() => startAudio(), 100);
    }
  }, [isAudioEnabled, stopAudio, startAudio]);

  return {
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
  };
}
