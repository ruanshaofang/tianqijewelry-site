/* Tianqi Jewelry website assistant widget. Shows only when /api/chat/health reports ok. */
(function () {
  var L = {
    en: { open: "Ask us", title: "Tianqi assistant", sub: "AI · replies in your language", hi: "Hello! I can answer questions about our pearls, minimums, samples, shipping and payment. What are you looking for?", ph: "Type your question…", send: "Send", note: "AI answers may contain mistakes. Prices and orders are confirmed by our team.", wa: "Chat with a person on WhatsApp", err: "Sorry, something went wrong. Please message us on WhatsApp.", close: "Close" },
    zh: { open: "在线咨询", title: "田琦珠宝助手", sub: "AI · 用您的语言回复", hi: "您好！我可以解答珍珠品类、起订量、样品、物流和付款等问题。请问您需要什么？", ph: "输入您的问题…", send: "发送", note: "AI 回答可能有误，价格和订单以我们团队确认为准。", wa: "在 WhatsApp 上联系真人", err: "抱歉，出了点问题，请通过 WhatsApp 联系我们。", close: "关闭" },
    de: { open: "Fragen Sie uns", title: "Tianqi-Assistent", sub: "KI · antwortet in Ihrer Sprache", hi: "Hallo! Ich beantworte Fragen zu unseren Perlen, Mindestmengen, Mustern, Versand und Zahlung. Was suchen Sie?", ph: "Ihre Frage…", send: "Senden", note: "KI-Antworten können Fehler enthalten. Preise und Aufträge bestätigt unser Team.", wa: "Mit einer Person auf WhatsApp chatten", err: "Leider ist ein Fehler aufgetreten. Bitte schreiben Sie uns auf WhatsApp.", close: "Schließen" },
    fr: { open: "Une question ?", title: "Assistant Tianqi", sub: "IA · répond dans votre langue", hi: "Bonjour ! Je réponds à vos questions sur nos perles, minimums, échantillons, livraison et paiement. Que recherchez-vous ?", ph: "Votre question…", send: "Envoyer", note: "Les réponses de l'IA peuvent contenir des erreurs. Prix et commandes sont confirmés par notre équipe.", wa: "Parler à une personne sur WhatsApp", err: "Désolé, une erreur s'est produite. Écrivez-nous sur WhatsApp.", close: "Fermer" },
    es: { open: "Pregúntenos", title: "Asistente Tianqi", sub: "IA · responde en su idioma", hi: "¡Hola! Respondo preguntas sobre nuestras perlas, mínimos, muestras, envío y pago. ¿Qué busca?", ph: "Escriba su pregunta…", send: "Enviar", note: "Las respuestas de la IA pueden contener errores. Precios y pedidos los confirma nuestro equipo.", wa: "Hablar con una persona por WhatsApp", err: "Lo sentimos, algo falló. Escríbanos por WhatsApp.", close: "Cerrar" },
    it: { open: "Chiedici", title: "Assistente Tianqi", sub: "IA · risponde nella tua lingua", hi: "Ciao! Rispondo a domande su perle, minimi d'ordine, campioni, spedizione e pagamento. Cosa cerchi?", ph: "Scrivi la tua domanda…", send: "Invia", note: "Le risposte dell'IA possono contenere errori. Prezzi e ordini sono confermati dal nostro team.", wa: "Parla con una persona su WhatsApp", err: "Si è verificato un errore. Scrivici su WhatsApp.", close: "Chiudi" },
    pt: { open: "Fale conosco", title: "Assistente Tianqi", sub: "IA · responde no seu idioma", hi: "Olá! Respondo dúvidas sobre nossas pérolas, pedidos mínimos, amostras, envio e pagamento. O que procura?", ph: "Digite sua pergunta…", send: "Enviar", note: "As respostas da IA podem conter erros. Preços e pedidos são confirmados pela nossa equipe.", wa: "Falar com uma pessoa no WhatsApp", err: "Desculpe, algo deu errado. Fale conosco pelo WhatsApp.", close: "Fechar" },
    ru: { open: "Задать вопрос", title: "Ассистент Tianqi", sub: "ИИ · отвечает на вашем языке", hi: "Здравствуйте! Отвечу на вопросы о жемчуге, минимальных заказах, образцах, доставке и оплате. Что вас интересует?", ph: "Ваш вопрос…", send: "Отправить", note: "ИИ может ошибаться. Цены и заказы подтверждает наша команда.", wa: "Написать сотруднику в WhatsApp", err: "Произошла ошибка. Напишите нам в WhatsApp.", close: "Закрыть" },
    ja: { open: "お問い合わせ", title: "Tianqi アシスタント", sub: "AI · ご利用の言語で回答", hi: "こんにちは。真珠の種類、最小ロット、サンプル、配送、お支払いについてお答えします。どのような商品をお探しですか？", ph: "ご質問を入力…", send: "送信", note: "AIの回答には誤りが含まれる場合があります。価格とご注文は担当者が確認します。", wa: "WhatsAppで担当者と話す", err: "エラーが発生しました。WhatsAppでご連絡ください。", close: "閉じる" },
    ko: { open: "문의하기", title: "Tianqi 어시스턴트", sub: "AI · 고객님의 언어로 답변", hi: "안녕하세요! 진주 종류, 최소 주문량, 샘플, 배송, 결제에 대해 답변해 드립니다. 무엇을 찾으시나요?", ph: "질문을 입력하세요…", send: "보내기", note: "AI 답변에는 오류가 있을 수 있습니다. 가격과 주문은 담당자가 확인합니다.", wa: "WhatsApp으로 담당자와 대화", err: "오류가 발생했습니다. WhatsApp으로 문의해 주세요.", close: "닫기" },
    ar: { open: "اسألنا", title: "مساعد Tianqi", sub: "ذكاء اصطناعي · يرد بلغتك", hi: "مرحبًا! أجيب عن أسئلتك حول اللؤلؤ والحد الأدنى للطلب والعينات والشحن والدفع. عمّ تبحث؟", ph: "اكتب سؤالك…", send: "إرسال", note: "قد تحتوي إجابات الذكاء الاصطناعي على أخطاء. يؤكد فريقنا الأسعار والطلبات.", wa: "تحدث مع موظف عبر واتساب", err: "عذرًا، حدث خطأ. يرجى مراسلتنا عبر واتساب.", close: "إغلاق" }
  };
  var lang = (document.documentElement.lang || "en").toLowerCase();
  var key = lang.indexOf("zh") === 0 ? "zh" : lang.slice(0, 2);
  var T = L[key] || L.en;
  var WA = "https://wa.me/85251659258";
  var STORE = "tq-chat-" + key;
  var history = [];
  try { history = JSON.parse(sessionStorage.getItem(STORE) || "[]") || []; } catch (e) { history = []; }

  function save() { try { sessionStorage.setItem(STORE, JSON.stringify(history.slice(-20))); } catch (e) {} }

  fetch("/api/chat/health", { cache: "no-store" }).then(function (r) { return r.json(); })
    .then(function (j) { if (j && j.ok) build(); }).catch(function () {});

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; }

  function build() {
    var css = el("style");
    css.textContent =
      ".tqc-btn{position:fixed;z-index:60;bottom:calc(16px + env(safe-area-inset-bottom,0px));inset-inline-end:16px;display:flex;align-items:center;gap:8px;padding:12px 16px;border-radius:999px;border:0;background:var(--accent,#1f6a64);color:var(--on-accent,#fff);font:600 .9rem/1 var(--f-body,system-ui,sans-serif);box-shadow:0 6px 20px rgba(0,0,0,.18);cursor:pointer}" +
      ".tqc-btn svg{width:18px;height:18px}" +
      ".tqc-panel{position:fixed;z-index:61;bottom:calc(16px + env(safe-area-inset-bottom,0px));inset-inline-end:16px;width:min(380px,calc(100vw - 32px));height:min(560px,calc(100dvh - 32px));display:none;flex-direction:column;background:var(--bg,#fff);color:var(--ink,#14232a);border:1px solid var(--line,#d3dbd9);border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,.22);overflow:hidden;font-family:var(--f-body,system-ui,sans-serif)}" +
      ".tqc-panel.open{display:flex}" +
      ".tqc-head{display:flex;align-items:center;gap:10px;padding:12px 14px;background:var(--accent,#1f6a64);color:var(--on-accent,#fff)}" +
      ".tqc-head b{display:block;font-size:.95rem}.tqc-head small{opacity:.85;font-size:.75rem}" +
      ".tqc-x{margin-inline-start:auto;background:none;border:0;color:inherit;font-size:1.4rem;line-height:1;cursor:pointer;padding:4px 8px}" +
      ".tqc-log{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px}" +
      ".tqc-m{max-width:85%;padding:9px 12px;border-radius:12px;font-size:.9rem;line-height:1.5;white-space:pre-wrap;word-wrap:break-word}" +
      ".tqc-a{align-self:flex-start;background:var(--accent-soft,#d6e7e3)}.tqc-u{align-self:flex-end;background:var(--accent,#1f6a64);color:var(--on-accent,#fff)}" +
      ".tqc-typing{opacity:.6}" +
      ".tqc-foot{border-top:1px solid var(--line,#d3dbd9);padding:10px 12px;display:flex;flex-direction:column;gap:8px}" +
      ".tqc-row{display:flex;gap:8px;align-items:stretch}.tqc-panel .tqc-row textarea{flex:1;width:auto;min-width:0;min-height:0;margin:0;resize:none;height:42px;max-height:120px;padding:10px;box-sizing:border-box;border:1px solid var(--line,#d3dbd9);border-radius:10px;background:transparent;color:inherit;font:inherit;font-size:.9rem}" +
      ".tqc-panel .tqc-row button{height:42px;margin:0;border:0;border-radius:10px;padding:0 14px;background:var(--accent,#1f6a64);color:var(--on-accent,#fff);font:600 .85rem var(--f-body,sans-serif);cursor:pointer}" +
      ".tqc-row button:disabled{opacity:.5;cursor:default}" +
      ".tqc-note{font-size:.72rem;color:var(--muted,#56676d);line-height:1.4}.tqc-note a{color:var(--accent,#1f6a64)}";
    document.head.appendChild(css);

    var icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/></svg>';
    var btn = el("button", "tqc-btn"); btn.type = "button"; btn.innerHTML = icon; btn.appendChild(el("span", "", T.open));
    btn.setAttribute("aria-haspopup", "dialog");

    var panel = el("div", "tqc-panel"); panel.setAttribute("role", "dialog"); panel.setAttribute("aria-label", T.title);
    var head = el("div", "tqc-head"); var ht = el("div"); ht.appendChild(el("b", "", T.title)); ht.appendChild(el("small", "", T.sub));
    var x = el("button", "tqc-x", "×"); x.type = "button"; x.setAttribute("aria-label", T.close);
    head.appendChild(ht); head.appendChild(x);
    var log = el("div", "tqc-log"); log.setAttribute("aria-live", "polite");
    var foot = el("div", "tqc-foot"); var row = el("div", "tqc-row");
    var ta = el("textarea"); ta.placeholder = T.ph; ta.maxLength = 1000; ta.rows = 1; ta.setAttribute("aria-label", T.ph);
    var sb = el("button", "", T.send); sb.type = "button";
    row.appendChild(ta); row.appendChild(sb);
    var note = el("div", "tqc-note"); note.appendChild(document.createTextNode(T.note + " "));
    var wa = el("a", "", T.wa); wa.href = WA; wa.target = "_blank"; wa.rel = "noopener"; note.appendChild(wa);
    foot.appendChild(row); foot.appendChild(note);
    panel.appendChild(head); panel.appendChild(log); panel.appendChild(foot);
    document.body.appendChild(btn); document.body.appendChild(panel);

    function add(role, text, cls) {
      var m = el("div", "tqc-m " + (role === "user" ? "tqc-u" : "tqc-a") + (cls ? " " + cls : ""), text);
      log.appendChild(m); log.scrollTop = log.scrollHeight; return m;
    }
    add("assistant", T.hi);
    history.forEach(function (m) { add(m.role, m.content); });

    function open() { panel.classList.add("open"); btn.style.display = "none"; setTimeout(function () { ta.focus(); }, 50); }
    function close() { panel.classList.remove("open"); btn.style.display = ""; btn.focus(); }
    btn.addEventListener("click", open); x.addEventListener("click", close);
    panel.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });

    var busy = false;
    function send() {
      var q = ta.value.trim(); if (!q || busy) return;
      busy = true; sb.disabled = true; ta.value = "";
      add("user", q); history.push({ role: "user", content: q }); save();
      var wait = add("assistant", "…", "tqc-typing");
      fetch("/api/chat", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history.slice(-12), lang: document.documentElement.lang || "en", page: location.pathname })
      }).then(function (r) { return r.json(); }).then(function (j) {
        var a = (j && j.reply) ? String(j.reply).replace(/\*\*/g, "") : T.err;
        wait.textContent = a; wait.classList.remove("tqc-typing");
        if (j && j.reply && !j.error && !j.limited) { history.push({ role: "assistant", content: a }); save(); }
      }).catch(function () { wait.textContent = T.err; wait.classList.remove("tqc-typing"); })
        .then(function () { busy = false; sb.disabled = false; log.scrollTop = log.scrollHeight; ta.focus(); });
    }
    sb.addEventListener("click", send);
    ta.addEventListener("keydown", function (e) { if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); send(); } });
  }
})();
