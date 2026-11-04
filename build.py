#!/usr/bin/env python3
"""Erzeugt die Webseite aus content/site.json nach docs/ (wird von GitHub Pages ausgeliefert).

Aufruf:  python3 build.py
Keine Abhängigkeiten außer Python 3.
"""
import json, os, struct, html, hashlib
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")
D = json.load(open(os.path.join(ROOT, "content", "site.json"), encoding="utf-8"))
SITE = D["site"]
E = lambda s: html.escape(str(s or ""), quote=True)


def asset_v(name):
    """Kurzer Prüfwert, damit Browser nach Änderungen die neue Datei laden."""
    return hashlib.md5(open(os.path.join(OUT, "assets", name), "rb").read()).hexdigest()[:8]


# ---------- Bilder ----------
_dims = {}
def jpeg_size(path):
    with open(path, "rb") as f:
        f.read(2)
        while True:
            marker, = struct.unpack(">H", f.read(2))
            length, = struct.unpack(">H", f.read(2))
            if marker in (0xFFC0, 0xFFC1, 0xFFC2):
                f.read(1); h, w = struct.unpack(">HH", f.read(4)); return w, h
            f.seek(length - 2, 1)

def dims(rel):
    if rel not in _dims:
        _dims[rel] = jpeg_size(os.path.join(OUT, rel.lstrip("/")))
    return _dims[rel]

def img(name, alt="", sizes="100vw", cls="", eager=False, focus=None):
    """<img> mit kleiner und großer Variante."""
    t, f = f"/img/thumb/{name}", f"/img/full/{name}"
    tw, th = dims(t); fw, _ = dims(f)
    srcset = f"{t} {tw}w, {f} {fw}w" if fw > tw else f"{f} {fw}w"
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    st = f' style="object-position:{focus}"' if focus else ""
    return f'<img src="{t}" srcset="{srcset}" sizes="{sizes}" width="{tw}" height="{th}" alt="{E(alt)}" {load}{c}{st}>'

def video_thumb(v, fallback=None):
    p = f"/img/video/{v['id']}.jpg"
    if os.path.exists(os.path.join(OUT, p.lstrip("/"))):
        w, h = dims(p); return p, w, h
    if fallback:
        t = f"/img/thumb/{fallback}"; w, h = dims(t); return t, w, h
    return None, 16, 9


# ---------- Strukturierte Daten für Suchmaschinen ----------
PERSON = {
    "@type": "Person", "@id": SITE["url"] + "/#person",
    "name": "Daniel Samer", "jobTitle": ["Kameramann", "Director of Photography", "Fotograf"],
    "description": SITE["description"], "url": SITE["url"] + "/",
    "image": SITE["url"] + "/img/full/daniel_samer-160923.jpg",
    "email": "mailto:" + SITE["email"], "telephone": SITE["phone"],
    "address": {"@type": "PostalAddress", "streetAddress": SITE["street"], "postalCode": SITE["city"].split()[0],
                "addressLocality": "München", "addressCountry": "DE"},
    "birthPlace": "Füssen", "workLocation": {"@type": "Place", "name": "München"},
    "knowsAbout": ["Kamera", "Bildgestaltung", "Dokumentarfilm", "Kinodokumentarfilm", "Dokuserie", "Imagefilm", "Musikvideo", "Fotografie"],
    "award": "Preis für beste Bildgestaltung Dokumentarfilm, Filmkunstfest MV 2019 (CONGO CALLING)",
    "sameAs": [u for _, u in SITE["social"]],
}
PERSON_REF = {"@context": "https://schema.org", **PERSON}


