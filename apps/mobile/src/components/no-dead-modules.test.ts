import assert from 'node:assert/strict';
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join, normalize, relative } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

/**
 * No dead module (M05 finding 20): every source module outside `src/app` (Expo Router's routes,
 * which the router loads itself) is imported by another module or test. A hook or helper left
 * with no importer, as `src/hooks/use-recommendations.ts` was after P05.2, fails here.
 */
const src = dirname(dirname(fileURLToPath(import.meta.url)));
const files = (directory: string): string[] => readdirSync(directory).flatMap(name => {
  const path = join(directory, name);
  return statSync(path).isDirectory() ? files(path) : /\.(ts|tsx|js)$/.test(name) ? [path] : [];
});
const PLATFORMS = ['', '.web', '.native', '.ios', '.android'];
const EXTENSIONS = ['', '.ts', '.tsx', '.js'];

test('every source module outside src/app has an importer (M05 finding 20)', () => {
  const all = files(src), imported = new Set<string>();
  for (const file of all) {
    const source = readFileSync(file, 'utf8');
    for (const [, specifier] of source.matchAll(/(?:\bfrom\s+|\bimport\s*\(\s*|\brequire\s*\(\s*|\bimport\s+)['"](\.{1,2}\/[^'"]+)['"]/g)) {
      const base = normalize(join(dirname(file), specifier!)).replace(/\.(ts|tsx|js)$/, '');
      for (const platform of PLATFORMS) for (const extension of EXTENSIONS) {
        const candidate = `${base}${platform}${extension || ''}`;
        for (const path of [candidate, `${base}${platform}.ts`, `${base}${platform}.tsx`, `${base}${platform}.js`]) if (existsSync(path) && statSync(path).isFile()) imported.add(path);
      }
    }
  }
  const unimported = all.map(file => relative(src, file))
    .filter(path => !path.startsWith('app/') && !/\.test\.ts$/.test(path) && !/\.d\.ts$/.test(path) && !imported.has(join(src, path)));
  assert.deepEqual(unimported, []);
});
