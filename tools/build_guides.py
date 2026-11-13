#!/usr/bin/env python3
"""Build English buyer guides: site/guides/<slug>/index.html and the index site/guides/index.html

Guides answer the questions wholesale buyers search before they order (grading, sizes,
freshwater vs saltwater, importing, samples, origin). Each guide ends with an inquiry
call to action. Facts come from the homepage, catalogue and landing pages; no prices.

Also adds a "Buyer guides" link row to the English homepage, the guides to sitemap.xml,
and a link from the category pages' grading section. Safe to run repeatedly.
Run after tools/build_categories.py.
"""
import html
import json
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "site"
BASE = "https://tianqijewelry.com"
src = (ROOT / "products" / "index.html").read_text(encoding="utf-8")


def esc(s):
    return html.escape(str(s), quote=True)


head = src[src.find("<head>") + 6:src.find("</head>")]
for pat in [r"<title>.*?</title>", r'<meta name="description"[^>]*>', r'<link rel="canonical"[^>]*>',
            r'<link rel="alternate"[^>]*>', r'<meta property="og:[^>]*>', r'<meta name="twitter:[^>]*>',
            r'<script type="application/ld\+json">.*?</script>']:
    head = re.sub(pat, "", head, flags=re.S)
HEAD = re.sub(r"\n\s*\n+", "\n", head)
HEADER = re.sub(r'href="(/[a-z]{2})?/products/"(?= hreflang=)', lambda m: f'href="{m.group(1) or ""}/"',
                src[src.find("<header"):src.find("</header>") + 9]).replace(' aria-current="page"', "")
FOOTER = src[src.find("<footer"):src.find("</footer>") + 9]

CSS = """<style>
.crumbs{font-size:.8125rem;color:var(--muted);padding-block:22px 6px}.crumbs a{color:var(--muted)}
.guide{max-width:78ch;padding-bottom:40px}
.guide h1{margin:6px 0 14px;line-height:1.15}
.guide h2{font-size:var(--s2,1.35rem);margin:34px 0 12px}
.guide h3{font-size:1.05rem;margin:22px 0 8px}
.guide p,.guide li{line-height:1.7;color:var(--ink-2,#3b4a4f)}
.guide p{margin:0 0 14px}.guide ul{margin:0 0 14px;padding-inline-start:22px}
.guide .lead{font-size:1.05rem}
.guide .meta{color:var(--muted);font-size:.85rem;margin:0 0 18px}
.guide .toc{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 18px;margin:18px 0}
.guide .toc ol{margin:6px 0 0;padding-inline-start:20px}.guide .toc li{line-height:1.6}
.gtable{width:100%;border-collapse:collapse;font-size:.9rem;background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:8px 0}
.gtable th,.gtable td{text-align:start;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
.gtable thead th{color:var(--muted);font-weight:500}
.gtable tr:last-child td,.gtable tr:last-child th{border-bottom:0}
.gscroll{overflow-x:auto}.gscroll .gtable{min-width:680px}
.guide h2{scroll-margin-top:90px}
.spec{background:var(--surface);border:1px solid var(--line);border-inline-start:4px solid var(--accent);border-radius:10px;padding:14px 16px;font-family:var(--f-mono,monospace);font-size:.85rem;line-height:1.7;white-space:pre-wrap}
.lp-cta{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0 6px}.lp-cta .btn{display:inline-flex}
.faq details{border-bottom:1px solid var(--line);padding:12px 0}.faq summary{cursor:pointer;font-weight:600}
.faq p{margin:8px 0 0}
.glist{list-style:none;padding:0;display:grid;gap:14px;max-width:78ch}
.glist a{display:block;padding:16px 18px;border:1px solid var(--line);border-radius:12px;background:var(--surface);text-decoration:none;color:inherit}
.glist strong{display:block;margin-bottom:4px}.glist span{color:var(--muted);font-size:.92rem}
</style>"""


def wa(msg):
    return "https://wa.me/85251659258?text=" + esc(urllib.parse.quote(msg))


def faq_html(items):
    return '<div class="faq">' + "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in items) + "</div>"


def page(canon, title, desc, og_title, crumbs, main, ld):
    return f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(og_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}/assets/og-image.jpg">