# ---------- Bausteine ----------
ICONS = {
 "Instagram": '<path d="M12 2.2c3.2 0 3.6 0 4.8.1 3.3.1 4.8 1.7 4.9 4.9.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 3.2-1.7 4.8-4.9 4.9-1.3.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-3.3-.1-4.8-1.7-4.9-4.9C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8C2.4 3.9 3.9 2.4 7.2 2.3 8.4 2.2 8.8 2.2 12 2.2zM12 0C8.7 0 8.3 0 7.1.1 2.7.3.3 2.7.1 7.1 0 8.3 0 8.7 0 12s0 3.7.1 4.9c.2 4.4 2.6 6.8 7 7 1.2.1 1.6.1 4.9.1s3.7 0 4.9-.1c4.4-.2 6.8-2.6 7-7 .1-1.2.1-1.6.1-4.9s0-3.7-.1-4.9c-.2-4.4-2.6-6.8-7-7C15.7 0 15.3 0 12 0zm0 5.8a6.2 6.2 0 100 12.4 6.2 6.2 0 000-12.4zM12 16a4 4 0 110-8 4 4 0 010 8zm6.4-11.8a1.4 1.4 0 100 2.9 1.4 1.4 0 000-2.9z"/>',
 "YouTube": '<path d="M23.5 6.2a3 3 0 00-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 00.5 6.2 31 31 0 000 12a31 31 0 00.5 5.8 3 3 0 002.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 002.1-2.1A31 31 0 0024 12a31 31 0 00-.5-5.8zM9.6 15.6V8.4l6.3 3.6-6.3 3.6z"/>',
 "Facebook": '<path d="M24 12a12 12 0 10-13.9 11.9v-8.4H7.1V12h3V9.4c0-3 1.8-4.7 4.5-4.7 1.3 0 2.7.2 2.7.2v2.9h-1.5c-1.5 0-2 .9-2 1.9V12h3.4l-.5 3.5h-2.9v8.4A12 12 0 0024 12z"/>',
}

def header(active):
    nav = [("Kamera", "/#kamera", "kamera"), ("Fotografie", "/fotografie/", "fotografie"), ("Info", "/info/", "info")]
    links = "".join(f'<a href="{h}"{" aria-current=page" if k == active else ""}>{t}</a>' for t, h, k in nav)
    social = "".join(f'<a href="{u}" target="_blank" rel="noopener" aria-label="{n}"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[n]}</svg></a>' for n, u in SITE["social"])
    return f'''<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<header class="site-header">
  <a class="logo" href="/">{E(SITE["name"])}</a>
  <button class="menu-btn" aria-label="Menü" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
  <nav class="nav" id="nav">{links}<span class="social">{social}</span></nav>
</header>'''

def footer():
    return f'''<footer class="site-footer"><div class="wrap">
  <span>© {date.today().year} Daniel Samer · Kameramann &amp; Fotograf · München</span>
  <nav><a href="mailto:{SITE["email"]}">{SITE["email"]}</a><a href="/impressum/">Impressum</a><a href="/datenschutz/">Datenschutz</a></nav>
</div></footer>'''

def page(path, title, body, desc=None, active="", hero=True, og_image=None, ld=None):
    full_title = title or "Daniel Samer – Kameramann München | Dokumentarfilm, Serie, Imagefilm"
    canonical = SITE["url"] + path
    og = f'<meta property="og:image" content="{SITE["url"]}{og_image}">' if og_image else ""
    doc = f'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(full_title)}</title>
<meta name="description" content="{E(desc or SITE["description"])}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{E(full_title)}">
<meta property="og:description" content="{E(desc or SITE["description"])}">
<meta property="og:url" content="{canonical}">
{og}
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="Daniel Samer – Kameramann">
<script type="application/ld+json">{json.dumps(ld or PERSON_REF, ensure_ascii=False)}</script>
<meta name="theme-color" content="#0e0e0e">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/poppins-600.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/poppins-300.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css?v={asset_v("style.css")}">
</head>
<body{"" if hero else ' class="no-hero"'}>
{header(active)}
<main id="inhalt">
{body}
</main>
{footer()}
<script src="/assets/site.js?v={asset_v("site.js")}" defer></script>
</body>
</html>
'''
    dst = os.path.join(OUT, path.strip("/"), "index.html") if path != "/" else os.path.join(OUT, "index.html")
    if path.endswith(".html"): dst = os.path.join(OUT, path.strip("/"))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8").write(doc)
    return path

def video_box(v, title, fallback=None):
    src, w, h = video_thumb(v, fallback)
    poster = f'<img src="{src}" width="{w}" height="{h}" alt="" loading="lazy" decoding="async">' if src else ""
    hattr = f' data-h="{v["h"]}"' if v.get("h") else ""
    return f'''<div class="video" data-type="{v["type"]}" data-id="{v["id"]}"{hattr} data-title="{E(title)}">
  <button aria-label="Video „{E(title)}“ abspielen">{poster}<span class="play"><i></i></span></button>
