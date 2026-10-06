"""Static site generator for mintyideas.com (deployed to GitHub Pages by .github/workflows/deploy.yml).
Usage: python3 build.py  -> writes ../dist/site (production, clean URLs) and ../dist/preview (relative links).
"""
import json, os, shutil, html
from datetime import date
from content import *

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "..", "dist")
TODAY = date.today().isoformat()
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;1,400;1,500&family=Manrope:wght@400;500;600;700&display=swap">')

LEAF = ('<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="16" fill="#2c6a4b"/>'
        '<path d="M9.5 23.5C9 15 14 8.5 24 8c.4 9.6-5.6 15.4-14.5 15.5Z" fill="#93c3a1"/>'
        '<path d="M10 23 19.5 13" stroke="#1b4231" stroke-width="1.6" stroke-linecap="round"/></svg>')

# ---------- page registry ----------
PAGES = {}  # key -> dict(prod_path, preview_file)
def reg(key, prod, prev):
    PAGES[key] = {"prod": prod, "prev": prev}
reg("home", "/", "./")
reg("services", "/services/", "services.html")
for s in SERVICES:
    reg(s["key"], f"/services/{s['key']}/", f"{s['key']}.html")
reg("work", "/work/", "work.html")
reg("about", "/about/", "about.html")
reg("faq", "/faq/", "faq.html")
reg("contact", "/contact/", "contact.html")

MODE = "prod"
def L(key, anchor=""):
    p = PAGES[key][MODE if MODE == "prod" else "prev"]
    return p + anchor
def url(key):
    return DOMAIN + PAGES[key]["prod"]
def asset(name):
    return "/" + name if MODE == "prod" else name

e = html.escape

# ---------- schema ----------
BUSINESS_ID = DOMAIN + "/#business"
PERSON_ID = DOMAIN + "/#tyler"
def business_node():
    node = {
        "@type": "ProfessionalService",
        "@id": BUSINESS_ID,
        "name": BRAND,
        "url": DOMAIN + "/",
        "email": EMAIL,
        "logo": DOMAIN + "/logo.png",
        "image": DOMAIN + "/og-image.png",
        "description": "Marketing consultancy specializing in short-form video content creation and community growth on TikTok, LinkedIn, and YouTube, plus marketing strategy consulting and website revamps with SEO and AEO.",
        "founder": {"@id": PERSON_ID},
        "address": {"@type": "PostalAddress", "addressLocality": CITY, "addressRegion": REGION, "addressCountry": "US"},
        "areaServed": {"@type": "Country", "name": "United States"},
        "knowsAbout": ["Short-form video marketing", "TikTok marketing", "LinkedIn content strategy", "YouTube channel growth",
                        "YouTube Shorts", "Community management", "Marketing strategy", "B2B marketing", "Account-based marketing",
                        "Content strategy", "Website design", "Search engine optimization", "Answer engine optimization"],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Marketing services", "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": url(s["key"])}} for s in SERVICES]},
    }
    if SOCIALS:
        node["sameAs"] = [u for _, u in SOCIALS]
    return node
def person_node():
    n = {"@type": "Person", "@id": PERSON_ID, "name": FOUNDER, "jobTitle": "Founder and Marketing Consultant",
         "worksFor": {"@id": BUSINESS_ID}, "url": url("about"), "email": EMAIL,
         "knowsAbout": ["Short-form video", "TikTok", "LinkedIn", "YouTube", "Campaign marketing", "Account-based marketing", "Paid media", "Marketing automation"],
         "homeLocation": {"@type": "Place", "name": f"{CITY}, Arizona"}}
    if SOCIALS:
        n["sameAs"] = [u for _, u in SOCIALS]
    return n
def website_node():
    return {"@type": "WebSite", "@id": DOMAIN + "/#website", "url": DOMAIN + "/", "name": BRAND, "publisher": {"@id": BUSINESS_ID}, "inLanguage": "en-US"}
