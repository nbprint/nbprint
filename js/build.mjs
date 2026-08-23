import { bundle } from "./tools/bundle.mjs";
import { bundle_css } from "./tools/css.mjs";
import { node_modules_external } from "./tools/externals.mjs";

import fs from "fs";
import cpy from "cpy";

const BUNDLES = [
  {
    entryPoints: ["src/js/index.js"],
    plugins: [node_modules_external()],
    outfile: "dist/index.js",
  },
  {
    entryPoints: ["src/js/embedded.js"],
    outfile: "dist/embedded.js",
  },
];

<<<<<<< before updating
const BUILD_TARGETS = [
  "../nbprint/extension",
  "../nbprint/templates/nbprint/static",
  "../nbprint/voila/static",
];

async function copy_to_targets(pattern, options = { flat: true }) {
  await Promise.all(
    BUILD_TARGETS.map((target) => cpy(pattern, target, options)),
  );
}

async function build() {
  fs.mkdirSync("dist", { recursive: true });
  BUILD_TARGETS.forEach((target) => fs.mkdirSync(target, { recursive: true }));
=======
async function build() {
  fs.rmSync("dist", { recursive: true, force: true });
  fs.rmSync("../nbprint/extension", {
    recursive: true,
    force: true,
  });

  // Bundle css
  await bundle_css();

  // Copy HTML
  await cpy("src/html/*", "dist/");

  // Copy images
  if (fs.existsSync("src/img")) {
    fs.mkdirSync("dist/img", { recursive: true });
    await cpy("src/img/*", "dist/img");
  }
>>>>>>> after updating

  await bundle_css("src/css");
  await Promise.all(BUNDLES.map(bundle)).catch(() => process.exit(1));

<<<<<<< before updating
  await copy_to_targets("dist/*.js");
  await copy_to_targets("dist/css/*");
  await copy_to_targets(
    "node_modules/@fortawesome/fontawesome-free/css/fontawesome.min.css",
  );
=======
  // Copy servable assets to python extension (exclude esm/)
  fs.mkdirSync("../nbprint/extension", { recursive: true });
  await cpy("dist/**/*", "../nbprint/extension", {
    filter: (file) =>
      !file.relativePath.startsWith("esm/") &&
      !file.relativePath.startsWith("dist/esm/"),
  });
>>>>>>> after updating
}

await build();