</div>'''


# ---------- Startseite ----------
def build_home():
    projects = D["projects"]
    lead = projects[0]
    tiles = []
    for i, p in enumerate(projects):
        tile_alt = f"{p['title']} – {p['category'].title()}, Kamera: Daniel Samer"
        sizes = "(max-width: 760px) 100vw, 100vw" if i % 5 == 0 else "(max-width: 760px) 100vw, 50vw"
        tiles.append(f'''<a class="tile reveal" href="/{p["slug"]}/">
  <div class="tile-media">{img(p["cover"], tile_alt, sizes, focus=p.get("focus"))}</div>
  <div class="tile-text"><h3>{E(p["title"])}</h3><div class="eyebrow">{E(p["category"])}</div></div>
</a>''')
    works = []
    for m in D["more"]:
        if m.get("image"):
            src = f"/img/thumb/{m['image']}"; w, h = dims(src)
        else:
            src, w, h = video_thumb(m["video"])
        hattr = f' data-h="{m["video"]["h"]}"' if m["video"].get("h") else ""
        works.append(f'''<button class="work reveal" data-play data-type="{m["video"]["type"]}" data-id="{m["video"]["id"]}"{hattr} data-title="{E(m["title"])}">
  <div class="thumb"><img src="{src}" width="{w}" height="{h}" alt="" loading="lazy" decoding="async"><span class="play"><i></i></span></div>
  <h3>{E(m["title"])}</h3><div class="eyebrow">{E(m["meta"])}</div>
</button>''')
    body = f'''<section class="hero">
  {img("ur-be05c8.jpg", "Berglandschaft in Uri – Szene aus UR", "100vw", eager=True)}
  <div class="hero-text">
    <div class="eyebrow">Daniel Samer · Kameramann &amp; Fotograf · München</div>
    <h1>Dokumentarische Kamera – <br>für Kino, Serie und Imagefilm.</h1>
    <a class="more" href="#kamera">Arbeiten ansehen ↓</a>
  </div>
</section>
<section class="section intro">
  <div class="wrap reveal">
    <p class="intro-text">Daniel Samer ist Kameramann und Fotograf in München. Seit 2010 dreht er weltweit Kinodokumentarfilme, Dokuserien und Dokumentationen für ARTE, ZDF, BR und SRF sowie Imagefilme und Musikvideos. Für die Bildgestaltung von CONGO CALLING wurde er beim Filmkunstfest MV 2019 ausgezeichnet.</p>
    <p class="intro-links"><a href="mailto:{SITE["email"]}">{SITE["email"]}</a><a href="/info/">Mehr über Daniel Samer →</a></p>
  </div>
</section>
<section class="section" id="kamera" style="padding-top:0">
  <div class="wrap">
    <div class="section-head reveal"><h2>Kamera</h2><span class="eyebrow">Ausgewählte Arbeiten</span></div>
    <div class="grid">{"".join(tiles)}</div>
  </div>
</section>
<section class="section" id="mehr" style="padding-top:0">
  <div class="wrap">
    <div class="section-head reveal"><h2>Weitere Arbeiten</h2><span class="eyebrow">Musikvideos · Imagefilme · Kurzfilme</span></div>
    <div class="works">{"".join(works)}</div>
  </div>
