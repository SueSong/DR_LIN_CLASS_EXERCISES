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
 * Request microphone access
 */
export async function requestMicrophoneAccess(deviceId?: string): Promise<MediaStream | null> {
  try {
    const constraints: MediaStreamConstraints = {
      audio: deviceId ? { deviceId: { exact: deviceId } } : true,
      video: false
    };
    
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    console.log('🎤 Microphone access granted');
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
  private onAudioChunk?: (chunk: ArrayBuffer) => void;
  private onTranscript?: (text: string) => void;
  
  constructor(
    onAudioChunk?: (chunk: ArrayBuffer) => void,
    onTranscript?: (text: string) => void
  ) {
    this.onAudioChunk = onAudioChunk;
    this.onTranscript = onTranscript;
  }
  
  async start(deviceId?: string): Promise<boolean> {
    this.stream = await requestMicrophoneAccess(deviceId);
    
    if (!this.stream) {
      return false;
    }
    
    try {
      // Create audio context with 16kHz sample rate (Whisper compatible)
      this.audioContext = new AudioContext({ sampleRate: 16000 });
      this.source = this.audioContext.createMediaStreamSource(this.stream);
      
      // Create processor for raw audio (4096 samples at a time)
      this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
      
      this.processor.onaudioprocess = (event) => {
        if (this.onAudioChunk) {
          const audioData = event.inputBuffer.getChannelData(0);
          
          // Convert Float32Array to Int16Array (raw PCM format)
          const int16Array = new Int16Array(audioData.length);
          for (let i = 0; i < audioData.length; i++) {
            // Clamp to prevent overflow
            const s = Math.max(-1, Math.min(1, audioData[i]));
            int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
          }
          
          // Send raw PCM data
          this.onAudioChunk(int16Array.buffer);
        }
      };
      
      // Connect the audio pipeline
      this.source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);
      
      console.log('🎙️ Recording started (Raw PCM, 16kHz)');
      return true;
      
    } catch (error) {
      console.error('Error starting recorder:', error);
      return false;
    }
  }
  
  stop() {
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
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

