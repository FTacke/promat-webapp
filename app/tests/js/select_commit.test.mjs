import test from 'node:test';
import assert from 'node:assert/strict';

import { bindSelectCommit } from '../../static/js/modules/research/select-commit.js';

function fakeSelect(initial) {
  const listeners = {};
  return {
    value: initial,
    addEventListener(type, handler) {
      (listeners[type] ||= []).push(handler);
    },
    fire(type, event = {}) {
      for (const handler of listeners[type] || []) handler(event);
    },
  };
}

test.beforeEach(() => {
  globalThis.window = { setTimeout: (fn) => { fn(); return 0; } };
});

test('a pointer or assistive-technology change commits immediately', () => {
  const select = fakeSelect('a');
  const committed = [];
  bindSelectCommit(select, (value) => committed.push(value));

  select.fire('pointerdown');
  select.value = 'b';
  select.fire('change');

  assert.deepEqual(committed, ['b']);
});

test('arrow keys browse the options without committing until Enter or blur', () => {
  const select = fakeSelect('a');
  const committed = [];
  bindSelectCommit(select, (value) => committed.push(value));

  select.fire('keydown', { key: 'ArrowDown' });
  select.value = 'b';
  select.fire('change');
  select.value = 'c';
  select.fire('change');
  assert.deepEqual(committed, [], 'no navigation while browsing with the keyboard');

  select.fire('blur');
  assert.deepEqual(committed, ['c']);
});

test('Enter commits the browsed option once', () => {
  const select = fakeSelect('a');
  const committed = [];
  bindSelectCommit(select, (value) => committed.push(value));

  select.fire('keydown', { key: 'ArrowDown' });
  select.value = 'b';
  select.fire('change');
  select.fire('keydown', { key: 'Enter' });
  select.fire('blur');

  assert.deepEqual(committed, ['b']);
});

test('an unchanged value never commits and reset re-syncs after a refused change', () => {
  const select = fakeSelect('a');
  const committed = [];
  const binding = bindSelectCommit(select, (value) => committed.push(value));

  select.fire('change');
  assert.deepEqual(committed, []);

  select.value = 'b';
  select.fire('change');
  binding.reset('a');
  select.value = 'b';
  select.fire('change');
  assert.deepEqual(committed, ['b', 'b']);
});
