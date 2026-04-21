/**
 * Global setup for integration tests — runs the nbprint CLI to generate
 * fresh HTML outputs before Playwright tests start.
 *
 * Invoked via `globalSetup` in integration.config.js.
 */
import { execSync } from "child_process";
import { existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, "..", "..");

const TEMPLATES = ["basic", "inline", "finance", "research", "landscape"];

export default function globalSetup() {
  // Check if nbprint CLI is available
  try {
    execSync("nbprint --help", { stdio: "ignore" });
  } catch {
    console.warn("nbprint CLI not available — skipping HTML generation");
    return;
  }

  for (const template of TEMPLATES) {
    const yamlPath = resolve(REPO_ROOT, "examples", `${template}.yaml`);
    if (!existsSync(yamlPath)) {
      console.warn(`Skipping ${template}: ${yamlPath} not found`);
      continue;
    }

    console.log(`Generating ${template}.html ...`);
    try {
      execSync(`nbprint run ${yamlPath} ++outputs.target=html`, {
        cwd: REPO_ROOT,
        stdio: "pipe",
        timeout: 120_000,
      });
    } catch (e) {
      console.error(`Failed to generate ${template}: ${e.message}`);
    }
  }
}
