import assert from 'node:assert/strict';
import test from 'node:test';
import { inVisibleArea, visibleMessages, type Box } from './visibility.ts';

const area = { offset: 300, height: 400 }; // The visible area is 300 to 700 of the scroll content.

test('a row is in view only when its whole box lies inside the visible area (CX8; DM-23 2.1)', () => {
  assert.equal(inVisibleArea({ top: 300, height: 80 }, area), true);
  assert.equal(inVisibleArea({ top: 620, height: 80 }, area), true, 'its bottom edge on the area\'s');
  assert.equal(inVisibleArea({ top: 620.5, height: 80 }, area), true, 'within sub-pixel rounding');
  assert.equal(inVisibleArea({ top: 660, height: 80 }, area), false, 'half below the fold');
  assert.equal(inVisibleArea({ top: 700, height: 80 }, area), false, 'below the fold');
  assert.equal(inVisibleArea({ top: 260, height: 80 }, area), false, 'half above');
  assert.equal(inVisibleArea({ top: 0, height: 80 }, area), false, 'scrolled past');
});

test('a row taller than the visible area counts when it fills the area', () => {
  assert.equal(inVisibleArea({ top: 250, height: 500 }, area), true);
  assert.equal(inVisibleArea({ top: 350, height: 500 }, area), false);
});

test('an unmeasured row or an unmeasured area is never in view', () => {
  assert.equal(inVisibleArea(undefined, area), false);
  assert.equal(inVisibleArea({ top: 300, height: 0 }, area), false);
  assert.equal(inVisibleArea({ top: 0, height: 10 }, { offset: 0, height: 0 }), false);
});

test('visibleMessages keeps the given order and skips rows not yet measured', () => {
  const boxes = new Map<string, Box>([['a', { top: 200, height: 80 }], ['b', { top: 320, height: 80 }], ['d', { top: 500, height: 80 }], ['e', { top: 690, height: 80 }]]);
  assert.deepEqual(visibleMessages(['a', 'b', 'c', 'd', 'e'], boxes, area), ['b', 'd']);
});
