/**
 * Global setup for integration tests — runs the nbprint CLI to generate
 * fresh HTML outputs before Playwright tests start.
 *
 * Invoked via `globalSetup` in integration.config.js.
 *
 * Two kinds of fixtures are processed:
 *   1. YAML templates under examples/ — traditional YAML-driven configs.
 *   2. Notebook / YAML wrapper fixtures under nbprint/tests/files/ — E2E
 *      fixtures that originate from an .ipynb and exercise notebook-first
 *      features (section routing, overlays, section-level styles).
 */
import { execSync } from "child_process";
import { existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, "..", "..");

// YAML-driven report templates (under examples/)
const TEMPLATES = ["basic", "inline", "finance", "research", "landscape"];

// Notebook-first E2E fixtures. The YAML wrapper variant pins output naming
// via a thin YAML; the bare .ipynb variants embed `outputs.naming` in their
// own notebook-level nbprint metadata so the generated HTML lands at a
// predictable path.
const NOTEBOOK_FIXTURES = [
  { name: "e2e_notebook", config: "nbprint/tests/files/e2e_notebook.yaml" },
  {
    name: "notebook-sections",
    config: "examples/notebook-sections.ipynb",
    overrides: ["++nbprint.outputs.naming='{{name}}'"],
  },
  {
    name: "notebook-runtime",
    config: "examples/notebook-runtime.ipynb",
    overrides: ["++nbprint.outputs.naming='{{name}}'"],
  },
  {
    name: "notebook-overlays",
    config: "examples/notebook-overlays.ipynb",
    overrides: ["++nbprint.outputs.naming='{{name}}'"],
  },
];

function runConfig(name, configPath, overrides = []) {
  const abs = resolve(REPO_ROOT, configPath);
  if (!existsSync(abs)) {
    console.warn(`Skipping ${name}: ${abs} not found`);
    return;
  }
  console.log(`Generating ${name}.html ...`);
  const script = `from nbprint.cli import run\nrun(${JSON.stringify(configPath)}, overrides=${JSON.stringify(overrides)})\n`;
  try {
    execSync(`python -`, {
      cwd: REPO_ROOT,
      input: script,
      stdio: ["pipe", "pipe", "pipe"],
      timeout: 180_000,
    });
  } catch (e) {
    console.error(`Failed to generate ${name}: ${e.message}`);
  }
}

export default function globalSetup() {
  // Check if nbprint CLI is available
  try {
    execSync("nbprint --help", { stdio: "ignore" });
  } catch {
    console.warn("nbprint CLI not available — skipping HTML generation");
    return;
  }

  for (const template of TEMPLATES) {
    runConfig(template, `examples/${template}.yaml`);
  }

  for (const { name, config, overrides } of NOTEBOOK_FIXTURES) {
    runConfig(name, config, overrides);
  }
}

// Exported for use by spec files so the fixture list stays single-sourced.
export { TEMPLATES, NOTEBOOK_FIXTURES };
