/**
 * Interactive Demo Script for WhatsApp Attribution Router
 */
document.addEventListener('DOMContentLoaded', function () {
  const PRESETS = {
    google_ads: {
      source: 'google',
      medium: 'cpc',
      campaign: 'lahore_property_leads',
      content: 'search_ad_v2',
      term: 'luxury apartments lahore',
      click_id: 'gclid_example_98765'
    },
    meta_ads: {
      source: 'facebook',
      medium: 'paid_social',
      campaign: 'cro_audit_offer',
      content: 'video_testimonial',
      term: '',
      click_id: 'fbclid_example_12345'
    },
    tiktok_influencer: {
      source: 'tiktok',
      medium: 'influencer',
      campaign: 'creator_collab_2026',
      content: 'unboxing_review',
      term: '',
      click_id: ''
    },
    direct: {
      source: '',
      medium: '',
      campaign: '',
      content: '',
      term: '',
      click_id: ''
    }
  };

  // Form Elements
  const sourceInput = document.getElementById('in-source');
  const mediumInput = document.getElementById('in-medium');
  const campaignInput = document.getElementById('in-campaign');
  const contentInput = document.getElementById('in-content');
  const termInput = document.getElementById('in-term');
  const phoneInput = document.getElementById('in-phone');
  const messageInput = document.getElementById('in-message');
  const modelSelect = document.getElementById('in-model');
  const storageSelect = document.getElementById('in-storage');

  // Preview Outputs
  const previewUrl = document.getElementById('preview-url');
  const previewMsg = document.getElementById('preview-msg');
  const previewPayload = document.getElementById('preview-payload');
  const previewSheets = document.getElementById('preview-sheets');
  const previewGhl = document.getElementById('preview-ghl');
  const simClickBtn = document.getElementById('btn-simulate-click');
  const realOpenBtn = document.getElementById('btn-open-real');

  function getRouterInstance() {
    return new WhatsAppAttributionRouter({
      phoneNumber: phoneInput.value || '923167417135',
      storageType: storageSelect.value || 'sessionStorage',
      attributionModel: modelSelect.value || 'last_touch',
      defaultMessage: messageInput.value || 'Hi, I reviewed your services and would like to discuss a project.'
    });
  }

  function updatePreview() {
    const router = getRouterInstance();
    const mockParams = {};

    if (sourceInput.value.trim()) mockParams.utm_source = sourceInput.value.trim();
    if (mediumInput.value.trim()) mockParams.utm_medium = mediumInput.value.trim();
    if (campaignInput.value.trim()) mockParams.utm_campaign = campaignInput.value.trim();
    if (contentInput.value.trim()) mockParams.utm_content = contentInput.value.trim();
    if (termInput.value.trim()) mockParams.utm_term = termInput.value.trim();

    // Store in router memory
    router.storage.setItem('war_attr_last', JSON.stringify({
      params: mockParams,
      landing_page: 'https://hamid-resume.web.app/services/whatsapp-attribution',
      referrer: 'https://www.google.com/'
    }));
    router.storage.setItem('war_lead_ref', 'lead_sim_' + Math.random().toString(36).substring(2, 8));

    const msg = router.buildMessage({ message: messageInput.value });
    const waUrl = router.buildWhatsAppUrl({ message: messageInput.value });

    previewMsg.textContent = msg;
    previewUrl.textContent = waUrl;
    realOpenBtn.href = waUrl;
  }

  function triggerSimulation() {
    const router = getRouterInstance();
    const event = router.createEventPayload('demo_simulator_button', {
      simulated: true,
      user_agent_sample: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    });

    previewPayload.textContent = JSON.stringify(event, null, 2);

    // Build Simulated Google Sheets row
    const attr = event.attribution || {};
    const sheetRow = {
      timestamp: event.occurred_at,
      event_id: event.event_id,
      event_name: event.event_name,
      lead_reference: event.lead_reference,
      utm_source: attr.utm_source || '(direct)',
      utm_medium: attr.utm_medium || '(none)',
      utm_campaign: attr.utm_campaign || '(not set)',
      utm_content: attr.utm_content || '',
      utm_term: attr.utm_term || '',
      landing_page: event.page ? event.page.landing_page : '',
      destination: event.destination ? event.destination.phone_number : '',
      lead_status: 'unconfirmed_click (WhatsApp initiated)'
    };
    previewSheets.textContent = JSON.stringify(sheetRow, null, 2);

    // Build Simulated GoHighLevel Contact Mapping
    const ghlPayload = {
      locationId: 'loc_DEMO_ACCOUNT_123',
      source: 'WhatsApp Attribution Router',
      tags: [
        'WhatsApp Clicked',
        'Source: ' + (attr.utm_source || 'direct'),
        'Campaign: ' + (attr.utm_campaign || 'none')
      ],
      customFields: [
        { id: 'lead_reference', value: event.lead_reference },
        { id: 'utm_source', value: attr.utm_source || '' },
        { id: 'utm_medium', value: attr.utm_medium || '' },
        { id: 'utm_campaign', value: attr.utm_campaign || '' }
      ],
      note: 'Visitor clicked WhatsApp button from campaign [' + (attr.utm_campaign || 'direct') + ']. Actual conversation delivery pending inbound message.'
    };
    previewGhl.textContent = JSON.stringify(ghlPayload, null, 2);
  }

  // Preset Buttons
  document.querySelectorAll('.preset-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const key = btn.getAttribute('data-preset');
      const p = PRESETS[key] || PRESETS.google_ads;

      sourceInput.value = p.source;
      mediumInput.value = p.medium;
      campaignInput.value = p.campaign;
      contentInput.value = p.content;
      termInput.value = p.term;

      updatePreview();
      triggerSimulation();
    });
  });

  // Tab switching
  document.querySelectorAll('.tab-btn').forEach(function (tBtn) {
    tBtn.addEventListener('click', function () {
      const tabTarget = tBtn.getAttribute('data-tab');
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      tBtn.classList.add('active');
      const targetEl = document.getElementById('tab-' + tabTarget);
      if (targetEl) targetEl.classList.add('active');
    });
  });

  // Input listeners
  [sourceInput, mediumInput, campaignInput, contentInput, termInput, phoneInput, messageInput, modelSelect, storageSelect].forEach(function (input) {
    if (input) {
      input.addEventListener('input', updatePreview);
      input.addEventListener('change', updatePreview);
    }
  });

  simClickBtn.addEventListener('click', triggerSimulation);

  // Initial Run
  updatePreview();
  triggerSimulation();
});
