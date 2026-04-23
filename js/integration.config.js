import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright configuration for integration tests.
 *
 * These tests run the full nbprint Python pipeline (via globalSetup)
 * to generate HTML, then open each report in Chromium and verify
 * structural correctness (pages rendered, no overflow, no blank pages).
 */
export default defineConfig({
  testDir: "tests",
  testMatch: ["integration.spec.js", "integration-visual.spec.js"],

  // Snapshot configuration for visual regression tests
  snapshotPathTemplate:
    "{testDir}/{testFileDir}/{testFileName}-snapshots/{arg}{ext}",
  expect: {
    toHaveScreenshot: {
      maxDiffPixelRatio: 0.01,
    },
  },

  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  reporter: [["html", { open: "never" }]],

  globalSetup: "./tests/integration.setup.mjs",

  use: {
    baseURL: "http://127.0.0.1:3000",
    trace: "on-first-retry",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  webServer: {
    command: "pnpm start:tests",
    url: "http://127.0.0.1:3000",
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
