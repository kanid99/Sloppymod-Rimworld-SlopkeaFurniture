"""About/Preview.png (640x360) and About/ModIcon.png (256x256), in the SloppyMods
store-art house style (see the TrashPower and Mending make_about_art.py): a dark
charcoal card, SLOPPYMODS label, two-tone title with an accent rule, a short
tagline, and the mod's own in-game art - here a furnished room laid out by the
same join rules as the game, plus a strip of single pieces.

python3 Source/Art/make_about_art.py   (from the repo root)
"""
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, "Source/Art")
from compose import render, tinted  # noqa: E402
from draw_sprites import rocker_path  # noqa: E402

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, H = 640, 360
ACCENT = (255, 204, 0, 255)          # flat-pack yellow, the mod's one accent
WOOD, OAK, FABRIC, RUG, WHITE = (150, 108, 70), (176, 132, 88), (88, 120, 164), (170, 64, 52), (236, 234, 228)


def shadow(img, blur=7, alpha=140, off=(3, 5)):
    pad = blur * 3
    sh = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", img.size, (0, 0, 0, alpha)), (pad + off[0], pad + off[1]), img.split()[3])
    return sh.filter(ImageFilter.GaussianBlur(blur)), pad


def place(card, img, pos):
    assert pos[0] >= 0 and pos[1] >= 0 and pos[0] + img.width <= W and pos[1] + img.height <= H, (pos, img.size)
    sh, pad = shadow(img)
    card.alpha_composite(sh, (pos[0] - pad, pos[1] - pad))
    card.alpha_composite(img, pos)


def room():
    """A kitchen-diner: a kitchen run and cube shelving along the back wall, an L sectional on a
    rug, and a dragged-out table with a bench and chairs."""
    sc = {}
    for x, m in enumerate(("Cabinet", "Sink", "Cabinet", "Hob")):
        sc[(x, 7)] = (m, "south")
    for x in range(5, 8):
        sc[(x, 7)] = ("shelf", "south")
    for x in range(0, 4):
        sc[(x, 5)] = ("sect", "south")
    for z in range(2, 5):
        sc[(0, z)] = ("sect", "east")
    for x in range(4, 8):
        for z in range(2, 4):
            sc[(x, z)] = ("table",)
    for x in range(4, 8):
        sc[(x, 1)] = ("Bench", "north")
    sc[(5, 4)] = ("sect", "south")
    sc[(6, 4)] = ("sect", "south")
    rugs = {(x, z) for x in range(1, 4) for z in range(1, 5)}
    return render(sc, {"table": WOOD, "sect": FABRIC, "Cabinet": WHITE, "Sink": WHITE, "Hob": WHITE, "shelf": WHITE, "Bench": WOOD, "rug": RUG},
                  (8, 8), 40, bg=None, rugs=rugs)


def piece(path, color, mask=None, size=44):
    im = tinted(path, color, mask)
    im = im.crop(im.getbbox())
    s = size / max(im.size)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


def main():
    card = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(card)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip((48, 44, 40), (26, 24, 22))) + (255,))

    # The room stands on a plank floor, so it reads as a room rather than loose
    # pieces (the Riimba preview's floor does the same job).
    hero = room()
    floor = Image.new("RGBA", hero.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(floor)
    fd.rounded_rectangle([0, 0, hero.width - 1, hero.height - 1], radius=10, fill=(84, 70, 58, 255))
    for k, y in enumerate(range(0, hero.height, 20)):
        fd.line([(6, y), (hero.width - 7, y)], fill=(70, 58, 48, 255), width=2)
        for x in range(((k * 53) % 90) + 10, hero.width - 10, 90):
            fd.line([(x, y), (x, y + 19)], fill=(70, 58, 48, 255), width=2)
    floor.alpha_composite(hero)
    place(card, floor, (W - floor.width - 18, (H - floor.height) // 2))

    d = ImageDraw.Draw(card)
    d.text((30, 36), "SLOPPYMODS", font=ImageFont.truetype(BOLD, 18), fill=(146, 142, 136, 255))
    d.text((30, 60), "SLOPKEA", font=ImageFont.truetype(BOLD, 46), fill=(238, 234, 228, 255))
    d.text((30, 106), "FURNITURE", font=ImageFont.truetype(BOLD, 34), fill=ACCENT)
    d.line([(32, 152), (200, 152)], fill=ACCENT, width=3)
    for i, line in enumerate(("Flat-pack furniture that", "joins up into any shape.", "Some assembly required.")):
        d.text((30, 162 + i * 20), line, font=ImageFont.truetype(BOLD, 15), fill=(168, 164, 158, 255))

    # A strip of single pieces, each in its own tile, as Entertaining Ideas does.
    tiles = [piece(rocker_path("Cloth", "south"), FABRIC, rocker_path("Cloth", "south", True)),
             piece(rocker_path("Wood", "south"), WOOD),
             piece("Textures/Things/Building/Furniture/Slopkea/Kitchen/Slopkea_Hob_south.png", WHITE,
                   "Textures/Things/Building/Furniture/Slopkea/Kitchen/Slopkea_Hob_southm.png"),
             piece("Textures/Things/Building/Furniture/Slopkea/Planter/Slopkea_Planter_0.png", WOOD,
                   "Textures/Things/Building/Furniture/Slopkea/Planter/Slopkea_Planter_0_m.png"),
             piece("Textures/Things/Building/Furniture/Slopkea/Wardrobe/Slopkea_Wardrobe_south.png", OAK,
                   "Textures/Things/Building/Furniture/Slopkea/Wardrobe/Slopkea_Wardrobe_southm.png")]
    x0, y0, tw = 30, 252, 50
    d.rectangle([x0 - 4, y0 - 4, x0 + len(tiles) * tw + 2, y0 + tw + 2], fill=(30, 28, 26, 255), outline=(70, 66, 62, 255))
    for k, t in enumerate(tiles):
        card.alpha_composite(t, (x0 + k * tw + (tw - 2 - t.width) // 2, y0 + (tw - t.height) // 2))
    card.convert("RGB").save("About/Preview.png")

    # Shown at about 32px in the mod list: one sectional corner, filling it.
    icon_scene = {(0, 1): ("sect", "south"), (1, 1): ("sect", "south"), (0, 0): ("sect", "east")}
    src = render(icon_scene, {"sect": FABRIC, "table": WOOD}, (2, 2), 128, bg=None)
    src = src.crop(src.getbbox())
    s = 250 / max(src.size)
    small = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
    icon = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    icon.alpha_composite(small, ((256 - small.width) // 2, (256 - small.height) // 2))
    icon.save("About/ModIcon.png")
    print("wrote About/Preview.png and About/ModIcon.png")


if __name__ == "__main__":
    main()
