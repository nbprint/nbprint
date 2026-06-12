import { getarg } from "./getarg.mjs";

import { bundleAsync } from "lightningcss";
import fs from "fs";
import path from "path";

const DEBUG = getarg("--debug");

const DEFAULT_RESOLVER = {
  resolve(specifier, originatingFile) {
    if (/^https?:\/\//.test(specifier)) {
      return specifier;
    }

    if (specifier.startsWith("perspective-viewer-")) {
      const viewerCssDir = path.resolve(
        "node_modules/@perspective-dev/viewer/dist/css",
      );
      const normalized = specifier.replace(/^perspective-viewer-/, "");
      const normalizedPath = path.join(viewerCssDir, normalized);
      if (fs.existsSync(normalizedPath)) {
        return normalizedPath;
      }
      return path.join(viewerCssDir, specifier);
    }
    return path.resolve(path.dirname(originatingFile), specifier);
  },
};

// paged.js (css-tree@1.1.3) cannot parse Media Queries Level 4 range syntax
// (e.g. `(width<=1180px)`). Without explicit targets, lightningcss minifies
// `min-width`/`max-width` queries into that range form, which paged.js then
// mishandles and renders as blank pages. Target pre-range-syntax browsers so
// the legacy `min-width`/`max-width` form is preserved.
const TARGETS = {
  safari: 13 << 16,
  chrome: 80 << 16,
  firefox: 78 << 16,
};

const bundle_one = async (file, resolver) => {
  const { code } = await bundleAsync({
    filename: path.resolve(file),
    minify: !DEBUG,
    sourceMap: false,
    resolver: resolver || DEFAULT_RESOLVER,
    targets: TARGETS,
  });
  const outName = path.basename(file);
  fs.mkdirSync("./dist/css", { recursive: true });
  fs.writeFileSync(path.join("./dist/css", outName), code);
};

export const bundle_css = async (root = "src/css/index.css", resolver = null) => {
  const resolved = path.resolve(root);
  if (fs.statSync(resolved).isDirectory()) {
    const files = fs.readdirSync(resolved).filter((f) => f.endsWith(".css"));
    for (const file of files) {
      await bundle_one(path.join(root, file), resolver);
    }
  } else {
    await bundle_one(root, resolver);
  }
}
