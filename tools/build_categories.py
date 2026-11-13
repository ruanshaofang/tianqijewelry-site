#!/usr/bin/env python3
"""Build English category landing pages: site/pearls/<slug>/index.html

Each page targets one buyer search ("akoya pearls wholesale", "OEM pearl jewelry
manufacturer"...): what the pearl is, sizes/colours we supply, grading, how ordering
works, the matching catalogue items, and an FAQ. Facts come from the homepage and
catalogue; no prices or invented specs.

Also adds links to these pages from the English homepage, catalogue and product pages,
and adds the pages to sitemap.xml. Run after tools/build_products.py.
"""
import html
import json
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "site"
BASE = "https://tianqijewelry.com"
CAT_PAGE = ROOT / "products" / "index.html"
src = CAT_PAGE.read_text(encoding="utf-8")
CAT = json.loads(re.search(r"window\.CAT=(\{.*?\});window\.", src, re.S).group(1))
PRODS = json.loads(re.search(r"window\.PRODS=(\[.*?\]);", src, re.S).group(1))
PURL = json.loads(re.search(r"window\.PURL=(\{.*?\});", src, re.S).group(1))


def esc(s):
    return html.escape(str(s), quote=True)


ORDER = [
    ("Minimum order", "5 pcs per item and USD 100 per order (wholesale). OEM from 50 pcs per design"),
    ("Quote", "Within two business days, with real photos or video of the lot"),
    ("Dispatch", "In-stock lots ship from Zhuji, Zhejiang in 1–3 business days"),
    ("Delivery", "One tracking number door to door. DDP (duties paid) to the US; landed-cost quotes for the EU. Usually 9–15 days to major US and European destinations"),
    ("Samples", "Recommended before bulk; samples and their shipping are paid separately"),
    ("Payment", "T/T or PayPal. Invoiced by our Hong Kong affiliate, or by Shenzhen Tianqi on request"),
]

FAQ_COMMON = [
    ("Are these pearls natural or cultured?",
     "All our pearls are cultured, freshwater and saltwater (Akoya, South Sea, Tahitian). We do not sell imitation or shell pearls. The pearl type and any treatment are stated on the invoice."),
    ("What is the minimum order?",
     "Wholesale starts at 5 pieces per item and USD 100 per order. Custom (OEM/ODM) production starts at 50 pieces per design."),
    ("How long does shipping take, and do I pay import duty?",
     "In-stock items are processed in 1–3 business days in Zhuji. Delivery to major US and European destinations usually takes 9–15 days. US orders can ship DDP, so the buyer pays no duty on arrival; for the EU we quote landed cost."),
    ("Can I order samples first?",
     "Yes, and we recommend it for wholesale and custom orders. Samples and their shipping are paid separately, and bulk orders are checked against the approved sample."),
]

