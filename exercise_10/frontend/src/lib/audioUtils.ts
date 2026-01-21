/**
 * Audio utilities for WebRTC voice calls
 */

export interface AudioDevice {
  deviceId: string;
  label: string;
}

/**
 * Get available audio input devices (microphones)
 */
export async function getAudioDevices(): Promise<AudioDevice[]> {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    return devices
      .filter(device => device.kind === 'audioinput')
      .map(device => ({
        deviceId: device.deviceId,
        label: device.label || `Microphone ${device.deviceId.substring(0, 5)}`
      }));
  } catch (error) {
    console.error('Error getting audio devices:', error);
    return [];
  }
}

/**
 * Detect if headphones are likely connected
 * This is a heuristic - browsers don't directly expose headphone detection
 */
async function detectHeadphones(): Promise<boolean> {
  try {
    // Try to enumerate audio output devices
    const devices = await navigator.mediaDevices.enumerateDevices();
    const audioOutputs = devices.filter(d => d.kind === 'audiooutput');
    
    // If multiple audio outputs, user might have headphones
    // This is not perfect, but helps
    if (audioOutputs.length > 1) {
      console.log('🎧 Multiple audio outputs detected - assuming headphones may be connected');
      return true; // Assume headphones for safety
    }
    
    // Default: assume speakers (safer for echo cancellation)
    return false;
  } catch (e) {
    // If we can't detect, assume speakers (safer)
    console.warn('⚠️ Could not detect audio outputs, assuming speakers');
    return false;
  }
}

/**
 * Request microphone access
 * Automatically enables echo cancellation when using speakers (no headphones)
 */
export async function requestMicrophoneAccess(deviceId?: string, enableEchoCancellation: boolean = false): Promise<MediaStream | null> {
  try {
    // If echo cancellation is disabled (for monitoring), check if headphones are connected
    let shouldUseEchoCancellation = enableEchoCancellation;
    
    if (!enableEchoCancellation) {
      // Monitoring is enabled - check if headphones are connected
      const hasHeadphones = await detectHeadphones();
      if (!hasHeadphones) {
        // No headphones detected - enable echo cancellation to prevent feedback
        console.warn('⚠️ No headphones detected - enabling echo cancellation to prevent feedback');
        console.warn('⚠️ Monitoring disabled when using speakers to prevent audio feedback loops');
        shouldUseEchoCancellation = true;
      } else {
        console.log('🎧 Headphones detected - echo cancellation disabled for monitoring');
      }
    }
    
    const constraints: MediaStreamConstraints = {
      audio: deviceId 
        ? { 
            deviceId: { exact: deviceId },
            echoCancellation: shouldUseEchoCancellation,
            noiseSuppression: true,
            autoGainControl: true
          } 
        : {
            echoCancellation: shouldUseEchoCancellation,
            noiseSuppression: true,
            autoGainControl: true
          },
      video: false
    };
    
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    console.log(`🎤 Microphone access granted (echoCancellation: ${shouldUseEchoCancellation})`);
    
    // Log the actual constraints applied by the browser
    if (stream.getAudioTracks().length > 0) {
      const track = stream.getAudioTracks()[0];
      const settings = track.getSettings();
      console.log(`🎤 Actual audio settings:`, {
        echoCancellation: settings.echoCancellation,
        noiseSuppression: settings.noiseSuppression,
        autoGainControl: settings.autoGainControl,
        sampleRate: settings.sampleRate
      });
      
      // Warn if echo cancellation is still enabled when monitoring is on
      if (!enableEchoCancellation && settings.echoCancellation) {
        console.warn('⚠️ Echo cancellation enabled to prevent feedback (using speakers)');
        console.warn('💡 Tip: Use headphones to enable monitoring and hear yourself');
      }
    }
    
    return stream;
  } catch (error: any) {
    console.error('Error accessing microphone:', error);
    
    if (error.name === 'NotAllowedError') {
      alert('Microphone access denied. Please allow microphone access in your browser settings.');
    } else if (error.name === 'NotFoundError') {
      alert('No microphone found. Please connect a microphone and try again.');
    } else {
      alert(`Microphone error: ${error.message}`);
    }
    
    return null;
  }
}

/**
 * Stop all tracks in a media stream
 */
export function stopMediaStream(stream: MediaStream | null) {
  if (stream) {
    stream.getTracks().forEach(track => {
      track.stop();
      console.log('🛑 Stopped track:', track.kind);
    });
  }
}

/**
 * Get audio level from audio stream (for visualization)
 */