<meta property="og:site_name" content="Tianqi Jewelry">
<meta name="twitter:card" content="summary_large_image">
{HEAD}
{CSS}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
{HEADER}
<main id="top">
<div class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>
{main}
</div>
</main>
{FOOTER}
</body>
</html>
"""


# ---------------------------------------------------------------- guides
GUIDES = []

# ---- 1. Pearl grading ----
G1_FAQ = [
    ("Is there an official pearl grading standard?",
     "There is no single international letter scale. Laboratories and national standards grade separate quality factors instead: GIA uses seven value factors, and China's national standard GB/T 18781-2023 \"Pearl grading\" covers colour, size, shape, lustre, surface, nacre thickness and matching. Letter grades such as AAA are trade shorthand that each supplier defines for itself."),
    ("What does AAA mean when a supplier uses it?",
     "Whatever that supplier says it means. One supplier's AAA can be another's AA. Ask the supplier to describe each grade in terms of lustre, surface, shape, size and matching, and compare samples photographed under the same light."),
    ("Which factors move the price most?",
     "Size and lustre usually have the largest effect, followed by surface and shape. Close matching adds cost too, because more pearls have to be sorted to build each pair or strand."),
    ("How do I check quality before I pay?",
     "Ask for photos and a short video of the actual lot, in daylight or under a plain white light, with the pearls rolled so you see the whole surface. For wholesale and custom orders, approve a paid sample first and have the bulk order checked against it."),
    ("Can I get a third-party test report?",
     "Yes, on request. Tell us when you send your inquiry and we will arrange it with the order details the laboratory needs."),
]

G1_MAIN = f"""  <article class="guide">
    <span class="eyebrow">Buyer guide</span>
    <h1>Pearl grading for wholesale buyers: the five factors to put in your spec</h1>
    <p class="meta">Tianqi Jewelry · Shanxiahu, Zhuji · Updated 13 November 2026</p>
    <p class="lead">Two lots labelled "AAA" from two suppliers can look very different. There is no single international letter scale for pearls: A–AAA (or A–D) is trade shorthand, and each supplier sets its own line between the letters.</p>
    <p>Laboratories and national standards grade separate quality factors instead. GIA uses seven value factors, and China's national standard GB/T 18781-2023 <em>Pearl grading</em> covers colour, size, shape, lustre, surface, nacre thickness and matching. For a buyer the practical answer is the same: describe each factor in your request for quote, and approve a sample before bulk.</p>
    <p>This guide explains the five factors we quote against at our sourcing base in Shanxiahu, Zhuji — <strong>lustre, surface, shape, size and matching</strong> — plus colour and nacre, and shows how to write them into a spec.</p>
    <nav class="toc" aria-label="Contents"><strong>Contents</strong><ol>
      <li><a href="#at-a-glance">The five factors at a glance</a></li>
      <li><a href="#lustre">Lustre</a></li><li><a href="#surface">Surface</a></li><li><a href="#shape">Shape</a></li>
      <li><a href="#size">Size</a></li><li><a href="#matching">Matching</a></li>
      <li><a href="#colour-nacre">Colour and nacre</a></li>
      <li><a href="#letter-grades">What to do with letter grades</a></li>
      <li><a href="#write-a-spec">How to write a pearl spec</a></li>
      <li><a href="#how-we-grade">How we grade at Tianqi</a></li>
      <li><a href="#faq">Questions buyers ask</a></li>
    </ol></nav>

    <h2 id="at-a-glance">The five factors at a glance</h2>
    <div class="gscroll"><table class="gtable">
      <thead><tr><th>Factor</th><th>What it describes</th><th>How to write it in a spec</th><th>How to check it on photos</th></tr></thead>
      <tbody>
        <tr><th>Lustre</th><td>How bright and sharp the reflection on the surface is</td><td>High / medium lustre; "reflection of a light clearly visible"</td><td>Look at the reflection of a window or lamp: crisp edges mean high lustre, a blurry or chalky glow means low</td></tr>
        <tr><th>Surface</th><td>Number, size and placement of spots, pits, lines and bumps</td><td>"Clean to the eye on most of the surface; minor marks near the drill hole accepted"</td><td>Ask for a video with the pearls rolled, so you see all sides</td></tr>
        <tr><th>Shape</th><td>Round, near-round, oval, drop, button, baroque</td><td>Name the shape; for round, say whether near-round is acceptable</td><td>Round pearls roll straight on a flat surface; near-round ones wobble</td></tr>
        <tr><th>Size</th><td>Diameter in millimetres</td><td>A 0.5 mm range, e.g. 7.0–7.5 mm; for strands, end-to-centre sizes</td><td>Ask for a caliper reading in the photo, not a ruler</td></tr>
        <tr><th>Matching</th><td>How consistent colour, lustre, size and shape are across a pair or strand</td><td>"Matched pairs" or "strand uniform within 0.5 mm"</td><td>Photograph the whole pair or strand together on a neutral background</td></tr>
      </tbody>
    </table></div>

    <h2 id="lustre">Lustre</h2>
    <p>Lustre is the light a pearl reflects from its surface and from just below it. High-lustre pearls show a bright, sharp reflection, almost like a mirror; low-lustre pearls look soft or chalky. Many buyers see lustre as the factor that makes a pearl look "alive", and it is the first thing end customers notice.</p>
    <p>Lustre is hard to judge from retouched or over-lit photos. Ask for pictures in daylight or under a plain white light, with a recognisable object reflected on the pearls.</p>

    <h2 id="surface">Surface</h2>
    <p>Pearls grow in a living animal, so almost every pearl has some marks: small spots, pits, wrinkles, growth lines or bumps. Surface grading is about how many there are, how large and how visible they are, and where they sit. A mark next to the drill hole or under a setting matters far less than one on the face of a stud earring.</p>
    <p>Tell your supplier how the pearls will be used. For studs, the visible face must be clean; for strands, marks spread around the pearl are more noticeable; for set pendants, one clean side may be enough.</p>

    <h2 id="shape">Shape</h2>
    <p>Shapes run from round and near-round through oval, drop and button to baroque (free-form). Perfectly round pearls are the rarest, so they cost the most. Drop and button shapes suit earrings and pendants, and <a href="/pearls/baroque-pearls-wholesale/">baroque pearls</a> are popular in contemporary designs because every piece is different.</p>
    <p>For round pearls, say whether near-round is acceptable. For baroque, describe the look you want and approve a sample, because a single word covers a very wide range.</p>

    <h2 id="size">Size</h2>
    <p>Size is the diameter in millimetres, quoted in 0.5 mm steps (for example 7.0–7.5 mm). Strands are graduated or uniform: a graduated strand lists end-to-centre sizes, such as 6–9 mm. Larger pearls take longer to grow and cost more, often sharply more at the top of each pearl type's range.</p>
    <p>Typical ranges: <a href="/pearls/freshwater-pearls-wholesale/">freshwater</a> 2–12 mm, <a href="/pearls/akoya-pearls-wholesale/">Akoya</a> 2–10 mm, <a href="/pearls/tahitian-pearls-wholesale/">Tahitian</a> 8–16 mm and <a href="/pearls/south-sea-pearls-wholesale/">South Sea</a> 9–20 mm.</p>

    <h2 id="matching">Matching</h2>
    <p>Matching is how consistent pearls are when they sit together: colour, overtone, lustre, size and shape across a pair of earrings or a strand. It is what makes a strand look like one piece rather than a mix. Close matching takes time and a larger pool of pearls to choose from, which is one reason sourcing at the origin helps.</p>
    <p>If you sell pairs or strands, put matching in the spec explicitly. Otherwise each pearl may be in range on its own and still not look right next to its partner.</p>

    <h2 id="colour-nacre">Colour and nacre</h2>
    <p><strong>Colour</strong> combines body colour (white, pink, lavender, gold, dark), overtone (the tint on top, such as pink or silver) and, on some pearls, orient — a shimmer of colours. Specify the body colour and overtone you want, and whether the colour must be natural. We state the pearl type and any treatment on the invoice.</p>
    <p><strong>Nacre</strong> is the layered material that makes up the pearl. <a href="/pearls/akoya-pearls-wholesale/">Akoya</a>, <a href="/pearls/south-sea-pearls-wholesale/">South Sea</a>, <a href="/pearls/tahitian-pearls-wholesale/">Tahitian</a> and <a href="/pearls/edison-pearls-wholesale/">Edison</a> pearls grow around a bead, so the thickness of the nacre over the bead matters for durability and lustre. Most freshwater pearls, and <a href="/pearls/keshi-pearls-wholesale/">keshi</a> pearls, form without a bead and are almost entirely nacre.</p>

    <h2 id="letter-grades">What to do with letter grades</h2>
    <p>Letter grades are fine as a shorthand once you and your supplier agree on what they mean. Before you rely on them:</p>
    <ul>
      <li>Ask the supplier to describe each letter in terms of the five factors above.</li>
      <li>When you compare suppliers, compare samples or photos taken under the same light, not the letters.</li>
      <li>Keep the approved sample. It is the reference for every later order.</li>
    </ul>

    <h2 id="write-a-spec">How to write a pearl spec</h2>
    <p>A good request for quote states each factor, the quantity and how the pearls will be used. For example:</p>
    <div class="spec">Pearl type: cultured freshwater, natural colour
