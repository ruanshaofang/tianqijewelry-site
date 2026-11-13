/* Tianqi Jewelry — visitor analytics, cookie banner and inquiry source tracking.
 *
 * Loaded on every page with <script src="/assets/analytics.js" defer>.
 * Google Analytics 4 runs only when GA_ID below is set (e.g. "G-ABC123XYZ").
 *
 * Consent:
 *  - Visitors whose browser time zone is in Europe (EU/EEA/UK/CH rules): nothing is
 *    stored and GA sets no cookies until they click Accept.
 *  - Everyone else: analytics is on by default; Decline turns it off.
 *  - The choice is kept in localStorage ("tq-consent") and the banner does not return.
 *
 * Conversion events sent to GA4:
 *  generate_lead   — inquiry form sent successfully (mark as Key event in GA4)
 *  whatsapp_click  — any wa.me link (mark as Key event in GA4)
 *  email_click     — any mailto: link
 *  contact_copy    — "Copy" button next to a contact detail
 *  chat_open       — AI assistant opened
 *
 * Inquiry source: the first landing page, referrer and utm_* tags of the visit are
 * added to the inquiry (fields src / landing / ref), so every inquiry email says
 * where the buyer came from. Kept in sessionStorage only, with consent.
 */
(function () {
  var GA_ID = ""; // ← paste the GA4 Measurement ID here, e.g. "G-ABC123XYZ"

  var KEY = "tq-consent", SKEY = "tq-src";
  var lang = (document.documentElement.lang || "en").slice(0, 2).toLowerCase();

  var TXT = {
    en: ["We use Google Analytics cookies to see how visitors find and use this site. No advertising.", "Accept", "Decline", "Privacy policy"],
    zh: ["我们使用 Google Analytics Cookie 了解访客如何找到和使用本网站，不用于广告。", "接受", "拒绝", "隐私政策"],
    de: ["Wir verwenden Google-Analytics-Cookies, um zu sehen, wie Besucher diese Website finden und nutzen. Keine Werbung.", "Akzeptieren", "Ablehnen", "Datenschutz"],
    fr: ["Nous utilisons des cookies Google Analytics pour comprendre comment les visiteurs trouvent et utilisent ce site. Aucune publicité.", "Accepter", "Refuser", "Confidentialité"],
    es: ["Usamos cookies de Google Analytics para saber cómo los visitantes encuentran y usan este sitio. Sin publicidad.", "Aceptar", "Rechazar", "Privacidad"],
    it: ["Usiamo cookie di Google Analytics per capire come i visitatori trovano e usano questo sito. Nessuna pubblicità.", "Accetta", "Rifiuta", "Privacy"],
    pt: ["Usamos cookies do Google Analytics para entender como os visitantes encontram e usam este site. Sem publicidade.", "Aceitar", "Recusar", "Privacidade"],
    ru: ["Мы используем файлы cookie Google Analytics, чтобы понять, как посетители находят и используют сайт. Без рекламы.", "Принять", "Отклонить", "Конфиденциальность"],
    ja: ["当サイトでは、訪問者がサイトをどのように見つけ、利用しているかを知るために Google アナリティクスの Cookie を使用します。広告には使用しません。", "同意する", "拒否する", "プライバシー"],
    ko: ["방문자가 사이트를 어떻게 찾고 이용하는지 파악하기 위해 Google 애널리틱스 쿠키를 사용합니다. 광고에는 사용하지 않습니다.", "동의", "거부", "개인정보 처리방침"],
    ar: ["نستخدم ملفات تعريف الارتباط من Google Analytics لمعرفة كيف يصل الزوار إلى هذا الموقع ويستخدمونه. بدون إعلانات.", "قبول", "رفض", "سياسة الخصوصية"]
  };

  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  // Europe (EU/EEA/UK/CH) → opt-in; elsewhere → opt-out.
  var tz = "";
  try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; } catch (e) {}
  var optIn = /^Europe\//.test(tz) || /^Atlantic\/(Reykjavik|Canary|Madeira|Azores|Faroe)$/.test(tz);
  var choice = lsGet(KEY); // "granted" | "denied" | null
  var granted = choice ? choice === "granted" : !optIn;

  // ---------- Google Analytics 4 with Consent Mode ----------
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;
  if (GA_ID) {
    gtag("consent", "default", {
      analytics_storage: granted ? "granted" : "denied",
      ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied"
    });
    gtag("js", new Date());
    gtag("config", GA_ID, { anonymize_ip: true });
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(GA_ID);
    document.head.appendChild(s);
  }
  function track(name, params) { if (GA_ID) window.gtag("event", name, params || {}); }

  // ---------- where this visit came from ----------
  function currentSource() {
    var q = new URLSearchParams(location.search), utm = [];
    ["utm_source", "utm_medium", "utm_campaign"].forEach(function (k) { if (q.get(k)) utm.push(q.get(k)); });
    var ref = document.referrer || "", host = "";
    try { host = ref ? new URL(ref).hostname : ""; } catch (e) {}
    if (host === location.hostname) host = ""; // internal navigation is not a source
    var src = utm.length ? utm.join(" / ") : q.get("gclid") ? "google / cpc" : host || "direct";
    return { src: src, landing: location.pathname + location.search, ref: host ? ref : "" };
  }
  function visitSource() {
    var saved = null;
    try { saved = JSON.parse(sessionStorage.getItem(SKEY) || "null"); } catch (e) {}
    if (saved) return saved;
    var cur = currentSource();
    if (granted) { try { sessionStorage.setItem(SKEY, JSON.stringify(cur)); } catch (e) {} }
    return cur;
  }
  var source = visitSource();

  // ---------- inquiry form: add the source, report the lead ----------
  if (window.fetch) {
    var origFetch = window.fetch;
    window.fetch = function (input, init) {
      var url = typeof input === "string" ? input : (input && input.url) || "";
      var isInquiry = /\/api\/inquiry\/?$/.test(url) && init && String(init.method || "").toUpperCase() === "POST";
      var body = null;
      if (isInquiry) {
        try {
          body = JSON.parse(init.body);
          body.src = source.src; body.landing = source.landing; body.ref = source.ref;
          init = Object.assign({}, init, { body: JSON.stringify(body) });
        } catch (e) {}
      }
      var p = origFetch.call(this, input, init);
      if (isInquiry) {
        p.then(function (r) {
          r.clone().json().then(function (j) {
            if (j && j.ok) track("generate_lead", { inquiry_type: body && body.type || "", page_path: location.pathname });
          }).catch(function () {});
        }).catch(function () {});
      }
      return p;
    };
  }

  // ---------- clicks on contact links ----------
  document.addEventListener("click", function (e) {
    var t = e.target && e.target.closest ? e.target : null;
    if (!t) return;
    var a = t.closest("a[href]");
    if (a) {
      var h = a.getAttribute("href") || "";
      if (/wa\.me\//.test(h)) track("whatsapp_click", { link_id: a.id || "", page_path: location.pathname });
      else if (/^mailto:/i.test(h)) track("email_click", { page_path: location.pathname });
    }
    var c = t.closest(".copy[data-copy]");
    if (c) track("contact_copy", { item: c.getAttribute("data-copy"), page_path: location.pathname });
    if (t.closest(".tqc-btn")) track("chat_open", { page_path: location.pathname });
  }, true);

  // ---------- cookie banner (only when GA is on and no choice yet) ----------
  if (!GA_ID || choice) return;
  function showBanner() {
    var L = TXT[lang] || TXT.en;
    var css = document.createElement("style");
    css.textContent =
      ".tqk{position:fixed;z-index:62;inset-inline-start:16px;bottom:calc(16px + env(safe-area-inset-bottom,0px));max-width:400px;" +
      "background:var(--surface,#f9faf9);color:var(--ink,#14232a);border:1px solid var(--line,#d3dbd9);border-radius:14px;" +
      "box-shadow:0 10px 30px rgba(0,0,0,.16);padding:14px 16px;font:400 .85rem/1.5 var(--f-body,system-ui,sans-serif)}" +
      ".tqk p{margin:0 0 10px}.tqk a{color:var(--accent,#1f6a64)}" +
      ".tqk .r{display:flex;gap:8px;flex-wrap:wrap}" +
      ".tqk button{font-family:inherit;font-weight:600;font-size:.82rem;line-height:1;padding:9px 14px;border-radius:999px;cursor:pointer;border:1px solid var(--accent,#1f6a64)}" +
      ".tqk .y{background:var(--accent,#1f6a64);color:var(--on-accent,#fff)}.tqk .n{background:transparent;color:var(--accent,#1f6a64)}" +
      "@media (max-width:640px){.tqk{inset-inline:12px;max-width:none;bottom:calc(76px + env(safe-area-inset-bottom,0px))}}";
    document.head.appendChild(css);
    var box = document.createElement("div");
    box.className = "tqk"; box.setAttribute("role", "dialog"); box.setAttribute("aria-label", L[3]);
    if (lang === "ar") box.dir = "rtl";
    var p = document.createElement("p");
    p.textContent = L[0] + " ";
    var link = document.createElement("a"); link.href = "/privacy.html"; link.textContent = L[3];
    p.appendChild(link);
    var row = document.createElement("div"); row.className = "r";
    var yes = document.createElement("button"); yes.type = "button"; yes.className = "y"; yes.textContent = L[1];
    var no = document.createElement("button"); no.type = "button"; no.className = "n"; no.textContent = L[2];
    row.appendChild(yes); row.appendChild(no);
    box.appendChild(p); box.appendChild(row);
    function decide(v) {
      lsSet(KEY, v);
      window.gtag("consent", "update", { analytics_storage: v });
      if (v === "granted") { try { sessionStorage.setItem(SKEY, JSON.stringify(source)); } catch (e) {} }
      else { try { sessionStorage.removeItem(SKEY); } catch (e) {} }
      box.remove();
    }
    yes.addEventListener("click", function () { decide("granted"); });
    no.addEventListener("click", function () { decide("denied"); });
    document.body.appendChild(box);
  }
  if (document.body) showBanner(); else document.addEventListener("DOMContentLoaded", showBanner);
})();