</section>'''
    page("/", "", body, active="kamera", og_image="/img/full/ur-be05c8.jpg")


# ---------- Projektseiten ----------
def build_projects():
    ps = D["projects"]
    for i, p in enumerate(ps):
        prev, nxt = ps[i - 1], ps[(i + 1) % len(ps)]
        stills_src = [x for x in p["images"]]
        still_alt = f"{p['title']} – Filmstill, Kamera: Daniel Samer"
        hero_img = p["cover"]
        # Videos
        vids = ""
        if p["videos"]:
            titles = p.get("videoTitles") or [p["title"]] * len(p["videos"])
            fallback = stills_src[0] if stills_src else hero_img
            items = []
            for v, t in zip(p["videos"], titles):
                cap = f'<div class="eyebrow video-title">{E(t)}</div>' if p.get("videoTitles") else ""
                items.append(f'<div class="reveal">{video_box(v, t, fallback)}{cap}</div>')
            vids = f'<section class="section" style="padding-top:0"><div class="wrap project-videos">{"".join(items)}</div></section>'
        # Text + Credits
        sub = f'<p class="subtitle">{E(p["subtitle"])}</p>' if p.get("subtitle") else ""
        lead = "".join(f"<p>{E(t)}</p>" for t in p["description"])
        notes = "".join(f'<p class="small-print">{E(t)}</p>' for t in p.get("notes", []))
        facts = "".join(f'<div class="row"><dt>{E(r)}</dt><dd>{E(n)}</dd></div>' for r, n in p["credits"])
        facts_html = f'<aside class="facts reveal"><dl>{facts}</dl></aside>' if facts else "<aside></aside>"
        awards = ""
        if p["awards"]:
            lis = "".join(f'<li><b>{E(a[0])}</b>{"<span>" + E(a[1]) + "</span>" if len(a) > 1 and a[1] else ""}</li>' for a in p["awards"])
            awards = f'<div class="awards reveal"><div class="eyebrow">{E(p["awardsTitle"])}</div><ul>{lis}</ul></div>'
        # Bilder
        stills = ""
        if stills_src:
            figs = []
            n = len(stills_src)
            for j, s in enumerate(stills_src):
                w, h = dims(f"/img/thumb/{s}")
                wide = (n % 2 == 1 and j == 0) or (w / h > 2.0)
                figs.append(f'<figure class="reveal{" wide" if wide else ""}" data-full="/img/full/{s}" tabindex="0" role="button" aria-label="Bild vergrößern">{img(s, still_alt, "(max-width:600px) 100vw, " + ("100vw" if wide else "50vw"))}</figure>')
            stills = f'<section class="section" style="padding-top:0"><div class="wrap"><div class="stills" data-gallery>{"".join(figs)}</div></div></section>'
        poster = ""
        if p.get("poster"):
            poster = f'''<section class="section" style="padding-top:0"><div class="wrap"><div class="eyebrow" style="margin-bottom:16px">Plakat</div>
<div class="poster reveal" data-gallery><div data-full="/img/full/{p["poster"]}">{img(p["poster"], "Filmplakat " + p["title"], "420px")}</div></div></div></section>'''
        has_images = p.get("hero", True)  # "hero": false → Seite ohne großes Titelbild
        if has_images:
            top = f'''<section class="hero short">
  {img(hero_img, still_alt, "100vw", eager=True, focus=p.get("focus"))}
  <div class="hero-text"><div class="eyebrow">{E(p["category"])}</div><h1>{E(p["title"])}</h1></div>
</section>'''
        else:
            # ohne eigene Bilder: Titel als Text, Video direkt darunter
            top = f'''<section class="section page-top" style="padding-bottom:clamp(28px,4vw,48px)"><div class="wrap">
  <div class="eyebrow" style="margin-bottom:14px">{E(p["category"])}</div><h1 class="page-title">{E(p["title"])}</h1>
</div></section>{vids}'''
            vids = ""
        body = f'''{top}
<section class="section"{"" if has_images else ' style="padding-top:0"'}>
  <div class="wrap">
    <div class="eyebrow reveal" style="margin-bottom:28px">{E(p["meta"])}</div>
    <div class="project-intro">
      <div class="lead reveal">{sub}{lead}{notes}</div>
      {facts_html}
    </div>
    {awards}
  </div>
</section>
{vids}
{stills}
{poster}
<div class="wrap"><nav class="pager">
  <a href="/{prev["slug"]}/"><div class="eyebrow">← Vorheriges Projekt</div><h3>{E(prev["title"])}</h3></a>
  <a href="/{nxt["slug"]}/"><div class="eyebrow">Nächstes Projekt →</div><h3>{E(nxt["title"])}</h3></a>