PAGES = [
    dict(slug="freshwater-pearls-wholesale", types=["freshwater"], name="Freshwater pearls",
         h1="Freshwater pearls wholesale, direct from Zhuji",
         title="Freshwater Pearls Wholesale from Zhuji, China | Loose, Strands & Jewelry | Tianqi Jewelry",
         desc="Wholesale cultured freshwater pearls from Zhuji (Shanxiahu), China: graded loose pearls, strands and finished jewelry. 2–12 mm, white, pink and lavender. From 5 pcs, DDP to the US.",
         spec=[("Origin", "Zhejiang, China — sourced and graded at Shanxiahu, Zhuji"), ("Sizes", "2–12 mm"),
               ("Colours", "White, pink, lavender"), ("Shapes", "Round, near-round, drop, button, baroque"),
               ("Supplied as", "Graded loose pearls, strands, semi-finished parts and finished jewelry")],
         body=["Freshwater pearls are cultured in mussels in Zhejiang. Our sourcing and dispatch team works at Shanxiahu in Zhuji, China's freshwater pearl hub, so we select, grade and match lots at the source and ship them from the same place.",
               "They come in a wide range of colours and shapes, from round to baroque, and offer strong value for everyday and volume lines: stud and drop earrings, pendants, strands and ready-to-sell jewelry. We quote against lustre, surface, shape, size and matching, and every lot ships with a grading note and real photos.",
               "Looking for a specific shape? See our pages for baroque, keshi and Edison pearls, which are also freshwater."],
         faq=[("Can you match pearls into pairs or strands?", "Yes. Matching is one of the five factors we grade on: we check consistency of colour, lustre and size across a strand or pair, and strands list end-to-centre sizes in 0.5 mm steps.")]),
    dict(slug="baroque-pearls-wholesale", types=["baroque"], name="Baroque pearls",
         h1="Baroque pearls wholesale",
         title="Baroque Pearls Wholesale | Freshwater Baroque Loose Pearls & Jewelry | Tianqi Jewelry",
         desc="Wholesale freshwater baroque pearls from Zhuji, China: loose, strands, pendants and jewelry, matched by size, colour and shape. From 5 pcs, real photos before you pay.",
         spec=[("Pearl type", "Cultured freshwater pearls with irregular, free-form shapes"), ("Origin", "Zhejiang, China — graded at Shanxiahu, Zhuji"),
               ("Supplied as", "Loose pearls, strands, pendants, necklaces and finished pieces"), ("Matching", "By size, colour and shape for pairs and strands")],
         body=["Baroque pearls have an irregular, free-form shape, so every piece is slightly different. That individuality is why designers use them for contemporary and handmade jewelry, from statement pendants to asymmetric earrings.",
               "Because no two are alike, consistency matters when you buy in volume. We sort baroque lots by size, colour, lustre and shape, match pairs and strands to your brief, and send real photos or video of the pearls you will actually receive before you pay."],
         faq=[("Will the pearls look exactly like the catalogue photo?", "Catalogue photos show typical lots. Each baroque pearl is unique, so before you pay we send photos or video of the actual pearls, and bulk orders are checked against the approved sample.")]),
    dict(slug="keshi-pearls-wholesale", types=["keshi"], name="Keshi & biwa pearls",
         h1="Keshi and biwa pearls wholesale",
         title="Keshi Pearls Wholesale | Keshi & Biwa Loose Pearls | Tianqi Jewelry",
         desc="Wholesale keshi and biwa pearls from Zhuji, China: high-lustre, organic shapes for earrings, pendants and charms. Loose and finished. From 5 pcs, DDP to the US.",
         spec=[("Pearl type", "Keshi: cultured pearls that form without a bead nucleus. Biwa: flat, elongated freshwater pearls"),
               ("Origin", "Zhejiang, China — graded at Shanxiahu, Zhuji"), ("Supplied as", "Loose pearls, pairs, strands and pendants")],
         body=["Keshi pearls form without a bead nucleus, so they are solid nacre with a high lustre and an organic, irregular shape. Biwa pearls are flat, elongated freshwater pearls with a distinctive profile.",
               "Both suit distinctive earrings, pendants and charms. We match keshi pairs for earrings and sort lots by size, lustre and colour so your designs stay consistent from sample to bulk order."],
         faq=[("Do keshi pearls have a bead inside?", "No. Keshi pearls form without a bead nucleus, which is why they are solid nacre and have a strong lustre.")]),
    dict(slug="edison-pearls-wholesale", types=["edison"], name="Edison pearls",
         h1="Edison pearls wholesale",
         title="Edison Pearls Wholesale | Large Round Freshwater Pearls | Tianqi Jewelry",
         desc="Wholesale Edison pearls from Zhuji, China: large, round, bead-nucleated freshwater pearls with strong lustre and metallic colours. Loose, strands and jewelry. From 5 pcs.",
         spec=[("Pearl type", "Bead-nucleated cultured freshwater pearls"), ("Origin", "Zhejiang, China — graded at Shanxiahu, Zhuji"),
               ("Character", "Larger and rounder than most freshwater pearls, strong lustre, metallic colours"),
               ("Supplied as", "Loose pearls, strands, pendants, bracelets and necklaces")],
         body=["Edison pearls are bead-nucleated freshwater pearls developed in Zhejiang. They grow larger and rounder than most freshwater pearls, with a strong lustre and metallic colours.",
               "That makes them a popular choice when buyers want the look of a large round pearl at freshwater pricing, for strands, studs and solitaire pendants. We grade each lot on lustre, surface, shape, size and matching."],
         faq=[("How are Edison pearls different from other freshwater pearls?", "Edison pearls are bead-nucleated, so they grow larger and rounder than most freshwater pearls, with a strong lustre and metallic colours.")]),
    dict(slug="akoya-pearls-wholesale", types=["akoya"], name="Akoya pearls",
         h1="Akoya pearls wholesale",
         title="Akoya Pearls Wholesale | Akoya Strands & Earrings | Tianqi Jewelry",
         desc="Wholesale cultured Akoya pearls: sharp lustre, round shape, 2–10 mm, white, silver-blue and rosé. Strands, matched earrings and loose pearls. From 5 pcs, DDP to the US.",
         spec=[("Pearl type", "Cultured saltwater pearls"), ("Origin", "Japan · China"), ("Sizes", "2–10 mm"),
               ("Colours", "White, silver-blue, rosé"), ("Supplied as", "Strands, matched earrings, loose pearls and finished jewelry")],
         body=["Akoya pearls are saltwater pearls with sharp lustre and a round shape, usually with pink or silver overtones. They are the classic choice for strands and matched earrings.",
               "Our Hong Kong office connects us to Hong Kong's saltwater pearl dealers and fairs, and we grade and match Akoya lots to your specification. The items below are a sample of what we offer; tell us the size, colour and quantity you need and we will quote with real photos or video."],
         faq=[("Which Akoya sizes can you supply?", "We supply Akoya pearls from 2 to 10 mm. Strands list end-to-centre sizes in 0.5 mm steps.")]),
    dict(slug="south-sea-pearls-wholesale", types=["southsea"], name="South Sea pearls",
         h1="South Sea pearls wholesale",
         title="South Sea Pearls Wholesale | Gold & White South Sea Pearls | Tianqi Jewelry",
         desc="Wholesale cultured South Sea pearls: thick nacre, 9–20 mm, gold, white and champagne. Loose, pendants and custom pieces. Real photos before you pay, DDP to the US.",
         spec=[("Pearl type", "Cultured saltwater pearls"), ("Origin", "Australia · Indonesia · Philippines"), ("Sizes", "9–20 mm"),
               ("Colours", "Gold, white, champagne"), ("Supplied as", "Loose pearls, pendants, rings, bracelets and custom pieces")],
         body=["South Sea pearls are saltwater pearls with thick nacre and large sizes, in gold and white. They suit high-value pieces and custom work.",
               "We source South Sea pearls through Hong Kong's saltwater pearl dealers and fairs. Because each pearl is a significant purchase, we send photos or video of the exact pearls before you pay, and high-value items are handled individually if anything goes wrong after delivery."],
         faq=[("What happens if a high-value pearl arrives damaged?", "Send us photos or a video after delivery. High-value items are returned and handled individually.")]),
    dict(slug="tahitian-pearls-wholesale", types=["tahitian"], name="Tahitian pearls",
         h1="Tahitian pearls wholesale",
         title="Tahitian Pearls Wholesale | Black Tahitian Pearls | Tianqi Jewelry",
         desc="Wholesale cultured Tahitian pearls from French Polynesia: naturally dark, 8–16 mm, peacock, grey and aubergine. Loose, necklaces, earrings and rings. From 5 pcs.",
         spec=[("Pearl type", "Cultured saltwater pearls"), ("Origin", "French Polynesia"), ("Sizes", "8–16 mm"),
               ("Colours", "Peacock, grey, aubergine"), ("Supplied as", "Loose pearls, necklaces, earrings and rings")],
         body=["Tahitian pearls from French Polynesia are naturally dark, with peacock-green and aubergine overtones. They work for both men's and women's designs.",
               "We source Tahitian pearls through Hong Kong's saltwater pearl dealers and fairs and grade them on lustre, surface, shape, size and matching. Tell us the size, overtone and quantity you need and we will quote with real photos or video."],
         faq=[("Are Tahitian pearls dyed?", "Tahitian pearls are naturally dark. The pearl type and any treatment are always stated on the invoice.")]),
]

