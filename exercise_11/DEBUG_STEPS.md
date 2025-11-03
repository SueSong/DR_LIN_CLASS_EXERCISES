# Debug Steps: Why No POST Requests?

## Problem
You're only seeing GET requests, which means messages aren't being sent to the backend.

## Quick Checks

### 1. Check Browser Console (F12)
When you click Send or press Enter, do you see:
- `[SSE] Sending message via SSE: ...` OR
- `[WS] Sending message via WebSocket: ...`

**If NO console logs:**
- The button isn't working
- Check if button is disabled (grayed out)

**If YES console logs but no POST:**
- Network issue
- CORS problem
- Backend not receiving

### 2. Check Connection Status

**For WebSocket:**
- Look at the chat page - does it show "Active Session" (green) or "Disconnected"?
- WebSocket button should only work if connected

**For SSE:**
- Does the page show "Session ready!" message?
- SSE should work as long as session_id exists

### 3. What to Try

**Option A: Use SSE (Enter key or SSE button)**
1. Make sure you see "Session ready!" in chat
2. Type message
3. Press Enter
4. Check browser console (F12) - should see `[SSE] Sending message...`
5. Check backend - should see `[SSE POST] /api/coach/stream called...`

**Option B: Use WebSocket (WS button)**
1. Make sure WebSocket is connected (green "Active Session")
2. Type message
3. Click WS button
4. Check browser console (F12) - should see `[WS] Sending message...`
5. Check backend - should see `[WEBSOCKET] Received message...`

## If Still No POST:

1. **Open browser console** (F12 → Console tab)
2. **Send a message**
3. **Check for errors** in console (red text)
4. **Share the errors** with me

The console will tell us exactly what's wrong!

