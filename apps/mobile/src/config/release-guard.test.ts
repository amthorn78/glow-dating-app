import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { developmentPreviewAvailable } from './release-guard.ts';

test('the layout\'s guard renders routes only in a development bundle in fixture mode (M05 finding 17)', () => {
  assert.equal(developmentPreviewAvailable(true, 'fixture'), true);
  for (const [isDevelopment, mode] of [[false, 'fixture'], [false, undefined], [true, undefined], [true, 'live'], [true, 'Fixture'], [true, '']] as const) {
    assert.equal(developmentPreviewAvailable(isDevelopment, mode), false, `__DEV__ ${isDevelopment}, mode ${String(mode)}`);
  }
});

test('the root layout gates every route on that guard, with __DEV__ and the inlined public mode (M05 finding 17)', () => {
  // Nothing can import the layout in Node (it imports Expo Router), so its gate is read from source.
  const source = readFileSync(new URL('../app/_layout.tsx', import.meta.url), 'utf8');
  const layout = source.slice(source.indexOf('export default function RootLayout()'));
  const gate = layout.match(/^\s*if \(!developmentPreviewAvailable\((.*)\)\) \{\n\s*return <SafeAreaProvider><Page><Text style=\{styles\.title\}>Development preview unavailable<\/Text>/m);
  assert.ok(gate, 'RootLayout first returns the unavailable screen unless the guard passes');
  assert.equal(gate[1], '__DEV__, process.env.EXPO_PUBLIC_GLOW_MODE');
  assert.ok(layout.indexOf(gate[0]) < layout.indexOf('<Navigation />'), 'the gate comes before the routes');
  assert.equal(source.match(/<Navigation \/>/g)?.length, 1, 'the routes render in one place only');
});