</nav></div>'''
        intro = p["description"][0] if p["description"] else ""
        cat = p["category"].title().replace("Arte", "ARTE")
        desc = f"Kamera: Daniel Samer. {p['title']} ({cat}). {intro}"
        desc = desc[:157].rsplit(" ", 1)[0] + "…" if len(desc) > 160 else desc
        title = f"{p['title'].title()} – {cat} | Kamera: Daniel Samer"
        roles = {"Regie": "director", "Produktion": "productionCompany", "Produktionsfirma": "productionCompany"}
        work = {"@context": "https://schema.org", "@type": "Movie" if "FILM" in p["category"] else "CreativeWork",
                "name": p["title"], "genre": p["category"].title(), "description": intro,
                "url": f"{SITE['url']}/{p['slug']}/",
                "image": f"{SITE['url']}/img/full/{(p['images'] or [hero_img])[0]}",
                "contributor": {"@type": "Role", "roleName": "Kamera", "contributor": {"@id": PERSON["@id"]}}}
        for r, n in p["credits"]:
            if r in roles and r != "Kamera":
                work.setdefault(roles[r], [{"@type": "Person" if r == "Regie" else "Organization", "name": n.title()}])
        ld = {"@context": "https://schema.org", "@graph": [PERSON, {k: v for k, v in work.items() if k != "@context"}]}
        page(f"/{p['slug']}/", title, body, desc=desc, active="kamera",
             hero=has_images, og_image=f"/img/full/{(p['images'] or [hero_img])[0]}", ld=ld)


# ---------- Fotografie ----------
def build_photos():
    def btn(i, s):
        w, h = dims(f"/img/thumb/{s}")
        sizes = "(max-width: 600px) 60vw, 40vw"
        return f'<button data-full="/img/full/{s}" style="--r:{w / h:.4f}" aria-label="Foto {i+1} vergrößern">{img(s, "Fotografie von Daniel Samer", sizes)}</button>'
    # Reihen werden im Browser bündig gesetzt (site.js); dies ist die Variante ohne JavaScript
    btns = "".join(btn(i, s) for i, s in enumerate(D["photos"]))
    body = f'''<section class="section page-top">
  <div class="wrap">
    <div class="section-head"><h1 style="font-size:clamp(30px,4.5vw,56px)">Fotografie</h1></div>
    <div class="photos" data-gallery data-justify>{btns}</div>
  </div>
</section>'''
    page("/fotografie/", "Fotografie – Daniel Samer, Fotograf München", body, desc="Fotografie von Daniel Samer, Fotograf und Kameramann aus München: Reportage, Portrait, Reise, Industrie und Werbung.", active="fotografie", hero=False, og_image=f"/img/full/{D['photos'][0]}")


# ---------- Info ----------
def build_info():
    i = D["info"]
    lead = "".join(f"<p>{E(t)}</p>" for t in i["about"])
    links = lambda xs: "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{E(n)}</a></li>' for n, u in xs)
    body = f'''<section class="section page-top">
  <div class="wrap about">
    <div class="portrait reveal">{img("daniel_samer-160923.jpg", "Daniel Samer", "(max-width: 900px) 100vw, 45vw", eager=True)}</div>
    <div>
      <div class="eyebrow" style="margin-bottom:14px">Info</div>
      <h1>Daniel Samer</h1>
      <div class="lead">{lead}</div>
      <div class="contact">
        <div><div class="eyebrow">Kontakt</div><a href="mailto:{SITE["email"]}">{SITE["email"]}</a><br><a href="tel:{SITE["phoneHref"]}">{SITE["phone"]}</a></div>
        <div><div class="eyebrow">Adresse</div>{E(SITE["street"])}<br>{E(SITE["city"])}</div>
      </div>
    </div>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap reveal">
    <div class="eyebrow" style="margin-bottom:20px">Preis · {E(i["award"]["title"])} · {E(i["award"]["detail"])}</div>
    <blockquote>„{E(i["award"]["quote"])}“<footer>Aus der Jurybegründung</footer></blockquote>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="wrap lists">
    <div class="reveal"><div class="eyebrow">Kunden</div><ul>{links(i["clients"])}</ul></div>
    <div class="reveal one"><div class="eyebrow">Sender</div><ul>{"".join(f"<li>{E(s)}</li>" for s in i["broadcasters"])}</ul></div>
    <div class="reveal"><div class="eyebrow">Produktionsfirmen</div><ul>{links(i["producers"])}</ul></div>
  </div>
