import { bundle } from "./tools/bundle.mjs";
import { bundle_css } from "./tools/css.mjs";
import { node_modules_external } from "./tools/externals.mjs";

import fs from "fs";
import cpy from "cpy";

<<<<<<< before updating
const DEBUG = getarg("--debug");

const BUILD = [
  {
    define: {
      global: "window",
    },
    entryPoints: ["src/js/index.js"],
    plugins: [NodeModulesExternal()],
    format: "esm",
    loader: {
      ".css": "text",
      ".html": "text",
    },
    outfile: "./dist/index.js",
  },
  {
    define: {
      global: "window",
    },
    entryPoints: ["src/js/embedded.js"],
    plugins: [],
    format: "esm",
    loader: {
      ".css": "text",
      ".html": "text",
    },
    outfile: "./dist/embedded.js",
=======
const BUNDLES = [
  {
    entryPoints: ["src/ts/index.ts"],
    plugins: [node_modules_external()],
    outfile: "dist/esm/index.js",
  },
  {
    entryPoints: ["src/ts/index.ts"],
    outfile: "dist/cdn/index.js",
>>>>>>> after updating
  },
];

async function build() {
  // Bundle css
  await bundle_css();

<<<<<<< before updating
async function cp_to_paths(path) {
  await cpy(path, "../nbprint/extension/", { flat: true });
  await cpy(path, "../nbprint/templates/nbprint/static/", { flat: true });
  (await cpy(path, "../nbprint/voila/static/"), { flat: true });
}

async function build_all() {
  /* make directories */
  fs.mkdirSync("../nbprint/extension", { recursive: true });
  fs.mkdirSync("../nbprint/templates/nbprint/static", { recursive: true });
  fs.mkdirSync("../nbprint/voila/static", { recursive: true });

  /* Compile and copy JS */
  await Promise.all(BUILD.map(build)).catch(() => process.exit(1));
  await cp_to_paths("./dist/*");

  /* Compile and copy css */
  await compile_css();
  await cp_to_paths("./src/css/*");
  await cp_to_paths(
    "node_modules/@fortawesome/fontawesome-free/css/fontawesome.min.css",
  );
=======
  // Copy HTML
  cpy("src/html/*", "dist/");

  // Copy images
  fs.mkdirSync("dist/img", { recursive: true });
  cpy("src/img/*", "dist/img");

  await Promise.all(BUNDLES.map(bundle)).catch(() => process.exit(1));

  // Copy servable assets to python extension (exclude esm/)
  fs.mkdirSync("../nbprint/extension", { recursive: true });
  cpy("dist/**/*", "../nbprint/extension", {
    filter: (file) => !file.relativePath.startsWith("esm"),
  });
>>>>>>> after updating
}

build();
