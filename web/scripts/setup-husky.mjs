// Wire Git hooks for the vNext app, which lives in a subdirectory (web/) of the
// repository. Husky's default flow assumes the package sits at the git root; it
// does not, so we point core.hooksPath at web/.husky ourselves. Idempotent, and
// a no-op outside a git checkout (e.g. CI installing from a tarball) so `npm ci`
// never fails on `prepare`.
import { execSync } from "node:child_process";
import { mkdirSync } from "node:fs";
import path from "node:path";

try {
  const gitRoot = execSync("git rev-parse --show-toplevel", {
    stdio: ["ignore", "pipe", "ignore"],
  })
    .toString()
    .trim();

  const webDir = process.cwd();
  const rel = path.relative(gitRoot, webDir).split(path.sep).join("/");
  const hooksPath = rel ? `${rel}/.husky` : ".husky";

  mkdirSync(path.join(webDir, ".husky"), { recursive: true });
  execSync(`git config core.hooksPath "${hooksPath}"`, { cwd: gitRoot, stdio: "ignore" });
  console.log(`[husky] core.hooksPath -> ${hooksPath}`);
} catch {
  console.log("[husky] skipped (not a git checkout)");
}
