"""Generates the placeholder (grayscale, stuff-tintable) textures. Run from repo root."""
from PIL import Image, ImageDraw, ImageFilter
import random

S = 128
T = "Textures/Slopkea/"
random.seed(7)

def blank():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))

def table_top():
    im = Image.new("RGBA", (S, S), (225, 225, 225, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, S, 32):  # planks
        d.line([(0, y), (S, y)], fill=(190, 190, 190, 255), width=2)
        for _ in range(6):
            gy = y + random.randint(4, 28)
            d.line([(random.randint(0, 60), gy), (random.randint(70, S), gy)], fill=(210, 210, 210, 255))
    return im

def table_edge():
    im = blank(); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, S, 9], fill=(150, 150, 150, 255))
    d.line([(0, 10), (S, 10)], fill=(90, 90, 90, 160), width=2)
    return im

def table_leg():
    im = blank(); d = ImageDraw.Draw(im)
    d.rectangle([S - 22, 4, S - 5, 21], fill=(110, 110, 110, 255), outline=(70, 70, 70, 255))
    return im

def seat():
    im = blank(); d = ImageDraw.Draw(im)
    d.rounded_rectangle([2, 2, S - 3, S - 3], radius=14, fill=(215, 215, 215, 255), outline=(150, 150, 150, 255), width=3)
    d.rounded_rectangle([14, 40, S - 15, S - 14], radius=12, outline=(180, 180, 180, 255), width=2)
    return im

def back():
    im = blank(); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, S - 1, 34], radius=10, fill=(175, 175, 175, 255), outline=(110, 110, 110, 255), width=3)
    return im

def arm():
    im = blank(); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, S - 1, 22], radius=10, fill=(185, 185, 185, 255), outline=(110, 110, 110, 255), width=3)
    return im

def rot(im, deg):  # clockwise
    return im.rotate(-deg)

def comp(*layers):
    out = blank()
    for l in layers:
        out = Image.alpha_composite(out, l)
    return out

tt, te, tl = table_top(), table_edge(), table_leg()
tt.save(T + "Table/Table_Top.png"); te.save(T + "Table/Table_Edge.png"); tl.save(T + "Table/Table_Leg.png")
comp(tt, *[rot(te, a) for a in (0, 90, 180, 270)], *[rot(tl, a) for a in (0, 90, 180, 270)]).save(T + "Table/Table_Icon.png")

se, ba, ar = seat(), back(), arm()
se.save(T + "Sectional/Sectional_Seat.png"); ba.save(T + "Sectional/Sectional_Back.png"); ar.save(T + "Sectional/Sectional_Arm.png")
comp(se, ba, rot(ar, 90), rot(ar, 270)).save(T + "Sectional/Sectional_Icon.png")

# Workshop preview: a little L sectional next to a table blob.
prev = Image.new("RGBA", (640, 360), (48, 52, 58, 255))
cells = {(1, 1): 180, (2, 1): 180, (3, 1): 180, (1, 2): 90, (1, 3): 90}
for (x, y), facing in cells.items():
    tile = comp(se, rot(ba, (facing + 180) % 360))
    prev.alpha_composite(tile.resize((64, 64)), (x * 64, y * 64 - 32))
for x in range(5, 9):
    for y in range(1, 4):
        prev.alpha_composite(tt.resize((64, 64)), (x * 64, y * 64 - 32))
ImageDraw.Draw(prev).text((20, 320), "SLOPKEA  -  some assembly required", fill=(255, 204, 0, 255))
prev.convert("RGB").save("About/Preview.png")
