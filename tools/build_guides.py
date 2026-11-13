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
.guide .note{color:var(--muted);font-size:.88rem}
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


# ---- 2. Pearl sizes and price ----
G2_FAQ = [
    ("Why does a 9 mm pearl cost so much more than an 8 mm pearl?",
     "Larger pearls need longer in the mollusc, and fewer of them grow clean and well shaped. So price rises faster than size, and the steps get steeper near the top of each pearl type's size range."),
    ("How are non-round pearls measured?",
     "Round and near-round pearls are measured across the diameter. Drop, oval, button and baroque pearls are usually given as length × width in millimetres."),
    ("How many pearls are in a 16-inch strand?",
     "Divide the length by the pearl size: about 406 mm ÷ 7 mm ≈ 58 pearls for a 7–7.5 mm strand. Knots between pearls and the clasp reduce the count slightly."),
    ("What size should I choose for stud earrings?",
     "It depends on your customers and price point. Many retail lines use 6–8 mm for everyday studs and go larger for statement pieces. Tell us your target price and we will suggest sizes and grades that fit."),
    ("Do you sell by piece, by strand or by weight?",
     "Our catalogue lists items per piece, pair or strand, with a minimum of 5 pcs per item and USD 100 per order. Prices depend on grade, size and quantity, and we quote each request with real photos."),
]

G2_ROWS = [(3, 135, 152), (4, 102, 114), (5, 81, 91), (6, 68, 76), (7, 58, 65), (8, 51, 57), (9, 45, 51), (10, 41, 46), (12, 34, 38)]

