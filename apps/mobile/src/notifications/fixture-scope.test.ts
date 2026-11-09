import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

/**
 * P06.3, D1 and D6: the notifications module is fixture-only. It imports no push or notification
 * package, no native module and no network client; the app's manifest and configuration add no
 * notification package, plugin or permission. The native module comes with P09.2.
 */
const APP = fileURLToPath(new URL('../../', import.meta.url));
const MODULE = join(APP, 'src', 'notifications');
const sources = () => readdirSync(MODULE).filter(name => /\.tsx?$/.test(name) && !name.endsWith('.test.ts')).map(name => join(MODULE, name));
const ALLOWED = /^(?:react|react-native|expo-router|\.\.?\/.+)$/;
/** `from '…'`, `import('…')`, `require('…')` and the bare side-effect form `import '…'` (correction C1, item 3). */
const SPECIFIER = /\bfrom\s*['"]([^'"]+)['"]|\bimport\s*\(\s*['"]([^'"]+)['"]|\brequire\s*\(\s*['"]([^'"]+)['"]|\bimport\s*['"]([^'"]+)['"]/g;
const specifiers = (text: string) => [...text.matchAll(SPECIFIER)].map(match => match[1] ?? match[2] ?? match[3] ?? match[4]!);

test('the module imports only React, React Native, Expo Router and the app\'s own code', () => {
  const files = sources();
  assert.ok(files.length >= 8);
  for (const file of [...files, join(APP, 'src', 'app', 'notifications.tsx')]) {
    const text = readFileSync(file, 'utf8');
    for (const specifier of specifiers(text)) assert.match(specifier, ALLOWED, `${file} imports ${specifier}`);
    assert.doesNotMatch(text, /\bfetch\s*\(|XMLHttpRequest|navigator\.|expo-notifications|\bLinking\b/, file);
  }
});

test('the import scan reads every import form, the bare side-effect form among them', () => {
  assert.deepEqual(specifiers(`import 'expo-device';\nimport x from "a";\nimport type { Y } from './b.ts';\nconst z = require('c');\nawait import('d');\nimport"e";`),
    ['expo-device', 'a', './b.ts', 'c', 'd', 'e']);
});

test('the manifest, lock and configuration add no notification package, plugin or permission', () => {
  const manifest = readFileSync(join(APP, 'package.json'), 'utf8');
  assert.doesNotMatch(manifest, /notification/i);
  assert.doesNotMatch(readFileSync(join(APP, 'package-lock.json'), 'utf8'), /expo-notifications/);
  assert.doesNotMatch(readFileSync(join(APP, 'app.config.ts'), 'utf8'), /notification|POST_NOTIFICATIONS|aps-environment|google-services/i);
});