</section>'''
    page("/info/", "Info & Kontakt – Daniel Samer, Kameramann München", body, desc="Daniel Samer ist Kameramann und Fotograf in München. Kinodokumentarfilme, Dokuserien und Imagefilme für ARTE, ZDF, BR, SRF. Kontakt und Referenzen.", active="info", hero=False)


# ---------- Rechtliches ----------
def build_legal():
    s = SITE
    imp = f'''<section class="section page-top"><div class="wrap prose">
<h1>Impressum</h1>
<p>Angaben gemäß § 5 DDG</p>
<p>Daniel Samer<br>Kameramann<br>{E(s["street"])}<br>{E(s["city"])}<br>Deutschland</p>
<h2>Kontakt</h2>
<p>Telefon: <a href="tel:{s["phoneHref"]}">{s["phone"]}</a><br>E-Mail: <a href="mailto:{s["email"]}">{s["email"]}</a></p>
<h2>Umsatzsteuer-ID</h2>
<p>Umsatzsteuer-Identifikationsnummer gemäß § 27a UStG: {E(s["vat"])}</p>
<h2>Verbraucherstreitbeilegung</h2>
<p>Ich bin nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
<h2>Haftung für Inhalte</h2>
<p>Die Inhalte dieser Seiten wurden mit größter Sorgfalt erstellt. Für die Richtigkeit, Vollständigkeit und Aktualität der Inhalte kann ich jedoch keine Gewähr übernehmen. Als Diensteanbieter bin ich für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich, jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen.</p>
<h2>Haftung für Links</h2>
<p>Diese Webseite enthält Links zu externen Webseiten Dritter, auf deren Inhalte ich keinen Einfluss habe. Für diese fremden Inhalte ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich. Bei Bekanntwerden von Rechtsverletzungen werde ich derartige Links umgehend entfernen.</p>
<h2>Urheberrecht</h2>
<p>Alle Inhalte dieser Webseite (Bilder, Fotos, Texte, Videos) unterliegen dem Urheberrecht. Bitte fragen Sie vorher, bevor Sie Inhalte verbreiten, vervielfältigen oder anderweitig verwerten. Fotos: Daniel Samer, sofern nicht anders angegeben.</p>
</div></section>'''
    page("/impressum/", "Impressum – Daniel Samer", imp, hero=False)

    ds = f'''<section class="section page-top"><div class="wrap prose">
