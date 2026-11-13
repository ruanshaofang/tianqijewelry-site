#!/usr/bin/env python3
"""Build one static page per catalogue item, in all 11 site languages.

  English:   site/products/<slug>/index.html
  Others:    site/<lang>/products/<slug>/index.html

Source of truth: window.PRODS / window.CAT in each language's catalogue page
(site/[<lang>/]products/index.html). Page text lives in tools/product_i18n.py.
Re-run after the catalogue changes:  python3 tools/build_products.py
It also links catalogue cards to the item pages and rewrites the item entries in sitemap.xml.
Safe to run repeatedly.
"""
import html
import json
import re
import sys
import urllib.parse
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from product_i18n import L  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent / "site"
BASE = "https://tianqijewelry.com"
LANGS = ["en", "zh", "de", "fr", "es", "it", "pt", "ru", "ja", "ko", "ar"]
SALT = {"akoya", "southsea", "tahitian"}


def esc(s):
    return html.escape(str(s), quote=True)


def prefix(lang):
    return "" if lang == "en" else f"/{lang}"


def slug(p):
    s = re.sub(r"[^a-z0-9]+", "-", p["t"].lower()).strip("-")
    if len(s) > 60:
        s = s[:61].rsplit("-", 1)[0]
    return f"{p['c'].lower()}-{s}"


# ---------- load every language's catalogue ----------
SRC, CAT, HL = {}, {}, {}
for lg in LANGS:
    f = ROOT / prefix(lg).lstrip("/") / "products" / "index.html"
    SRC[lg] = f.read_text(encoding="utf-8")
    CAT[lg] = json.loads(re.search(r"window\.CAT=(\{.*?\});window\.", SRC[lg], re.S).group(1))
    HL[lg] = re.search(r'<html lang="([^"]+)"', SRC[lg]).group(1)  # hreflang code, e.g. zh-CN
PRODS = json.loads(re.search(r"window\.PRODS=(\[.*?\]);", SRC["en"], re.S).group(1))
for p in PRODS:
    p["slug"] = slug(p)
    p["wh"] = Image.open(ROOT / "assets" / "products" / (p["i"][0] + ".webp")).size


def url(lg, p):
    return f"{prefix(lg)}/products/{p['slug']}/"


def shell(lg):
    src = SRC[lg]
    head = src[src.find("<head>") + 6:src.find("</head>")]
    for pat in [r"<title>.*?</title>", r'<meta name="description"[^>]*>', r'<link rel="canonical"[^>]*>',
                r'<link rel="alternate"[^>]*>', r'<meta property="og:[^>]*>', r'<meta name="twitter:[^>]*>',
                r'<script type="application/ld\+json">.*?</script>']:
        head = re.sub(pat, "", head, flags=re.S)
    head = re.sub(r"\n\s*\n+", "\n", head)
    html_tag = re.search(r"<html[^>]*>", src).group(0)
    header = src[src.find("<header"):src.find("</header>") + 9]
    footer = src[src.find("<footer"):src.find("</footer>") + 9]
    return html_tag, head, header, footer


SHELL = {lg: shell(lg) for lg in LANGS}

PAGE_CSS = """<style>
.crumbs{font-size:.8125rem;color:var(--muted);padding-block:22px 6px}
.crumbs a{color:var(--muted)}
.prod{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:36px;padding-block:10px 40px;align-items:start}
@media (max-width:820px){.prod{grid-template-columns:1fr;gap:20px}}
.prod-media img.big{display:block;width:100%;height:auto;max-height:80vh;object-fit:contain;background:#f3f3f1;border-radius:14px;border:1px solid var(--line)}
.prod-media .pd-thumbs{padding:8px 0}
.prod-info{display:flex;flex-direction:column;gap:14px}
.prod-info .code{font-family:var(--f-mono);color:var(--accent);font-size:.875rem;letter-spacing:.04em}
.prod-info h1{font-size:var(--s3,1.75rem);line-height:1.2;margin:0}
.tags{display:flex;gap:8px;flex-wrap:wrap}
.tags a{font-size:.8125rem;border:1px solid var(--line);border-radius:999px;padding:4px 10px;color:var(--ink);text-decoration:none;background:var(--surface)}
.facts{width:100%;border-collapse:collapse;font-size:.9rem}
.facts th,.facts td{text-align:start;padding:9px 0;border-bottom:1px solid var(--line);vertical-align:top}
.facts th{width:34%;color:var(--muted);font-weight:500;padding-inline-end:12px}
.prod-act{display:flex;gap:10px;flex-wrap:wrap}
.prod-act .btn{display:inline-flex}
.prod-act .add[aria-pressed="true"]{background:var(--accent);color:var(--on-accent)}
.note{color:var(--muted);font-size:.9rem}
.about-type{padding-block:10px 30px;max-width:72ch}
.about-type h2,.related h2{font-size:var(--s2,1.35rem);margin:0 0 10px}
.related{padding-block:10px 60px}
.related .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:14px}
.related a.card{text-decoration:none;color:inherit}
</style>"""


