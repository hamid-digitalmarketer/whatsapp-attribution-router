const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const WAR = require('../src/attribution-router.js');

describe('WhatsApp Click-to-Chat URL Generation & Formatting', () => {
  test('normalizes various international phone number formats', () => {
    assert.equal(WAR.normalizePhoneNumber('+92 316 7417135'), '923167417135');
    assert.equal(WAR.normalizePhoneNumber('92-316-741-7135'), '923167417135');
    assert.equal(WAR.normalizePhoneNumber('(92) 316 7417135'), '923167417135');
    assert.equal(WAR.normalizePhoneNumber('03167417135'), '923167417135', 'Converts Pakistan local 03xx to 923xx');
    assert.equal(WAR.normalizePhoneNumber('1-800-555-0199'), '18005550199');
  });

  test('constructs valid WhatsApp URL with default prefilled message', () => {
    const router = new WAR({
      phoneNumber: '923167417135',
      storageType: 'none',
      includeAttributionInMessage: false
    });

    const url = router.buildWhatsAppUrl();
    assert.ok(url.startsWith('https://wa.me/923167417135?text='));
    assert.ok(url.includes(encodeURIComponent('Hi, I reviewed your services')));
  });

  test('appends campaign attribution and lead reference to prefilled message', () => {
    const router = new WAR({
      phoneNumber: '923167417135',
      storageType: 'none',
      includeAttributionInMessage: true
    });

    // Manually prime storage
    router.storage.setItem('war_attr_last', JSON.stringify({
      params: {
        utm_source: 'google',
        utm_medium: 'cpc',
        utm_campaign: 'spring_leads'
      }
    }));
    router.storage.setItem('war_lead_ref', 'lead_test_abc123');

    const msg = router.buildMessage();
    assert.ok(msg.includes('Campaign ref: spring_leads'));
    assert.ok(msg.includes('Source: google'));
    assert.ok(msg.includes('Medium: cpc'));
    assert.ok(msg.includes('Ref: lead_test_abc123'));

    const url = router.buildWhatsAppUrl();
    assert.ok(url.includes('https://wa.me/923167417135?text='));
    assert.ok(url.includes(encodeURIComponent('spring_leads')));
  });

  test('supports custom message template function', () => {
    const router = new WAR({
      phoneNumber: '923167417135',
      storageType: 'none',
      messageTemplate: ({ baseMessage, attribution, leadReference }) => {
        return `Inquiry: ${baseMessage} [ID: ${leadReference}] (Source: ${attribution.utm_source || 'direct'})`;
      }
    });

    router.storage.setItem('war_attr_last', JSON.stringify({
      params: { utm_source: 'linkedin' }
    }));
    router.storage.setItem('war_lead_ref', 'lead_999');

    const msg = router.buildMessage({ message: 'Pricing check' });
    assert.equal(msg, 'Inquiry: Pricing check [ID: lead_999] (Source: linkedin)');
  });

  test('throws error if recipient phone number is missing or empty', () => {
    const router = new WAR({
      phoneNumber: '',
      storageType: 'none'
    });

    assert.throws(() => {
      router.buildWhatsAppUrl({ phoneNumber: '' });
    }, /valid recipient phone number is required/);
  });
});
