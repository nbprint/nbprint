import {NodeModulesExternal} from "@finos/perspective-esbuild-plugin/external.js";
import { build } from "@finos/perspective-esbuild-plugin/build.js";
import { BuildCss } from "@prospective.co/procss/target/cjs/procss.js";
import cpy from "cpy";
import fs from "fs";
import { createRequire } from 'node:module';


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

const require = createRequire(import.meta.url);
function add(builder, path, path2) {
  builder.add(
      path,
      fs.readFileSync(require.resolve(path2 || path)).toString()
  );
}

async function compile_css() {
  const builder1 = new BuildCss("");
  add(builder1, "./src/less/index.less");

  const css = builder1.compile().get("index.css");

  // write to extension
  fs.writeFileSync(
    "../nbprint/extension/index.css",
    css,
  );
  // write to template
  fs.writeFileSync(
    "../nbprint/templates/nbprint/static/nbprint.css",
    css,
  );

}

async function cp_to_paths(path) {
  await cpy(path, "../nbprint/extension/", {flat: true});
  await cpy(path, "../nbprint/templates/nbprint/static/", {flat: true});
  await cpy(path, "../nbprint/voila/static/"), {flat: true};
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
  await cp_to_paths("node_modules/\@fortawesome/fontawesome-free/css/fontawesome.min.css");
}

build_all();
