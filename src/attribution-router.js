/**
 * WhatsApp Attribution Router (WAR)
 *
 * Lightweight, privacy-conscious browser utility that captures campaign UTM parameters,
 * normalizes attribution models (first-touch & last-touch), constructs sanitized
 * WhatsApp click-to-chat links with prefilled campaign references, and dispatches
 * validated click events to your backend or CRM.
 *
 * @version 1.0.0
 * @license MIT
 */
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.WhatsAppAttributionRouter = factory();
    root.WAR = root.WhatsAppAttributionRouter;
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // Recognized attribution query parameters
  const STANDARD_PARAMS = [
    'utm_source',
    'utm_medium',
    'utm_campaign',
    'utm_content',
    'utm_term',
    'gclid',
    'gbraid',
    'wbraid',
    'fbclid'
  ];

  const STORAGE_KEYS = {
    FIRST_TOUCH: 'war_attr_first',
    LAST_TOUCH: 'war_attr_last',
    SESSION_ID: 'war_session_id',
    LEAD_REF: 'war_lead_ref'
  };

  /**
   * Generates a cryptographically random hexadecimal identifier
   * @param {string} prefix
   * @returns {string}
   */
  function generateId(prefix) {
    const p = prefix ? prefix + '_' : '';
    if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
      const bytes = new Uint8Array(8);
      crypto.getRandomValues(bytes);
      const hex = Array.from(bytes, function (b) {
        return b.toString(16).padStart(2, '0');
      }).join('');
      return p + Date.now().toString(36) + '_' + hex;
    }
    return p + Date.now().toString(36) + '_' + Math.random().toString(36).substring(2, 10);
  }

  /**
   * Sanitizes string values to prevent header/URL injection and excessive payload sizes
   * @param {*} val
   * @param {number} maxLen
   * @returns {string}
   */
  function sanitizeString(val, maxLen) {
    if (val === null || val === undefined) return '';
    const limit = maxLen || 120;
    const str = String(val)
      .replace(/[\r\n\t]/g, ' ')
      .replace(/[<>]/g, '')
      .trim();
    return str.length > limit ? str.slice(0, limit) : str;
  }

  /**
   * Normalizes an international phone number to WhatsApp format:
   * Only digits, no plus signs, no leading zeros, no punctuation.
   * @param {string} phone
   * @returns {string}
   */
  function normalizePhoneNumber(phone) {
    if (!phone) return '';
    let digits = String(phone).replace(/\D/g, '');
    // If user provided a Pakistani local number like 03167417135, convert to international 923167417135
    if (digits.startsWith('0') && digits.length === 11) {
      digits = '92' + digits.slice(1);
    }
    return digits;
  }

  /**
   * Safely accesses storage (sessionStorage or localStorage) with error handling
   * @param {string} storageType 'sessionStorage' | 'localStorage' | 'none'
   */
  function createStorageAdapter(storageType) {
    const memoryStore = {};

    if (storageType === 'none' || typeof window === 'undefined') {
      return {
        getItem: function (key) { return memoryStore[key] || null; },
        setItem: function (key, val) { memoryStore[key] = String(val); },
        removeItem: function (key) { delete memoryStore[key]; }
      };
    }

    try {
      const target = storageType === 'localStorage' ? window.localStorage : window.sessionStorage;
      const testKey = '__war_test__';
      target.setItem(testKey, '1');
      target.removeItem(testKey);
      return {
        getItem: function (key) {
          try { return target.getItem(key); } catch (e) { return null; }
        },
        setItem: function (key, val) {
          try { target.setItem(key, String(val)); } catch (e) { /* quota or privacy mode */ }
        },
        removeItem: function (key) {
          try { target.removeItem(key); } catch (e) { /* silent */ }
        }
      };
    } catch (e) {
      return {
        getItem: function (key) { return memoryStore[key] || null; },
        setItem: function (key, val) { memoryStore[key] = String(val); },
        removeItem: function (key) { delete memoryStore[key]; }
      };
    }
  }

  /**
   * Main Router Class
   */
  function WhatsAppAttributionRouter(options) {
    this.config = Object.assign({
      phoneNumber: '923167417135',
      storageType: 'sessionStorage', // 'sessionStorage' | 'localStorage' | 'none'
      attributionModel: 'last_touch', // 'last_touch' | 'first_touch' | 'both'
      requireConsent: false,
      hasConsent: null, // Callback returning boolean
      includeAttributionInMessage: true,
      customParams: [],
      apiEndpoint: '', // e.g. '/api/v1/events'
      buttonSelector: '[data-wa-button]',
      defaultMessage: 'Hi, I reviewed your services and would like to discuss a project.',
      messageTemplate: null // Optional custom template function: ({ baseMessage, attribution, leadRef }) => string
    }, options || {});

    this.config.phoneNumber = normalizePhoneNumber(this.config.phoneNumber);
    this.storage = createStorageAdapter(this.config.storageType);
    this._initialized = false;
  }

  /**
   * Checks if tracking consent is granted
   * @returns {boolean}
   */
  WhatsAppAttributionRouter.prototype.canTrack = function () {
    if (!this.config.requireConsent) return true;
    if (typeof this.config.hasConsent === 'function') {
      try {
        return Boolean(this.config.hasConsent());
      } catch (e) {
        return false;
      }
    }
    return false;
  };

  /**
   * Parses campaign parameters from a URL or query string
   * @param {string} [urlString]
   * @returns {Object}
   */
  WhatsAppAttributionRouter.prototype.parseParameters = function (urlString) {
    const result = {};
    let search = '';

    if (urlString) {
      try {
        const u = new URL(urlString, 'https://example.com');
        search = u.search;
      } catch (e) {
        const qIdx = urlString.indexOf('?');
        search = qIdx !== -1 ? urlString.slice(qIdx) : '';
      }
    } else if (typeof window !== 'undefined' && window.location) {
      search = window.location.search;
    }

    if (!search || search.length <= 1) return result;

    const params = new URLSearchParams(search);
    const allowed = STANDARD_PARAMS.concat(this.config.customParams || []);

    for (let i = 0; i < allowed.length; i++) {
      const key = allowed[i];
      if (params.has(key)) {
        const raw = params.get(key);
        if (raw !== null && raw !== '') {
          result[key] = sanitizeString(raw, 120);
        }
      }
    }

    return result;
  };

  /**
   * Initializes attribution capture from current window location
   */
  WhatsAppAttributionRouter.prototype.init = function () {
    if (typeof window === 'undefined') return this;

    const hasTrackingConsent = this.canTrack();
    const currentParams = this.parseParameters(window.location.search);
    const hasCampaignParams = Object.keys(currentParams).length > 0;
    const nowIso = new Date().toISOString();
    const landingPage = window.location.href.split('#')[0];
    const referrer = document.referrer ? document.referrer.slice(0, 300) : '';

    let sessionId = this.storage.getItem(STORAGE_KEYS.SESSION_ID);
    if (!sessionId) {
      sessionId = generateId('ses');
      if (hasTrackingConsent) {
        this.storage.setItem(STORAGE_KEYS.SESSION_ID, sessionId);
      }
    }

    let leadRef = this.storage.getItem(STORAGE_KEYS.LEAD_REF);
    if (!leadRef) {
      leadRef = generateId('lead');
      if (hasTrackingConsent) {
        this.storage.setItem(STORAGE_KEYS.LEAD_REF, leadRef);
      }
    }

    // Capture first touch if not already set and we have campaign data
    let firstTouch = null;
    const rawFirst = this.storage.getItem(STORAGE_KEYS.FIRST_TOUCH);
    if (rawFirst) {
      try { firstTouch = JSON.parse(rawFirst); } catch (e) { firstTouch = null; }
    }

    if (!firstTouch && hasCampaignParams && hasTrackingConsent) {
      firstTouch = {
        params: currentParams,
        landing_page: landingPage,
        referrer: referrer,
        captured_at: nowIso
      };
      this.storage.setItem(STORAGE_KEYS.FIRST_TOUCH, JSON.stringify(firstTouch));
    }

    // Capture or update last touch if campaign parameters are present
    let lastTouch = null;
    const rawLast = this.storage.getItem(STORAGE_KEYS.LAST_TOUCH);
    if (rawLast) {
      try { lastTouch = JSON.parse(rawLast); } catch (e) { lastTouch = null; }
    }

    if (hasCampaignParams && hasTrackingConsent) {
      lastTouch = {
        params: currentParams,
        landing_page: landingPage,
        referrer: referrer,
        captured_at: nowIso
      };
      this.storage.setItem(STORAGE_KEYS.LAST_TOUCH, JSON.stringify(lastTouch));
    }

    this._initialized = true;

    // Attach listeners to configured buttons
    this.bindButtons();

    return this;
  };

  /**
   * Returns current active attribution record based on configured model
   * @returns {Object}
   */
  WhatsAppAttributionRouter.prototype.getAttribution = function () {
    let first = null;
    let last = null;

    try {
      const rf = this.storage.getItem(STORAGE_KEYS.FIRST_TOUCH);
      if (rf) first = JSON.parse(rf);
    } catch (e) { first = null; }

    try {
      const rl = this.storage.getItem(STORAGE_KEYS.LAST_TOUCH);
      if (rl) last = JSON.parse(rl);
    } catch (e) { last = null; }

    const sessionId = this.storage.getItem(STORAGE_KEYS.SESSION_ID) || '';
    const leadRef = this.storage.getItem(STORAGE_KEYS.LEAD_REF) || '';

    const model = this.config.attributionModel;
    let active = null;

    if (model === 'first_touch') {
      active = first || last;
    } else if (model === 'both') {
      active = { first_touch: first, last_touch: last };
    } else {
      // Default: last_touch
      active = last || first;
    }

    return {
      model: model,
      active: active,
      first_touch: first,
      last_touch: last,
      session_id: sessionId,
      lead_reference: leadRef
    };
  };

  /**
   * Formats the prefilled WhatsApp message
   * @param {Object} [overrideOptions]
   * @returns {string}
   */
  WhatsAppAttributionRouter.prototype.buildMessage = function (overrideOptions) {
    const opts = Object.assign({}, overrideOptions || {});
    const baseMessage = sanitizeString(opts.message || this.config.defaultMessage, 400);

    const attrData = this.getAttribution();
    const active = attrData.active ? (attrData.active.params || (attrData.active.last_touch ? attrData.active.last_touch.params : {})) : {};
    const leadRef = opts.leadReference || attrData.lead_reference || '';

    if (typeof this.config.messageTemplate === 'function') {
      return this.config.messageTemplate({
        baseMessage: baseMessage,
        attribution: active,
        leadReference: leadRef,
        attributionData: attrData
      });
    }

    if (!this.config.includeAttributionInMessage) {
      return baseMessage;
    }

    const lines = [baseMessage];
    const details = [];

    if (active.utm_campaign) {
      details.push('Campaign ref: ' + active.utm_campaign);
    }
    if (active.utm_source) {
      details.push('Source: ' + active.utm_source);
    }
    if (active.utm_medium) {
      details.push('Medium: ' + active.utm_medium);
    }
    if (leadRef) {
      details.push('Ref: ' + leadRef);
    }

    if (details.length > 0) {
      lines.push('');
      lines.push(details.join('\n'));
    }

    return lines.join('\n');
  };

  /**
   * Builds the official WhatsApp click-to-chat URL
   * @param {Object} [options]
   * @returns {string}
   */
  WhatsAppAttributionRouter.prototype.buildWhatsAppUrl = function (options) {
    const opts = Object.assign({}, options || {});
    const phone = normalizePhoneNumber(opts.phoneNumber || this.config.phoneNumber);
    if (!phone) {
      throw new Error('WAR: A valid recipient phone number is required.');
    }

    const message = this.buildMessage(opts);
    const encoded = encodeURIComponent(message);
    return 'https://wa.me/' + phone + '?text=' + encoded;
  };

  /**
   * Constructs an event payload according to the WAR specification
   * @param {string} [buttonId]
   * @param {Object} [customData]
   * @returns {Object}
   */
  WhatsAppAttributionRouter.prototype.createEventPayload = function (buttonId, customData) {
    const attr = this.getAttribution();
    const activeParams = attr.active ? (attr.active.params || {}) : {};

    const landingPage = (typeof window !== 'undefined' && window.location)
      ? window.location.href.split('#')[0]
      : (attr.active ? attr.active.landing_page : '');

    const referrer = (typeof document !== 'undefined' && document.referrer)
      ? document.referrer.slice(0, 300)
      : '';

    return {
      event_name: 'whatsapp_click',
      event_id: generateId('evt'),
      occurred_at: new Date().toISOString(),
      lead_reference: attr.lead_reference,
      session_id: attr.session_id,
      attribution: {
        model: this.config.attributionModel,
        utm_source: activeParams.utm_source || null,
        utm_medium: activeParams.utm_medium || null,
        utm_campaign: activeParams.utm_campaign || null,
        utm_content: activeParams.utm_content || null,
        utm_term: activeParams.utm_term || null,
        gclid: activeParams.gclid || null,
        gbraid: activeParams.gbraid || null,
        wbraid: activeParams.wbraid || null,
        fbclid: activeParams.fbclid || null
      },
      page: {
        landing_page: landingPage,
        referrer: referrer
      },
      destination: {
        type: 'whatsapp',
        phone_number: this.config.phoneNumber,
        button_id: buttonId || 'default'
      },
      custom_data: customData || {}
    };
  };

  /**
   * Sends the attribution event to the configured backend API
   * @param {Object} payload
   * @returns {Promise<boolean>}
   */
  WhatsAppAttributionRouter.prototype.logEvent = function (payload) {
    if (!this.config.apiEndpoint) {
      return Promise.resolve(false);
    }

    const jsonString = JSON.stringify(payload);

    // Try navigator.sendBeacon first for reliable delivery during page transitions
    if (typeof navigator !== 'undefined' && typeof navigator.sendBeacon === 'function') {
      try {
        const blob = new Blob([jsonString], { type: 'application/json' });
        const sent = navigator.sendBeacon(this.config.apiEndpoint, blob);
        if (sent) return Promise.resolve(true);
      } catch (e) {
        // Fallback to fetch
      }
    }

    if (typeof fetch !== 'undefined') {
      return fetch(this.config.apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: jsonString,
        keepalive: true
      })
        .then(function (res) { return res.ok; })
        .catch(function () { return false; });
    }

    return Promise.resolve(false);
  };

  /**
   * Handles button click: logs the event, dispatches DOM event, and opens WhatsApp
   * @param {string} [buttonId]
   * @param {Object} [overrideOptions]
   */
  WhatsAppAttributionRouter.prototype.handleClick = function (buttonId, overrideOptions) {
    const payload = this.createEventPayload(buttonId, overrideOptions);
    const url = this.buildWhatsAppUrl(overrideOptions);

    // Dispatch DOM custom event for tag managers (GTM, Meta Pixel, GA4)
    if (typeof window !== 'undefined' && typeof window.dispatchEvent === 'function') {
      try {
        const customEvt = new CustomEvent('whatsapp:click', {
          detail: { payload: payload, url: url }
        });
        window.dispatchEvent(customEvt);
      } catch (e) { /* silent */ }
    }

    // Log to backend if endpoint configured
    if (this.config.apiEndpoint) {
      this.logEvent(payload);
    }

    return { payload: payload, url: url };
  };

  /**
   * Auto-binds click handlers to DOM elements matching the selector
   * @param {string} [selector]
   */
  WhatsAppAttributionRouter.prototype.bindButtons = function (selector) {
    if (typeof document === 'undefined') return;

    const sel = selector || this.config.buttonSelector;
    const buttons = document.querySelectorAll(sel);
    const self = this;

    for (let i = 0; i < buttons.length; i++) {
      const btn = buttons[i];
      if (btn.getAttribute('data-war-bound') === 'true') continue;

      btn.setAttribute('data-war-bound', 'true');
      btn.addEventListener('click', function (e) {
        const btnId = btn.getAttribute('data-wa-button-id') || btn.id || 'btn_' + i;
        const phoneOverride = btn.getAttribute('data-wa-phone');
        const msgOverride = btn.getAttribute('data-wa-message');

        const result = self.handleClick(btnId, {
          phoneNumber: phoneOverride,
          message: msgOverride
        });

        // If it is an anchor element without an explicit href or with a placeholder href, update it
        if (btn.tagName === 'A') {
          btn.setAttribute('href', result.url);
          btn.setAttribute('target', '_blank');
          btn.setAttribute('rel', 'noopener noreferrer');
        } else {
          // Open in new tab/window for button tags
          if (typeof window !== 'undefined') {
            window.open(result.url, '_blank', 'noopener,noreferrer');
          }
        }
      });
    }
  };

  // Expose utilities for testing and external consumption
  WhatsAppAttributionRouter.generateId = generateId;
  WhatsAppAttributionRouter.sanitizeString = sanitizeString;
  WhatsAppAttributionRouter.normalizePhoneNumber = normalizePhoneNumber;

  return WhatsAppAttributionRouter;
});
