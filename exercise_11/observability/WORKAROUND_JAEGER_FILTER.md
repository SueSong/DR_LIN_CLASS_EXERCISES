# Workaround: Jaeger Default Filter Can't Be Cleared

If Jaeger has a default filter that you can't clear, try these workarounds:

## Method 1: Override with Better Filter

Instead of clearing, **replace** the Tags filter with something useful:

**Remove:**
```
http.status_code=200 error=true
```

**Replace with:**
```
http.method=POST
```

This will show all POST requests regardless of status code.

**Or:**
```
http.status_code>=200
```

This shows all requests (success and errors).

---

## Method 2: Use Operation Filter Instead

Since Tags filter is stuck, use the **Operation** filter:

1. **Operation dropdown** - Try to find:
   - `POST /api/coach/start`
   - `GET /api/coach/stream`
   - Or any HTTP route operations

2. If you can't find them, the operation names might be different. Check what operations are available in the dropdown.

---

## Method 3: Ignore Tags Filter, Use Duration Filter

Even with a bad Tags filter, you can still find traces:

1. **Set Duration filters:**
   - **Min Duration:** `500ms` or `1s`
   - **Max Duration:** Leave empty or `10s`

2. This will filter by duration, which is what you actually need for p95!

3. The bad Tags filter might show fewer results, but you'll still see traces.

---

## Method 4: Clear Browser Cache/Storage

Jaeger might be storing the filter in browser localStorage:

1. **Open browser DevTools** (F12)
2. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
3. Find **Local Storage** → `http://localhost:16686`
4. Look for keys like `jaeger-ui-filter` or similar
5. **Delete** those keys
6. **Refresh** Jaeger UI

---

## Method 5: Use Different Browser/Session

1. Open Jaeger in:
   - **Incognito/Private window** (no saved settings)
   - **Different browser** (Chrome → Firefox)
   - **Clear cache** for localhost:16686

---

## Method 6: Work With What You Have

If the filter shows `http.status_code=200 error=true`:

**This filter is contradictory**, so it will match **nothing** (or very few traces).

**To see results:**

1. **Remove just `error=true` part:**
   ```
   http.status_code=200
   ```
   This shows successful requests.

2. **Or remove `http.status_code=200` part:**
   ```
   error=true
   ```
   This shows failed requests.

---

## Method 7: Direct URL Parameter

Try modifying the Jaeger URL directly:

**Normal URL:**
```
http://localhost:16686/search?service=child-growth-assistant
```

**With specific filter in URL:**
```
http://localhost:16686/search?service=child-growth-assistant&tags=http.method%3DPOST
```

URL encode the tags:
- `=` becomes `%3D`
- ` ` (space) becomes `%20`

---

## Recommended Quick Fix

**Try this sequence:**

1. **Open Jaeger in Incognito/Private window:**
   ```
   http://localhost:16686
   ```
   This bypasses saved filters.

2. **Set these filters:**
   - Service: `child-growth-assistant`
   - Operation: `all`
   - Tags: `http.method=POST` (or leave empty)
   - Min Duration: `500ms`

3. **Click "Find Traces"**

4. **Look for traces with:**
   - Operation names containing `/api/coach/`
   - Duration > 500ms (not microseconds!)

---

## If Nothing Works

**Bypass Jaeger UI entirely for SLO metrics:**

Use **k6 output** instead - it already calculates p95 and error rate:

```bash
cd exercise_11/load/k6
k6 run coach_scenario.js --duration 15m
```

Look for:
```
http_req_duration......: p(95)=2.1s  ← This is your p95!
http_req_failed........: 0.00%       ← This is your error rate!
```

**This is more accurate anyway!** ✅

---

## Troubleshooting Steps

1. ✅ **Try Incognito window** first (easiest)
2. ✅ **Clear browser localStorage** for localhost:16686
3. ✅ **Modify Tags filter** to remove contradictory parts
4. ✅ **Use Duration filter** instead of Tags
5. ✅ **Fallback: Use k6 output** for SLO metrics

Let me know which method works! 🎯

