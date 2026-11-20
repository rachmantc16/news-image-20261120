// news-image-20261120 — entry program (Node 22+, standard library only).
// Reads entry.png from this directory, validates it is a real PNG within the
// competition limits (at most 1024x1024 px, under 1 MiB), and copies it to the
// output directory given by MAKEFUN_OUTPUT_DIR (default /output) as entry.png.

import { copyFileSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const MAX_BYTES = 1048576;
const MAX_DIM = 1024;
const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function fail(message: string): never {
  console.error(`error: ${message}`);
  process.exit(1);
}

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, 'entry.png');

let data: Buffer;
try {
  data = readFileSync(source);
} catch {
  fail(`cannot read ${source}`);
}

if (data.length < 33) fail('entry.png is too small to be a PNG');
if (!data.subarray(0, 8).equals(PNG_SIGNATURE)) {
  fail('entry.png is not a PNG (bad 8-byte signature)');
}
if (data.length > MAX_BYTES) {
  fail(`entry.png is ${data.length} bytes, over the 1 MiB limit`);
}

// First chunk must be IHDR: length (4) + type (4) + 13 bytes of data.
const ihdrLength = data.readUInt32BE(8);
const ihdrType = data.toString('latin1', 12, 16);
if (ihdrType !== 'IHDR' || ihdrLength !== 13) {
  fail('entry.png has no valid IHDR chunk');
}
const width = data.readUInt32BE(16);
const height = data.readUInt32BE(20);
if (width === 0 || height === 0) fail('entry.png has zero width or height');
if (width > MAX_DIM || height > MAX_DIM) {
  fail(`entry.png is ${width}x${height}, over the 1024x1024 limit`);
}
// A complete PNG ends with a 12-byte IEND chunk: length 0, type "IEND".
if (data.length < 12 || data.readUInt32BE(data.length - 12) !== 0 ||
    data.toString('latin1', data.length - 8, data.length - 4) !== 'IEND') {
  fail('entry.png is truncated (no IEND chunk at the end)');
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
const dest = join(outDir, 'entry.png');
copyFileSync(source, dest);
const copied = statSync(dest).size;
if (copied !== data.length) fail('copied file size does not match entry.png');
console.log(`ok: entry.png ${width}x${height}, ${data.length} bytes -> ${dest}`);
