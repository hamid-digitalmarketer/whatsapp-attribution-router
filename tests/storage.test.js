const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const WAR = require('../src/attribution-router.js');

describe('Storage & Attribution Lifecycle', () => {
  test('handles memory storage when window storage is unavailable', () => {
    const router = new WAR({ storageType: 'none' });
    router.storage.setItem('key1', 'val1');
    assert.equal(router.storage.getItem('key1'), 'val1');
    router.storage.removeItem('key1');
    assert.equal(router.storage.getItem('key1'), null);
  });

  test('generates complete, valid event payload', () => {
    const router = new WAR({
      phoneNumber: '923167417135',
      storageType: 'none',
      attributionModel: 'last_touch'
    });

    router.storage.setItem('war_attr_last', JSON.stringify({
      params: {
        utm_source: 'meta',
        utm_medium: 'paid_social',
        utm_campaign: 'retargeting_q4',
        fbclid: 'fb_clk_789'
      },
      landing_page: 'https://example.com/demo',
      referrer: 'https://m.facebook.com/'
    }));
    router.storage.setItem('war_lead_ref', 'lead_unique_007');
    router.storage.setItem('war_session_id', 'ses_unique_007');

    const event = router.createEventPayload('header_cta', { test_mode: true });

    assert.equal(event.event_name, 'whatsapp_click');
    assert.ok(event.event_id.startsWith('evt_'));
    assert.equal(event.lead_reference, 'lead_unique_007');
    assert.equal(event.session_id, 'ses_unique_007');
    assert.equal(event.attribution.utm_source, 'meta');
    assert.equal(event.attribution.utm_medium, 'paid_social');
    assert.equal(event.attribution.utm_campaign, 'retargeting_q4');
    assert.equal(event.attribution.fbclid, 'fb_clk_789');
    assert.equal(event.destination.button_id, 'header_cta');
    assert.equal(event.destination.phone_number, '923167417135');
    assert.equal(event.custom_data.test_mode, true);
  });

  test('respects consent callback and blocks tracking when denied', () => {
    let consentGranted = false;
    const router = new WAR({
      storageType: 'none',
      requireConsent: true,
      hasConsent: () => consentGranted
    });

    assert.equal(router.canTrack(), false);
    consentGranted = true;
    assert.equal(router.canTrack(), true);
  });

  test('gracefully recovers from malformed stored JSON', () => {
    const router = new WAR({ storageType: 'none' });
    router.storage.setItem('war_attr_first', 'INVALID_JSON{{{');
    router.storage.setItem('war_attr_last', 'ANOTHER_INVALID');

    const attr = router.getAttribution();
    assert.equal(attr.first_touch, null);
    assert.equal(attr.last_touch, null);
    assert.equal(attr.active, null);
  });
});