export function getAudioLevel(stream: MediaStream): number {
  try {
    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const microphone = audioContext.createMediaStreamSource(stream);
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    
    microphone.connect(analyser);
    analyser.getByteFrequencyData(dataArray);
    
    // Calculate average level
    const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
    return average / 255; // Normalize to 0-1
  } catch (error) {
    console.error('Error getting audio level:', error);
    return 0;
  }
}

/**
 * Create an audio recorder that sends RAW PCM chunks to WebSocket
 * Uses Web Audio API for real-time streaming (better for 2-way audio)
 */
export class AudioRecorder {
  private stream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private processor: ScriptProcessorNode | null = null;
  private source: MediaStreamAudioSourceNode | null = null;
  private gainNode: GainNode | null = null;
  private onAudioChunk?: (chunk: ArrayBuffer) => void;
  private onTranscript?: (text: string) => void;
  private enableMonitoring: boolean = false;
  private monitoringVolume: number = 0.8; // 80% volume for monitoring (increased for better hearing)
  private _chunkCount: number = 0;
  
  constructor(
    onAudioChunk?: (chunk: ArrayBuffer) => void,
    onTranscript?: (text: string) => void,
    enableMonitoring: boolean = false
  ) {
    this.onAudioChunk = onAudioChunk;
    this.onTranscript = onTranscript;
    this.enableMonitoring = enableMonitoring;
  }
  
