# Where to See k6 Test Results (p95 & Failure Rate)

## Step-by-Step: Viewing k6 Output

### Step 1: Run the k6 Load Test

Open your terminal (PowerShell) and run:

```powershell
cd exercise_11\load\k6
k6 run coach_scenario.js
```

Or for a 15-minute test (as required for Task 7):

```powershell
cd exercise_11\load\k6
k6 run coach_scenario.js --duration 15m --vus 10
```

### Step 2: Look at the Terminal Output

The results appear **directly in your terminal** while the test runs and at the end.

You'll see output like this:

```
          /\      |‾‾| /‾‾/   /‾‾/   
     /\  /  \     |  |/  /   /  /    
    /  \/    \    |     (   /   ‾‾\  
   /          \   |  |\  \ |  (‾)  | 
  / __________ \  |__| \__\ \_____/ .io

  execution: local
     script: coach_scenario.js
     output: -

  scenarios: (100.00%) 1 scenario, 10 max VUs, 1m30s max duration
           ✓ default: 10 looping VUs for 30s

     ✓ http_req_failed.........: 0.00%  ✓ 0.00% < 1.00%    ← FAILURE RATE
     ✓ http_req_duration.......: avg=1.2s  min=500ms  med=1.1s  max=3.5s  p(95)=2.3s  ← P95 LATENCY

     http_reqs.................: 300     100/s
     iteration_duration........: avg=2.5s  min=1.5s   med=2.2s   max=5.0s
     iterations.................: 100
     vus........................: 10      min=10     max=10
     vus_max...................: 10      min=10     max=10

running (0m30.1s), 00/10 VUs, 300 complete and 0 interrupted iterations
default ✓ [======================================] 10 VUs  30s

✓ checks.........................: 100.00% ✓ 600        ✗ 0
```

### Step 3: Find These Specific Lines

**Look for these two lines in the output:**

1. **`http_req_failed`** - This is your **failure rate**
   ```
   ✓ http_req_failed.........: 0.00%  ✓ 0.00% < 1.00%
   ```
   - The first number is the actual failure rate
   - The checkmark (✓) means it passed the threshold (< 1%)
   - ✅ **This is what you need!**

2. **`http_req_duration`** - This contains **p95 latency**
   ```
   ✓ http_req_duration.......: avg=1.2s  min=500ms  med=1.1s  max=3.5s  p(95)=2.3s
   ```
   - `p(95)=2.3s` is the **95th percentile latency**
   - ✅ **This is what you need!**
   - The checkmark (✓) means it passed the threshold (p95 < 2500ms)

### Step 4: Reading the Results

**Example Output Interpretation:**

```
✓ http_req_failed.........: 0.00%  ✓ 0.00% < 1.00%
✓ http_req_duration.......: avg=1.2s  min=500ms  med=1.1s  max=3.5s  p(95)=2.3s
```

- **Failure Rate:** 0.00% ✅ (< 1% target) → **PASS**
- **p95 Latency:** 2.3s ✅ (< 2.5s target) → **PASS**

**If it fails:**
```
✗ http_req_failed.........: 1.50%  ✗ 1.50% > 1.00%
✗ http_req_duration.......: avg=2.8s  min=800ms  med=2.5s  max=5.0s  p(95)=3.2s
```

- **Failure Rate:** 1.50% ❌ (> 1% target) → **FAIL**
- **p95 Latency:** 3.2s ❌ (> 2.5s target) → **FAIL**

---

## Visual Guide: Where to Look

```
┌─────────────────────────────────────────────────────────────┐
│ PowerShell/Terminal Window                                  │
│                                                             │
│ PS> k6 run coach_scenario.js                                │
│                                                             │
│          /\      |‾‾| /‾‾/   /‾‾/                          │
│     /\  /  \     |  |/  /   /  /                            │
│    /  \/    \    |     (   /   ‾‾\                           │
│   /          \   |  |\  \ |  (‾)  |                          │
│  / __________ \  |__| \__\ \_____/ .io                       │
│                                                             │
│  scenarios: (100.00%) 1 scenario, 10 max VUs, 30s duration │
│                                                             │
│     ✓ http_req_failed.........: 0.00%  ✓ 0.00% < 1.00%    │ ← LOOK HERE!
│     ✓ http_req_duration.......: avg=1.2s ... p(95)=2.3s   │ ← LOOK HERE!
│                                                             │
│     http_reqs.................: 300     100/s                │
│     ...                                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## For Task 7: 15-Minute Test

Run this command:

```powershell
cd exercise_11\load\k6
k6 run coach_scenario.js --duration 15m --vus 10
```

**The output will look the same**, just with more data points:

```
✓ http_req_failed.........: 0.25%  ✓ 0.25% < 1.00%
✓ http_req_duration.......: avg=1.3s  min=400ms  med=1.2s  max=4.5s  p(95)=2.1s
```

---

## Screenshot/Report What to Include

For your Task 7 submission, capture:

1. **The terminal output** showing:
   - `http_req_failed` line with the percentage
   - `http_req_duration` line with `p(95)=X.XXs`

2. **Document in your report:**
   ```
   SLO Compliance Results (15-minute load test):
   
   - p95 Latency: 2.1s ✅ (target: ≤ 2.5s)
   - Failure Rate: 0.25% ✅ (target: ≤ 1%)
   
   Both SLO targets met.
   ```

---

## Troubleshooting

**Don't see the output?**
- Make sure you're running k6 in the correct directory
- Check that k6 is installed: `k6 version`
- Verify backend is running on port 8011

**Output too fast to read?**
- The summary appears at the END of the test
- Wait for the test to complete (30s, 15m, etc.)
- You can also scroll up in terminal to see previous output

**Want to save output to a file?**
```powershell
k6 run coach_scenario.js --duration 15m > test_results.txt
```

Then open `test_results.txt` to see the results!

---

## Quick Summary

**Where:** Terminal/PowerShell window where you ran k6  
**What to look for:** Two specific lines:
- `http_req_failed` → failure rate percentage
- `http_req_duration` → p95 value in `p(95)=X.XXs`

That's it! 🎯

