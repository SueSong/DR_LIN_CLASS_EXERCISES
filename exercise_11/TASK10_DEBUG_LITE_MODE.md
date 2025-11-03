# Task 10: Debugging Lite Mode Issue

## Problem
- Budget set to $0.01
- Dashboard shows "Lite Mode Turns"
- But chatbot still returns full-length responses

## Root Cause
The lite mode responses were not short enough to be noticeably different from full mode.

## Fixes Applied

### 1. Made Lite Mode Responses Much Shorter
**File**: `billing/lite_mode.py`
- Reduced max length from 200 to **120 characters**
- Only use first 2 sentences (instead of 3)
- Shortened base response text
- Simplified notice message

### 2. Added Frontend Notice Display
**File**: `frontend/src/app/coach/chat/page.tsx`
- Added handler for `notice` event from SSE
- Displays budget notice as system message
- Shows "⚠️ Daily budget exceeded. Using lite mode."

### 3. Added Debug Logging
**File**: `backend/app/api/sse.py`
- Logs budget check results
- Logs when lite mode is triggered
- Shows current cost vs budget limit

## How to Verify the Fix

### Step 1: Check Budget Status
```bash
curl http://localhost:8011/api/billing/budget/status
```

**Expected**: `is_over_budget: true` if budget is $0.01 and you've made requests

### Step 2: Check Backend Logs
Look for:
```
[BUDGET CHECK] is_over_budget=True, current_cost=$0.012345, budget_limit=$0.010000
[LITE MODE] Budget exceeded, using lite mode for session sess_xxx
```

### Step 3: Send Test Message
1. Open: http://localhost:3082/coach/chat
2. Send: "How to handle bedtime resistance?"
3. **Expected Results**:
   - ✅ Response is SHORT (max 120 chars + notice)
   - ✅ Notice appears: "⚠️ Daily budget exceeded. Using lite mode."
   - ✅ Response is clearly abbreviated

### Step 4: Compare with Full Mode

**Full Mode** (when budget not exceeded):
- Long detailed response (400+ characters)
- Multiple sentences
- Full citations
- No budget notice

**Lite Mode** (when budget exceeded):
- Short response (120 chars max)
- First 2 sentences only
- Brief citation (title only)
- Budget notice displayed

## Expected Lite Mode Response

**Example**:
```
Brief guidance on How to handle bedtime resistance:

Establishing a consistent bedtime routine helps children transition to sleep. Start the routine 30-60 minutes before bedtime.

📚 Bedtime Routine Best Practices

⚠️ Lite mode: Daily budget exceeded. Response simplified.
```

**Total length**: ~120-150 characters (vs 400+ for full mode)

## If Still Not Working

### Check 1: Budget Actually Exceeded?
```bash
curl http://localhost:8011/api/billing/budget/status
```

If `is_over_budget: false`, the budget hasn't been exceeded yet.

**Fix**: Make more requests until budget is exceeded, or set an even lower budget (e.g., $0.001).

### Check 2: Backend Logs
Check if lite mode is being triggered:
- Look for `[LITE MODE]` in logs
- Check `is_over_budget` value

### Check 3: Frontend Notice
- Check browser console for errors
- Notice should appear as a system message
- If notice doesn't appear, check SSE event handling

### Check 4: Response Length
- Full mode: 400+ characters
- Lite mode: 120-150 characters
- If response is still long, lite mode may not be active

## Testing Steps

1. **Set very low budget**:
   ```bash
   curl -X POST http://localhost:8011/api/billing/budget \
     -H "Content-Type: application/json" \
     -d "{\"daily_budget_usd\": 0.001}"
   ```

2. **Make one request** (will exceed budget):
   - Send any message via frontend
   - Check backend logs for budget check

3. **Make second request**:
   - Should now be lite mode
   - Response should be short
   - Notice should appear

4. **Verify in dashboard**:
   - Check: http://localhost:3082/admin/billing
   - Should show "Lite Mode Turns: 1" or more
   - Budget status should show over budget

