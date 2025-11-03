# How to Fill Out LOAD_TEST_REPORT.md

## Quick Guide

After running your k6 test, you'll see output in your terminal. Here's how to extract the values:

### Step 1: Run Your Test

```powershell
cd exercise_11\load\k6
k6 run coach_scenario.js --duration 15m --vus 10
```

### Step 2: Find These Lines in Terminal Output

Look for these specific lines in your terminal:

```
✓ http_req_failed.........: 0.25%  ✓ 0.25% < 1.00%
✓ http_req_duration.......: avg=1.2s  min=500ms  med=1.1s  max=3.5s  p(95)=2.3s
```

### Step 3: Copy Values to Report

Open `LOAD_TEST_REPORT.md` and fill in:

#### From `http_req_duration` line:
- **p95 Response Time**: Take the `p(95)=` value → `2.3s`
- **Average Response Time**: Take the `avg=` value → `1.2s`
- **Min/Max**: Optional, but helpful for context

#### From `http_req_failed` line:
- **Error Rate**: Take the percentage → `0.25%`

#### Other values you'll see:
```
http_reqs.................: 4500     5/s     ← Throughput (req/s)
iterations.................: 2250              ← Total Iterations
checks.........................: 100%  ✓ 13500  ✗ 0  ← Checks Passed
```

### Step 4: Determine Status

- **p95 ≤ 2.5s?** → ✅ Pass or ❌ Fail
- **Error Rate ≤ 1%?** → ✅ Pass or ❌ Fail

### Example Fill-In

If your terminal shows:
```
✓ http_req_failed.........: 0.25%
✓ http_req_duration.......: avg=1.3s ... p(95)=2.1s
http_reqs.................: 4500     5/s
iterations.................: 2250
```

Then in the report table, fill in:

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **p95 Response Time** | 2.1s | ≤ 2.5s | ✅ **Pass** |
| **Error Rate** | 0.25% | ≤ 1% | ✅ **Pass** |
| **Throughput** | 5 req/s | - | - |
| **Total Iterations** | 2250 | - | - |

### Step 5: Update SLO Verification Section

```
### SLO Verification
✅ **p95 Response Time**: 2.1s < 2.5s **PASS**  
✅ **Error Rate**: 0.25% < 1% **PASS**
```

### Quick Checklist

- [ ] Ran k6 test (15 minutes for Task 7)
- [ ] Found `p(95)=` value from terminal
- [ ] Found `http_req_failed` percentage
- [ ] Filled in values in `LOAD_TEST_REPORT.md`
- [ ] Marked status as ✅ or ❌
- [ ] Updated SLO Verification section

That's it! 🎯

