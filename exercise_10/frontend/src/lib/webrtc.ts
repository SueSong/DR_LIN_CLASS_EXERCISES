export class AudioStreamer {
    private mediaStream: MediaStream | null = null;
    private websocket: WebSocket | null = null;
    private audioContext: AudioContext | null = null;
    private processor: ScriptProcessorNode | null = null;
  
    async start(callId: string, wsUrl: string): Promise<void> {
      // Get microphone permission
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
        },
      });
  
      // Connect WebSocket
      this.websocket = new WebSocket(`${wsUrl}/ws/call/${callId}`);
      
      this.websocket.onopen = () => {
        console.log('✅ WebSocket connected');
        this.startStreaming();
      };
  
      this.websocket.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };
    }
  
    private startStreaming() {
      if (!this.mediaStream || !this.websocket) return;
  
      this.audioContext = new AudioContext({ sampleRate: 16000 });
      const source = this.audioContext.createMediaStreamSource(this.mediaStream);
      
      // Create processor for raw audio
      this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
      
      this.processor.onaudioprocess = (event) => {
        if (this.websocket?.readyState === WebSocket.OPEN) {
          const audioData = event.inputBuffer.getChannelData(0);
          
          // Convert Float32Array to Int16Array
          const int16Array = new Int16Array(audioData.length);
          for (let i = 0; i < audioData.length; i++) {
            int16Array[i] = Math.max(-32768, Math.min(32767, audioData[i] * 32768));
          }
          
          // Send to server
          this.websocket.send(int16Array.buffer);
        }
      };
  
      source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);
    }
  
    stop() {
      this.processor?.disconnect();
      this.audioContext?.close();
      this.mediaStream?.getTracks().forEach(track => track.stop());
      this.websocket?.close();
    }
  
    getAudioLevel(): number {
      // Return current volume level for visualization
      return 0.5; // Placeholder
    }
  }
