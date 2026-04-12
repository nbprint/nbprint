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

  await bundle_css("src/css");
  await Promise.all(BUNDLES.map(bundle)).catch(() => process.exit(1));

  await copy_to_targets("dist/*.js");
  await copy_to_targets("dist/css/*");
  await copy_to_targets(
    "node_modules/@fortawesome/fontawesome-free/css/fontawesome.min.css",
  );
}

build();
