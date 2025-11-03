# How to Run E2E Tests

## Available Commands

The correct npm scripts are:

### Basic Test (Headless)
```bash
npm run test:e2e
```

### Test with Browser Visible (Headed)
```bash
npm run test:e2e:headed
```

### Test + Show Report
```bash
npm run test:e2e:report
```

### Test in Headed Mode + Show Report (What you want!)
```bash
npm run test:e2e:headed:report
```

## What Was Wrong

You typed:
```bash
npm run test:e2e: headed :report  ❌ WRONG
```

**Problem**: 
- Spaces and extra colons break npm script names
- npm script names cannot have spaces
- The script name is `test:e2e:headed:report` (one continuous name)

**Correct**:
```bash
npm run test:e2e:headed:report  ✅ CORRECT
```

## Alternative: Direct Playwright Commands

You can also run Playwright directly:

```bash
# Headed mode with report
npx playwright test --headed && npx playwright show-report

# Just headed mode
npx playwright test --headed

# Just run tests
npx playwright test
```

## Requirements

Make sure:
1. **Backend is running**: `http://localhost:8011`
2. **Frontend is running**: `http://localhost:3082`
3. You're in the `frontend` directory:
   ```bash
   cd exercise_11/frontend
   npm run test:e2e:headed:report
   ```

## Troubleshooting

### "Command not found"
- Make sure you're in `exercise_11/frontend` directory
- Run `npm install` first if needed

### Tests fail immediately
- Check that backend and frontend servers are running
- Verify ports 8011 and 3082 are accessible

