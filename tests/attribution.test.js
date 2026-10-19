const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const WAR = require('../src/attribution-router.js');

describe('Attribution Parameter Parsing & Normalization', () => {
  test('parses standard UTM parameters and ad click IDs', () => {
    const router = new WAR({ storageType: 'none' });
    const url = 'https://example.com/pricing?utm_source=google&utm_medium=cpc&utm_campaign=summer_promo_2026&utm_content=banner_v1&utm_term=martech&gclid=test_gclid_123&fbclid=test_fbclid_456&ignored_param=secret';

    const params = router.parseParameters(url);

    assert.equal(params.utm_source, 'google');
    assert.equal(params.utm_medium, 'cpc');
    assert.equal(params.utm_campaign, 'summer_promo_2026');
    assert.equal(params.utm_content, 'banner_v1');
    assert.equal(params.utm_term, 'martech');
    assert.equal(params.gclid, 'test_gclid_123');
    assert.equal(params.fbclid, 'test_fbclid_456');
    assert.equal(params.ignored_param, undefined, 'Arbitrary unconfigured parameters should be ignored');
  });

  test('supports configured custom parameters', () => {
    const router = new WAR({
      storageType: 'none',
      customParams: ['affiliate_id', 'agent_ref']
    });
    const url = 'https://example.com/?utm_source=meta&affiliate_id=aff_99&agent_ref=rep_01&other=no';

    const params = router.parseParameters(url);

    assert.equal(params.utm_source, 'meta');
    assert.equal(params.affiliate_id, 'aff_99');
    assert.equal(params.agent_ref, 'rep_01');
    assert.equal(params.other, undefined);
  });

  test('sanitizes input parameters and enforces length limit', () => {
    const router = new WAR({ storageType: 'none' });
    const malicious = 'https://example.com/?utm_source=<script>alert("xss")</script>&utm_campaign=line1\r\nline2\tline3&utm_term=' + 'a'.repeat(200);

    const params = router.parseParameters(malicious);

    assert.ok(!params.utm_source.includes('<'));
    assert.ok(!params.utm_source.includes('>'));
    assert.ok(!params.utm_campaign.includes('\r'));
    assert.ok(!params.utm_campaign.includes('\n'));
    assert.equal(params.utm_term.length, 120);
  });

  test('handles clean URLs without parameters gracefully', () => {
    const router = new WAR({ storageType: 'none' });
    const empty = router.parseParameters('https://example.com/about');
    assert.deepEqual(empty, {});
  });
});
