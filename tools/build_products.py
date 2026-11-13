#!/usr/bin/env python3
"""Build one static page per catalogue item: site/products/<slug>/index.html (English).

Source of truth: window.PRODS / window.CAT in site/products/index.html.
Re-run after the catalogue changes:  python3 tools/build_products.py
It also links catalogue cards to the new pages and adds the pages to sitemap.xml.
"""
import html
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent / "site"
BASE = "https://tianqijewelry.com"
CAT_PAGE = ROOT / "products" / "index.html"

src = CAT_PAGE.read_text(encoding="utf-8")
CAT = json.loads(re.search(r"window\.CAT=(\{.*?\});window\.PRODS", src, re.S).group(1))
PRODS = json.loads(re.search(r"window\.PRODS=(\[.*?\]);", src, re.S).group(1))

# ---------- facts reused from the homepage / catalogue (no invented specs) ----------
TYPE_TEXT = {
    "freshwater": "Freshwater pearls are cultured in mussels in Zhejiang, close to our Shanxiahu base. They come in a wide range of colours and shapes, from round to baroque, and offer strong value for everyday and volume lines.",
    "baroque": "Baroque pearls have an irregular, free-form shape, so every piece is slightly different. They are popular for contemporary and handmade designs, and we can match them by size, colour and shape for pairs or strands.",
    "keshi": "Keshi pearls form without a bead nucleus, so they are solid nacre with a high lustre and an organic, irregular shape. Biwa pearls are flat, elongated freshwater pearls. Both suit distinctive earrings, pendants and charms.",
    "edison": "Edison pearls are bead-nucleated freshwater pearls developed in Zhejiang. They grow larger and rounder than most freshwater pearls, with a strong lustre and metallic colours.",
    "akoya": "Akoya pearls are saltwater pearls with sharp lustre and a round shape, usually with pink or silver overtones. They are the classic choice for strands and matched earrings.",
    "southsea": "South Sea pearls are saltwater pearls with thick nacre and large sizes, in gold and white. They suit high-value pieces and custom work.",
    "tahitian": "Tahitian pearls from French Polynesia are naturally dark, with peacock-green and aubergine overtones. They work for both men's and women's designs.",
}
SALT = {"akoya", "southsea", "tahitian"}

FACTS = [
    ("Minimum order", "5 pcs per item and USD 100 per order. OEM from 50 pcs per design"),
    ("Dispatch", "In-stock lots ship from Zhuji, Zhejiang in 1–3 business days"),
    ("Shipping", "Worldwide with one tracking number. DDP (duties paid) to the US; landed-cost quotes for the EU"),
    ("Pearls", "Cultured pearls only. Pearl type and any treatment are stated on the invoice"),
    ("Samples", "Available; samples and their shipping are paid separately"),
    ("Payment", "T/T or PayPal"),
]


def esc(s):
    return html.escape(str(s), quote=True)


def slug(p):
    s = re.sub(r"[^a-z0-9]+", "-", p["t"].lower()).strip("-")
    if len(s) > 60:
        s = s[:61].rsplit("-", 1)[0]
    return f"{p['c'].lower()}-{s}"


for p in PRODS:
    p["slug"] = slug(p)
    p["url"] = f"/products/{p['slug']}/"

# ---------- page shell taken from the live catalogue page ----------
head = src[src.find("<head>") + 6:src.find("</head>")]
for pat in [r"<title>.*?</title>", r'<meta name="description"[^>]*>', r'<link rel="canonical"[^>]*>',
            r'<link rel="alternate"[^>]*>', r'<meta property="og:[^>]*>', r'<meta name="twitter:[^>]*>',
            r'<script type="application/ld\+json">.*?</script>']:
    head = re.sub(pat, "", head, flags=re.S)
head = re.sub(r"\n\s*\n+", "\n", head)
header = src[src.find("<header"):src.find("</header>") + 9]
footer = src[src.find("<footer"):src.find("</footer>") + 9]

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


