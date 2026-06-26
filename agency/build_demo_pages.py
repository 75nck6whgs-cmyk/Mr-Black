#!/usr/bin/env python3
"""
Generates real HTML landing pages for all demo leads.
No API key needed — pages are handcrafted per business type.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.state import StateManager

state = StateManager()
BUILT_DIR = Path(__file__).resolve().parent / "state" / "built"
BUILT_DIR.mkdir(parents=True, exist_ok=True)


# ── Shared HTML components ─────────────────────────────────────────────────

def _google_font(name: str) -> str:
    slug = name.replace(" ", "+")
    return f'@import url("https://fonts.googleapis.com/css2?family={slug}:wght@400;600;700;800&display=swap");'


def _base_css_modern() -> str:
    return """
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Inter',sans-serif;background:#f8fafc;color:#1e293b}
    a{color:inherit;text-decoration:none}
    .btn{display:inline-block;padding:14px 32px;border-radius:8px;font-weight:700;font-size:16px;cursor:pointer;transition:all .2s;border:none}
    .btn-primary{background:#2563eb;color:#fff}
    .btn-primary:hover{background:#1d4ed8;transform:translateY(-1px)}
    .container{max-width:1100px;margin:0 auto;padding:0 20px}
    @media(max-width:768px){.container{padding:0 16px}}
    """


def _base_css_elegant() -> str:
    return """
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Playfair Display',serif;background:#1a1a1a;color:#faf9f6}
    a{color:inherit;text-decoration:none}
    .btn{display:inline-block;padding:14px 36px;border-radius:0;font-weight:600;font-size:15px;cursor:pointer;transition:all .25s;border:2px solid #c9a84c;font-family:'Lato',sans-serif;letter-spacing:.08em}
    .btn-primary{background:#c9a84c;color:#1a1a1a}
    .btn-primary:hover{background:transparent;color:#c9a84c}
    .container{max-width:1100px;margin:0 auto;padding:0 24px}
    @media(max-width:768px){.container{padding:0 16px}}
    """


def _base_css_bold() -> str:
    return """
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Montserrat',sans-serif;background:#f1faee;color:#1d3557}
    a{color:inherit;text-decoration:none}
    .btn{display:inline-block;padding:16px 36px;border-radius:4px;font-weight:800;font-size:16px;cursor:pointer;transition:all .15s;border:none;text-transform:uppercase;letter-spacing:.05em}
    .btn-primary{background:#e63946;color:#fff}
    .btn-primary:hover{background:#c1121f;transform:scale(1.02)}
    .container{max-width:1100px;margin:0 auto;padding:0 20px}
    @media(max-width:768px){.container{padding:0 16px}}
    """


# ── Page generators per business type ─────────────────────────────────────

def _restaurant_modern(biz: dict) -> str:
    name = biz["name"]; phone = biz.get("phone",""); addr = biz["address"]
    rating = biz["rating"]; reviews = biz["reviews"]
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name}</title>
<style>
{_google_font('Inter')}
{_base_css_modern()}
nav{{background:#fff;box-shadow:0 1px 8px rgba(0,0,0,.08);padding:16px 0;position:sticky;top:0;z-index:100}}
nav .inner{{display:flex;justify-content:space-between;align-items:center}}
.logo{{font-size:22px;font-weight:800;color:#2563eb}}
.nav-cta{{padding:10px 22px;background:#2563eb;color:#fff;border-radius:6px;font-weight:700;font-size:14px}}
.hero{{background:linear-gradient(135deg,#1e293b 0%,#2563eb 100%);color:#fff;padding:100px 0 80px;text-align:center}}
.hero h1{{font-size:clamp(36px,6vw,64px);font-weight:800;line-height:1.1;margin-bottom:16px}}
.hero p{{font-size:20px;opacity:.85;margin-bottom:32px;max-width:560px;margin-left:auto;margin-right:auto}}
.stars{{font-size:24px;margin-bottom:8px}}
.rating-text{{font-size:15px;opacity:.7;margin-bottom:36px}}
.hero-img{{width:100%;max-height:480px;object-fit:cover;border-radius:16px;margin-top:48px;box-shadow:0 24px 64px rgba(0,0,0,.3)}}
.section{{padding:72px 0}}
.section-title{{font-size:36px;font-weight:800;margin-bottom:8px;color:#1e293b}}
.section-sub{{font-size:18px;color:#64748b;margin-bottom:48px}}
.menu-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}}
.menu-card{{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.07)}}
.menu-card img{{width:100%;height:200px;object-fit:cover}}
.menu-card-body{{padding:20px}}
.menu-card-body h3{{font-size:20px;font-weight:700;margin-bottom:6px}}
.menu-card-body p{{color:#64748b;font-size:14px;margin-bottom:12px}}
.price{{font-size:22px;font-weight:800;color:#2563eb}}
.info-strip{{background:#2563eb;color:#fff;padding:56px 0;text-align:center}}
.info-strip h2{{font-size:32px;font-weight:800;margin-bottom:24px}}
.info-cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:24px;max-width:800px;margin:0 auto}}
.info-col h4{{font-size:14px;opacity:.7;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px}}
.info-col p{{font-size:18px;font-weight:600}}
footer{{background:#0f172a;color:#64748b;padding:32px 0;text-align:center;font-size:14px}}
footer a{{color:#2563eb}}
@media(max-width:600px){{.hero{{padding:64px 0 48px}}.info-cols{{grid-template-columns:1fr 1fr}}}}
</style></head><body>
<nav><div class="container inner">
  <div class="logo">{name}</div>
  <a href="tel:{phone}" class="nav-cta">Call Now</a>
</div></nav>
<section class="hero"><div class="container">
  <div class="stars">⭐⭐⭐⭐⭐</div>
  <p class="rating-text">{rating} stars · {reviews} happy customers</p>
  <h1>Authentic Flavors,<br>Straight from the Heart</h1>
  <p>Fresh ingredients, family recipes, unforgettable dining. Experience the taste that keeps {reviews}+ customers coming back.</p>
  <a href="tel:{phone}" class="btn btn-primary">Reserve a Table →</a>
  <br><img src="https://picsum.photos/seed/restaurant42/1100/480" alt="Restaurant interior" class="hero-img">
</div></section>
<section class="section"><div class="container">
  <div class="section-title">Our Menu</div>
  <div class="section-sub">Fresh, made-to-order dishes crafted daily</div>
  <div class="menu-grid">
    <div class="menu-card"><img src="https://picsum.photos/seed/food1/600/400" alt="Tacos"><div class="menu-card-body"><h3>Signature Tacos</h3><p>Slow-cooked meats with fresh salsa, guac & house-made tortillas</p><span class="price">$14</span></div></div>
    <div class="menu-card"><img src="https://picsum.photos/seed/food2/600/400" alt="Enchiladas"><div class="menu-card-body"><h3>Enchiladas Rojas</h3><p>Traditional red sauce over corn tortillas with queso fresco</p><span class="price">$16</span></div></div>
    <div class="menu-card"><img src="https://picsum.photos/seed/food3/600/400" alt="Burrito"><div class="menu-card-body"><h3>Super Burrito</h3><p>Massive hand-rolled burrito with your choice of protein</p><span class="price">$13</span></div></div>
  </div>
</div></section>
<div class="info-strip"><div class="container">
  <h2>Come Visit Us</h2>
  <div class="info-cols">
    <div class="info-col"><h4>Address</h4><p>{addr}</p></div>
    <div class="info-col"><h4>Phone</h4><p><a href="tel:{phone}" style="color:#fff">{phone}</a></p></div>
    <div class="info-col"><h4>Hours</h4><p>Mon–Sun 11am–10pm</p></div>
    <div class="info-col"><h4>Rating</h4><p>⭐ {rating} / 5.0</p></div>
  </div>
</div></div>
<footer><div class="container">
  <p>© 2025 {name} · {addr} · <a href="tel:{phone}">{phone}</a></p>
  <p style="margin-top:8px;font-size:12px">Demo site by <strong>NobleWeb Agency</strong> — your real site: $400, 48-hour delivery</p>
</div></footer>
</body></html>"""


def _generic_modern(biz: dict, tagline: str, service1: str, service2: str, service3: str) -> str:
    name = biz["name"]; phone = biz.get("phone",""); addr = biz["address"]
    rating = biz["rating"]; reviews = biz["reviews"]; btype = biz["type"].replace("_"," ").title()
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name}</title>
<style>
{_google_font('Inter')}
{_base_css_modern()}
nav{{background:#fff;padding:18px 0;box-shadow:0 1px 8px rgba(0,0,0,.07);position:sticky;top:0;z-index:100}}
nav .inner{{display:flex;justify-content:space-between;align-items:center}}
.logo{{font-size:20px;font-weight:800;color:#2563eb}}
.nav-cta{{padding:10px 22px;background:#2563eb;color:#fff;border-radius:6px;font-weight:700;font-size:14px}}
.hero{{background:linear-gradient(160deg,#0f172a,#1e3a8a);color:#fff;padding:96px 0 72px;text-align:center}}
.hero h1{{font-size:clamp(32px,5vw,58px);font-weight:800;line-height:1.1;margin-bottom:16px}}
.hero p{{font-size:18px;opacity:.8;max-width:520px;margin:0 auto 32px}}
.badge{{display:inline-block;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);border-radius:100px;padding:6px 18px;font-size:14px;margin-bottom:20px}}
.services{{padding:72px 0;background:#fff}}
.services h2{{text-align:center;font-size:36px;font-weight:800;margin-bottom:8px}}
.services .sub{{text-align:center;color:#64748b;font-size:17px;margin-bottom:48px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:24px}}
.card{{background:#f8fafc;border-radius:16px;padding:32px;border:1px solid #e2e8f0}}
.card .icon{{font-size:36px;margin-bottom:16px}}
.card h3{{font-size:20px;font-weight:700;margin-bottom:10px;color:#1e293b}}
.card p{{color:#64748b;line-height:1.6}}
.cta-band{{background:#2563eb;color:#fff;text-align:center;padding:72px 0}}
.cta-band h2{{font-size:36px;font-weight:800;margin-bottom:16px}}
.cta-band p{{font-size:18px;opacity:.85;margin-bottom:32px}}
.btn-white{{background:#fff;color:#2563eb}}
.btn-white:hover{{background:#eff6ff}}
.contact{{padding:64px 0;background:#0f172a;color:#fff;text-align:center}}
.contact h2{{font-size:32px;font-weight:800;margin-bottom:32px}}
.contact-row{{display:flex;flex-wrap:wrap;justify-content:center;gap:32px}}
.contact-item h4{{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:#64748b;margin-bottom:6px}}
.contact-item p{{font-size:18px;font-weight:600}}
footer{{background:#020617;color:#475569;padding:24px 0;text-align:center;font-size:13px}}
</style></head><body>
<nav><div class="container inner">
  <div class="logo">{name}</div>
  <a href="tel:{phone}" class="nav-cta">Call Now</a>
</div></nav>
<section class="hero"><div class="container">
  <div class="badge">⭐ {rating} stars · {reviews} verified reviews</div>
  <h1>{tagline}</h1>
  <p>Trusted by {reviews}+ customers in {biz['city']}. Professional, reliable, and always on time.</p>
  <a href="tel:{phone}" class="btn btn-primary">Get a Free Quote →</a>
</div></section>
<section class="services"><div class="container">
  <h2>What We Do</h2>
  <div class="sub">Professional {btype} services you can trust</div>
  <div class="grid">
    <div class="card"><div class="icon">✅</div><h3>{service1['title']}</h3><p>{service1['desc']}</p></div>
    <div class="card"><div class="icon">⚡</div><h3>{service2['title']}</h3><p>{service2['desc']}</p></div>
    <div class="card"><div class="icon">🛡️</div><h3>{service3['title']}</h3><p>{service3['desc']}</p></div>
  </div>
</div></section>
<div class="cta-band"><div class="container">
  <h2>Ready to Get Started?</h2>
  <p>Call us today for a free consultation. No pressure, no hidden fees.</p>
  <a href="tel:{phone}" class="btn btn-white">📞 {phone}</a>
</div></div>
<section class="contact"><div class="container">
  <h2>Find Us</h2>
  <div class="contact-row">
    <div class="contact-item"><h4>Address</h4><p>{addr}</p></div>
    <div class="contact-item"><h4>Phone</h4><p><a href="tel:{phone}" style="color:#93c5fd">{phone}</a></p></div>
    <div class="contact-item"><h4>Rating</h4><p>⭐ {rating} / 5.0 ({reviews} reviews)</p></div>
  </div>
</div></section>
<footer><div class="container">
  <p>© 2025 {name} &nbsp;·&nbsp; Demo by <strong>NobleWeb Agency</strong> — $400, 48-hour delivery</p>
</div></footer>
</body></html>"""


def _generic_elegant(biz: dict, headline: str) -> str:
    name = biz["name"]; phone = biz.get("phone",""); addr = biz["address"]
    rating = biz["rating"]; reviews = biz["reviews"]
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name}</title>
<style>
{_google_font('Playfair+Display')}
{_google_font('Lato')}
{_base_css_elegant()}
nav{{padding:24px 0;border-bottom:1px solid #333}}
nav .inner{{display:flex;justify-content:space-between;align-items:center}}
.logo{{font-size:24px;font-weight:700;color:#c9a84c;letter-spacing:.02em}}
.nav-phone{{font-family:'Lato',sans-serif;font-size:15px;color:#c9a84c;letter-spacing:.05em}}
.hero{{padding:120px 0 100px;text-align:center;border-bottom:1px solid #2a2a2a;background:radial-gradient(ellipse at center,#222 0%,#1a1a1a 70%)}}
.hero .overline{{font-family:'Lato',sans-serif;font-size:12px;letter-spacing:.2em;color:#c9a84c;text-transform:uppercase;margin-bottom:24px}}
.hero h1{{font-size:clamp(36px,5vw,64px);font-weight:700;line-height:1.15;margin-bottom:24px;color:#faf9f6}}
.hero .divider{{width:60px;height:1px;background:#c9a84c;margin:0 auto 24px}}
.hero p{{font-family:'Lato',sans-serif;font-size:18px;color:#aaa;max-width:500px;margin:0 auto 40px;line-height:1.7}}
.about{{padding:96px 0;display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center}}
.about img{{width:100%;border-radius:2px;filter:grayscale(20%)}}
.about-text .overline{{font-family:'Lato',sans-serif;font-size:11px;letter-spacing:.2em;color:#c9a84c;text-transform:uppercase;margin-bottom:16px}}
.about-text h2{{font-size:40px;font-weight:700;margin-bottom:24px;line-height:1.2}}
.about-text p{{font-family:'Lato',sans-serif;color:#bbb;line-height:1.8;margin-bottom:32px}}
.stats{{display:flex;gap:40px;margin-top:32px}}
.stat .num{{font-size:40px;font-weight:700;color:#c9a84c}}
.stat .label{{font-family:'Lato',sans-serif;font-size:13px;color:#888;margin-top:4px}}
.contact-band{{background:#111;border-top:1px solid #2a2a2a;border-bottom:1px solid #2a2a2a;padding:72px 0;text-align:center}}
.contact-band h2{{font-size:36px;font-weight:700;margin-bottom:32px}}
footer{{background:#0f0f0f;padding:28px 0;text-align:center;font-family:'Lato',sans-serif;font-size:13px;color:#555;border-top:1px solid #222}}
@media(max-width:768px){{.about{{grid-template-columns:1fr;gap:40px}}.stats{{flex-wrap:wrap;gap:24px}}}}
</style></head><body>
<nav><div class="container inner">
  <div class="logo">{name}</div>
  <a href="tel:{phone}" class="nav-phone">{phone}</a>
</div></nav>
<section class="hero"><div class="container">
  <div class="overline">Excellence · Precision · Trust</div>
  <h1>{headline}</h1>
  <div class="divider"></div>
  <p>Serving {biz['city']} with distinction. {reviews} clients trust us with what matters most.</p>
  <a href="tel:{phone}" class="btn btn-primary">Book a Consultation</a>
</div></section>
<section style="padding:0 0 96px"><div class="container">
  <div class="about">
    <img src="https://picsum.photos/seed/elegant{biz['place_id']}/700/500" alt="{name}">
    <div class="about-text">
      <div class="overline">Our Story</div>
      <h2>Crafting Excellence,<br>One Client at a Time</h2>
      <p>For years, {name} has built a reputation for exceptional quality and genuine care. Every client who walks through our door receives our full attention and expertise.</p>
      <p>With a {rating}-star rating from {reviews} satisfied customers, our track record speaks for itself.</p>
      <div class="stats">
        <div class="stat"><div class="num">{reviews}+</div><div class="label">Happy Clients</div></div>
        <div class="stat"><div class="num">{rating}</div><div class="label">Star Rating</div></div>
        <div class="stat"><div class="num">100%</div><div class="label">Satisfaction</div></div>
      </div>
    </div>
  </div>
</div></section>
<section class="contact-band"><div class="container">
  <h2>Ready to Experience the Difference?</h2>
  <a href="tel:{phone}" class="btn btn-primary">Call {phone}</a>
  <p style="font-family:'Lato',sans-serif;color:#888;margin-top:24px;font-size:14px">{addr}</p>
</div></section>
<footer><div class="container">
  © 2025 {name} &nbsp;·&nbsp; Demo by <strong style="color:#c9a84c">NobleWeb Agency</strong> — $400, ready in 48 hrs
</div></footer>
</body></html>"""


def _generic_bold(biz: dict, headline: str) -> str:
    name = biz["name"]; phone = biz.get("phone",""); addr = biz["address"]
    rating = biz["rating"]; reviews = biz["reviews"]; city = biz["city"]
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name}</title>
<style>
{_google_font('Montserrat')}
{_google_font('Open+Sans')}
{_base_css_bold()}
nav{{background:#1d3557;padding:16px 0}}
nav .inner{{display:flex;justify-content:space-between;align-items:center}}
.logo{{font-size:20px;font-weight:800;color:#fff;text-transform:uppercase;letter-spacing:.05em}}
.nav-cta{{background:#e63946;color:#fff;padding:10px 22px;border-radius:4px;font-weight:800;font-size:13px;text-transform:uppercase;letter-spacing:.06em}}
.hero{{background:#1d3557;color:#fff;padding:100px 0;text-align:center;clip-path:polygon(0 0,100% 0,100% 88%,0 100%)}}
.hero .label{{display:inline-block;background:#e63946;color:#fff;font-size:12px;font-weight:800;letter-spacing:.15em;text-transform:uppercase;padding:6px 16px;margin-bottom:24px;border-radius:2px}}
.hero h1{{font-size:clamp(36px,6vw,72px);font-weight:800;line-height:1.05;margin-bottom:20px;text-transform:uppercase;letter-spacing:-.02em}}
.hero h1 span{{color:#e63946}}
.hero p{{font-family:'Open Sans',sans-serif;font-size:18px;opacity:.8;max-width:560px;margin:0 auto 36px}}
.features{{padding:96px 0 72px;background:#f1faee}}
.features h2{{text-align:center;font-size:40px;font-weight:800;text-transform:uppercase;letter-spacing:-.02em;margin-bottom:8px}}
.features .sub{{text-align:center;font-family:'Open Sans',sans-serif;color:#457b9d;font-size:16px;margin-bottom:56px}}
.feat-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px}}
.feat{{background:#fff;border-radius:4px;padding:32px;border-top:4px solid #e63946;box-shadow:0 2px 16px rgba(0,0,0,.06)}}
.feat .num{{font-size:48px;font-weight:800;color:#e63946;line-height:1}}
.feat h3{{font-size:18px;font-weight:800;margin:12px 0 8px;text-transform:uppercase;letter-spacing:.03em}}
.feat p{{font-family:'Open Sans',sans-serif;color:#457b9d;font-size:14px;line-height:1.6}}
.cta-section{{background:#e63946;color:#fff;text-align:center;padding:72px 0}}
.cta-section h2{{font-size:40px;font-weight:800;text-transform:uppercase;letter-spacing:-.02em;margin-bottom:16px}}
.cta-section p{{font-family:'Open Sans',sans-serif;font-size:17px;opacity:.9;margin-bottom:32px}}
.btn-dark{{background:#1d3557;color:#fff}}
.btn-dark:hover{{background:#12253a}}
.contact{{background:#1d3557;color:#fff;padding:56px 0;text-align:center}}
.contact-row{{display:flex;flex-wrap:wrap;justify-content:center;gap:48px;margin-top:32px}}
.citem h4{{font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:#a8dadc;margin-bottom:6px}}
.citem p{{font-size:18px;font-weight:700}}
footer{{background:#0d1b2a;color:#457b9d;padding:24px 0;text-align:center;font-family:'Open Sans',sans-serif;font-size:13px}}
@media(max-width:600px){{.hero{{clip-path:none;padding:72px 0}}}}
</style></head><body>
<nav><div class="container inner">
  <div class="logo">{name}</div>
  <a href="tel:{phone}" class="nav-cta">Call Now</a>
</div></nav>
<section class="hero"><div class="container">
  <div class="label">⭐ {rating} Stars · {reviews} Reviews</div>
  <h1>{headline.replace(' ', '<br>', 1) if len(headline) > 25 else headline}</h1>
  <p>{city}'s most trusted — {reviews} customers can't be wrong. Call today and see why.</p>
  <a href="tel:{phone}" class="btn btn-primary">Get Started Now →</a>
</div></section>
<section class="features"><div class="container">
  <h2>Why Choose Us</h2>
  <div class="sub">The results speak for themselves</div>
  <div class="feat-grid">
    <div class="feat"><div class="num">{reviews}</div><h3>Happy Clients</h3><p>Real reviews from real customers in {city}. Zero paid reviews, all organic.</p></div>
    <div class="feat"><div class="num">{rating}</div><h3>Star Rating</h3><p>Consistently ranked among the best in the area on Google Maps.</p></div>
    <div class="feat"><div class="num">48h</div><h3>Fast Response</h3><p>We respond to every inquiry within hours, not days. Time is money.</p></div>
    <div class="feat"><div class="num">100%</div><h3>Satisfaction</h3><p>We don't stop until you're completely happy with the result.</p></div>
  </div>
</div></section>
<section class="cta-section"><div class="container">
  <h2>Don't Wait. Call Today.</h2>
  <p>Free consultation. No obligation. Just results.</p>
  <a href="tel:{phone}" class="btn btn-dark">📞 {phone}</a>
</div></section>
<section class="contact"><div class="container">
  <h2 style="font-size:28px;font-weight:800;text-transform:uppercase">Find Us</h2>
  <div class="contact-row">
    <div class="citem"><h4>Address</h4><p>{addr}</p></div>
    <div class="citem"><h4>Phone</h4><p>{phone}</p></div>
    <div class="citem"><h4>Rating</h4><p>⭐ {rating} ({reviews})</p></div>
  </div>
</div></section>
<footer><div class="container">© 2025 {name} &nbsp;·&nbsp; Demo site by <strong style="color:#a8dadc">NobleWeb Agency</strong> — $400 flat, 48-hr delivery</div></footer>
</body></html>"""


# ── Lead-specific page configs ─────────────────────────────────────────────

PAGE_CONFIGS = {
    "a1b2c3d4": {
        "modern":  lambda b: _restaurant_modern(b),
        "elegant": lambda b: _generic_elegant(b, "Taste the Tradition,\nFeel the Warmth"),
        "bold":    lambda b: _generic_bold(b, "Authentic. Fresh. Unforgettable."),
    },
    "b2c3d4e5": {
        "modern":  lambda b: _generic_modern(b, "Your Car Fixed Right,\nThe First Time", {"title":"Full Diagnostics","desc":"State-of-the-art diagnostic equipment to find problems fast and fix them right."},{"title":"Same-Day Service","desc":"Most repairs completed the same day. No waiting weeks for your car back."},{"title":"Honest Pricing","desc":"Transparent quotes before we start. No hidden fees, ever."}),
        "elegant": lambda b: _generic_elegant(b, "Precision Auto Care\nYou Can Trust"),
        "bold":    lambda b: _generic_bold(b, "Expert Auto Repair. Honest Prices."),
    },
    "c3d4e5f6": {
        "modern":  lambda b: _generic_modern(b, "Nails That Make You\nFeel Amazing", {"title":"Gel & Acrylics","desc":"Long-lasting gel and acrylic sets by certified technicians using premium products."},{"title":"Nail Art","desc":"From minimalist to intricate designs — our artists bring your vision to life."},{"title":"Spa Packages","desc":"Full relaxation packages including mani, pedi, and massage add-ons."}),
        "elegant": lambda b: _generic_elegant(b, "Where Beauty Meets\nPerfection"),
        "bold":    lambda b: _generic_bold(b, "Nails. Art. Perfection."),
    },
    "d4e5f6g7": {
        "modern":  lambda b: _generic_modern(b, "A Smile You'll\nLove to Show", {"title":"General Dentistry","desc":"Cleanings, fillings, and preventive care to keep your smile healthy for life."},{"title":"Cosmetic Dentistry","desc":"Whitening, veneers, and bonding to give you the smile you've always wanted."},{"title":"Gentle & Caring","desc":"Anxiety-free dentistry for all ages. We make every visit comfortable."}),
        "elegant": lambda b: _generic_elegant(b, "Expert Dental Care\nWith a Gentle Touch"),
        "bold":    lambda b: _generic_bold(b, "Beautiful Smiles Start Here."),
    },
    "e5f6g7h8": {
        "modern":  lambda b: _generic_modern(b, "Get Stronger.\nGet Healthier.\nGet Results.", {"title":"Modern Equipment","desc":"The latest cardio and strength equipment to maximize every workout session."},{"title":"Expert Trainers","desc":"Certified personal trainers available to guide you toward your fitness goals."},{"title":"All Fitness Levels","desc":"Whether you're a beginner or elite athlete, FitLife has a program for you."}),
        "elegant": lambda b: _generic_elegant(b, "Elevate Your Fitness.\nTransform Your Life."),
        "bold":    lambda b: _generic_bold(b, "Train Hard. Live Better."),
    },
    "f6g7h8i9": {
        "modern":  lambda b: _generic_modern(b, "Your Property,\nPerfectly Maintained", {"title":"Lawn Care","desc":"Weekly and bi-weekly mowing, edging, and cleanup to keep your lawn pristine."},{"title":"Landscaping Design","desc":"Transform your outdoor space with custom landscape design and installation."},{"title":"Seasonal Cleanup","desc":"Spring and fall cleanup, leaf removal, and seasonal planting services."}),
        "elegant": lambda b: _generic_elegant(b, "Landscapes That\nInspire"),
        "bold":    lambda b: _generic_bold(b, "Beautiful Yards. Every Time."),
    },
}


def build_all():
    leads = state.list_all("checked")
    built_count = 0

    for lead in leads:
        lid = lead["id"]
        if lid not in PAGE_CONFIGS:
            continue

        biz = lead["business"]
        print(f"\nBuilding pages for: {biz['name']}")
        pages = []

        for style, generator in PAGE_CONFIGS[lid].items():
            html = generator(biz)
            filename = f"{lid}_{style}.html"
            path = BUILT_DIR / filename
            path.write_text(html, encoding="utf-8")
            pages.append({"style": style, "file": str(path), "vibe": style})
            print(f"  ✓ {style} ({len(html):,} chars) → {filename}")

        lead["pages"] = pages
        state.save("checked", lead)
        built_count += 1

    print(f"\n{built_count} leads with pages built → state/built/")
    print(f"{len(list(BUILT_DIR.glob('*.html')))} HTML files in state/built/")


if __name__ == "__main__":
    build_all()