  async start(deviceId?: string): Promise<boolean> {
    // Reset chunk counter
    this._chunkCount = 0;
    
    console.log(`🎙️ Starting recorder with monitoring: ${this.enableMonitoring}`);
    
    // Check if headphones are connected before deciding on echo cancellation
    const hasHeadphones = await detectHeadphones();
    
    // If monitoring is enabled but no headphones, disable monitoring to prevent feedback
    if (this.enableMonitoring && !hasHeadphones) {
      console.warn('⚠️ Monitoring requested but no headphones detected');
      console.warn('⚠️ Disabling monitoring to prevent audio feedback when using speakers');
      this.enableMonitoring = false; // Temporarily disable for this session
    }
    
    // Disable echo cancellation if monitoring is enabled AND headphones are connected
    // Otherwise, always enable echo cancellation to prevent feedback
    const shouldDisableEchoCancellation = this.enableMonitoring && hasHeadphones;
    this.stream = await requestMicrophoneAccess(deviceId, !shouldDisableEchoCancellation);
    
    if (!this.stream) {
      console.error('❌ Failed to get microphone access');
      return false;
    }
    
    try {
      // Create audio context with 16kHz sample rate (Whisper compatible)
      this.audioContext = new AudioContext({ sampleRate: 16000 });
      
      // Resume audio context if suspended (required by browsers)
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
        console.log('🔊 Audio context resumed');
      }
      
      this.source = this.audioContext.createMediaStreamSource(this.stream);
      
      // Create processor for raw audio (4096 samples at a time)
      this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
      
      this.processor.onaudioprocess = (event) => {
        this._chunkCount++;
        
        if (!this.onAudioChunk) {
          if (this._chunkCount <= 3) {
            console.warn('⚠️ onAudioChunk callback not set!');
          }
          return;
        }
        
        const audioData = event.inputBuffer.getChannelData(0);
        
        // Check if audio is actually being captured (not silent)
        let hasAudio = false;
        let maxAmplitude = 0;
        for (let i = 0; i < audioData.length; i++) {
          const abs = Math.abs(audioData[i]);
          maxAmplitude = Math.max(maxAmplitude, abs);
          if (abs > 0.01) {
            hasAudio = true;
          }
        }
        
        // Convert Float32Array to Int16Array (raw PCM format)
        const int16Array = new Int16Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
          // Clamp to prevent overflow
          const s = Math.max(-1, Math.min(1, audioData[i]));
          int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        
        // Log first few chunks to verify audio is being captured
        if (this._chunkCount <= 5) {
          console.log(`🎤 Audio processor chunk ${this._chunkCount}: ${int16Array.length} samples, hasAudio: ${hasAudio}, maxAmp: ${maxAmplitude.toFixed(4)}`);
        }
        
        // Send raw PCM data
        try {
          this.onAudioChunk(int16Array.buffer);
        } catch (error) {
          console.error('❌ Error in onAudioChunk callback:', error);
        }
      };
      
      // Connect the audio pipeline for recording
      // IMPORTANT: processor must be connected to destination to work!
      this.source.connect(this.processor);
      this.processor.connect(this.audioContext.destination); // This is required for ScriptProcessorNode to work!
      
      console.log('🔗 Audio pipeline connected: source -> processor -> destination');
      console.log(`🔍 Checking monitoring: enableMonitoring = ${this.enableMonitoring}`);
      
      // If monitoring is enabled, also connect to speakers (with volume control)
      if (this.enableMonitoring) {
        console.log('✅ Monitoring is ENABLED - setting up audio feedback...');
        // Create a separate gain node for monitoring with higher volume
        this.gainNode = this.audioContext.createGain();
        this.gainNode.gain.value = this.monitoringVolume;
        
        // Create a splitter to send audio to both processor and monitoring
        // Since we can't use ChannelSplitterNode for this, we'll connect source to both
        // The processor is already connected, so we connect monitoring separately
        this.source.connect(this.gainNode);
        this.gainNode.connect(this.audioContext.destination);
        
        console.log(`🔊 Audio monitoring enabled at ${(this.monitoringVolume * 100).toFixed(0)}% volume (you can hear yourself)`);
        console.log(`🔊 Monitoring gain node value: ${this.gainNode.gain.value}`);
        console.log(`🔊 Audio context state: ${this.audioContext.state}`);
        console.log(`🔊 Monitoring connection: source -> gainNode(${this.gainNode.gain.value}) -> destination`);
        
        // Verify monitoring connection
        if (this.gainNode.numberOfInputs > 0 && this.gainNode.numberOfOutputs > 0) {
          console.log('✅ Monitoring gain node is properly connected');
        } else {
          console.warn('⚠️ Monitoring gain node connection issue');
        }
        
        // Test: Play a short beep to verify audio output works
        try {
          const oscillator = this.audioContext.createOscillator();
          const testGain = this.audioContext.createGain();
          oscillator.connect(testGain);
          testGain.connect(this.audioContext.destination);
          oscillator.frequency.value = 440; // A4 note
          testGain.gain.value = 0.1; // Low volume test
          oscillator.start();
          oscillator.stop(this.audioContext.currentTime + 0.1);
          console.log('🔊 Test beep played - if you heard it, audio output is working');
        } catch (e) {
          console.warn('Could not play test beep:', e);
        }
        
        // Additional test: Play monitoring audio after a delay to verify it's working
        setTimeout(() => {
          if (this.gainNode && this.audioContext && this.audioContext.state === 'running') {
            console.log('🔊 Monitoring should be active now - speak and you should hear yourself');
            console.log(`🔊 If you still can't hear yourself:`);
            console.log(`   1. Check your system volume`);
            console.log(`   2. Check if you heard the test beep`);
            console.log(`   3. Try speaking louder`);
            console.log(`   4. Try using speakers instead of headphones`);
            
            // Test monitoring by temporarily increasing volume
            const originalGain = this.gainNode.gain.value;
            this.gainNode.gain.value = 1.0; // 100% for test
            console.log(`🔊 Temporarily increased monitoring to 100% for testing...`);
            setTimeout(() => {
              if (this.gainNode) {
                this.gainNode.gain.value = originalGain;
                console.log(`🔊 Monitoring volume restored to ${(originalGain * 100).toFixed(0)}%`);
              }
            }, 2000);
          }
        }, 1000);
      } else {
        console.log('🔇 Audio monitoring disabled');
      }
      
      // Verify stream has active tracks
      const tracks = this.stream.getAudioTracks();
      console.log(`🎤 Audio tracks: ${tracks.length}, enabled: ${tracks.map(t => t.enabled).join(',')}, readyState: ${tracks.map(t => t.readyState).join(',')}`);
      
      console.log('🎙️ Recording started (Raw PCM, 16kHz)');
      return true;
      
    } catch (error) {
      console.error('Error starting recorder:', error);
      return false;
    }
  }
  
  setMonitoringVolume(volume: number) {
    this.monitoringVolume = Math.max(0, Math.min(1, volume)); // Clamp between 0 and 1
    if (this.gainNode) {
      this.gainNode.gain.value = this.monitoringVolume;
    }
  }
  
  stop() {
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    
    if (this.gainNode) {
      this.gainNode.disconnect();
      this.gainNode = null;
    }
    
    if (this.source) {
      this.source.disconnect();
      this.source = null;
    }
    
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    
    stopMediaStream(this.stream);
    this.stream = null;
    
    console.log('🎙️ Recording stopped');
  }
  
  isRecording(): boolean {
    return this.audioContext?.state === 'running';
  }
  
  getStream(): MediaStream | null {
    return this.stream;
  }
}

// Audio playback using Web Audio API for raw PCM
let playbackAudioContext: AudioContext | null = null;
let audioEnabled = false;
let nextPlayTime = 0;
const sampleRate = 16000; // Must match recording sample rate

/**
 * Enable audio playback (must be called after user interaction)
 */
