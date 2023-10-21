import {NodeModulesExternal} from "@finos/perspective-esbuild-plugin/external.js";
import { build } from "@finos/perspective-esbuild-plugin/build.js";
import { BuildCss } from "@prospective.co/procss/target/cjs/procss.js";
import cpy from "cpy";
import fs from "fs";
import path_mod from "path";

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
    outfile: "../nbcx/extension/index.js",
  },
  {
    define: {
      global: "window",
    },
    entryPoints: ["src/js/nbconvert.js"],
    plugins: [],
    format: "esm",
    loader: {
      ".css": "text",
      ".html": "text",
    },
    outfile: "../nbcx/templates/nbcx/static/embedded.js",
  },
  {
    define: {
      global: "window",
    },
    entryPoints: ["src/js/nbconvert.js"],
    plugins: [],
    format: "esm",
    loader: {
      ".css": "text",
      ".html": "text",
    },
    outfile: "../nbcx/voila/static/embedded.js",
  },
];

function add(builder, path) {
  builder.add(
    path,
    fs.readFileSync(path_mod.join("./src/less", path)).toString(),
  );
}

async function compile_css() {
  fs.mkdirSync("../nbcx/extension", { recursive: true });
  fs.mkdirSync("../nbcx/templates/nbcx/static", { recursive: true });
  const builder1 = new BuildCss("");
  add(builder1, "./index.less");
  fs.writeFileSync(
    "../nbcx/extension/index.css",
    builder1.compile().get("index.css"),
  );
}

async function build_all() {
  await compile_css();
  await cpy("./src/css/*", "../nbcx/extension/");
  await cpy("./src/css/*", "../nbcx/templates/nbcx/static/");
  await cpy("./src/css/*", "../nbcx/voila/static/");
  await Promise.all(BUILD.map(build)).catch(() => process.exit(1));
}

build_all();
