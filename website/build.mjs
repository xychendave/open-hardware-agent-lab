import { cp, mkdir, readFile, rm } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const dist = join(root, "dist");
const required = ["index.html", "styles.css", "main.js"];

for (const file of required) {
  await readFile(join(root, file));
}

await rm(dist, { recursive: true, force: true });
await mkdir(dist, { recursive: true });

for (const file of required) {
  await cp(join(root, file), join(dist, file));
}

for (const optional of ["assets", "favicon.svg", "site.webmanifest", "robots.txt", "sitemap.xml", ".nojekyll"]) {
  try {
    await cp(join(root, optional), join(dist, optional), { recursive: true });
  } catch (error) {
    if (error?.code !== "ENOENT") throw error;
  }
}

console.log(`Built static site at ${dist}`);
