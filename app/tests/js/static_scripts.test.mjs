import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const jsRoot = join(dirname(fileURLToPath(import.meta.url)), '..', '..', 'static', 'js');

function scriptFiles(directory) {
  return readdirSync(directory).flatMap((name) => {
    const path = join(directory, name);
    if (statSync(path).isDirectory()) return scriptFiles(path);
    return /\.m?js$/.test(name) ? [path] : [];
  });
}

// A syntax error in a page script silently disables that page; the unit tests above only import helpers.
for (const file of scriptFiles(jsRoot)) {
  test(`static script parses: ${relative(jsRoot, file).split(sep).join('/')}`, () => {
    const result = spawnSync(process.execPath, ['--input-type=module', '--check'], { input: readFileSync(file) });
    assert.equal(result.status, 0, result.stderr.toString());
  });
}
