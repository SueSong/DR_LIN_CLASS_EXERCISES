# Customer Simulator

A simple HTML page to simulate customer calls for testing the AI Call Center Assistant.

## Usage

### Option 1: Open directly in browser
```bash
open customer-sim/index.html
# or
firefox customer-sim/index.html
# or
chrome customer-sim/index.html
```

### Option 2: Serve with Python
```bash
cd customer-sim
python3 -m http.server 8080
# Open http://localhost:8080 in your browser
```

### Option 3: Serve with Node.js
```bash
cd customer-sim
npx http-server -p 8080
# Open http://localhost:8080 in your browser
```

## How to Test

1. **Start the backend server**
   ```bash
   cd ../backend
   uvicorn app.main:app --reload
   ```

2. **Open the customer simulator**
   - Open `index.html` in your browser

3. **Configure connection**
   - Default WebSocket URL: `ws://localhost:8000/ws/call/`
   - Enter your name (e.g., "John Doe")

4. **Start a call**
   - Click "📞 Start Call"
   - Status should change to "🟢 Connected"

5. **Send messages**
   - Type a message or click a quick message button
   - Click "💬 Send Message"
   - Message appears in the transcript

6. **End the call**
   - Click "📴 End Call"
   - Status returns to "⚫ Disconnected"

## Quick Messages

The simulator includes preset messages for common scenarios:
- **Order inquiry:** "Hi, I need help with order #78901"
- **Refund request:** "I want to request a refund"
- **Account issue:** "My account is locked"
- **Upgrade question:** "How do I upgrade my plan?"

## Features

- ✅ WebSocket connection to backend
- ✅ Send text messages (simulating transcription)
- ✅ Receive responses from backend
- ✅ Real-time transcript display
- ✅ Color-coded messages (customer vs agent vs system)
- ✅ Quick message templates
- ✅ Clean, modern UI

## Troubleshooting

### Can't connect
- Ensure backend is running on port 8000
- Check WebSocket URL is correct
- Open browser console (F12) for error messages

### Messages not sending
- Ensure call is started (status should be "In call")
- Check backend logs for WebSocket errors

### No response from agent
- This is expected! The simulator only sends text messages
- The backend will echo your messages back
- Real agent responses require AI integration (Phase 4 of student tasks)

## Next Steps

This simulator is for **basic testing** of WebSocket connectivity and message passing.

For full testing with:
- **Real audio:** Implement WebRTC audio capture
- **AI responses:** Integrate OpenAI GPT-4 for suggestions
- **Transcription:** Add Whisper API for speech-to-text

See `STUDENT_TASKS.md` for implementation steps.

