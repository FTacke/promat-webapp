import test from 'node:test';
import assert from 'node:assert/strict';

import { createAlertHTML } from '../../static/js/md3/alert-utils.js';
import { isAllowedDatawrapperOrigin } from '../../static/js/modules/core/datawrapper.js';

test('createAlertHTML escapes dynamic title and message content', () => {
  const html = createAlertHTML('error', '<strong>Oops</strong>', '<img src=x onerror=alert(1)>');

  assert.match(html, /&lt;strong&gt;Oops&lt;\/strong&gt;/);
  assert.match(html, /&lt;img src=x onerror=alert\(1\)&gt;/);
  assert.doesNotMatch(html, /<strong>Oops<\/strong>/);
  assert.doesNotMatch(html, /<img src=x onerror=alert\(1\)>/);
});

test('isAllowedDatawrapperOrigin accepts only the Datawrapper embed origin', () => {
  assert.equal(isAllowedDatawrapperOrigin('https://datawrapper.dwcdn.net'), true);
  assert.equal(isAllowedDatawrapperOrigin('http://datawrapper.dwcdn.net'), false);
  assert.equal(isAllowedDatawrapperOrigin('https://evil.example'), false);
  assert.equal(isAllowedDatawrapperOrigin(''), false);
});