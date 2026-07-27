/**
 * Qefro Partner Program — referral capture (?ref=<code>)
 *
 * When a visitor lands with ?ref=, we:
 *   1. validate the code server-side (never trust the query param alone),
 *   2. store it in a cookie on the parent domain (.qefro.com, 90 days),
 *   3. keep a localStorage backup,
 *   4. record an anonymous click event,
 *   5. decorate every app.qefro.com link with ?ref= as a final fallback.
 *
 * app.qefro.com reads the cookie/param at signup and sends `partner_ref`;
 * the backend re-validates before attributing. Customers never type codes.
 */
(function () {
  "use strict";

  var API_URL = (document.documentElement.dataset && document.documentElement.dataset.apiUrl) || "https://api.qefro.com";
  var COOKIE_NAME = "qefro_ref";
  var STORAGE_KEY = "qefro_ref";
  var COOKIE_DAYS = 90;

  // URL-safe, lowercase; mirrors backend is_valid_referral_code().
  function sanitize(raw) {
    if (!raw) return null;
    var code = String(raw).trim().toLowerCase();
    if (!code || code.length > 64) return null;
    return /^[a-z0-9_-]+$/.test(code) ? code : null;
  }

  function cookieDomain() {
    var host = window.location.hostname;
    if (host === "localhost" || /^[0-9.]+$/.test(host)) return "";
    var parts = host.split(".");
    if (parts.length < 2) return "";
    return "." + parts.slice(-2).join(".");
  }

  function setRefCookie(code) {
    var expires = new Date(Date.now() + COOKIE_DAYS * 24 * 60 * 60 * 1000).toUTCString();
    var cookie = COOKIE_NAME + "=" + encodeURIComponent(code) + "; expires=" + expires + "; path=/; SameSite=Lax";
    var domain = cookieDomain();
    if (domain) cookie += "; domain=" + domain;
    if (window.location.protocol === "https:") cookie += "; Secure";
    document.cookie = cookie;
  }

  function getRefCookie() {
    var match = document.cookie.match(new RegExp("(?:^|;\\s*)" + COOKIE_NAME + "=([^;]*)"));
    return match ? sanitize(decodeURIComponent(match[1])) : null;
  }

  function storeRef(code) {
    setRefCookie(code);
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ code: code, ts: Date.now() }));
    } catch (e) {
      /* private mode — cookie is enough */
    }
  }

  function storedRef() {
    var fromCookie = getRefCookie();
    if (fromCookie) return fromCookie;
    try {
      var raw = window.localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      if (!parsed || !parsed.ts || Date.now() - parsed.ts > COOKIE_DAYS * 24 * 60 * 60 * 1000) return null;
      return sanitize(parsed.code);
    } catch (e) {
      return null;
    }
  }

  /** Add ?ref= to app.qefro.com links so signup works even without cookies. */
  function decorateAppLinks(code) {
    var links = document.querySelectorAll('a[href*="app.qefro.com"]');
    for (var i = 0; i < links.length; i++) {
      try {
        var url = new URL(links[i].href);
        if (!url.searchParams.get("ref")) {
          url.searchParams.set("ref", code);
          links[i].href = url.toString();
        }
      } catch (e) {
        /* malformed href — skip */
      }
    }
  }

  function trackClick(code) {
    try {
      fetch(API_URL + "/api/v1/public/partners/track-click", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: code, source: "marketing_site" }),
        keepalive: true,
      }).catch(function () {});
    } catch (e) {
      /* analytics only — never block the page */
    }
  }

  function init() {
    var params = new URLSearchParams(window.location.search);
    var incoming = sanitize(params.get("ref"));

    if (incoming) {
      // Server-side validation before persisting; first-touch (do not
      // overwrite an existing stored referral with a different code).
      fetch(API_URL + "/api/v1/public/partners/validate?code=" + encodeURIComponent(incoming))
        .then(function (res) { return res.ok ? res.json() : { valid: false }; })
        .then(function (data) {
          if (!data || !data.valid) return;
          if (!storedRef()) storeRef(incoming);
          var active = storedRef() || incoming;
          decorateAppLinks(active);
          trackClick(incoming);
        })
        .catch(function () {});
      return;
    }

    var existing = storedRef();
    if (existing) decorateAppLinks(existing);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