def related(lg, p):
    C = CAT[lg]
    same = [q for q in PRODS if q is not p and q["y"] == p["y"] and q["k"] == p["k"]]
    more = [q for q in PRODS if q is not p and q not in same and (q["y"] == p["y"] or q["k"] == p["k"])]
    return "".join(
        f'<a class="card" href="{url(lg, q)}"><img src="/assets/products/{q["i"][0]}-t.webp" alt="{esc(q["t"])}" loading="lazy" decoding="async" width="480" height="480">'
        f'<div class="meta"><span class="code">{q["c"]}</span><h3>{esc(q["t"])}</h3><span class="ty">{esc(C["types"][q["y"]])}</span></div></a>'
        for q in (same + more)[:6])


def page(lg, p):
    T, C = L[lg], CAT[lg]
    html_tag, head, header, footer = SHELL[lg]
    pre = prefix(lg)
    t, ty, cat = p["t"], C["types"][p["y"]], C["cats"][p["k"]]
    canon = BASE + url(lg, p)
    title = f"{t} | {p['c']} {T['title_suffix']}"
    desc = T["desc"].format(t=t, ty=ty, cat=cat, c=p["c"])[:300]
    og_img = f"{BASE}/assets/products/{p['i'][0]}.webp"
    alts = "".join(f'<link rel="alternate" hreflang="{HL[x]}" href="{BASE}{url(x, p)}">\n' for x in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{BASE}{url("en", p)}">\n'
    hdr = re.sub(r'href="(/[a-z]{2})?/products/"', lambda m: f'href="{m.group(1) or ""}/products/{p["slug"]}/"', header)
    wa_text = (f"Hello Tianqi Jewelry, I'd like a quote for {p['c']} · {t}.\nQuantity: \nDestination country: \n"
               f"Language: {C.get('langName', lg)}\n\n{canon}")
    wa = "https://wa.me/85251659258?text=" + esc(urllib.parse.quote(wa_text))
    W, H = p["wh"]
    thumbs = ""
    if len(p["i"]) > 1:
        thumbs = '<div class="pd-thumbs">' + "".join(
            f'<button type="button" data-src="/assets/products/{n}.webp" aria-current="{str(ix == 0).lower()}" aria-label="{p["c"]} {ix + 1}"><img src="/assets/products/{n}-t.webp" alt=""></button>'
            for ix, n in enumerate(p["i"])) + "</div>"
    water = T["salt"] if p["y"] in SALT else T["fresh"]
    rows = [(C["code"], p["c"]), (T["l_category"], cat), (T["l_type"], f"{ty} ({water})")] + T["facts"]
    facts = "".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in rows)
    mail = f'<a href="mailto:info@tianqijewelry.com?subject={p["c"]}%20quote">info@tianqijewelry.com</a>'
    form = f'<a href="{pre}/#inquiry">{esc(T["form"])}</a>'
    email_line = esc(T["email"]).replace("{mail}", mail).replace("{form}", form)
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Product", "name": t, "sku": p["c"], "mpn": p["c"],
         "image": [f"{BASE}/assets/products/{i}.webp" for i in p["i"]],
         "description": desc, "category": f"{cat} > {ty}",
         "brand": {"@type": "Brand", "name": "Tianqi Jewelry"},
         "manufacturer": {"@id": f"{BASE}/#org"}, "url": canon},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": T["home"], "item": f"{BASE}{pre}/"},
            {"@type": "ListItem", "position": 2, "name": T["catalogue"], "item": f"{BASE}{pre}/products/"},
            {"@type": "ListItem", "position": 3, "name": p["c"], "item": canon}]}]}
    added = f"✓ {C['added']} — {T['added_hint']}"
    add = f"+ {C['add']}"
    return f"""<!DOCTYPE html>
{html_tag}
<head>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
{alts}<meta property="og:type" content="product">
<meta property="og:title" content="{esc(t)} — Tianqi Jewelry">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og_img}">
<meta property="og:site_name" content="Tianqi Jewelry">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{og_img}">
{head}
{PAGE_CSS}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
{hdr}
<main id="top">
<div class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{pre}/">{esc(T['home'])}</a> / <a href="{pre}/products/">{esc(T['catalogue'])}</a> / <a href="{pre}/products/#{p['c']}">{esc(cat)}</a> / {p['c']}</nav>
  <section class="prod">
    <div class="prod-media">
      <img class="big" id="big" src="/assets/products/{p['i'][0]}.webp" alt="{esc(t)}" width="{W}" height="{H}" decoding="async">
      {thumbs}
    </div>
    <div class="prod-info">
      <span class="code">{esc(C['code'])} {p['c']}</span>
      <h1 lang="en">{esc(t)}</h1>
      <div class="tags"><a href="{pre}/products/">{esc(ty)}</a><a href="{pre}/products/">{esc(cat)}</a><a href="{pre}/#services">{esc(T['wholesale_tag'])}</a></div>
      <p class="note">{esc(T['prices'])}</p>
      <div class="prod-act">
        <a class="btn" href="{wa}" target="_blank" rel="noopener">{esc(T['wa_btn'])}</a>
        <button class="btn ghost add" type="button" id="add" aria-pressed="false">{esc(add)}</button>
      </div>
      <table class="facts"><tbody>{facts}</tbody></table>
      <p class="note">{esc(T['photos'])}</p>
      <p class="note">{email_line}</p>
    </div>
  </section>
  <section class="about-type">
    <h2>{esc(T['about'].format(ty=ty))}</h2>
    <p>{esc(T['types'][p['y']])}</p>
    <p class="note">{esc(T['grading'])} <a href="{pre}/#pearls">{esc(T['compare'])}</a> · <a href="{pre}/#process">{esc(T['process'])}</a></p>
  </section>
  <section class="related">
    <h2>{esc(T['similar'])}</h2>
    <div class="grid">{related(lg, p)}</div>
    <p style="margin-top:18px"><a class="btn ghost" style="display:inline-flex" href="{pre}/products/">{esc(T['see_all'].format(n=len(PRODS)))}</a></p>
  </section>
</div>
</main>
{footer}
<script>
(function(){{
  var KEY='tq-inq',c={json.dumps(p['c'])},b=document.getElementById('add'),list=[],ADD={json.dumps(add, ensure_ascii=False)},DONE={json.dumps(added, ensure_ascii=False)};
  try{{list=JSON.parse(localStorage.getItem(KEY)||'[]')||[]}}catch(e){{}}
  function sync(){{var on=list.indexOf(c)>-1;b.setAttribute('aria-pressed',String(on));b.textContent=on?DONE:ADD}}
  b.addEventListener('click',function(){{var i=list.indexOf(c);if(i>-1)list.splice(i,1);else list.push(c);try{{localStorage.setItem(KEY,JSON.stringify(list))}}catch(e){{}}sync()}});
  sync();
  var big=document.getElementById('big');
  document.querySelectorAll('.pd-thumbs button').forEach(function(t){{t.addEventListener('click',function(){{big.src=t.dataset.src;document.querySelectorAll('.pd-thumbs button').forEach(function(x){{x.setAttribute('aria-current',String(x===t))}})}})}});
  document.addEventListener('click',function(e){{var d=document.querySelector('.langs');if(d&&d.open&&!d.contains(e.target))d.open=false}});
}})();
</script>
</body>
</html>
"""