def jsonld(p):
    imgs = [f"{BASE}/assets/products/{i}.webp" for i in p["i"]]
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Product",
                "name": p["t"],
                "sku": p["c"],
                "mpn": p["c"],
                "image": imgs,
                "description": f"{p['t']} ({CAT['types'][p['y']]}, {CAT['cats'][p['k']]}). Cultured pearls supplied wholesale from Zhuji, China by Tianqi Jewelry.",
                "category": f"{CAT['cats'][p['k']]} > {CAT['types'][p['y']]}",
                "brand": {"@type": "Brand", "name": "Tianqi Jewelry"},
                "manufacturer": {"@id": f"{BASE}/#org"},
                "url": BASE + p["url"],
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
                    {"@type": "ListItem", "position": 2, "name": "Catalogue", "item": BASE + "/products/"},
                    {"@type": "ListItem", "position": 3, "name": p["c"], "item": BASE + p["url"]},
                ],
            },
        ],
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


def related(p):
    same = [q for q in PRODS if q is not p and q["y"] == p["y"] and q["k"] == p["k"]]
    more = [q for q in PRODS if q is not p and q not in same and (q["y"] == p["y"] or q["k"] == p["k"])]
    picks = (same + more)[:6]
    cards = "".join(
        f'<a class="card" href="{q["url"]}"><img src="/assets/products/{q["i"][0]}-t.webp" alt="{esc(q["t"])}" loading="lazy" decoding="async" width="480" height="480">'
        f'<div class="meta"><span class="code">{q["c"]}</span><h3>{esc(q["t"])}</h3><span class="ty">{esc(CAT["types"][q["y"]])}</span></div></a>'
        for q in picks)
    return cards


def page(p):
    t, ty, cat = p["t"], CAT["types"][p["y"]], CAT["cats"][p["k"]]
    title = f"{t} | {p['c']} wholesale | Tianqi Jewelry"
    desc = (f"{t} — {ty.lower()} {cat.lower()}, item {p['c']}. Cultured pearls direct from Zhuji, China. "
            f"Wholesale from 5 pcs, ships in 1–3 business days, DDP to the US.")[:300]
    canon = BASE + p["url"]
    og_img = f"{BASE}/assets/products/{p['i'][0]}.webp"
    wa_text = f"Hello Tianqi Jewelry, I'd like a quote for {p['c']} · {t}.\nQuantity: \nDestination country: \n\n{canon}"
    wa = "https://wa.me/85251659258?text=" + html.escape(__import__("urllib.parse").parse.quote(wa_text))
    W, H = Image.open(ROOT / "assets" / "products" / (p["i"][0] + ".webp")).size
    thumbs = ""
    if len(p["i"]) > 1:
        thumbs = '<div class="pd-thumbs">' + "".join(
            f'<button type="button" data-src="/assets/products/{n}.webp" aria-current="{str(ix == 0).lower()}" aria-label="{p["c"]} photo {ix + 1}"><img src="/assets/products/{n}-t.webp" alt=""></button>'
            for ix, n in enumerate(p["i"])) + "</div>"
    facts = "".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in
                    [("Item code", p["c"]), ("Category", cat), ("Pearl type", ty + (" (saltwater)" if p["y"] in SALT else " (freshwater)"))] + FACTS)
    return f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="product">