G2_MAIN = f"""  <article class="guide">
    <span class="eyebrow">Buyer guide</span>
    <h1>Pearl sizes and price: how millimetres change what you pay</h1>
    <p class="meta">Tianqi Jewelry · Shanxiahu, Zhuji · Updated 13 November 2026</p>
    <p class="lead">Size is the easiest pearl factor to specify and one of the biggest drivers of price. This guide explains how pearls are measured, the size ranges of each pearl type, how many pearls go into a strand, and how to balance size against quality within a budget.</p>
    <nav class="toc" aria-label="Contents"><strong>Contents</strong><ol>
      <li><a href="#measuring">How pearl size is measured</a></li>
      <li><a href="#ranges">Size ranges by pearl type</a></li>
      <li><a href="#price">Why price rises faster than size</a></li>
      <li><a href="#strands">Strands: sizes, lengths and pearl counts</a></li>
      <li><a href="#by-use">Choosing sizes by product</a></li>
      <li><a href="#budget">Size or quality? Working to a budget</a></li>
      <li><a href="#faq">Questions buyers ask</a></li>
    </ol></nav>

    <h2 id="measuring">How pearl size is measured</h2>
    <p>Pearl size is the diameter in millimetres. Round and near-round pearls are measured straight across; drop, oval, button and baroque pearls are usually given as length × width.</p>
    <p>Wholesale lots are quoted in 0.5 mm ranges, such as 7.0–7.5 mm: every pearl in the lot falls inside that range. A range of 7–8 mm is wider and cheaper to fill, but the pearls will look less even side by side. If you sell pairs or uniform strands, ask for a 0.5 mm range and put <a href="/guides/pearl-grading-guide/#matching">matching</a> in your spec.</p>
    <p>When you check photos, ask for a caliper reading on a few pearls rather than a ruler next to the lot.</p>

    <h2 id="ranges">Size ranges by pearl type</h2>
    <div class="gscroll"><table class="gtable">
      <thead><tr><th>Pearl type</th><th>Typical sizes we supply</th><th>Notes</th></tr></thead>
      <tbody>
        <tr><th><a href="/pearls/freshwater-pearls-wholesale/">Freshwater</a></th><td>2–12 mm</td><td>Widest choice of shapes and colours; strong value for volume lines</td></tr>
        <tr><th><a href="/pearls/edison-pearls-wholesale/">Edison</a></th><td>Larger round freshwater sizes</td><td>Bead-nucleated, so they grow larger and rounder than most freshwater pearls</td></tr>
        <tr><th><a href="/pearls/akoya-pearls-wholesale/">Akoya</a></th><td>2–10 mm</td><td>The classic round strand and stud pearl</td></tr>
        <tr><th><a href="/pearls/tahitian-pearls-wholesale/">Tahitian</a></th><td>8–16 mm</td><td>Naturally dark colours</td></tr>
        <tr><th><a href="/pearls/south-sea-pearls-wholesale/">South Sea</a></th><td>9–20 mm</td><td>The largest cultured pearls; gold, white and champagne</td></tr>
      </tbody>
    </table></div>
    <p>Each type is priced on its own scale. A 9 mm freshwater pearl and a 9 mm Akoya pearl are different products, so compare sizes within a type.</p>

    <h2 id="price">Why price rises faster than size</h2>
    <p>A larger pearl spends longer growing, and the longer it grows the more chances there are for marks and uneven shape. Fewer pearls reach the larger sizes with good lustre and a clean surface, so each extra half-millimetre costs more than the one before, and the steps get steeper near the top of each type's range.</p>
    <p>Size also multiplies through a design. A strand of larger pearls needs fewer pearls, but each one costs more, and matching them takes a bigger pool to choose from.</p>

    <h2 id="strands">Strands: sizes, lengths and pearl counts</h2>
    <p>Strands are either uniform (all pearls in one 0.5 mm range) or graduated (larger in the centre, written end-to-centre, such as 6–9 mm). Common necklace lengths are about 16 in (40 cm, choker) and 18 in (45 cm, princess); longer matinee and opera lengths are made to order.</p>
    <p>Approximate number of pearls per strand, before knots and clasp:</p>
    <div class="gscroll"><table class="gtable">
      <thead><tr><th>Pearl size</th><th>16 in / 40 cm strand</th><th>18 in / 45 cm strand</th></tr></thead>
      <tbody>{"".join(f"<tr><th>{d} mm</th><td>about {a}</td><td>about {b}</td></tr>" for d, a, b in G2_ROWS)}</tbody>
    </table></div>
    <p class="note">Calculated as strand length ÷ pearl size. Hand-knotting between pearls and the clasp reduce the count a little.</p>

    <h2 id="by-use">Choosing sizes by product</h2>
    <ul>
      <li><strong>Stud earrings</strong>: many everyday lines use 6–8 mm; smaller sizes suit minimalist or children's styles, larger ones statement pieces. Order matched pairs, half-drilled.</li>
      <li><strong>Drop earrings and pendants</strong>: drop, button and baroque shapes are given as length × width; a single pendant pearl can go larger than a strand for the same budget.</li>
      <li><strong>Necklaces</strong>: choose a uniform or graduated strand and a length, then count pearls with the table above.</li>
      <li><strong>Bracelets</strong>: usually smaller than the matching necklace, so the piece sits comfortably on the wrist.</li>
      <li><strong>Beading and DIY</strong>: small freshwater pearls (2–5 mm) and <a href="/pearls/keshi-pearls-wholesale/">keshi</a> are popular for layered and handmade designs.</li>
    </ul>

    <h2 id="budget">Size or quality? Working to a budget</h2>
    <p>For a fixed price per piece, you usually trade size against lustre and surface. Stepping down half a millimetre often frees enough budget for noticeably better lustre, which end customers see first. For pieces sold on a "bigger is better" story, the opposite trade may sell better.</p>
    <p>The quickest way to decide is to compare two samples side by side: the size you want at a lower grade, and half a millimetre smaller at a higher grade. Tell us your target price and quantity and we will quote both with real photos.</p>
    <div class="lp-cta"><a class="btn" href="/#inquiry">Ask for a size and price quote</a><a class="btn ghost" href="{wa('Hello Tianqi Jewelry, I am comparing pearl sizes.' + chr(10) + 'Pearl type: ' + chr(10) + 'Product (studs / strand / pendant): ' + chr(10) + 'Size range: ' + chr(10) + 'Target price per piece: ' + chr(10) + 'Quantity: ' + chr(10) + 'Destination country: ' + chr(10) + chr(10) + BASE + '/guides/pearl-sizes-and-price/')}" target="_blank" rel="noopener">Ask on WhatsApp</a></div>

    <h2 id="faq">Questions buyers ask</h2>
    {faq_html(G2_FAQ)}
    <div class="lp-cta"><a class="btn" href="/#inquiry">Ask for a quote</a><a class="btn ghost" href="/products/">Browse the catalogue</a></div>
  </article>"""

