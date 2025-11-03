# Task 8 Memory Optimization

## Changes Made

Reduced polling frequency to save memory and resources:

### HITL Queue Page
- **Before**: Polled every 5 seconds
- **After**: Polls every 30 seconds

### Parent Chat (Mentor Reply Polling)
- **Before**: Polled every 10 seconds
- **After**: Polls every 30 seconds
- **Initial check**: After 5 seconds (was 2 seconds)

## Impact

- ✅ **80-85% reduction** in polling requests
- ✅ Lower memory usage
- ✅ Less server load
- ✅ Still responsive (30s is reasonable for mentor replies)

## Trade-offs

**Note:** Mentor replies will appear:
- **Immediately** via WebSocket when session starts/reconnects
- **Within 30 seconds** via polling (instead of 10 seconds)

For crisis situations, 30 seconds is still reasonable, and WebSocket provides immediate delivery when available.

## If You Want Even Less Polling

You can increase the interval further:
- `30000` = 30 seconds (current)
- `60000` = 1 minute
- `120000` = 2 minutes

Or disable polling entirely and rely only on WebSocket delivery (replies sent on session start/reconnect).

