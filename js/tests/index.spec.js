import { test, expect } from "@playwright/test";

<<<<<<< before updating
test.describe("Basic tests", () => {
  test("exists", async ({ page }) => {});
=======
test.describe("Basics", () => {
  test("basic", async () => {
    await expect("").toBe("");
  });
>>>>>>> after updating
});