GUIDES.append(dict(
    slug="pearl-sizes-and-price",
    name="Pearl sizes and price",
    h1="Pearl sizes and price: how millimetres change what you pay",
    title="Pearl Sizes and Price Guide: mm Ranges, Strand Counts, Choosing Sizes | Tianqi Jewelry",
    desc="How pearl size is measured, size ranges for freshwater, Akoya, Tahitian and South Sea pearls, pearls per strand, sizes by product and how to trade size against quality on a budget.",
    blurb="How pearls are measured, size ranges by type, how many pearls fill a strand, and how to balance size against quality on a budget.",
    published="2026-11-13", faq=G2_FAQ, main=G2_MAIN))


# ---- 3. Freshwater vs saltwater ----
G3_FAQ = [
    ("Which is better, freshwater or Akoya pearls?",
     "Neither is better for every product. Akoya pearls are the classic round, sharp-lustre pearl for strands and studs. Freshwater pearls give more shapes, colours and sizes for the money and suit volume and fashion lines. Choose by your customer, design and price point."),
    ("Are freshwater pearls real pearls?",
     "Yes. Freshwater pearls are real cultured pearls, grown in mussels. In US advertising they should be described as cultured pearls, for example 'cultured freshwater pearls', because the unqualified word 'pearl' is reserved for natural pearls."),
    ("Can I tell freshwater from Akoya by looking?",
     "Not reliably, especially with today's round freshwater pearls. Shape, lustre and drill-hole details give clues, but only testing confirms it. We state the pearl type and any treatment on the invoice, and a third-party test report is available on request."),
    ("Are coloured pearls dyed?",
     "Some are, some are not. Freshwater white, pink and lavender occur naturally, Tahitian pearls are naturally dark, and South Sea pearls are naturally white or gold. Bright fashion colours are usually dyed. We state any treatment on the invoice, and you should disclose it in your listings."),
    ("Can I mix pearl types in one order?",
     "Yes. Many buyers combine freshwater for volume lines with a few saltwater pieces for higher price points. The minimum is 5 pcs per item and USD 100 per order."),
]