Shape: round (near-round acceptable)
Size: 7.0–7.5 mm
Colour: white body, pink overtone
Lustre: high — sharp reflection
Surface: clean to the eye on the face; minor marks near the drill hole accepted
Matching: matched in pairs (colour, lustre, size)
Drilling: half-drilled, for stud earrings
Quantity: 200 pairs
Delivery: Los Angeles, USA (DDP)</div>
    <p>Not sure about one of the lines? Leave it open and tell us how the pearls will be used; we will suggest what fits your price range and show you photos.</p>

    <h2 id="how-we-grade">How we grade at Tianqi</h2>
    <p>Our sourcing and dispatch team works at Shanxiahu in Zhuji, China's freshwater pearl hub, and our Hong Kong office connects us to the city's saltwater pearl dealers and fairs. Every quote states lustre, surface, shape, size and matching, and every lot ships with a grading note.</p>
    <ul>
      <li>Before you pay, we send real photos or video of the pearls you will actually receive.</li>
      <li>For wholesale and custom orders we recommend a sample first; samples and their shipping are paid separately.</li>
      <li>Bulk orders are checked against the sample you approved.</li>
    </ul>
    <div class="lp-cta"><a class="btn" href="/#inquiry">Send us your spec</a><a class="btn ghost" href="{wa('Hello Tianqi Jewelry, here is my pearl spec:' + chr(10) + 'Pearl type: ' + chr(10) + 'Shape: ' + chr(10) + 'Size: ' + chr(10) + 'Colour: ' + chr(10) + 'Lustre / surface: ' + chr(10) + 'Matching: ' + chr(10) + 'Quantity: ' + chr(10) + 'Destination country: ' + chr(10) + chr(10) + BASE + '/guides/pearl-grading-guide/')}" target="_blank" rel="noopener">Send it on WhatsApp</a></div>

    <h2 id="faq">Questions buyers ask</h2>
    {faq_html(G1_FAQ)}
    <div class="lp-cta"><a class="btn" href="/#inquiry">Ask for a quote</a><a class="btn ghost" href="/products/">Browse the catalogue</a></div>
  </article>"""

GUIDES.append(dict(
    slug="pearl-grading-guide",
    name="Pearl grading guide",
    h1="Pearl grading for wholesale buyers: the five factors to put in your spec",
    title="Pearl Grading Guide for Wholesale Buyers: Lustre, Surface, Shape, Size, Matching | Tianqi Jewelry",
    desc="How pearls are graded and how to write a pearl spec: lustre, surface, shape, size and matching, plus colour, nacre and what AAA really means. A buyer's guide from Shanxiahu, Zhuji.",
    blurb="Lustre, surface, shape, size and matching — what each means, how to check it on photos, and how to write it into a request for quote.",
    published="2026-11-13", faq=G1_FAQ, main=G1_MAIN))


# ---------------------------------------------------------------- build
def guide_ld(g):
    canon = f"{BASE}/guides/{g['slug']}/"
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "@id": canon + "#article", "mainEntityOfPage": canon, "headline": g["h1"],
         "description": g["desc"], "datePublished": g["published"], "dateModified": g["published"],
         "image": f"{BASE}/assets/og-image.jpg", "inLanguage": "en",
         "author": {"@id": f"{BASE}/#org"}, "publisher": {"@id": f"{BASE}/#org"}, "isPartOf": {"@id": f"{BASE}/#site"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Buyer guides", "item": BASE + "/guides/"},
            {"@type": "ListItem", "position": 3, "name": g["name"], "item": canon}]},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in g["faq"]]},
    ]}


for g in GUIDES:
    out = ROOT / "guides" / g["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    crumbs = f'<a href="/">Home</a> / <a href="/guides/">Buyer guides</a> / {esc(g["name"])}'
    out.write_text(page(f"{BASE}/guides/{g['slug']}/", g["title"], g["desc"], g["h1"] + " — Tianqi Jewelry", crumbs, g["main"], guide_ld(g)), encoding="utf-8")

# index
idx_desc = "Practical guides for jewelry brands and wholesalers buying cultured pearls from China: grading, sizes, pearl types, samples and delivery."
items = "".join(f'<li><a href="/guides/{g["slug"]}/"><strong>{esc(g["h1"])}</strong><span>{esc(g["blurb"])}</span></a></li>' for g in GUIDES)
idx_main = f"""  <section class="guide">
    <span class="eyebrow">Buyer guides</span>
    <h1>Pearl buyer guides</h1>
    <p class="lead">Practical notes for jewelry brands, wholesalers and online sellers buying cultured pearls, from our team at Shanxiahu, Zhuji. More guides are on the way.</p>
    <ul class="glist">{items}</ul>
    <div class="lp-cta"><a class="btn" href="/#inquiry">Send an inquiry</a><a class="btn ghost" href="/products/">Browse the catalogue</a></div>
  </section>"""
idx_ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "CollectionPage", "@id": f"{BASE}/guides/", "url": f"{BASE}/guides/", "name": "Pearl buyer guides", "description": idx_desc,
     "isPartOf": {"@id": f"{BASE}/#site"}, "mainEntity": {"@type": "ItemList", "itemListElement": [
         {"@type": "ListItem", "position": i + 1, "url": f"{BASE}/guides/{g['slug']}/", "name": g["h1"]} for i, g in enumerate(GUIDES)]}}]}
(ROOT / "guides" / "index.html").write_text(
    page(f"{BASE}/guides/", "Pearl Buyer Guides for Wholesale and Jewelry Brands | Tianqi Jewelry", idx_desc, "Pearl buyer guides — Tianqi Jewelry",
         '<a href="/">Home</a> / Buyer guides', idx_main, idx_ld).replace('<meta property="og:type" content="article">', '<meta property="og:type" content="website">'),
    encoding="utf-8")

# ---------- links ----------
GROW = ('<p class="guide-links" style="margin-top:6px;font-size:.9rem">Buyer guides: ' +
        " · ".join(f'<a href="/guides/{g["slug"]}/">{esc(g["name"])}</a>' for g in GUIDES) + ' · <a href="/guides/">All guides</a></p>')
home_p = ROOT / "index.html"
home = home_p.read_text(encoding="utf-8")
home = re.sub(r'<p class="guide-links".*?</p>', "", home, flags=re.S)
m = re.search(r'<p class="lp-links".*?</p>', home, flags=re.S)
if m:
    home = home[:m.end()] + GROW + home[m.end():]
    home_p.write_text(home, encoding="utf-8")

GLINK = ' <a class="guide-link" href="/guides/pearl-grading-guide/">Read our pearl grading guide →</a>'
n = 0
for f in (ROOT / "pearls").glob("*/index.html"):
    s = f.read_text(encoding="utf-8")
    s = s.replace(GLINK, "")
    s2 = s.replace("Bulk production starts after you approve the sample.</p>", "Bulk production starts after you approve the sample." + GLINK + "</p>", 1)
    if s2 != s:
        n += 1
    f.write_text(s2, encoding="utf-8")

# ---------- sitemap ----------
sm_path = ROOT / "sitemap.xml"
sm = sm_path.read_text(encoding="utf-8")
sm = re.sub(r"\s*<url><loc>https://tianqijewelry\.com/guides/[^<]*</loc>.*?</url>", "", sm, flags=re.S)
urls = [f"{BASE}/guides/"] + [f"{BASE}/guides/{g['slug']}/" for g in GUIDES]
sm = sm.replace("</urlset>", "".join(f"\n  <url><loc>{u}</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>" for u in urls) + "\n</urlset>")
sm_path.write_text(sm, encoding="utf-8")
print(f"built {len(GUIDES)} guide(s) + index; homepage link row {'added' if m else 'NOT FOUND'}; grading link on {n} category pages; sitemap {sm.count('<loc>')} URLs")