FULL = {"en": "Full details", "zh": "查看详情", "de": "Alle Details", "fr": "Voir le détail", "es": "Ver detalles",
        "it": "Tutti i dettagli", "pt": "Ver detalhes", "ru": "Подробнее", "ja": "詳細を見る", "ko": "자세히 보기", "ar": "كل التفاصيل"}

total = 0
for lg in LANGS:
    for p in PRODS:
        out = ROOT / prefix(lg).lstrip("/") / "products" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(lg, p), encoding="utf-8")
        total += 1

    cf = ROOT / prefix(lg).lstrip("/") / "products" / "index.html"
    cat = cf.read_text(encoding="utf-8")
    for p in PRODS:
        pat = re.compile(r'(<span class="code">' + p["c"] + r'</span><h3>)(?!<a )(.*?)(</h3>)', re.S)
        cat = pat.sub(lambda m: f'{m.group(1)}<a href="{url(lg, p)}" style="color:inherit;text-decoration:none">{m.group(2)}</a>{m.group(3)}', cat, count=1)
    if 'id="pd-page"' not in cat:
        cat = cat.replace('<a class="btn ghost" id="pd-wa"', f'<a class="btn ghost" id="pd-page" href="#">{FULL[lg]}</a><a class="btn ghost" id="pd-wa"', 1)
        cat = cat.replace("var pa=document.getElementById('pd-add'); pa.dataset.c=p.c;",
                          "var pg=document.getElementById('pd-page'); if(pg&&window.PURL)pg.href=window.PURL[p.c]||'#';\n  var pa=document.getElementById('pd-add'); pa.dataset.c=p.c;", 1)
    cat = re.sub(r"window\.PURL=\{.*?\};", "", cat)
    cat = cat.replace("window.PRODS=", "window.PURL=" + json.dumps({p["c"]: url(lg, p) for p in PRODS}) + ";window.PRODS=", 1)
    cf.write_text(cat, encoding="utf-8")

sm_path = ROOT / "sitemap.xml"
sm = sm_path.read_text(encoding="utf-8")
sm = re.sub(r"\s*<url><loc>https://tianqijewelry\.com(/[a-z]{2})?/products/tq\d{3}-[^<]*</loc>.*?</url>", "", sm, flags=re.S)
entries = "".join(f"\n  <url><loc>{BASE}{url(lg, p)}</loc><changefreq>monthly</changefreq><priority>{'0.6' if lg == 'en' else '0.5'}</priority></url>"
                  for lg in LANGS for p in PRODS)
sm = sm.replace("</urlset>", entries + "\n</urlset>")
sm_path.write_text(sm, encoding="utf-8")
print(f"built {total} item pages in {len(LANGS)} languages; sitemap now has {sm.count('<loc>')} URLs")