OEM = dict(slug="oem-pearl-jewelry-manufacturer", name="OEM / ODM pearl jewelry",
           h1="OEM & ODM pearl jewelry manufacturer",
           title="OEM Pearl Jewelry Manufacturer in China | Custom Pearl Jewelry, Your Logo | Tianqi Jewelry",
           desc="Custom pearl jewelry made to your design, with your logo and packaging. From 50 pcs per design, samples in 7–10 business days, bulk 2–4 weeks after approval. Zhuji, China.")


def card(p):
    return (f'<a class="card" href="{PURL[p["c"]]}"><img src="/assets/products/{p["i"][0]}-t.webp" alt="{esc(p["t"])}" loading="lazy" decoding="async" width="480" height="480">'
            f'<div class="meta"><span class="code">{p["c"]}</span><h3>{esc(p["t"])}</h3><span class="ty">{esc(CAT["cats"][p["k"]])}</span></div></a>')


src_head = src[src.find("<head>") + 6:src.find("</head>")]
for pat in [r"<title>.*?</title>", r'<meta name="description"[^>]*>', r'<link rel="canonical"[^>]*>',
            r'<link rel="alternate"[^>]*>', r'<meta property="og:[^>]*>', r'<meta name="twitter:[^>]*>',
            r'<script type="application/ld\+json">.*?</script>']:
    src_head = re.sub(pat, "", src_head, flags=re.S)
