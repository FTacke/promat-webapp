import test from 'node:test';
import assert from 'node:assert/strict';

import { buildUiLangSwitchUrl } from '../../static/js/modules/navigation/app-bar.js';
import {
  buildComparisonStateUrl,
  parseComparisonUrlState,
  shouldExposeComparisonSetId,
} from '../../static/js/modules/research/comparison-url-state.js';
import { resolveActiveTimedItem } from '../../static/js/modules/research/player-highlight.js';

test('buildUiLangSwitchUrl preserves workbench query state on localized routes', () => {
  const nextUrl = buildUiLangSwitchUrl(
    'en',
    'http://promat.test/de/research/spanish/player/ES-L-0001-2026-S01/text?source=speakers&compare_session=ES-N-0001-2026-S01&render_mode=sentence_list',
    'http://promat.test',
  );

  assert.equal(
    nextUrl,
    '/en/research/spanish/player/ES-L-0001-2026-S01/text?source=speakers&compare_session=ES-N-0001-2026-S01&render_mode=sentence_list&lang=en',
  );
});

test('buildUiLangSwitchUrl rewrites nested local next targets for the target locale', () => {
  const nextUrl = buildUiLangSwitchUrl(
    'en',
    'http://promat.test/login?next=%2Fde%2Fresearch%2Fspanish%2Fcomparison%3Fset_id%3Ddraft-42%26task%3Dtext',
    'http://promat.test',
  );

  assert.equal(
    nextUrl,
    '/login?next=%2Fen%2Fresearch%2Fspanish%2Fcomparison%3Fset_id%3Ddraft-42%26task%3Dtext&lang=en',
  );
});

test('comparison URL helpers preserve stable filter and set state', () => {
  const nextUrl = buildComparisonStateUrl(
    '/de/research/spanish/comparison',
    {
      setId: 'draft-42',
      task: 'text',
      filters: {
        search: 'ES-L-0001',
        levels: ['a2', 'B1'],
        l1: 'DE',
        gender: 'female',
        exposure: 'yes',
      },
    },
    'http://promat.test',
  );

  assert.equal(
    nextUrl,
    '/de/research/spanish/comparison?set_id=draft-42&task=text&search=ES-L-0001&levels=A2%2CB1&l1=DE&gender=female&exposure=yes',
  );

  assert.deepEqual(
    parseComparisonUrlState(`http://promat.test${nextUrl}`, 'http://promat.test'),
    {
      setId: 'draft-42',
      task: 'text',
      filters: {
        search: 'ES-L-0001',
        levels: ['A2', 'B1'],
        l1: 'DE',
        gender: 'female',
        exposure: 'yes',
      },
    },
  );
});

test('shouldExposeComparisonSetId keeps default all-items drafts out of the URL during normal selection work', () => {
  assert.equal(
    shouldExposeComparisonSetId({
      activeSetId: 'draft-empty',
      requestedSetId: null,
      isExplicitMaterialSelection: false,
      isImplicitDraft: true,
      isDefaultCompleteSet: true,
      selectedSessionIds: [],
    }),
    false,
  );

  assert.equal(
    shouldExposeComparisonSetId({
      activeSetId: 'draft-with-selection',
      requestedSetId: null,
      isExplicitMaterialSelection: false,
      isImplicitDraft: true,
      isDefaultCompleteSet: true,
      selectedSessionIds: ['ES-L-0001-2026-S01'],
    }),
    false,
  );

  assert.equal(
    shouldExposeComparisonSetId({
      activeSetId: 'explicit-set',
      requestedSetId: null,
      isExplicitMaterialSelection: true,
      isImplicitDraft: false,
      isDefaultCompleteSet: true,
      selectedSessionIds: ['ES-L-0001-2026-S01'],
    }),
    true,
  );
});

test('resolveActiveTimedItem never falls back to the global last item during sentence gaps', () => {
  const items = [
    { itemId: 'd_01', itemIndex: 0, startMs: 0, endMs: 900 },
    { itemId: 'd_02', itemIndex: 1, startMs: 1100, endMs: 1900 },
    { itemId: 'd_03', itemIndex: 2, startMs: 2100, endMs: 2900 },
  ];

  assert.deepEqual(resolveActiveTimedItem(items, 950), { itemId: 'd_01', itemIndex: 0 });
  assert.deepEqual(resolveActiveTimedItem(items, 2050), { itemId: 'd_02', itemIndex: 1 });
  assert.deepEqual(resolveActiveTimedItem(items, 50), { itemId: 'd_01', itemIndex: 0 });
  assert.deepEqual(resolveActiveTimedItem(items, 3500), { itemId: 'd_03', itemIndex: 2 });
  assert.deepEqual(resolveActiveTimedItem(items, -10), { itemId: null, itemIndex: -1 });
});
