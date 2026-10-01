"""Every variant plus a few assembled layouts on one sheet, for review.
python3 Source/Art/contact_sheet.py /tmp/sheet.png"""
import sys
from PIL import Image, ImageDraw

from compose import render, tinted
from draw_sprites import FACINGS, ROCKER_KINDS, SIDE_STATES, rocker_path, sect_path, table_path
from slopkea_draw import CELL

WOOD = (133, 94, 62)
FABRIC = (70, 110, 150)
T = 96  # thumbnail cell


def scenes():
    # U-shaped sectional around a coffee spot, and an L table.
    s = {}
    for x in range(1, 5):
        s[(x, 5)] = ("sect", "south")
    for z in range(2, 5):
        s[(0, z)] = ("sect", "east")
        s[(5, z)] = ("sect", "west")
    s[(0, 5)] = ("sect", "south")
    s[(5, 5)] = ("sect", "south")
    t = {}
    for x in range(1, 5):
        for z in range(1, 3):
            t[(x, z)] = ("table",)
    for z in range(3, 5):
        t[(1, z)] = ("table",)
    t[(0, 1)] = ("sect", "east")
    t[(5, 2)] = ("sect", "west")
    t[(2, 0)] = ("sect", "north")
    t[(3, 3)] = ("sect", "south")
    return s, t


def main(out):
    tables = [tinted(table_path(i), WOOD) for i in range(16)]
    sects = [tinted(sect_path(f, a, b), FABRIC, sect_path(f, a, b, True))
             for f in FACINGS for a in SIDE_STATES for b in SIDE_STATES]
    s, t = scenes()
    u = render(s, {"table": WOOD, "sect": FABRIC}, (6, 6), T)
    lt = render(t, {"table": WOOD, "sect": FABRIC}, (6, 6), T)
    sheet = Image.new("RGBA", (12 * T + 40, 4 * T + 2 * T + 6 * T + 80), (40, 40, 44, 255))
    d = ImageDraw.Draw(sheet)
    d.text((10, 4), "table variants 0-15 (bits N1 E2 S4 W8 = joined)", fill="white")
    for i, im in enumerate(tables):
        sheet.alpha_composite(im.resize((T // 2 * 2, T // 2 * 2)), (10 + (i % 8) * (T + 4), 20 + (i // 8) * (T + 4)))
    y0 = 20 + 2 * (T + 4) + 10
    d.text((10, y0 - 14), "sectional: rows north/east/south/west, cols cw,ccw in a/j/c", fill="white")
    small = T // 2
    for i, im in enumerate(sects):
        r, c = divmod(i, 9)
        sheet.alpha_composite(im.resize((small, small)), (10 + c * (small + 4), y0 + r * (small + 4)))
    y1 = y0 + 4 * (small + 4) + 20
    d.text((10, y1 - 14), "assembled: U sectional; L table with seats", fill="white")
    sheet = sheet.crop((0, 0, max(sheet.width, 2 * u.width + 30), y1 + u.height + 10))
    sheet.alpha_composite(u, (10, y1))
    sheet.alpha_composite(lt, (20 + u.width, y1))
    # Rocking chairs, one row per kind, all four views.
    y2 = sheet.height + 20
    full = Image.new("RGBA", (sheet.width, y2 + 2 * (T + 4) + 10), (40, 40, 44, 255))
    full.alpha_composite(sheet, (0, 0))
    ImageDraw.Draw(full).text((10, y2 - 14), "rocking chairs: wood (all stuff), cloth (stuff upholstery, oak frame)", fill="white")
    for r, (kind, color) in enumerate(zip(ROCKER_KINDS, (WOOD, (150, 60, 60)))):
        for c, f in enumerate(FACINGS):
            m = rocker_path(kind, f, True) if kind == "Cloth" else None
            full.alpha_composite(tinted(rocker_path(kind, f), color, m).resize((T, T)), (10 + c * (T + 4), y2 + r * (T + 4)))
    # Desk, rug and shelving, assembled.
    sc = {}
    for x in range(1, 5):
        sc[(x, 6)] = ("shelf", "south")
    for z in range(3, 6):
        sc[(0, z)] = ("shelf", "east")
        sc[(9, z)] = ("shelf", "west")
    for x in range(6, 9):
        sc[(x, 6)] = ("shelf", "north")
    for x in range(3, 7):
        sc[(x, 2)] = ("desk",)
    for z in range(0, 2):
        sc[(6, z)] = ("desk",)
    sc[(3, 1)] = ("sect", "north")
    sc[(5, 1)] = ("sect", "north")
    rugs = {(x, z) for x in range(2, 8) for z in range(3, 6)} | {(8, 4), (8, 5), (2, 2), (2, 1)}
    mod = render(sc, {"table": WOOD, "sect": FABRIC}, (10, 8), 64, rugs=rugs)
    y3 = full.height + 20
    final = Image.new("RGBA", (max(full.width, mod.width + 20), y3 + mod.height + 10), (40, 40, 44, 255))
    final.alpha_composite(full, (0, 0))
    ImageDraw.Draw(final).text((10, y3 - 14), "cube shelving (all four facings), L desk, rug with inside corners", fill="white")
    final.alpha_composite(mod, (10, y3))
    final.convert("RGB").save(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "sheet.png")