G3_MAIN = f"""  <article class="guide">
    <span class="eyebrow">Buyer guide</span>
    <h1>Freshwater or saltwater pearls? How to choose for your jewelry line</h1>
    <p class="meta">Tianqi Jewelry · Shanxiahu, Zhuji · Updated 13 November 2026</p>
    <p class="lead">Freshwater, Akoya, Tahitian and South Sea pearls are all cultured pearls, but they differ in size, colour, shape and price. This guide compares them side by side and shows which fits which kind of product and customer.</p>
    <nav class="toc" aria-label="Contents"><strong>Contents</strong><ol>
      <li><a href="#compare">The four main types at a glance</a></li>
      <li><a href="#freshwater">Freshwater pearls</a></li>
      <li><a href="#saltwater">Saltwater pearls: Akoya, Tahitian, South Sea</a></li>
      <li><a href="#choose">Which type for which product</a></li>
      <li><a href="#colour">Natural colour and treatments</a></li>
      <li><a href="#labelling">Describing pearls in your listings</a></li>
      <li><a href="#faq">Questions buyers ask</a></li>
    </ol></nav>

    <h2 id="compare">The four main types at a glance</h2>
    <div class="gscroll"><table class="gtable">
      <thead><tr><th></th><th>Freshwater</th><th>Akoya</th><th>Tahitian</th><th>South Sea</th></tr></thead>
      <tbody>
        <tr><th>Grown in</th><td>Freshwater mussels</td><td>Saltwater oysters</td><td>Saltwater oysters</td><td>Saltwater oysters</td></tr>
        <tr><th>Main origin</th><td>Zhejiang, China</td><td>Japan · China</td><td>French Polynesia</td><td>Australia · Indonesia · Philippines</td></tr>
        <tr><th>Sizes we supply</th><td>2–12 mm</td><td>2–10 mm</td><td>8–16 mm</td><td>9–20 mm</td></tr>
        <tr><th>Colours</th><td>White, pink, lavender</td><td>White, silver-blue, rosé</td><td>Peacock, grey, aubergine</td><td>Gold, white, champagne</td></tr>
        <tr><th>Shapes</th><td>Round to baroque; widest range</td><td>Mostly round</td><td>Round, drop, circled, baroque</td><td>Round, drop, baroque</td></tr>
        <tr><th>Inside</th><td>Mostly solid nacre (Edison: bead-nucleated)</td><td>Bead with nacre layer</td><td>Bead with nacre layer</td><td>Bead with thick nacre</td></tr>
        <tr><th>Relative price</th><td>$</td><td>$$</td><td>$$$</td><td>$$$$</td></tr>
        <tr><th>Best for</th><td>Volume and fashion lines, beading, baroque designs</td><td>Classic strands and studs</td><td>Dark statement pieces, men's jewelry</td><td>High-value and custom pieces</td></tr>
      </tbody>
    </table></div>
    <p class="note">Relative price compares typical lots of similar size and grade; a top freshwater lot can cost more than a low Akoya lot.</p>

    <h2 id="freshwater">Freshwater pearls</h2>
    <p><a href="/pearls/freshwater-pearls-wholesale/">Freshwater pearls</a> are cultured in mussels, mostly in Zhejiang, China. One mussel can grow many pearls at once, which is why freshwater pearls offer the most choice for the money. Most form without a bead, so they are almost entirely nacre and hold up well to everyday wear.</p>
    <p>They come in more shapes and natural colours than any other type: round and near-round for classic styles, <a href="/pearls/baroque-pearls-wholesale/">baroque</a> and <a href="/pearls/keshi-pearls-wholesale/">keshi</a> for contemporary designs, and bead-nucleated <a href="/pearls/edison-pearls-wholesale/">Edison pearls</a> when you want a large round pearl at freshwater pricing.</p>

    <h2 id="saltwater">Saltwater pearls: Akoya, Tahitian, South Sea</h2>
    <p>Saltwater pearls grow in oysters around a bead nucleus, usually one or two pearls per oyster at a time, so supply is smaller and prices are higher.</p>
    <ul>
      <li><a href="/pearls/akoya-pearls-wholesale/"><strong>Akoya</strong></a>: round, with sharp lustre and pink or silver overtones. The classic choice for matched strands and studs.</li>
      <li><a href="/pearls/tahitian-pearls-wholesale/"><strong>Tahitian</strong></a>: naturally dark, with peacock-green and aubergine overtones. Works for both men's and women's designs.</li>
      <li><a href="/pearls/south-sea-pearls-wholesale/"><strong>South Sea</strong></a>: the largest cultured pearls, with thick nacre, in white and gold. For high-value pieces and custom work.</li>
    </ul>
    <p>We source saltwater pearls through Hong Kong's pearl dealers and fairs and grade them on the same <a href="/guides/pearl-grading-guide/">five factors</a> as freshwater pearls.</p>

    <h2 id="choose">Which type for which product</h2>
    <div class="gscroll"><table class="gtable">
      <thead><tr><th>You are making…</th><th>Start with</th><th>Why</th></tr></thead>
      <tbody>
        <tr><th>Everyday studs and pendants at an accessible price</th><td>Freshwater, round or button</td><td>Good lustre for the price, wide size choice</td></tr>
        <tr><th>Classic strands and bridal pieces</th><td>Akoya, or high-grade round freshwater</td><td>Round shape and close matching</td></tr>
        <tr><th>Contemporary or handmade designs</th><td>Baroque, keshi, biwa</td><td>Every piece is different; strong lustre</td></tr>
        <tr><th>Large round pearls on a mid budget</th><td>Edison</td><td>Large, round and bright at freshwater pricing</td></tr>
        <tr><th>Dark or men's pieces</th><td>Tahitian</td><td>Naturally dark colours</td></tr>
        <tr><th>High-value, one-off or custom pieces</th><td>South Sea</td><td>Size, nacre and natural gold or white colour</td></tr>
      </tbody>
    </table></div>
    <p>Many brands combine types: freshwater for the core range, one or two saltwater lines for higher price points. If you are not sure, tell us the product and target retail price and we will suggest options with photos.</p>

    <h2 id="colour">Natural colour and treatments</h2>
    <p>Freshwater pearls grow naturally in white, pink and lavender; Tahitian pearls are naturally dark; South Sea pearls are naturally white or gold. Bright fashion colours, such as green or blue, are usually dyed. Treatment is not a problem in itself, but it must be disclosed.</p>
    <p>We state the pearl type and any treatment on the invoice. Pass that information on in your own product descriptions.</p>

    <h2 id="labelling">Describing pearls in your listings</h2>
    <p>If you sell in the United States, the FTC's Jewelry Guides (16 CFR §23.20) say a cultured pearl should not be called a "pearl" unless the word is immediately preceded, with equal conspicuousness, by "cultured" or "cultivated". In practice: write "cultured freshwater pearl" or "freshwater cultured pearl", not just "pearl" or "natural pearl". Other markets have similar consumer-protection rules, so naming the type and treatment clearly is the safe default everywhere.</p>
    <div class="lp-cta"><a class="btn" href="/#inquiry">Ask which type fits your line</a><a class="btn ghost" href="{wa('Hello Tianqi Jewelry, I am choosing between pearl types.' + chr(10) + 'Product: ' + chr(10) + 'Target retail price: ' + chr(10) + 'Quantity: ' + chr(10) + 'Destination country: ' + chr(10) + chr(10) + BASE + '/guides/freshwater-vs-saltwater-pearls/')}" target="_blank" rel="noopener">Ask on WhatsApp</a></div>

    <h2 id="faq">Questions buyers ask</h2>
    {faq_html(G3_FAQ)}
    <div class="lp-cta"><a class="btn" href="/#inquiry">Ask for a quote</a><a class="btn ghost" href="/products/">Browse the catalogue</a></div>
  </article>"""

GUIDES.append(dict(
    slug="freshwater-vs-saltwater-pearls",
    name="Freshwater vs saltwater",
    h1="Freshwater or saltwater pearls? How to choose for your jewelry line",
    title="Freshwater vs Saltwater Pearls (Akoya, Tahitian, South Sea): Buyer's Comparison | Tianqi Jewelry",
    desc="Freshwater, Akoya, Tahitian and South Sea pearls compared: origin, sizes, colours, shapes, relative price, which suits which product, treatments and how to label cultured pearls.",
    blurb="Freshwater, Akoya, Tahitian and South Sea compared side by side, which type fits which product, and how to describe them in listings.",
    published="2026-11-13", faq=G3_FAQ, main=G3_MAIN))


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


def related(g):
    others = [o for o in GUIDES if o["slug"] != g["slug"]]
    if not others:
        return ""
    return ('<h2>More buyer guides</h2><ul class="glist">' + "".join(
        f'<li><a href="/guides/{o["slug"]}/"><strong>{esc(o["h1"])}</strong><span>{esc(o["blurb"])}</span></a></li>' for o in others) + "</ul>")


for g in GUIDES:
    g["main"] = g["main"].replace("  </article>", related(g) + "\n  </article>")
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