<h1>Datenschutzerklärung</h1>
<h2>1. Verantwortlicher</h2>
<p>Daniel Samer, {E(s["street"])}, {E(s["city"])}<br>E-Mail: <a href="mailto:{s["email"]}">{s["email"]}</a></p>
<h2>2. Grundsatz</h2>
<p>Diese Webseite verwendet keine Cookies, keine Analyse- oder Tracking-Werkzeuge und keine Werbung. Schriften werden lokal von diesem Server geladen; es findet keine Verbindung zu Google Fonts statt.</p>
<h2>3. Hosting und Server-Logfiles</h2>
<p>Diese Webseite wird über den Dienst „GitHub Pages“ der GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, USA, bereitgestellt. Beim Aufruf der Seite werden technisch notwendige Daten verarbeitet, insbesondere IP-Adresse, Datum und Uhrzeit, aufgerufene Seite, Browser und Betriebssystem. GitHub verarbeitet diese Daten, um die Webseite sicher und stabil auszuliefern und vor Missbrauch zu schützen (Art. 6 Abs. 1 lit. f DSGVO). Dabei können Daten in die USA übertragen werden; GitHub ist unter dem EU-US Data Privacy Framework zertifiziert. Weitere Informationen: <a href="https://docs.github.com/de/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener">Datenschutzerklärung von GitHub</a>.</p>
<h2>4. Eingebettete Videos (YouTube und Vimeo)</h2>
<p>Auf dieser Webseite werden Videos von YouTube (Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Irland) und Vimeo (Vimeo.com, Inc., 330 West 34th Street, New York, NY 10001, USA) eingebunden. Die Videos werden erst geladen, wenn Sie aktiv auf „Abspielen“ klicken. Vorher wird keine Verbindung zu YouTube oder Vimeo hergestellt. Nach dem Klick werden Daten wie Ihre IP-Adresse an den jeweiligen Anbieter übertragen; YouTube wird dabei im „erweiterten Datenschutzmodus“ (youtube-nocookie.com) und Vimeo mit dem Parameter „Do Not Track“ eingebunden. Rechtsgrundlage ist Ihre Einwilligung durch den Klick (Art. 6 Abs. 1 lit. a DSGVO, § 25 Abs. 1 TDDDG). Weitere Informationen: <a href="https://policies.google.com/privacy" target="_blank" rel="noopener">Datenschutzerklärung von Google</a>, <a href="https://vimeo.com/privacy" target="_blank" rel="noopener">Datenschutzerklärung von Vimeo</a>.</p>
<h2>5. Kontakt per E-Mail oder Telefon</h2>
<p>Wenn Sie mich per E-Mail oder Telefon kontaktieren, verarbeite ich Ihre Angaben zur Bearbeitung der Anfrage (Art. 6 Abs. 1 lit. b bzw. f DSGVO). Die Daten werden gelöscht, sobald sie nicht mehr erforderlich sind und keine gesetzlichen Aufbewahrungspflichten bestehen.</p>
<h2>6. Links zu sozialen Netzwerken</h2>
<p>Links zu Instagram, YouTube und Facebook sind einfache Verweise. Erst wenn Sie einen Link anklicken, gelangen Sie auf die Seite des jeweiligen Anbieters, für die dessen Datenschutzbestimmungen gelten.</p>
<h2>7. Ihre Rechte</h2>
<p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit sowie Widerspruch gegen die Verarbeitung (Art. 15–21 DSGVO). Eine erteilte Einwilligung können Sie jederzeit mit Wirkung für die Zukunft widerrufen. Sie haben außerdem das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu beschweren, z. B. beim Bayerischen Landesamt für Datenschutzaufsicht.</p>
<p class="small-print">Stand: {date.today().strftime("%B %Y").replace("January","Januar").replace("February","Februar").replace("March","März").replace("May","Mai").replace("June","Juni").replace("July","Juli").replace("October","Oktober").replace("December","Dezember")}</p>
</div></section>'''
    page("/datenschutz/", "Datenschutz – Daniel Samer", ds, hero=False)


def build_extras():
    ps = D["projects"]
    # alte Squarespace-Adressen weiterleiten (GitHub Pages kennt keine Server-Weiterleitungen)
    redirects = {"ber": "/info/", "photographie": "/fotografie/", "kamera": "/#kamera", "cart": "/"}
    redirects.update({p["old"]: f"/{p['slug']}/" for p in ps if p["old"] != p["slug"]})
    for old, new in redirects.items():
        os.makedirs(os.path.join(OUT, old), exist_ok=True)
        open(os.path.join(OUT, old, "index.html"), "w", encoding="utf-8").write(
            f'<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Weiterleitung</title>'
            f'<meta name="robots" content="noindex"><link rel="canonical" href="{SITE["url"]}{new}">'
            f'<meta http-equiv="refresh" content="0; url={new}"></head>'
            f'<body><a href="{new}">Weiter zur Seite</a></body></html>\n')
    # GitHub Pages: keine Jekyll-Verarbeitung; eigene Domain, sobald umgestellt
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    cname = os.path.join(OUT, "CNAME")
    if SITE.get("live"):
        open(cname, "w").write(SITE["url"].split("//")[1] + "\n")
    elif os.path.exists(cname):
        os.remove(cname)
    urls = ["/", "/fotografie/", "/info/", "/impressum/", "/datenschutz/"] + [f"/{p['slug']}/" for p in ps]
    open(os.path.join(OUT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE['url']}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n")
    open(os.path.join(OUT, "favicon.svg"), "w").write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#141414"/>'
        '<text x="50%" y="54%" text-anchor="middle" dominant-baseline="middle" font-family="Poppins,Arial,sans-serif" font-weight="600" font-size="28" fill="#fff">DS</text></svg>')
    body = '''<section class="section page-top"><div class="wrap prose">
<h1>Seite nicht gefunden</h1><p>Diese Seite gibt es leider nicht (mehr).</p><p><a href="/">Zur Startseite</a></p>
</div></section>'''
    page("/404.html", "Seite nicht gefunden – Daniel Samer", body, hero=False)


if __name__ == "__main__":
    build_home(); build_projects(); build_photos(); build_info(); build_legal(); build_extras()
    print(f"Fertig: {len(D['projects'])} Projekte, {len(D['photos'])} Fotos → docs/")