def faq_node(faqs):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
def crumbs_node(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": url(k)} for i, (n, k) in enumerate(trail)]}
def webpage_node(key, title, desc):
    return {"@type": "WebPage", "@id": url(key) + "#webpage", "url": url(key), "name": title, "description": desc,
            "isPartOf": {"@id": DOMAIN + "/#website"}, "about": {"@id": BUSINESS_ID}, "dateModified": TODAY, "inLanguage": "en-US"}
def ld(nodes):
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": nodes}, indent=1) + "</script>"

# ---------- chrome ----------
def header(active):
    items = [("work", "Work"), ("services", "Services"), ("about", "About"), ("faq", "FAQ")]
    cur = ' aria-current="page"'
    lis = "".join(f'<li><a href="{L(k)}"{cur if active == k else ""}>{t}</a></li>' for k, t in items)
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap nav">
<a class="brand" href="{L("home")}" aria-label="{BRAND} home">{LEAF}<span class="brand-name">minty <i>ideas</i></span></a>
<nav aria-label="Main" class="nav-scroll"><ul class="nav-links">{lis}</ul></nav>
<a class="btn btn-primary nav-cta" href="{L("contact")}">Book a call</a>
</div></header>'''

def footer():
    svc = "".join(f'<li><a href="{L(s["key"])}">{e(s["short"])}</a></li>' for s in SERVICES)
    soc = "".join(f'<li><a href="{u}" rel="me noopener" target="_blank">{n}</a></li>' for n, u in SOCIALS)
    return f'''<footer class="site-footer"><div class="wrap">
<div class="foot-grid">
<div><a class="brand" href="{L("home")}">{LEAF}<span class="brand-name">minty <i>ideas</i></span></a>
<p>Marketing consulting, short-form video, and community growth on TikTok, LinkedIn, and YouTube. Based in {CITY}, Arizona. Working with clients everywhere.</p>
<p><a class="email-line" style="font-size:1.25rem" href="mailto:{EMAIL}">{EMAIL}</a></p></div>
<div><h4>Services</h4><ul>{svc}</ul></div>
<div><h4>Company</h4><ul><li><a href="{L("work")}">Work and campaigns</a></li><li><a href="{L("about")}">About Tyler</a></li><li><a href="{L("faq")}">FAQ</a></li><li><a href="{L("contact")}">Contact</a></li>{soc}</ul></div>
</div>
<div class="legal"><span>&copy; <span data-year>{date.today().year}</span> {BRAND}. All rights reserved.</span><span>{CITY}, Arizona</span></div>
</div></footer>'''

def cta(heading="Let's make something people <em>want</em> to watch.", body="Tell me what you are building and where you want to grow. I will reply within two business days with next steps."):
    return f'''<section><div class="wrap"><div class="cta">
<span class="eyebrow">Work with Minty Ideas</span>
<h2>{heading}</h2><p>{body}</p>
<div class="row"><a class="btn btn-primary" href="{L("contact")}">Start a project <span class="arrow">&rarr;</span></a></div>
<a class="email-line" href="mailto:{EMAIL}">{EMAIL}</a>
</div></div></section>'''

def page(key, title, desc, body, schema_nodes, active=None, noindex=False):
    canon = url(key) if key else DOMAIN + "/404"
    himg = {"work": "amber", "about": "liquid", "contact": "amber", "faq": "liquid"}.get(key, "rain")
    body = body.replace('class="page-hero"', f'class="page-hero ph-{himg}"', 1)
    preview_attr = ' data-preview' if MODE == "preview" else ''
    robots = '<meta name="robots" content="noindex">' if noindex else '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">'
    og = DOMAIN + "/og-image.png"
    return f'''<!doctype html>
<html lang="en"{preview_attr}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
{robots}
<meta name="author" content="{FOUNDER}">
<meta name="theme-color" content="#0b120e">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{og}">
<link rel="icon" href="{asset("favicon.svg")}" type="image/svg+xml">
<link rel="icon" href="{asset("favicon-32.png")}" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{asset("apple-touch-icon.png")}">
<link rel="manifest" href="{asset("site.webmanifest")}">
{FONTS}
<link rel="stylesheet" href="{asset("styles.css")}">
{ld(schema_nodes) if schema_nodes else ""}
</head>
<body>
{header(active)}
<main id="main">
{body}
</main>
{footer()}
<script src="{asset("main.js")}" defer></script>
</body>
</html>
'''

def faq_html(faqs, open_first=True):
    out = []
    for i, (q, a) in enumerate(faqs):
        out.append(f'<details{" open" if (i == 0 and open_first) else ""}><summary>{e(q)}</summary><div class="a"><p>{e(a)}</p></div></details>')
    return '<div class="faq">' + "".join(out) + "</div>"

def crumbs_html(trail):
    lis = []
    for i, (n, k) in enumerate(trail):
        if i == len(trail) - 1:
            lis.append(f'<li aria-current="page">{e(n)}</li>')
        else:
            lis.append(f'<li><a href="{L(k)}">{e(n)}</a></li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(lis)}</ol></nav>'

def service_cards():
    return '<div class="cards">' + "".join(
        f'<a class="card" href="{L(s["key"])}"><span class="kicker">{e(s["kicker"])}</span><h3>{e(s["short"].capitalize() if s["short"][0].islower() else s["short"])}</h3><p>{e(s["card"])}</p><span class="more">Learn more &rarr;</span></a>'
        for s in SERVICES) + "</div>"

def steps_html(compact=False):
    tiles = []
    for i, (word, ital, img, name, d) in enumerate(PROCESS):
        w = f"<em>{word}</em>" if ital else word
        tiles.append(f'<li class="tri-item"><div class="tri-img" style="background-image:url({asset(img + ("-sm" if compact else "") + ".webp")})"><span class="tri-word" aria-hidden="true">{w}</span></div>'
                     f'<div class="tri-text"><span class="tri-step">Step {i+1}</span><h3>{name}</h3><p>{d}</p></div></li>')
    return f'<ol class="triad{" compact" if compact else ""}">' + "".join(tiles) + "</ol>"

RETENTION_SVG = '''<svg viewBox="0 0 200 92" role="img" aria-label="Illustrative audience retention curve: a strong hook keeps viewers through the payoff and loop">
<line x1="6" y1="78" x2="194" y2="78" stroke="rgba(214,232,220,.18)" stroke-width="1"/>
<path d="M6 10 C 18 12, 24 26, 40 28 S 120 36, 160 42 S 186 40, 194 36 L194 78 L6 78 Z" fill="rgba(147,195,161,.16)"/>
<path d="M6 10 C 18 12, 24 26, 40 28 S 120 36, 160 42 S 186 40, 194 36" fill="none" stroke="#93c3a1" stroke-width="2"/>
<circle cx="194" cy="36" r="3" fill="#93c3a1"/>
<text x="8" y="90" font-size="8" fill="#9aa89f" font-family="Manrope, sans-serif">0:00 hook</text>
<text x="88" y="90" font-size="8" fill="#9aa89f" font-family="Manrope, sans-serif">payoff</text>
<text x="162" y="90" font-size="8" fill="#9aa89f" font-family="Manrope, sans-serif">loop</text>
</svg>'''

# ---------- pages ----------
def build_home():
    title = "Minty Ideas | Short-Form Video and Social Media Marketing Consultant"
    desc = "Minty Ideas is a marketing consultancy specializing in short-form video and community growth on TikTok, LinkedIn, and YouTube, plus strategy and website revamps. Based in Tempe, AZ."
    home_faqs = GENERAL_FAQS[:1] + GENERAL_FAQS[3:5] + GENERAL_FAQS[6:8]
    body = f'''
<section class="hero"><div class="wrap hero-grid">
<div class="hero-copy">
<span class="eyebrow">Marketing consulting and short-form video</span>
<h1>Content people <em>stop scrolling</em> for.</h1>
<p class="lede">Minty Ideas is a marketing consultancy that helps brands and founders grow engaged communities on TikTok, LinkedIn, and YouTube. Strategy, short-form video content creation, and website revamps, all from one partner.</p>
<div class="row"><a class="btn btn-primary" href="{L("contact")}">Book an intro call <span class="arrow">&rarr;</span></a><a class="btn btn-ghost" href="{L("services")}">Explore services</a></div>
<ul class="hero-meta"><li>Short-form video</li><li>TikTok</li><li>LinkedIn</li><li>YouTube</li><li>Strategy</li><li>Website revamps</li></ul>
</div>
<div class="hero-visual" aria-hidden="true">
<div class="phone"><div class="screen">
<div class="progress"><span></span></div>
<div class="tag">For You</div>
<div class="captions"><p>Your first three seconds decide <em>everything.</em></p><p>So we script the hook <em>first.</em></p><p>Then we give them a reason to <em>stay.</em></p></div>
<div class="rail"><span></span><small>12.4K</small><span></span><small>318</small><span></span><small>Share</small></div>
<div class="handle"><b>@yourbrand</b>Short-form video, made to be watched to the end.</div>
</div></div>
<div class="float-card"><div class="label">Retention curve</div>{RETENTION_SVG}</div>
</div>
</div></section>

<div class="strip"><div class="wrap"><ul><li>Where I grow audiences</li><li>TikTok</li><li>LinkedIn</li><li>YouTube</li><li>YouTube Shorts</li><li>Instagram Reels</li></ul></div></div>

<section class="paper" id="services"><div class="wrap">
<div class="section-head"><span class="eyebrow">Services</span><h2>Everything you need to be <em>seen</em>, followed, and found.</h2>
<p class="lede">Hire Minty Ideas for one piece or the whole system: a strategy, a content engine, a growing community, and a website that turns attention into customers.</p></div>
{service_cards()}
</div></section>

<section class="work-teaser"><div class="wrap">
<div class="section-head"><span class="eyebrow">Selected work</span><h2>Videos people <em>actually</em> watched.</h2>
<p class="lede">Viral TikToks from my own account and brand content for Posit PBC. Press play to watch right here.</p></div>
{video_grid(sorted([v for v in WORK_VIDEOS if v["group"] == "personal"], key=lambda v: -v["views"])[:2] + sorted([v for v in WORK_VIDEOS if v["group"] == "brand"], key=lambda v: -v["views"])[:2])}
<div class="row mt-2"><a class="btn btn-primary" href="{L("work")}">See all work <span class="arrow">&rarr;</span></a></div>
</div></section>

<section><div class="wrap">
<div class="section-head"><span class="eyebrow">The approach</span><h2>Every short video has three jobs.</h2>
<p class="lede">Platforms reward videos people finish, rewatch, and share. That is why every script starts with the hook and works backward from what the viewer gets.</p></div>
<div class="anatomy">
<div><div class="bar"></div><span class="time">0:00 to 0:03</span><h3>Hook</h3><p>A line, a visual, or a question that earns the next ten seconds.</p></div>
<div><div class="bar"></div><span class="time">0:03 to 0:40</span><h3>Payoff</h3><p>The useful, funny, or surprising part. One idea, delivered fast, with on-screen text for people watching on mute.</p></div>
<div><div class="bar"></div><span class="time">Last 2 seconds</span><h3>Loop or ask</h3><p>An ending that loops back to the start, or one clear next step.</p></div>
</div>
</div></section>

<section class="band"><div class="wrap">
<div class="section-head"><span class="eyebrow">How it works</span><h2>Ideate. Create. <em>Share.</em></h2>
<p class="lede">Every engagement follows the same three moves, whether we are building a TikTok presence from zero or rebuilding your website.</p></div>
{steps_html()}
</div></section>

<section><div class="wrap">
<div class="section-head"><span class="eyebrow">Results</span><h2>Built for engagement, measured in <em>outcomes</em>.</h2></div>
<div class="stats">
<div class="stat"><b>{fmt(totals()[0])}</b><span>organic TikTok views across the {totals()[3]} videos on my <a href="{L("work")}">Work page</a></span></div>
<div class="stat"><b>{fmt(max(v["views"] for v in WORK_VIDEOS))}</b><span>views on a single personal TikTok, with {fmt(max(WORK_VIDEOS, key=lambda v: v["views"])["comments"])} comments</span></div>
<div class="stat"><b>{fmt(totals("brand")[0])}</b><span>views on TikToks made for Posit PBC, a B2B data science company</span></div>
</div>
<figure class="quote"><blockquote>[Client testimonial: one or two sentences about what changed after working with Minty Ideas.]</blockquote><figcaption><cite>[Client name, title, company]</cite></figcaption></figure>
</div></section>

<section class="paper"><div class="wrap split">
<div class="portrait"><span>TM</span><!-- REPLACE: <img src="/tyler.jpg" alt="Tyler Minear, founder of Minty Ideas" width="800" height="1000"> --></div>
<div class="stack" style="gap:1.4rem">
<span class="eyebrow">Meet the founder</span>
<h2>Campaign marketer by training. <em>Creator</em> by instinct.</h2>
<p class="lede">I'm Tyler Minear. I've spent my career in B2B campaign marketing: account-based programs, paid media, and marketing automation. Alongside that, I've grown audiences on TikTok, LinkedIn, and YouTube. Minty Ideas brings both together: the discipline of a campaign plan and the instincts of someone who makes content people actually watch.</p>
<div class="row"><a class="btn btn-primary" href="{L("about")}">More about Tyler <span class="arrow">&rarr;</span></a></div>
</div>
</div></section>

<section><div class="wrap split">
<div class="section-head" style="margin:0"><span class="eyebrow">FAQ</span><h2>Common questions</h2><p class="lede">Straight answers about how Minty Ideas works.</p><div><a class="btn btn-ghost" href="{L("faq")}">All FAQs</a></div></div>
{faq_html(home_faqs)}
</div></section>
{cta()}
'''
    nodes = [business_node(), website_node(), person_node(), webpage_node("home", title, desc), faq_node(home_faqs)]
    return page("home", title, desc, body, nodes, active="home")

def build_services():
    title = "Marketing Services: Short-Form Video, TikTok, LinkedIn, YouTube | Minty Ideas"
    desc = "Marketing services from Minty Ideas: short-form video content creation, TikTok, LinkedIn, and YouTube growth, marketing strategy consulting, and website revamps with SEO and AEO."
    trail = [("Home", "home"), ("Services", "services")]
    body = f'''
<section class="page-hero"><div class="wrap">{crumbs_html(trail)}<div class="hero-copy">
<span class="eyebrow">Services</span><h1>Marketing services for brands that want an <em>audience</em>.</h1>
<p class="answer">Minty Ideas offers six marketing services: short-form video content creation, TikTok growth, LinkedIn content strategy, YouTube channel growth, marketing strategy consulting, and website revamps with SEO and AEO. Hire one service or combine them into a full growth program.</p>
</div></div></section>
<section class="paper"><div class="wrap">{service_cards()}</div></section>
<section><div class="wrap"><div class="section-head"><span class="eyebrow">How it works</span><h2>Ideate. Create. <em>Share.</em></h2></div>{steps_html()}</div></section>
{cta()}'''
    nodes = [business_node(), webpage_node("services", title, desc), crumbs_node(trail),
             {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": s["name"], "url": url(s["key"])} for i, s in enumerate(SERVICES)]}]
    return page("services", title, desc, body, nodes, active="services")

def build_service(s):
    trail = [("Home", "home"), ("Services", "services"), (s["short"].capitalize() if s["short"][0].islower() else s["short"], s["key"])]
    inc = "".join(f"<li><div><strong>{e(t)}</strong><span>{e(d)}</span></div></li>" for t, d in s["included"])
    who = "".join(f"<li><div><span>{e(w)}</span></div></li>" for w in s["for"])
    others = [o for o in SERVICES if o["key"] != s["key"]][:3]
    rel = "".join(f'<a href="{L(o["key"])}"><h3>{e(o["short"].capitalize() if o["short"][0].islower() else o["short"])}</h3><span>{e(o["card"])}</span></a>' for o in others)
    body = f'''
<section class="page-hero"><div class="wrap">{crumbs_html(trail)}<div class="hero-copy">
<span class="eyebrow">{e(s["kicker"])}</span><h1>{s["h1"]}</h1>
<p class="answer">{e(s["answer"])}</p>
<div class="row"><a class="btn btn-primary" href="{L("contact")}">Talk about your goals <span class="arrow">&rarr;</span></a><a class="btn btn-ghost" href="#faq">Read the FAQ</a></div>
</div></div></section>
<section><div class="wrap split">
<div class="section-head" style="margin:0"><span class="eyebrow">What's included</span><h2>What you get with {e(s["short"].lower() if not s["short"].startswith(("TikTok","LinkedIn","YouTube")) else s["short"])}</h2><p class="lede">Every engagement is scoped to your goals. These are the building blocks.</p></div>
<ul class="checks">{inc}</ul>
</div></section>
<section class="paper"><div class="wrap split">
<div class="section-head" style="margin:0"><span class="eyebrow">Who it's for</span><h2>A good fit if you are&hellip;</h2></div>
<ul class="checks">{who}</ul>
</div></section>
<section class="band"><div class="wrap"><div class="section-head"><span class="eyebrow">How it works</span><h2>Ideate. Create. <em>Share.</em></h2></div>{steps_html(compact=True)}</div></section>
<section id="faq"><div class="wrap split">
<div class="section-head" style="margin:0"><span class="eyebrow">FAQ</span><h2>{e(s["short"].capitalize() if s["short"][0].islower() else s["short"])} questions</h2></div>
{faq_html(s["faqs"])}
</div></section>
<section style="padding-top:0"><div class="wrap"><div class="section-head"><span class="eyebrow">Related services</span><h2>Pairs well with</h2></div><div class="related">{rel}</div></div></section>
{cta()}'''
    nodes = [business_node(), webpage_node(s["key"], s["title"], s["meta"]), crumbs_node(trail),
             {"@type": "Service", "@id": url(s["key"]) + "#service", "name": s["name"], "serviceType": s["name"], "description": s["answer"],
              "provider": {"@id": BUSINESS_ID}, "areaServed": {"@type": "Country", "name": "United States"}, "url": url(s["key"])},
             faq_node(s["faqs"])]
    return page(s["key"], s["title"], s["meta"], body, nodes, active="services")

def build_about():
    title = "About Tyler Minear, Founder of Minty Ideas"
    desc = "Tyler Minear is the founder of Minty Ideas, a Tempe, Arizona marketing consultancy. Background in B2B campaign marketing and growing audiences on TikTok, LinkedIn, and YouTube."
    trail = [("Home", "home"), ("About", "about")]
    body = f'''
<section class="page-hero"><div class="wrap">{crumbs_html(trail)}<div class="hero-copy">
<span class="eyebrow">About</span><h1>Hi, I'm <em>Tyler</em>.</h1>
<p class="answer">Tyler Minear is the founder of Minty Ideas, a marketing consultancy based in Tempe, Arizona. She combines a background in B2B campaign marketing with hands-on experience creating short-form video and growing engaged communities on TikTok, LinkedIn, and YouTube.</p>
</div></div></section>
<section><div class="wrap split">
<div class="portrait"><span>TM</span><!-- REPLACE: <img src="/tyler.jpg" alt="Tyler Minear, founder of Minty Ideas" width="800" height="1000"> --></div>
<div class="prose">
<span class="eyebrow">My story</span>
<h2>Why Minty Ideas exists</h2>
<p>I've spent my career in campaign marketing, running <strong>account-based marketing programs, paid media, and marketing automation</strong> for B2B technology companies. That work taught me how to plan campaigns, read the data, and connect marketing to revenue.</p>
<p>Outside of that, I've been making content. I've <strong>grown audiences on TikTok, LinkedIn, and YouTube</strong>, including a personal TikTok that reached {fmt(max(v["views"] for v in WORK_VIDEOS))} views, and brand TikToks for Posit that earned {fmt(totals("brand")[0])} views with a technical audience. That taught me firsthand what makes people stop, watch, comment, and follow. <a href="{L("work")}">See the videos</a>.</p>
<p>Most brands get one half of that equation. They have a strategy and no content people want to watch, or they post constantly with no plan behind it. Minty Ideas exists to bring both together.</p>
<p>The name is a reminder of the standard I hold the work to: ideas that feel fresh, and growth that stays green long after a trend fades.</p>
</div>
</div></section>
<section class="paper"><div class="wrap">
<div class="section-head"><span class="eyebrow">How I work</span><h2>What clients can expect</h2></div>
<ul class="checks">
<li><div><strong>Native content, not ads in disguise</strong><span>Videos and posts made the way each platform's audience actually watches and reads.</span></div></li>
<li><div><strong>Systems your team can keep</strong><span>Formats, templates, and calendars that outlast our engagement.</span></div></li>
<li><div><strong>Plain-language reporting</strong><span>A monthly read-out of what worked, what did not, and what is next. No vanity dashboards.</span></div></li>
<li><div><strong>Remote-friendly, Arizona-based</strong><span>Based in Tempe, working with clients across the United States.</span></div></li>
</ul>
</div></section>
{cta("Want to work together?", "I take on a small number of clients at a time so each one gets real attention. Tell me about yours.")}'''
    nodes = [business_node(), person_node(), {**webpage_node("about", title, desc), "@type": "AboutPage", "mainEntity": {"@id": PERSON_ID}}, crumbs_node(trail)]
    return page("about", title, desc, body, nodes, active="about")

def build_faq():
    title = "FAQ: Working With Minty Ideas"
    desc = "Answers to common questions about Minty Ideas: services, platforms, pricing, timelines, how results are measured, and how to get started."
    trail = [("Home", "home"), ("FAQ", "faq")]
    svc_faqs = [(q, a) for s in SERVICES for q, a in s["faqs"][:1]]
    body = f'''
<section class="page-hero"><div class="wrap">{crumbs_html(trail)}<div class="hero-copy">
<span class="eyebrow">FAQ</span><h1>Frequently asked <em>questions</em></h1>
<p class="answer">Quick answers about Minty Ideas, a marketing consultancy in Tempe, Arizona that specializes in short-form video and community growth on TikTok, LinkedIn, and YouTube. Have a question that is not here? Email {EMAIL}.</p>
</div></div></section>
<section><div class="wrap split">
<div class="section-head" style="margin:0"><span class="eyebrow">General</span><h2>Working together</h2></div>
{faq_html(GENERAL_FAQS)}
</div></section>
<section class="paper"><div class="wrap split">
<div class="section-head" style="margin:0"><span class="eyebrow">By service</span><h2>Platforms and services</h2><p class="lede">Each service page has more detail.</p></div>
{faq_html(svc_faqs, open_first=False)}
</div></section>
{cta()}'''
    nodes = [business_node(), webpage_node("faq", title, desc), crumbs_node(trail), faq_node(GENERAL_FAQS + svc_faqs)]
    return page("faq", title, desc, body, nodes, active="faq")

def build_contact():
    title = "Contact Minty Ideas | Book a Marketing Consultation"
    desc = f"Contact Minty Ideas to talk about short-form video, TikTok, LinkedIn, or YouTube growth, marketing strategy, or a website revamp. Email {EMAIL}."
    trail = [("Home", "home"), ("Contact", "contact")]
    chips = "".join(f'<label><input type="checkbox" name="services" value="{e(s["short"])}" id="svc-{s["key"]}"> {e(s["short"].capitalize() if s["short"][0].islower() else s["short"])}</label>' for s in SERVICES)
    # GitHub Pages is static, so FormSubmit (formsubmit.co) emails each submission to EMAIL.
    action = f' action="https://formsubmit.co/{EMAIL}"' if MODE == "prod" else ""
    hidden = (f'<input type="hidden" name="_next" value="{url("contact")}?sent=1">'
              '<input type="hidden" name="_subject" value="New inquiry from mintyideas.com">'
              '<input type="hidden" name="_template" value="table">') if MODE == "prod" else ""
    body = f'''
<section class="page-hero"><div class="wrap">{crumbs_html(trail)}<div class="hero-copy">
<span class="eyebrow">Contact</span><h1>Let's talk about your <em>growth</em>.</h1>
<p class="answer">To work with Minty Ideas, fill out the form below or email {EMAIL}. Share what you are working on and which platforms matter most, and you will hear back within two business days to set up a free intro call.</p>
</div></div></section>
<section><div class="wrap split">
<form class="contact" name="contact" method="POST"{action}>
{hidden}
<p class="hp"><label for="company_url">Leave this empty</label><input id="company_url" name="_honey" tabindex="-1" autocomplete="off"></p>
<div class="two">
<div class="field"><label for="name">Name</label><input id="name" name="name" autocomplete="name" required></div>
<div class="field"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required></div>
</div>
<div class="two">
<div class="field"><label for="company">Company or brand</label><input id="company" name="company" autocomplete="organization"></div>
<div class="field"><label for="website">Website or main social profile</label><input id="website" name="website" inputmode="url" placeholder="https://"></div>
</div>
<fieldset><legend>What are you interested in?</legend><div class="chips">{chips}</div></fieldset>
<div class="field"><label for="budget">Monthly budget</label>
<select id="budget" name="budget"><option value="">Select a range</option><option>Under $2,500</option><option>$2,500 to $5,000</option><option>$5,000 to $10,000</option><option>$10,000+</option><option>Not sure yet</option></select></div>
<div class="field"><label for="message">What are you working on?</label><textarea id="message" name="message" required placeholder="Your goals, current channels, and timeline"></textarea></div>
<div class="row"><button class="btn btn-primary" type="submit">Send message <span class="arrow">&rarr;</span></button></div>
<p class="form-note" hidden></p>
</form>
<aside class="contact-aside">
<div class="box"><span class="eyebrow">Email</span><a class="email-line" href="mailto:{EMAIL}">{EMAIL}</a><p>Prefer email? Write directly. Replies within two business days.</p></div>
<div class="box"><span class="eyebrow">Location</span><h3>{CITY}, Arizona</h3><p>Working remotely with clients across the United States.</p></div>
<div class="box"><span class="eyebrow">What happens next</span><p>1. You send a note. 2. We hop on a 30-minute intro call. 3. You get a written proposal with scope and pricing.</p></div>
</aside>
</div></section>'''
    nodes = [business_node(), {**webpage_node("contact", title, desc), "@type": "ContactPage"}, crumbs_node(trail)]
    return page("contact", title, desc, body, nodes, active="contact")

def build_404():
    body = f'''<section><div class="wrap center-404"><span class="eyebrow">404</span><h1>This page <em>wandered off</em>.</h1>
<p class="lede">The page you are looking for does not exist or has moved.</p>
<div class="row"><a class="btn btn-primary" href="{L("home")}">Back to home</a><a class="btn btn-ghost" href="{L("services")}">See services</a></div></div></section>'''
    return page(None, "Page not found | Minty Ideas", "This page could not be found.", body, None, noindex=True)


# ---------- work / portfolio ----------
import re as _re
PLAT = {"tiktok": "TikTok", "youtube": "YouTube", "linkedin": "LinkedIn", "instagram": "Instagram"}

def parse_media(v):
    """Return (embed_src, ratio, thumb) for a video entry, or (None, ratio, None)."""
    u, p = v.get("url", ""), v["platform"]
    if not u:
        return None, ("16/9" if p == "youtube" else "4/5" if p == "linkedin" else "9/16"), None
    if p == "tiktok":
        m = _re.search(r"/(video|photo)/(\d+)", u)
        if not m: return None, "9/16", None
        # TikTok's official Embed Player (works for videos and photo posts)
        return (f"https://www.tiktok.com/player/v1/{m.group(2)}?rel=0&music_info=0&description=0", "9/16", None)
    if p == "youtube":
        m = _re.search(r"(?:v=|youtu\.be/|/shorts/|/embed/)([\w-]{11})", u)
        if not m: return None, "16/9", None
        vid = m.group(1)
        return f"https://www.youtube-nocookie.com/embed/{vid}?autoplay=1&rel=0", ("9/16" if "/shorts/" in u else "16/9"), f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
    if p == "instagram":
        m = _re.search(r"instagram\.com/(?:[\w.]+/)?(reel|p|tv)/([\w-]+)", u)
        return (f"https://www.instagram.com/{m.group(1)}/{m.group(2)}/embed" if m else None), "9/16", None
    if p == "linkedin":
        m = _re.search(r"urn:li:(activity|share|ugcPost):(\d+)", u) or _re.search(r"(activity)[-:](\d{15,})", u)
        return (f"https://www.linkedin.com/embed/feed/update/urn:li:{m.group(1)}:{m.group(2)}" if m else None), "4/5", None
    return None, "9/16", None

def fmt(n):
    if n >= 1_000_000: s = f"{n/1_000_000:.1f}".rstrip("0").rstrip(".") + "M"
    elif n >= 10_000: s = f"{n/1_000:.1f}".rstrip("0").rstrip(".") + "K"
    else: s = f"{n:,}"
    return s

BG_CYCLE = ["rain-ripples", "liquid-light", "amber-glass"]
def video_card(v, i=0):
    src, ratio, thumb = parse_media(v)
    plat = PLAT[v["platform"]]
    bg = thumb or asset(BG_CYCLE[i % 3] + "-sm.webp")
    title = f'<span class="vc-title">{e(v["title"])}</span>' if v.get("title") else ""
    meta = f'<span class="vc-meta"><span>{fmt(v["likes"])} likes</span><span>{fmt(v["comments"])} comments</span></span>'
    inner = f"""<span class="vc-top"><span class="vc-plat">{plat}</span><span class="vc-acct">{e(v["account"])}</span></span>
<span class="vc-play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></span>
<span class="vc-bottom">{title}<span class="vc-stat">{fmt(v["views"])}<small> views</small></span>{meta}</span>"""
    attrs = f' data-embed="{e(src)}"' if src else ""
    label = v.get("title") or f'{fmt(v["views"])}-view video by {v["account"]}'
    return (f'<a class="vc" href="{e(v["url"])}" target="_blank" rel="noopener" data-platform="{v["platform"]}" data-group="{v["group"]}"{attrs}'
            f' style="--ratio:{ratio};--thumb:url({bg})" aria-label="Watch on {plat}: {e(label)}">{inner}</a>')

def embed_card(v, src):
    """Live site: the real TikTok player, embedded. Shows the video's own cover and plays in place."""
    label = v.get("title") or f'TikTok by {v["account"]}, {fmt(v["views"])} views'
    title = f'<p class="ve-title">{e(v["title"])}</p>' if v.get("title") else ""
    return f"""<figure class="ve" data-group="{v["group"]}" data-platform="{v["platform"]}">
<div class="ve-frame"><iframe src="{e(src)}" title="{e(label)}" loading="lazy" allow="encrypted-media; fullscreen; picture-in-picture; clipboard-write" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe></div>
<figcaption>{title}<div class="ve-row"><span class="ve-views">{fmt(v["views"])}<small> views</small></span><a class="ve-open" href="{e(v["url"])}" target="_blank" rel="noopener">Open on TikTok &#8599;</a></div>
<div class="ve-meta"><span>{e(v["account"])}</span><span>{fmt(v["likes"])} likes</span><span>{fmt(v["comments"])} comments</span></div></figcaption>
</figure>"""

def video_grid(vids):
    vids = sorted(vids, key=lambda v: -v["views"])
    out = []
    for i, v in enumerate(vids):
        src = parse_media(v)[0]
        out.append(embed_card(v, src) if (src and MODE == "prod") else video_card(v, i))
    return '<div class="vgrid">' + "".join(out) + "</div>"

def totals(group=None):
    vs = [v for v in WORK_VIDEOS if group is None or v["group"] in (group if isinstance(group, tuple) else (group,))]
    return sum(v["views"] for v in vs), sum(v["likes"] for v in vs), sum(v["comments"] for v in vs), len(vs)

def campaign_card(c):
    chips = "".join(f"<li>{e(ch)}</li>" for ch in c["channels"])
    res = "".join(f"<li>{e(r)}</li>" for r in c["results"])
    return f"""<article class="case">
<header><span class="kicker">{e(c["client"])}</span><h3>{e(c["name"])}</h3><ul class="case-chips">{chips}</ul></header>
<dl><div><dt>The challenge</dt><dd>{e(c["challenge"])}</dd></div><div><dt>What I did</dt><dd>{e(c["approach"])}</dd></div></dl>
<div class="case-results"><span class="kicker">Results</span><ul>{res}</ul></div>
</article>"""

def build_work():
    title = "Work: Viral TikTok and Short-Form Video Examples | Minty Ideas"
    desc = "Short-form video examples by Tyler Minear of Minty Ideas: viral TikToks including one with 3.3M views, Posit PBC brand TikToks, and marketing campaigns."
    trail = [("Home", "home"), ("Work", "work")]
    mine = [v for v in WORK_VIDEOS if v["group"] in ("personal", "spiritual")]
    brand = [v for v in WORK_VIDEOS if v["group"] == "brand"]
    tv, tl, tc, tn = totals()
    mv, ml, mc, mn = totals(("personal", "spiritual"))
    bv, bl, bc, bn = totals("brand")
    top = max(WORK_VIDEOS, key=lambda v: v["views"])
    groups = [("all", "All"), ("personal", "@imarcadia"), ("spiritual", "@selfspiritualcrystals"), ("brand", "Posit PBC")]
    filt = "".join(f'<button type="button" class="filter" data-filter="{g}" aria-pressed="{"true" if g == "all" else "false"}">{n}</button>' for g, n in groups if g == "all" or any(v["group"] == g for v in WORK_VIDEOS))
    chans = "".join(
        (f'<a class="chan" href="{u}" target="_blank" rel="noopener"><span class="vc-plat">{n}</span><strong>{e(h)}</strong><span>View channel &rarr;</span></a>' if u
         else f'<div class="chan vc-empty"><span class="vc-plat">{n}</span><strong>{e(h)}</strong><span>[Add profile link]</span></div>')
        for n, h, u in BRAND_CHANNELS)
    cases = "".join(campaign_card(c) for c in CAMPAIGNS)
    body = f"""
<section class="page-hero"><div class="wrap">{crumbs_html(trail)}<div class="hero-copy">
<span class="eyebrow">Work</span><h1>Selected <em>work</em> and campaigns</h1>
<p class="answer">Examples of short-form video and campaigns by Tyler Minear, founder of Minty Ideas. The {tn} TikToks on this page have earned {fmt(tv)} organic views, {fmt(tl)} likes, and {fmt(tc)} comments, including a personal video with {fmt(top["views"])} views and brand content for Posit PBC with {fmt(bv)} combined views.</p>
<dl class="work-stats">
<div><dt>{fmt(tv)}</dt><dd>organic views</dd></div>
<div><dt>{fmt(tl)}</dt><dd>likes</dd></div>
<div><dt>{fmt(tc)}</dt><dd>comments</dd></div>
<div><dt>{fmt(top["views"])}</dt><dd>views on one video</dd></div>
</dl>
<div class="filters" role="group" aria-label="Filter by account">{filt}</div>
</div></div></section>

<section class="work-sec" data-sec><div class="wrap">
<div class="section-head"><span class="eyebrow">My own accounts</span><h2>Videos that <em>broke out</em></h2>
<p class="lede">{fmt(mv)} views across {mn} videos from my personal TikTok, @imarcadia, and my spiritual content account, @selfspiritualcrystals. Press play on any video to watch it here.</p></div>
{video_grid(mine)}
</div></section>

<section class="work-sec band" data-sec><div class="wrap">
<div class="section-head"><span class="eyebrow">Brand content</span><h2>Making data science <em>scroll-stopping</em></h2>
<p class="lede">Short-form video for Posit PBC, the open-source data science company: {fmt(bv)} views and {fmt(bl)} likes across {bn} TikToks, for a technical B2B audience. {e(BRAND_NOTE)}</p></div>
{video_grid(brand)}
<div class="chans">{chans}</div>
</div></section>

<section class="paper" id="campaigns"><div class="wrap">
<div class="section-head"><span class="eyebrow">Campaigns</span><h2>Campaigns I've helped <em>run</em></h2>
<p class="lede">Integrated programs across paid, organic, and owned channels, from planning to reporting.</p></div>
<div class="cases">{cases}</div>
</div></section>
{cta("Want results like these for your brand?", "Tell me which platforms matter most and what you want to grow. I will reply within two business days with next steps.")}"""
    items = [{"@type": "ListItem", "position": i + 1, "item": {"@type": "CreativeWork", "name": v["title"] or f'TikTok by {v["account"]} ({fmt(v["views"])} views)', "url": v["url"],
              "creator": {"@id": PERSON_ID}, "genre": "Short-form video"}} for i, v in enumerate(WORK_VIDEOS) if v.get("url")]
    nodes = [business_node(), person_node(), {**webpage_node("work", title, desc), "@type": "CollectionPage"}, crumbs_node(trail)]
    if items:
        nodes.append({"@type": "ItemList", "name": "Selected work", "itemListElement": items})
    return page("work", title, desc, body, nodes, active="work")

# ---------- write ----------
def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)

def out_path(base, key):
    if MODE == "prod":
        p = PAGES[key]["prod"].strip("/")
        return os.path.join(base, p, "index.html") if p else os.path.join(base, "index.html")
    return os.path.join(base, "index.html" if key == "home" else PAGES[key]["prev"])

def build(mode):
    global MODE
    MODE = mode
    base = os.path.join(DIST, "site" if mode == "prod" else "preview")
    shutil.rmtree(base, ignore_errors=True)
    os.makedirs(base)
    write(out_path(base, "home"), build_home())
    write(out_path(base, "services"), build_services())
    for s in SERVICES:
        write(out_path(base, s["key"]), build_service(s))
    write(out_path(base, "work"), build_work())
    write(out_path(base, "about"), build_about())
    write(out_path(base, "faq"), build_faq())
    write(out_path(base, "contact"), build_contact())
    write(os.path.join(base, "404.html"), build_404())
    for f in ["styles.css", "main.js"]:
        shutil.copy(os.path.join(ROOT, f), base)
    assets = os.path.join(ROOT, "assets")
    if os.path.isdir(assets):
        for f in os.listdir(assets):
            shutil.copy(os.path.join(assets, f), base)
    if mode == "prod":
        write_seo_files(base)
    return base

def write_seo_files(base):
    keys = list(PAGES.keys())
    pri = {"home": "1.0", "services": "0.9", "work": "0.9", "contact": "0.8", "about": "0.7", "faq": "0.7"}
    urls = "".join(f"<url><loc>{url(k)}</loc><lastmod>{TODAY}</lastmod><priority>{pri.get(k, '0.8')}</priority></url>\n" for k in keys)
    write(os.path.join(base, "sitemap.xml"), f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    bots = ["Googlebot", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot", "Applebot-Extended"]
    robots = "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)
    write(os.path.join(base, "robots.txt"), f"# Search engines and AI answer engines are welcome here.\n{robots}User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    svc_lines = "\n".join(f"- [{s['name']}]({url(s['key'])}): {s['card']}" for s in SERVICES)
    faq_lines = "\n".join(f"### {q}\n{a}\n" for q, a in GENERAL_FAQS)
    write(os.path.join(base, "llms.txt"), f"""# {BRAND}

> {BRAND} is a marketing consultancy founded by {FOUNDER} and based in {CITY}, Arizona. It specializes in short-form video content creation and growing engaged communities on TikTok, LinkedIn, and YouTube, and also offers marketing strategy consulting and website revamps with SEO and answer engine optimization (AEO). Contact: {EMAIL}.

## Services

{svc_lines}

## About

- [About {FOUNDER}]({url('about')}): Founder background in B2B campaign marketing (account-based marketing, paid media, marketing automation) and hands-on audience growth on TikTok, LinkedIn, and YouTube.
- [Work and campaigns]({url('work')}): Examples of viral TikToks, Posit PBC brand content on TikTok, Instagram, YouTube, and LinkedIn, and marketing campaigns.
- [FAQ]({url('faq')}): Services, platforms, pricing approach, measurement, and how to get started.
- [Contact]({url('contact')}): Contact form and email.

## Key facts

- Business name: {BRAND}
- Founder: {FOUNDER}
- Location: {CITY}, Arizona, USA (serves clients remotely across the United States)
- Email: {EMAIL}
- Website: {DOMAIN}
- Specialties: short-form video, TikTok marketing, LinkedIn content strategy and ghostwriting, YouTube and YouTube Shorts growth, community management, B2B marketing strategy, website revamps, SEO, AEO

## Frequently asked questions

{faq_lines}""")
    write(os.path.join(base, "site.webmanifest"), json.dumps({"name": BRAND, "short_name": "Minty Ideas", "icons": [
        {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}],
        "theme_color": "#0b120e", "background_color": "#0b120e", "display": "standalone", "start_url": "/"}, indent=1))
    # GitHub Pages custom domain. www.mintyideas.com redirects here automatically once its DNS points at GitHub.
    write(os.path.join(base, "CNAME"), DOMAIN.split("://", 1)[1] + "\n")

if __name__ == "__main__":
    print(build("prod"))
    print(build("preview"))