HEAD = re.sub(r"\n\s*\n+", "\n", src_head)
HEADER = re.sub(r'href="(/[a-z]{2})?/products/"(?= hreflang=)', lambda m: f'href="{m.group(1) or ""}/"', src[src.find("<header"):src.find("</header>") + 9]).replace(' aria-current="page"', "")
FOOTER = src[src.find("<footer"):src.find("</footer>") + 9]

CSS = """<style>
.crumbs{font-size:.8125rem;color:var(--muted);padding-block:22px 6px}.crumbs a{color:var(--muted)}
.lp-hero{padding-block:14px 26px;max-width:78ch}.lp-hero h1{margin:6px 0 14px;line-height:1.15}
.lp-hero p{color:var(--ink-2,#3b4a4f);font-size:1.02rem;line-height:1.65;margin:0 0 12px}
.lp-grid{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:36px;align-items:start;padding-block:6px 30px}
@media (max-width:860px){.lp-grid{grid-template-columns:1fr;gap:18px}}
.facts{width:100%;border-collapse:collapse;font-size:.92rem;background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.facts th,.facts td{text-align:start;padding:10px 14px;border-bottom:1px solid var(--line);vertical-align:top}
.facts tr:last-child th,.facts tr:last-child td{border-bottom:0}
.facts th{width:36%;color:var(--muted);font-weight:500}
.lp h2{font-size:var(--s2,1.35rem);margin:30px 0 12px}
.lp .note{color:var(--muted);font-size:.9rem}
.lp-cta{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0 6px}.lp-cta .btn{display:inline-flex}
.items{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:14px}
.items a.card{text-decoration:none;color:inherit}
.faq details{border-bottom:1px solid var(--line);padding:12px 0}.faq summary{cursor:pointer;font-weight:600}
.faq p{margin:8px 0 0;color:var(--ink-2,#3b4a4f);line-height:1.6}
.types-nav{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 40px}
.types-nav a{font-size:.85rem;border:1px solid var(--line);border-radius:999px;padding:5px 12px;text-decoration:none;color:var(--ink);background:var(--surface)}
.types-nav a[aria-current="page"]{background:var(--accent);color:var(--on-accent);border-color:var(--accent)}
.lp-steps{counter-reset:s;list-style:none;padding:0;display:grid;gap:10px}
.lp-steps li{counter-increment:s;padding-inline-start:38px;position:relative;line-height:1.55}
.lp-steps li::before{content:counter(s);position:absolute;inset-inline-start:0;top:0;width:26px;height:26px;border-radius:50%;background:var(--accent);color:var(--on-accent);display:grid;place-items:center;font-size:.8rem;font-weight:600}
</style>"""


