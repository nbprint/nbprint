import { NodeModulesExternal } from "@finos/perspective-esbuild-plugin/external.js";
import { build } from "@finos/perspective-esbuild-plugin/build.js";
import { transform } from "lightningcss";
import { getarg } from "./tools/getarg.mjs";
import fs from "fs";
import cpy from "cpy";

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
  },
];

async function compile_css() {
  const process_path = (path) => {
    const outpath = path.replace("src/css", "dist/css");
    fs.mkdirSync(outpath, { recursive: true });

    fs.readdirSync(path, { withFileTypes: true }).forEach((entry) => {
      const input = `${path}/${entry.name}`;
      const output = `${outpath}/${entry.name}`;

      if (entry.isDirectory()) {
        process_path(input);
      } else if (entry.isFile() && entry.name.endsWith(".css")) {
        const source = fs.readFileSync(input);
        const { code } = transform({
          filename: entry.name,
          code: source,
          minify: !DEBUG,
          sourceMap: false,
        });
        fs.writeFileSync(output, code);
      }
    });
  };

  process_path("src/css");
}

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
}

build_all();
