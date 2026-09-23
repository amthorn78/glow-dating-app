import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import test from 'node:test';
import validators from '../../../apps/mobile/src/contracts/generated/validators.js';
import { assertUniqueKeys } from '../../../apps/mobile/src/contracts/validation.ts';
import { parseDevelopmentRecommendations } from '../../../apps/mobile/src/contracts/recommendations.ts';
import { parseAppIntent, parseAppResponse } from '../../../apps/mobile/src/contracts/production.ts';

const corpus = JSON.parse(readFileSync(new URL('../corpus/shared-v1.json', import.meta.url)));
for (const row of corpus.cases) {
  test(row.name, () => {
    const validate = validators[`validate${row.definition}`];
    assert.equal(typeof validate, 'function');
    assert.equal(Boolean(validate(row.value) && assertUniqueKeys(row.value)), row.valid);
    const parse = row.definition === 'DevelopmentRecommendations' ? parseDevelopmentRecommendations
      : row.definition === 'AppIntent' ? parseAppIntent : row.definition === 'AppResponse' ? parseAppResponse : null;
    if (parse && row.valid) assert.deepEqual(parse(row.value), row.value);
    if (parse && !row.valid) assert.throws(() => parse(row.value));
  });
}