def types_nav(current):
    allp = PAGES + [OEM]
    return '<nav class="types-nav" aria-label="Pearl types">' + "".join(
        f'<a href="/pearls/{q["slug"]}/"{" aria-current=\"page\"" if q["slug"] == current else ""}>{esc(q["name"])}</a>' for q in allp) + "</nav>"


def faq_html(items):
    return '<div class="faq">' + "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in items) + "</div>"


def wa(msg):
    return "https://wa.me/85251659258?text=" + esc(urllib.parse.quote(msg))


def shell(pg, main, ld):
    canon = f"{BASE}/pearls/{pg['slug']}/"
    return f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<title>{esc(pg['title'])}</title>
<meta name="description" content="{esc(pg['desc'])}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(pg['h1'])} — Tianqi Jewelry">
<meta property="og:description" content="{esc(pg['desc'])}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{pg.get('og', BASE + '/assets/og-image.jpg')}">
<meta property="og:site_name" content="Tianqi Jewelry">
<meta name="twitter:card" content="summary_large_image">
{HEAD}
{CSS}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
{HEADER}
<main id="top" class="lp">
<div class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/#pearls">Pearls</a> / {esc(pg['name'])}</nav>
{main}
  {types_nav(pg['slug'])}
</div>
</main>
{FOOTER}
</body>
</html>
"""


def ld_for(pg, faqs, items=None):
    canon = f"{BASE}/pearls/{pg['slug']}/"
    graph = [
        {"@type": "CollectionPage" if items is not None else "WebPage", "@id": canon, "url": canon, "name": pg["h1"],
         "description": pg["desc"], "isPartOf": {"@id": f"{BASE}/#site"}, "about": pg["name"],
         "provider": {"@id": f"{BASE}/#org"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Pearls", "item": BASE + "/#pearls"},
            {"@type": "ListItem", "position": 3, "name": pg["name"], "item": canon}]},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]},
    ]
    if items:
        graph[0]["mainEntity"] = {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": BASE + PURL[p["c"]], "name": p["t"]} for i, p in enumerate(items)]}
    return {"@context": "https://schema.org", "@graph": graph}


def type_page(pg):
    items = [p for p in PRODS if p["y"] in pg["types"]]
    if items:
        pg["og"] = f"{BASE}/assets/products/{items[0]['i'][0]}.webp"
    faqs = pg["faq"] + FAQ_COMMON
    spec = "".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in pg["spec"])
    order = "".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in ORDER)
    body = "".join(f"<p>{esc(x)}</p>" for x in pg["body"])
    msg = f"Hello Tianqi Jewelry, I'm interested in wholesale {pg['name'].lower()}.\nSize / quality: \nQuantity: \nDestination country: \n\n{BASE}/pearls/{pg['slug']}/"
    main = f"""  <section class="lp-hero">
    <span class="eyebrow">Wholesale · OEM · Dropship</span>
    <h1>{esc(pg['h1'])}</h1>
    {body}
    <div class="lp-cta"><a class="btn" href="/#inquiry">Ask for wholesale pricing</a><a class="btn ghost" href="{wa(msg)}" target="_blank" rel="noopener">WhatsApp us</a></div>
  </section>
  <section class="lp-grid">
    <div><h2 style="margin-top:0">What we supply</h2><table class="facts"><tbody>{spec}</tbody></table></div>
    <div><h2 style="margin-top:0">How ordering works</h2><table class="facts"><tbody>{order}</tbody></table></div>
  </section>
  <section>
    <h2>{esc(pg['name'])} in our catalogue ({len(items)} items)</h2>
    <p class="note">Catalogue photos show typical lots. Before you pay, we send photos or video of the pearls you will actually receive. More lots are available on request.</p>
    <div class="items">{''.join(card(p) for p in items)}</div>
  </section>
  <section>
    <h2>How we grade</h2>
    <table class="facts"><tbody>
      <tr><th>Lustre</th><td>How sharp and bright the reflection is</td></tr>
      <tr><th>Surface</th><td>Number and placement of spots, pits and lines</td></tr>
      <tr><th>Shape</th><td>Round, near-round, drop, button, baroque</td></tr>
      <tr><th>Size</th><td>In 0.5 mm steps; strands list end-to-centre sizes</td></tr>
      <tr><th>Matching</th><td>Consistency of colour, lustre and size across a strand or pair</td></tr>
    </tbody></table>
    <p class="note">Each lot ships with a grading note and real photos. Bulk production starts after you approve the sample.</p>
  </section>
  <section>
    <h2>Questions buyers ask</h2>
    {faq_html(faqs)}
    <div class="lp-cta"><a class="btn" href="/#inquiry">Send an inquiry</a><a class="btn ghost" href="/products/">Browse the full catalogue</a></div>
  </section>"""
    return shell(pg, main, ld_for(pg, faqs, items))


def oem_page(pg):
    faqs = [
        ("What is the minimum order for custom pearl jewelry?", "50 pieces per design for OEM/ODM production."),
        ("How long do samples and bulk production take?", "Samples take 7–10 business days and the sample fee is paid separately. Bulk production takes 2–4 weeks after you approve the sample."),
        ("Can you add our logo and packaging?", "Yes. We sample and produce from your drawings or references, with your logo and packaging."),
    ] + FAQ_COMMON[0:1] + FAQ_COMMON[2:3]
    msg = f"Hello Tianqi Jewelry, I'd like to discuss custom (OEM/ODM) pearl jewelry.\nDesign / reference: \nQuantity per design: \nTarget price: \nDestination country: \n\n{BASE}/pearls/{pg['slug']}/"
    main = f"""  <section class="lp-hero">
    <span class="eyebrow">OEM · ODM · Private label</span>
    <h1>{esc(pg['h1'])}</h1>
    <p>We sample and produce pearl jewelry from your drawings or references, with your logo and packaging. Pearls are selected, graded and matched at Shanxiahu in Zhuji, China's freshwater pearl hub, and saltwater pearls come through Hong Kong's pearl dealers and fairs, so one team handles the pearls, the production and the export.</p>
    <p>Typical projects are earrings, pendants, necklaces, strands, bracelets and rings for jewelry brands and online sellers in North America, Europe and Southeast Asia.</p>
    <div class="lp-cta"><a class="btn" href="/#inquiry">Send a custom brief</a><a class="btn ghost" href="{wa(msg)}" target="_blank" rel="noopener">WhatsApp us</a></div>
  </section>
  <section class="lp-grid">
    <div><h2 style="margin-top:0">Terms</h2><table class="facts"><tbody>
      <tr><th>Minimum order</th><td>50 pcs per design</td></tr>
      <tr><th>Sample</th><td>7–10 business days; sample fee paid separately</td></tr>
      <tr><th>Bulk production</th><td>2–4 weeks after sample approval</td></tr>
      <tr><th>Branding</th><td>Your logo and packaging</td></tr>
      <tr><th>Pearls</th><td>Cultured freshwater and saltwater (Akoya, South Sea, Tahitian); type and any treatment stated on the invoice</td></tr>
      <tr><th>Delivery</th><td>One tracking number door to door; DDP to the US, landed-cost quotes for the EU</td></tr>
      <tr><th>Payment</th><td>T/T or PayPal; invoiced by our Hong Kong affiliate, or by Shenzhen Tianqi on request</td></tr>
    </tbody></table></div>
    <div><h2 style="margin-top:0">How a custom order runs</h2><ol class="lp-steps">
      <li><strong>Brief.</strong> Send drawings or references, pearl type and size, quantity and target price.</li>
      <li><strong>Quote and sample.</strong> We quote with real photos or video within two business days, then make the sample in 7–10 business days.</li>
      <li><strong>Approve.</strong> You approve the sample; we issue a proforma invoice.</li>
      <li><strong>Produce and inspect.</strong> Bulk production in 2–4 weeks, checked against the approved sample.</li>
      <li><strong>Ship and support.</strong> Shipped from Zhuji with tracking; any issue is resolved from your photos.</li>
    </ol></div>
  </section>
  <section>
    <h2>Pearls we work with</h2>
    <p>Choose the pearl first, then the design: <a href="/pearls/freshwater-pearls-wholesale/">freshwater</a>, <a href="/pearls/baroque-pearls-wholesale/">baroque</a>, <a href="/pearls/keshi-pearls-wholesale/">keshi</a>, <a href="/pearls/edison-pearls-wholesale/">Edison</a>, <a href="/pearls/akoya-pearls-wholesale/">Akoya</a>, <a href="/pearls/south-sea-pearls-wholesale/">South Sea</a> and <a href="/pearls/tahitian-pearls-wholesale/">Tahitian</a>. Our <a href="/products/">catalogue</a> shows 165 current items you can use as a starting point.</p>
  </section>
  <section>
    <h2>Questions buyers ask</h2>
    {faq_html(faqs)}
    <div class="lp-cta"><a class="btn" href="/#inquiry">Send a custom brief</a></div>
  </section>"""
    return shell(pg, main, ld_for(pg, faqs))


for pg in PAGES:
    out = ROOT / "pearls" / pg["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(type_page(pg), encoding="utf-8")
out = ROOT / "pearls" / OEM["slug"] / "index.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(oem_page(OEM), encoding="utf-8")

# ---------- internal links (English) ----------
LINKROW = ('<p class="lp-links" style="margin-top:18px;font-size:.9rem">Wholesale pages: ' + " · ".join(
    f'<a href="/pearls/{q["slug"]}/">{esc(q["name"])}</a>' for q in PAGES + [OEM]) + "</p>")
home = (ROOT / "index.html").read_text(encoding="utf-8")
home = re.sub(r'<p class="lp-links".*?</p>', "", home, flags=re.S)
i = home.find('id="pearls"')
j = home.find("</section>", i)
home = home[:j] + LINKROW + home[j:]
(ROOT / "index.html").write_text(home, encoding="utf-8")

cat = CAT_PAGE.read_text(encoding="utf-8")
cat = re.sub(r'<p class="lp-links".*?</p>', "", cat, flags=re.S)
cat = cat.replace('<div class="cat-notes">', LINKROW + '<div class="cat-notes">', 1)
CAT_PAGE.write_text(cat, encoding="utf-8")

TYPE2SLUG = {t: pg["slug"] for pg in PAGES for t in pg["types"]}
n = 0
for f in (ROOT / "products").glob("tq*/index.html"):
    s = f.read_text(encoding="utf-8")
    s = re.sub(r' <a class="lp-type"[^>]*>.*?</a>', "", s)
    code = re.search(r'"sku": "([A-Z0-9]+)"', s).group(1)
    p = next(q for q in PRODS if q["c"] == code)
    link = f' <a class="lp-type" href="/pearls/{TYPE2SLUG[p["y"]]}/">More about wholesale {esc(CAT["types"][p["y"]])} pearls →</a>'
    s = re.sub(r'(<section class="about-type">\s*<h2>.*?</h2>\s*<p>.*?)(</p>)', lambda m: m.group(1) + link + m.group(2), s, count=1, flags=re.S)
    f.write_text(s, encoding="utf-8")
    n += 1

# ---------- sitemap ----------
sm_path = ROOT / "sitemap.xml"
sm = sm_path.read_text(encoding="utf-8")
sm = re.sub(r"\s*<url><loc>https://tianqijewelry\.com/pearls/[^<]*</loc>.*?</url>", "", sm, flags=re.S)
sm = sm.replace("</urlset>", "".join(f"\n  <url><loc>{BASE}/pearls/{q['slug']}/</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>" for q in PAGES + [OEM]) + "\n</urlset>")
sm_path.write_text(sm, encoding="utf-8")
print(f"built {len(PAGES) + 1} category pages; linked from homepage, catalogue and {n} product pages; sitemap {sm.count('<loc>')} URLs")
