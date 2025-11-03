import { defineConfig, devices } from '@playwright/test';

const base = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3082';

export default defineConfig({
  testDir: './e2e',
  timeout: 60000, // Increase timeout for slower tests
  expect: { timeout: 5000 },
  fullyParallel: false, // Disable parallel execution to avoid server overload
  workers: 1, // Run tests sequentially
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'on-failure' }],
  ],
  use: {
    baseURL: base,
    trace: 'on-first-retry',
    video: 'on',
    screenshot: 'only-on-failure',
    // Slow down actions so you can see what's happening
    // Uncomment the line below to slow tests (500ms delay between actions)
    // slowMo: 500,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
