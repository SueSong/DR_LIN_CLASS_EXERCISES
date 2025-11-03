# Quick Test Options (Instead of 15 Minutes)

## Option 1: Run in Background & Come Back Later ✅ Recommended

Start the 15-minute test and let it run while you do other things:

```powershell
cd exercise_11\load\k6
k6 run coach_scenario.js --duration 15m --vus 10 > test_results.txt
```

**Then:**
- The test runs in the background
- Results save to `test_results.txt`
- You can do other work
- Come back in 15 minutes to check results

**To view results later:**
```powershell
cat test_results.txt
# Or in Windows:
type test_results.txt
```

---

## Option 2: Short Test First (Verify Everything Works)

Run a **2-minute test** first to make sure everything works:

```powershell
cd exercise_11\load\k6
k6 run coach_scenario.js --duration 2m --vus 10
```

**Why do this:**
- ✅ Verifies k6 works
- ✅ Shows you how to read output
- ✅ Catches any errors quickly
- ✅ Gets p95 and failure rate format

**Then later, when ready:**
```powershell
k6 run coach_scenario.js --duration 15m --vus 10
```

---

## Option 3: Reduce Load (Faster but Less Realistic)

Use fewer virtual users to reduce load:

```powershell
cd exercise_11\load\k6
k6 run coach_scenario.js --duration 15m --vus 5
```

**Trade-off:**
- Less load on your system
- Faster to complete (still 15 minutes though)
- Less realistic load scenario

---

## Option 4: Split into Multiple Shorter Tests

Run three 5-minute tests and average results:

```powershell
# Test 1
k6 run coach_scenario.js --duration 5m --vus 10 > test1.txt

# Test 2  
k6 run coach_scenario.js --duration 5m --vus 10 > test2.txt

# Test 3
k6 run coach_scenario.js --duration 5m --vus 10 > test3.txt
```

**Note:** Task 7 specifically asks for "15-min load test", so you'll still need to run one full 15-minute test for submission.

---

## Recommended Approach

**For development/debugging:**
```powershell
# Quick 2-minute test
k6 run coach_scenario.js --duration 2m --vus 10
```

**For Task 7 submission (when ready):**
```powershell
# Full 15-minute test (run in background)
k6 run coach_scenario.js --duration 15m --vus 10 > test_results.txt

# Check results later
type test_results.txt
```

---

## Why 15 Minutes?

The 15-minute requirement tests:
- **Sustained performance** (not just spikes)
- **Memory leaks** or resource accumulation
- **Real-world usage patterns**
- **Consistent SLO compliance** over time

A 30-second test might look good, but 15 minutes reveals issues that only appear under sustained load.

---

## Time-Saving Tips

1. **Start it, walk away**: Let it run while you work on other tasks
2. **Save output to file**: Use `> results.txt` so you don't need to watch it
3. **Run overnight**: Start it before leaving, check results in the morning
4. **Verify with short test first**: Make sure everything works with 2min test before committing to 15min

---

## Quick Command Reference

```powershell
# Quick test (2 minutes) - for verification
k6 run coach_scenario.js --duration 2m --vus 10

# Full test (15 minutes) - for Task 7
k6 run coach_scenario.js --duration 15m --vus 10

# Full test + save to file (best option!)
k6 run coach_scenario.js --duration 15m --vus 10 > test_results.txt
```

**My recommendation:** Use Option 1 (background + file output). Start it and come back later! 🎯