export function enableAudioPlayback() {
  if (!playbackAudioContext) {
    playbackAudioContext = new AudioContext({ sampleRate });
    nextPlayTime = playbackAudioContext.currentTime;
  }
  audioEnabled = true;
  console.log('🔊 Audio playback enabled (16kHz PCM)');
}

/**
 * Play raw PCM audio received from WebSocket
 */
export async function playAudioChunk(audioData: Blob | ArrayBuffer) {
  if (!audioEnabled || !playbackAudioContext) {
    return;
  }
  
  try {
    // Convert Blob to ArrayBuffer if needed
    const arrayBuffer = audioData instanceof Blob ? await audioData.arrayBuffer() : audioData;
    
    // Convert Int16Array PCM to Float32Array
    const int16Array = new Int16Array(arrayBuffer);
    const float32Array = new Float32Array(int16Array.length);
    
    // Calculate audio level to check if it's silent
    let maxAmplitude = 0;
    let sumAmplitude = 0;
    
    for (let i = 0; i < int16Array.length; i++) {
      // Convert Int16 to Float32 (-1.0 to 1.0)
      float32Array[i] = int16Array[i] / (int16Array[i] < 0 ? 0x8000 : 0x7FFF);
      
      // Track amplitude for debugging
      const amplitude = Math.abs(float32Array[i]);
      maxAmplitude = Math.max(maxAmplitude, amplitude);
      sumAmplitude += amplitude;
    }
    
    const avgAmplitude = sumAmplitude / float32Array.length;
    
    // Create audio buffer
    const audioBuffer = playbackAudioContext.createBuffer(1, float32Array.length, sampleRate);
    audioBuffer.getChannelData(0).set(float32Array);
    
    // Create and schedule audio source
    const source = playbackAudioContext.createBufferSource();
    source.buffer = audioBuffer;
    
    // Add gain node to boost volume (2x amplification)
    const gainNode = playbackAudioContext.createGain();
    gainNode.gain.value = 2.0; // Boost volume
    
    source.connect(gainNode);
    gainNode.connect(playbackAudioContext.destination);
    
    // Schedule playback to prevent gaps
    const playTime = Math.max(nextPlayTime, playbackAudioContext.currentTime);
    source.start(playTime);
    
    // Update next play time
    nextPlayTime = playTime + audioBuffer.duration;
    
    console.log(`✅ Audio chunk played (${int16Array.length} samples, ${audioBuffer.duration.toFixed(2)}s) | Max: ${maxAmplitude.toFixed(4)}, Avg: ${avgAmplitude.toFixed(4)}`);
  } catch (error: any) {
    console.error('❌ Error playing audio:', error);
    
    // Reset timing if there's an error
    if (playbackAudioContext) {
      nextPlayTime = playbackAudioContext.currentTime;
    }
  }
}

/**
 * Audio visualization using Web Audio API
 */
export class AudioVisualizer {
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private dataArray: Uint8Array | null = null;
  private animationId: number | null = null;
  
  constructor(private canvas: HTMLCanvasElement) {}
  
  start(stream: MediaStream) {
    this.audioContext = new AudioContext();
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 256;
    
    const microphone = this.audioContext.createMediaStreamSource(stream);
    microphone.connect(this.analyser);
    
    const bufferLength = this.analyser.frequencyBinCount;
    this.dataArray = new Uint8Array(bufferLength);
    
    this.draw();
  }
  
  private draw() {
    if (!this.analyser || !this.dataArray) return;
    
    this.animationId = requestAnimationFrame(() => this.draw());
    
    this.analyser.getByteFrequencyData(this.dataArray);
    
    const ctx = this.canvas.getContext('2d');
    if (!ctx) return;
    
    const width = this.canvas.width;
    const height = this.canvas.height;
    
    ctx.fillStyle = 'rgb(15, 23, 42)'; // slate-900
    ctx.fillRect(0, 0, width, height);
    
    const barWidth = (width / this.dataArray.length) * 2.5;
    let x = 0;
    
    for (let i = 0; i < this.dataArray.length; i++) {
      const barHeight = (this.dataArray[i] / 255) * height;
      
      const gradient = ctx.createLinearGradient(0, height - barHeight, 0, height);
      gradient.addColorStop(0, 'rgb(59, 130, 246)'); // blue-500
      gradient.addColorStop(1, 'rgb(37, 99, 235)'); // blue-600
      
      ctx.fillStyle = gradient;
      ctx.fillRect(x, height - barHeight, barWidth, barHeight);
      
      x += barWidth + 1;
    }
  }
  
  stop() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    
    if (this.audioContext) {
      this.audioContext.close();
    }
    
    this.audioContext = null;
    this.analyser = null;
    this.dataArray = null;
  }
}

