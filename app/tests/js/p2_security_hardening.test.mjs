import test from 'node:test';
import assert from 'node:assert/strict';

import { createAlertHTML } from '../../static/js/md3/alert-utils.js';
import {
  getEffectiveDatawrapperDarkMode,
  isAllowedDatawrapperOrigin,
  withDatawrapperDarkFlag,
} from '../../static/js/modules/core/datawrapper.js';

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

test('withDatawrapperDarkFlag pins allowed iframe URLs to the effective theme', () => {
  assert.equal(
    withDatawrapperDarkFlag('https://datawrapper.dwcdn.net/Uza2n/1/', false),
    'https://datawrapper.dwcdn.net/Uza2n/1/?dark=false',
  );
  assert.equal(
    withDatawrapperDarkFlag('https://datawrapper.dwcdn.net/Uza2n/1/?dark=false', true),
    'https://datawrapper.dwcdn.net/Uza2n/1/?dark=true',
  );
  assert.equal(
    withDatawrapperDarkFlag('https://evil.example/Uza2n/1/', false),
    'https://evil.example/Uza2n/1/',
  );
});

test('getEffectiveDatawrapperDarkMode follows explicit and automatic app themes', () => {
  assert.equal(
    getEffectiveDatawrapperDarkMode({ dataset: { theme: 'light', systemDark: 'true' } }),
    false,
  );
  assert.equal(
    getEffectiveDatawrapperDarkMode({ dataset: { theme: 'dark', systemDark: 'false' } }),
    true,
  );
  assert.equal(
    getEffectiveDatawrapperDarkMode({ dataset: { theme: 'auto', systemDark: 'true' } }),
    true,
  );
  assert.equal(
    getEffectiveDatawrapperDarkMode({ dataset: { theme: 'auto', systemDark: 'false' } }),
    false,
  );
});
