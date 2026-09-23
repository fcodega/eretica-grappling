"""Genera gli asset web ottimizzati per ereticajiujitsu.com.
Gli originali in assets/ restano intatti e fanno da sorgente."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

ROOT = r"C:\Personal_proj\eretica-grappling"
A = os.path.join(ROOT, "assets")
FONT_BLACK = r"C:\Windows\Fonts\ariblk.ttf"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
ACCENT = (255, 62, 62)


def kb(p):
    return round(os.path.getsize(p) / 1024, 1)


def report(p):
    im = Image.open(p)
    print(f"  {os.path.basename(p):24s} {str(im.size):14s} {kb(p):7.1f} KB")


def logo_alpha(size_h):
    """Logo bianco su fondo trasparente, altezza size_h."""
    src = Image.open(os.path.join(A, "logo_small.jpg")).convert("L")
    w = round(src.width * size_h / src.height)
    src = src.resize((w, size_h), Image.LANCZOS)
    # le linee sono bianche su nero: la luminanza diventa il canale alpha
    white = Image.new("L", src.size, 255)
    out = Image.merge("LA", (white, src))
    return out


def cover(im, tw, th):
    """Crop centrale in stile background-size: cover."""
    sr, tr = im.width / im.height, tw / th
    if sr > tr:
        nw = round(im.height * tr)
        box = ((im.width - nw) // 2, 0, (im.width + nw) // 2, im.height)
    else:
        nh = round(im.width / tr)
        box = (0, (im.height - nh) // 2, im.width, (im.height + nh) // 2)
    return im.crop(box).resize((tw, th), Image.LANCZOS)


def save_jpg(im, name, quality):
    p = os.path.join(A, name)
    im.convert("RGB").save(p, "JPEG", quality=quality, optimize=True, progressive=True)
    report(p)


# ---------------------------------------------------------------- 1. logo nav
print("\nLogo e icone")
p = os.path.join(A, "logo-nav.png")
logo_alpha(96).save(p, "PNG", optimize=True)
report(p)

# watermark di sfondo (sostituisce l'immagine hotlinkata da bjjee.com)
p = os.path.join(A, "watermark.png")
logo_alpha(800).convert("RGBA").quantize(colors=8, method=Image.FASTOCTREE).save(p, "PNG", optimize=True)
report(p)

# favicon + apple touch icon dal PNG con alpha
fav = Image.open(os.path.join(A, "favicon.png")).convert("RGBA")
p = os.path.join(A, "favicon-32.png")
fav.resize((32, 32), Image.LANCZOS).save(p, "PNG", optimize=True)
report(p)
p = os.path.join(A, "apple-touch-icon.png")
# apple touch icon non supporta la trasparenza: fondo nero
at = Image.new("RGBA", fav.size, (0, 0, 0, 255))
at.alpha_composite(fav)
at.convert("RGB").resize((180, 180), Image.LANCZOS).quantize(colors=64, method=Image.MEDIANCUT).save(p, "PNG", optimize=True)
report(p)

# ---------------------------------------------------------------- 2. foto web
print("\nFoto")
anto = Image.open(os.path.join(A, "anto.jpg")).convert("L")
save_jpg(anto.resize((1100, 1100), Image.LANCZOS), "hero-bg.jpg", 56)

coach = Image.open(os.path.join(A, "coach.JPG")).convert("L")
save_jpg(coach.resize((1600, round(1600 * coach.height / coach.width)), Image.LANCZOS),
         "coach-web.jpg", 76)

kids = Image.open(os.path.join(A, "kids.jpg")).convert("L")
save_jpg(kids.resize((800, round(800 * kids.height / kids.width)), Image.LANCZOS),
         "tatami-web.jpg", 74)

# ---------------------------------------------------------------- 3. og image
print("\nOpen Graph 1200x630")


def og(src_name, out_name, title_lines, kicker, darken=0.42):
    src = Image.open(os.path.join(A, src_name)).convert("L")
    base = cover(src, 1200, 630).convert("RGB")
    base = ImageEnhance.Brightness(base).enhance(1 - darken * 0.5)

    # velo scuro dal basso, per far staccare il testo
    veil = Image.new("L", (1, 630))
    for y in range(630):
        t = y / 629
        veil.putpixel((0, y), int(255 * min(1.0, 0.15 + 0.85 * (t ** 1.6))))
    veil = veil.resize((1200, 630))
    black = Image.new("RGB", (1200, 630), (0, 0, 0))
    base = Image.composite(black, base, veil.point(lambda v: int(v * 0.82)))

    d = ImageDraw.Draw(base)

    # logo in alto a sinistra
    lg = logo_alpha(112)
    base.paste(Image.new("RGB", lg.size, (255, 255, 255)), (64, 52), lg.getchannel("A"))

    f_title = ImageFont.truetype(FONT_BLACK, 82 if len(title_lines) > 1 else 96)
    f_kick = ImageFont.truetype(FONT_BOLD, 30)

    y = 630 - 104
    d.text((64, y), kicker, font=f_kick, fill=(190, 190, 190))
    y -= 22
    for line in reversed(title_lines):
        bbox = d.textbbox((0, 0), line, font=f_title)
        y -= (bbox[3] - bbox[1]) + 30
        d.text((64, y - bbox[1]), line, font=f_title, fill=(255, 255, 255))

    # barra rossa sopra il blocco di testo
    d.rectangle([64, y - 34, 64 + 76, y - 26], fill=ACCENT)

    p = os.path.join(A, out_name)
    base.save(p, "JPEG", quality=84, optimize=True, progressive=True)
    report(p)


og("anto.jpg", "og-home.jpg", ["ERETICA"], "BJJ & GRAPPLING  ·  SONDRIO")
og("coach.JPG", "og-prova.jpg", ["PRIMA LEZIONE", "GRATUITA"], "ERETICA  ·  SONDRIO")
og("kids.jpg", "og-bambini.jpg", ["BJJ PER BAMBINI"], "DAI 5 ANNI  ·  SONDRIO")

print("\nTotale nuovo peso per pagina tipo (logo+favicon+hero): ", end="")
tot = sum(kb(os.path.join(A, f)) for f in ["logo-nav.png", "favicon-32.png", "hero-bg.jpg"])
print(f"{tot:.1f} KB")
