import test from 'node:test';
import assert from 'node:assert/strict';

import { resolveHashTarget } from '../../static/js/modules/navigation/scroll-state.js';

test('resolveHashTarget resolves encoded fragment IDs without treating them as page navigation', () => {
  const expected = { id: 'fn-spanish-design-1-de' };
  const root = {
    getElementById(id) {
      return id === expected.id ? expected : null;
    },
  };

  assert.equal(resolveHashTarget('#fn-spanish-design-1-de', root), expected);
  assert.equal(resolveHashTarget('#fn-spanish-design-1%2Dde', root), expected);
  assert.equal(resolveHashTarget('#missing', root), null);
  assert.equal(resolveHashTarget('#%E0%A4%A', root), null);
  assert.equal(resolveHashTarget('', root), null);
});
