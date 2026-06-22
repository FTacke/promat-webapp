import test from 'node:test';
import assert from 'node:assert/strict';

import { setReadingExpandableState } from '../../static/js/modules/core/reading-expandables.js';

function buildExpandableFixture() {
  const classes = new Set();
  const attributes = new Map();
  const properties = new Map();
  const toggle = {
    dataset: { labelShow: 'Show', labelHide: 'Hide' },
    setAttribute(name, value) {
      attributes.set(name, value);
    },
  };
  const label = { textContent: '' };
  const viewport = {
    scrollHeight: 640,
    style: {
      setProperty(name, value) {
        properties.set(name, value);
      },
    },
  };
  const expandable = {
    classList: {
      toggle(name, enabled) {
        if (enabled) classes.add(name);
        else classes.delete(name);
      },
    },
    querySelector(selector) {
      if (selector === '[data-pm-expandable-toggle]') return toggle;
      if (selector === '[data-pm-expandable-toggle-label]') return label;
      if (selector === '[data-pm-expandable-viewport]') return viewport;
      return null;
    },
  };

  return { expandable, classes, attributes, properties, label };
}

test('reading expandable synchronizes visual, accessible, and localized state', () => {
  const fixture = buildExpandableFixture();

  setReadingExpandableState(fixture.expandable, false);
  assert.equal(fixture.attributes.get('aria-expanded'), 'false');
  assert.equal(fixture.label.textContent, 'Show');
  assert.equal(fixture.classes.has('is-expanded'), false);
  assert.equal(fixture.properties.get('--pm-expandable-expanded-height'), '640px');

  setReadingExpandableState(fixture.expandable, true);
  assert.equal(fixture.attributes.get('aria-expanded'), 'true');
  assert.equal(fixture.label.textContent, 'Hide');
  assert.equal(fixture.classes.has('is-expanded'), true);

  setReadingExpandableState(fixture.expandable, false);
  assert.equal(fixture.attributes.get('aria-expanded'), 'false');
  assert.equal(fixture.label.textContent, 'Show');
  assert.equal(fixture.classes.has('is-expanded'), false);
});
