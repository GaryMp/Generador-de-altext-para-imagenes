from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 630
BG       = "#ffffff"
GREEN    = "#228B22"
GOLD     = "#8B6914"
RED      = "#DC143C"
DARK     = "#1a1a1a"
GRAY     = "#555555"
LIGHT    = "#f8f9fa"
BORDER   = "#e9ecef"

img  = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# --- Intentar cargar fuentes del sistema (Windows) ---
def font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/Arial Bold.ttf" if bold else "C:/Windows/Fonts/Arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

# --- Barra rasta superior ---
bar_h = 10
seg = W // 3
draw.rectangle([0, 0, seg, bar_h], fill=GREEN)
draw.rectangle([seg, 0, seg * 2, bar_h], fill=GOLD)
draw.rectangle([seg * 2, 0, W, bar_h], fill=RED)

# --- Fondo sutil central ---
draw.rectangle([60, 80, W - 60, H - 60], fill=LIGHT, outline=BORDER, width=2)

# --- Logo: GaryText Pro ---
f_logo_gary = font(82, bold=True)
f_logo_text = font(82, bold=True)
f_logo_pro  = font(82, bold=True)

gary_w = draw.textlength("Gary", font=f_logo_gary)
text_w = draw.textlength("Text", font=f_logo_text)
pro_w  = draw.textlength(" Pro", font=f_logo_pro)
total_logo_w = gary_w + text_w + pro_w

x = (W - total_logo_w) / 2
y = 140

draw.text((x, y),            "Gary", font=f_logo_gary, fill=DARK)
draw.text((x + gary_w, y),   "Text", font=f_logo_text, fill=GREEN)
draw.text((x + gary_w + text_w, y), " Pro", font=f_logo_pro, fill=GOLD)

# --- Tagline ---
f_tag = font(32)
tagline = "Generador de textos alternativos gratis con IA"
tag_w = draw.textlength(tagline, font=f_tag)
draw.text(((W - tag_w) / 2, 270), tagline, font=f_tag, fill=GRAY)

# --- Separador ---
sep_y = 340
sep_w = 160
draw.rectangle([(W - sep_w) / 2, sep_y, (W + sep_w) / 2, sep_y + 3],
               fill=GREEN)

# --- Badges ---
f_badge = font(24, bold=True)
badges = [
    ("✓ WCAG 2.2 AA",     GREEN),
    ("✓ Español e inglés", GOLD),
    ("✓ Sin registro",     RED),
    ("✓ 100% gratis",      "#0056b3"),
]

badge_pad_x, badge_pad_y = 22, 10
badge_r = 8
total_badge_w = sum(
    draw.textlength(t, font=f_badge) + badge_pad_x * 2
    for t, _ in badges
) + (len(badges) - 1) * 16

bx = (W - total_badge_w) / 2
by = 370

for text_b, color in badges:
    tw = draw.textlength(text_b, font=f_badge)
    bw = tw + badge_pad_x * 2
    bh = 44
    draw.rounded_rectangle([bx, by, bx + bw, by + bh],
                            radius=badge_r, fill=color)
    draw.text((bx + badge_pad_x, by + badge_pad_y),
              text_b, font=f_badge, fill="white")
    bx += bw + 16

# --- URL footer ---
f_url = font(22)
url_text = "descubrir.digitalaccessibility.cl"
url_w = draw.textlength(url_text, font=f_url)
draw.text(((W - url_w) / 2, 470), url_text, font=f_url, fill=GRAY)

# --- Barra rasta inferior ---
draw.rectangle([0, H - 8, seg, H], fill=GREEN)
draw.rectangle([seg, H - 8, seg * 2, H], fill=GOLD)
draw.rectangle([seg * 2, H - 8, W, H], fill=RED)

# --- Guardar ---
out = "docs/og-image.png"
img.save(out, "PNG", optimize=True)
print(f"✓ og-image.png generada: {W}x{H}px → {out}")
