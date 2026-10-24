import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

/**
 * DM-22 7.1: the app holds no provider package and opens no socket or event stream; it
 * talks to Glow's API with `fetch` only (OD-45; the brief's point g). The patterns are built
 * from fragments so that this file, which the scan also reads, names none of them.
 */
const APP = fileURLToPath(new URL('../../', import.meta.url));
const escape = (value: string) => value.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&');
const PACKAGE_NAMES = ['stream' + '-chat', 'get' + 'stream', '@stream' + '-io/'];
const PROVIDER_PACKAGE = new RegExp(PACKAGE_NAMES.map(escape).join('|'), 'i');
const TRANSPORTS = ['Web' + 'Socket', 'Event' + 'Source'].join('|');
const CONSTRUCTIONS = [
  new RegExp(`\\bnew\\s+(?:[\\w$]+\\s*\\??\\.\\s*)*(?:${TRANSPORTS})\\b`),
  new RegExp(`\\bnew\\s+[\\w$.]*\\[\\s*['"\`](?:${TRANSPORTS})['"\`]\\s*\\]`),
  new RegExp(`\\bReflect\\s*\\.\\s*construct\\s*\\(\\s*(?:[\\w$]+\\s*\\.\\s*)*(?:${TRANSPORTS})\\b`),
];
const SPECIFIERS = [/\bfrom\s*['"`]([^'"`]+)['"`]/g, /\bimport\s*\(\s*['"`]([^'"`]+)['"`]\s*\)/g, /\bimport\s*['"`]([^'"`]+)['"`]/g, /\brequire\s*\(\s*['"`]([^'"`]+)['"`]\s*\)/g];
const SOURCE = /\.(?:[cm]?[jt]sx?)$/;

function files(directory: string): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    if (entry.name === 'node_modules' || entry.name === '.work' || entry.name === '.expo') return [];
    const path = join(directory, entry.name);
    return entry.isDirectory() ? files(path) : entry.isFile() && SOURCE.test(entry.name) ? [path] : [];
  });
}
/** The app's source: everything under `src/`, and the app's own top-level and script files. */
function appSource(): string[] {
  const top = readdirSync(APP, { withFileTypes: true }).filter(entry => entry.isFile() && SOURCE.test(entry.name)).map(entry => join(APP, entry.name));
  return [...files(join(APP, 'src')), ...top, ...files(join(APP, 'scripts'))];
}
const dependencyNames = (manifest: Record<string, unknown>) => ['dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies', 'overrides', 'bundleDependencies']
  .flatMap(field => { const value = manifest[field]; return value && typeof value === 'object' ? Object.keys(value) : Array.isArray(value) ? value as string[] : []; });

/** Every finding, so a failure names each file and package. */
function providerFindings(): string[] {
  const findings: string[] = [];
  const manifestText = readFileSync(join(APP, 'package.json'), 'utf8');
  const manifest = JSON.parse(manifestText) as Record<string, unknown>;
  for (const name of dependencyNames(manifest)) if (PROVIDER_PACKAGE.test(name)) findings.push(`package.json names ${name}`);
  if (PROVIDER_PACKAGE.test(manifestText)) findings.push('package.json names a provider package');
  const lockText = readFileSync(join(APP, 'package-lock.json'), 'utf8');
  const lock = JSON.parse(lockText) as { packages?: Record<string, Record<string, unknown>> };
  for (const [path, entry] of Object.entries(lock.packages ?? {})) {
    for (const name of [path, String(entry.name ?? ''), String(entry.resolved ?? ''), ...dependencyNames(entry)]) {
      if (PROVIDER_PACKAGE.test(name)) findings.push(`package-lock.json names ${name}`);
    }
  }
  if (PROVIDER_PACKAGE.test(lockText)) findings.push('package-lock.json names a provider package');
  for (const file of appSource()) {
    const text = readFileSync(file, 'utf8'), where = relative(APP, file);
    for (const pattern of SPECIFIERS) for (const match of text.matchAll(pattern)) {
      if (PROVIDER_PACKAGE.test(match[1]!)) findings.push(`${where} imports ${match[1]}`);
    }
    for (const pattern of CONSTRUCTIONS) if (pattern.test(text)) findings.push(`${where} constructs a socket or event stream`);
  }
  return findings;
}

test('the app\'s manifest, lock and source name no provider package and construct no socket or event stream (DM-22 7.1)', () => {
  assert.ok(appSource().some(file => file.endsWith(join('src', 'chat', 'fixture-adapter.ts'))), 'the scan reads the app\'s source');
  assert.deepEqual(providerFindings(), []);
});

test('the patterns find what DM-22 7.1 names', () => {
  for (const name of PACKAGE_NAMES) assert.ok(PROVIDER_PACKAGE.test(`${name}${name.endsWith('/') ? 'client' : ''}`));
  assert.ok(PROVIDER_PACKAGE.test(`@stream${'-io'}/video-react-native-sdk`));
  const sockets = [`new ${'Web'}Socket('x')`, `new window.${'Web'}Socket(u)`, `new globalThis?.${'Event'}Source(u)`, `new self['${'Web'}Socket'](u)`, `Reflect.construct(${'Event'}Source, [u])`];
  for (const source of sockets) assert.ok(CONSTRUCTIONS.some(pattern => pattern.test(source)), source);
  assert.equal(CONSTRUCTIONS.some(pattern => pattern.test('fetch(url)')), false);
  const imports = [`import x from '${PACKAGE_NAMES[0]}';`, `const y = require("${PACKAGE_NAMES[1]}");`, `await import('${PACKAGE_NAMES[2]}chat');`, `import '${PACKAGE_NAMES[0]}/dist';`];
  for (const source of imports) assert.ok(SPECIFIERS.some(pattern => [...source.matchAll(pattern)].some(match => PROVIDER_PACKAGE.test(match[1]!))), source);
});