<meta property="og:title" content="{esc(t)} — Tianqi Jewelry">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og_img}">
<meta property="og:site_name" content="Tianqi Jewelry">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{og_img}">
{head}
{PAGE_CSS}
{jsonld(p)}
</head>
<body>
{header}
<main id="top">
<div class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/products/">Catalogue</a> / <a href="/products/#{p['c']}">{esc(cat)}</a> / {p['c']}</nav>
  <section class="prod">
    <div class="prod-media">
      <img class="big" id="big" src="/assets/products/{p['i'][0]}.webp" alt="{esc(t)}" width="{W}" height="{H}" decoding="async">
      {thumbs}
    </div>
    <div class="prod-info">
      <span class="code">Item code {p['c']}</span>
      <h1>{esc(t)}</h1>
      <div class="tags"><a href="/products/">{esc(ty)}</a><a href="/products/">{esc(cat)}</a><a href="/#services">Wholesale · OEM · Dropship</a></div>
      <p class="note">Prices depend on grade, size and quantity. Send us your quantity and destination and we will quote, with real photos or video, within two business days.</p>
      <div class="prod-act">
        <a class="btn" href="{wa}" target="_blank" rel="noopener">Ask for a quote on WhatsApp</a>
        <button class="btn ghost add" type="button" id="add" data-c="{p['c']}" aria-pressed="false">+ Add to inquiry list</button>
      </div>
      <table class="facts"><tbody>{facts}</tbody></table>
      <p class="note">Catalogue photos show typical lots. Before you pay, we send photos or video of the pearls you will actually receive. Bulk orders are checked against the approved sample.</p>
      <p class="note">Prefer email? Write to <a href="mailto:info@tianqijewelry.com?subject={esc(p['c'])}%20quote">info@tianqijewelry.com</a> or use the <a href="/#inquiry">inquiry form</a>.</p>
    </div>
  </section>
  <section class="about-type">
    <h2>About {esc(ty)} pearls</h2>
    <p>{esc(TYPE_TEXT[p['y']])}</p>
    <p class="note">Every lot is graded on lustre, surface, shape, size and matching, and ships with a grading note and real photos. <a href="/#pearls">Compare pearl types</a> · <a href="/#process">How an order runs</a></p>
  </section>
  <section class="related">
    <h2>Similar items</h2>
    <div class="grid">{related(p)}</div>
    <p style="margin-top:18px"><a class="btn ghost" style="display:inline-flex" href="/products/">See all 165 items</a></p>
  </section>
</div>
</main>
{footer}
<script>
(function(){{
  var KEY='tq-inq',c='{p['c']}',b=document.getElementById('add'),list=[];
  try{{list=JSON.parse(localStorage.getItem(KEY)||'[]')||[]}}catch(e){{}}
  function sync(){{var on=list.indexOf(c)>-1;b.setAttribute('aria-pressed',String(on));b.textContent=on?'✓ Added — view list in catalogue':'+ Add to inquiry list'}}
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


# ---------- write pages ----------
for p in PRODS:
    out = ROOT / "products" / p["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(p), encoding="utf-8")

# ---------- link catalogue cards (English catalogue) to the item pages ----------
cat = CAT_PAGE.read_text(encoding="utf-8")
for p in PRODS:
    t = esc(p["t"]).replace("&#x27;", "'")
    pat = re.compile(r'(<span class="code">' + p["c"] + r'</span><h3>)(?!<a )(.*?)(</h3>)', re.S)
    cat = pat.sub(lambda m: f'{m.group(1)}<a href="{p["url"]}" style="color:inherit;text-decoration:none">{m.group(2)}</a>{m.group(3)}', cat, count=1)
# "full details" link inside the quick-view dialog
if 'id="pd-page"' not in cat:
    cat = cat.replace('<a class="btn ghost" id="pd-wa"', '<a class="btn ghost" id="pd-page" href="#">Full details</a><a class="btn ghost" id="pd-wa"', 1)
    cat = cat.replace("var pa=document.getElementById('pd-add'); pa.dataset.c=p.c;",
                      "var pg=document.getElementById('pd-page'); if(pg&&window.PURL)pg.href=window.PURL[p.c]||'#';\n  var pa=document.getElementById('pd-add'); pa.dataset.c=p.c;", 1)
purl = "window.PURL=" + json.dumps({p["c"]: p["url"] for p in PRODS}) + ";"
cat = re.sub(r"window\.PURL=\{.*?\};", "", cat)
cat = cat.replace("window.PRODS=", purl + "window.PRODS=", 1)
CAT_PAGE.write_text(cat, encoding="utf-8")

# ---------- sitemap ----------
sm_path = ROOT / "sitemap.xml"
sm = sm_path.read_text(encoding="utf-8")
sm = re.sub(r"\s*<url><loc>https://tianqijewelry\.com/products/tq\d{3}-[^<]*</loc>.*?</url>", "", sm, flags=re.S)
entries = "".join(f"\n  <url><loc>{BASE}{p['url']}</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>" for p in PRODS)
sm = sm.replace("</urlset>", entries + "\n</urlset>")
sm_path.write_text(sm, encoding="utf-8")

print(f"built {len(PRODS)} item pages; catalogue linked; sitemap now has {sm.count('<loc>')} URLs")
