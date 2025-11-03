/**
 * Performance Configuration
 * Thresholds and timing requirements for the application
 */

export const PERFORMANCE_CONFIG = {
  /**
   * First token timeout threshold (in milliseconds)
   * Task 3 requirement: First token < 1.5s
   */
  FIRST_TOKEN_THRESHOLD_MS: 1500,
  
  /**
   * First token timeout threshold (in seconds) - for display
   */
  get FIRST_TOKEN_THRESHOLD_SECONDS(): number {
    return this.FIRST_TOKEN_THRESHOLD_MS / 1000;
  },
  
  /**
   * Chunk streaming delay (in milliseconds)
   * How long to wait between streaming chunks for visible effect
   */
  STREAMING_CHUNK_DELAY_MS: 50,
} as const;

